"""On-demand, immutable-source research coverage shared by issuer, not owner."""
import json
from . import store,repository
from .sources import identity,discover,now
from .documents import ingest,retrieve
from .network import SourceError
from .facts import summary_facts
from .report_insights import compare_reports,commitment_ledger
from . import statements,results,segments

POLICY='primary-pack-v2'
LEGACY_POLICY='primary-pack-v1'
TOPICS={
    'overview':('Business and revenue mix','business segments products revenue mix'),
    'cash':('Where the cash went','cash flow investing capital expenditure acquisition dividend borrowing'),
    'promises':('Management commitments','guidance target expect plan achieve next year'),
    'flags':('Risks and accounting notes','risk contingent liability impairment auditor related party'),
    'bull_bear':('Evidence for and against','growth demand opportunity risks challenges uncertainty'),
    'balance':('Balance sheet and cash quality','cash receivables inventory debt borrowings operating cash flow'),
}


def key(symbol):return POLICY+'-'+symbol


async def build(progress,symbol,annual_count=2):
    from .research import worker
    async with worker:
        progress['stage']='Verifying company identity'
        company=await identity(symbol)
        previous=repository.get('_public','research_packs',key(symbol))
        # An ordinary refresh must not silently discard an explicitly expanded
        # historical document set.
        annual_count=max(annual_count,(previous or {}).get('annual_reports_requested',2))
        annual_count=max(2,min(5,annual_count))
        progress['stage']=f'Discovering {annual_count} annual reports and four calls'
        sources=await discover(company,annual_count=annual_count,transcript_count=4)
        docs=[];gaps=[]
        for source in sources:
            progress['stage']='Reading '+source['title']+' · '+source['discovery_period']
            try:docs.append(await ingest(company,source,progress))
            except SourceError as exc:gaps.append({'kind':source['kind'],'period':source['discovery_period'],'message':exc.message,'url':source['original_url']})
        for kind,required in [('annual',annual_count),('transcript',4)]:
            count=sum(d['kind']==kind for d in docs)
            if count<required:gaps.append({'kind':kind,'message':f'{count} of {required} requested {kind} documents verified and readable.'})
        if not docs:raise SourceError('no_readable_documents','No issuer-verified documents could be read.')
        progress['stage']='Indexing supported research sections'
        sections=[];facts=[];statement_facts=[];mixes=[]
        for section,(label,query) in TOPICS.items():
            selected=[d for d in docs if d['kind']==('transcript' if section=='promises' else 'annual')]
            evidence=retrieve(selected,query)[:3] if selected else []
            sections.append({'id':section,'label':label,'evidence':evidence,
                'status':'source_passages' if evidence else 'missing_documents',
                'note':'Relevant source passages for inspection; no numerical reconciliation or verdict has been inferred.'})
        for doc in docs:
            if doc['kind']!='annual':continue
            with store.db() as c:
                rows=c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(doc['version'],)).fetchall()
            facts.extend(summary_facts(doc,rows))
            extracted=statements.extract(doc,rows);statement_facts.extend(extracted)
            mixes.extend(segments.extract(doc,rows,extracted))
        # Reuse the latest retained filing versions for quarter actuals. This
        # does not promise discovery of an unobserved historical quarter.
        quarterly_facts=[];quarterly_sources=[]
        with store.db() as c:
            retained=c.execute("SELECT meta FROM documents WHERE symbol=? AND kind='filing' ORDER BY json_extract(meta,'$.fetched_at') DESC LIMIT 24",(symbol,)).fetchall()
        used=set()
        for record in retained:
            meta=json.loads(record['meta'])
            if meta['hash'] in used or store.cached('latest-document-filing-'+meta['download_url'])!=meta['version']:continue
            used.add(meta['hash'])
            with store.db() as c:
                rows=c.execute('SELECT id,page,text FROM chunks WHERE hash=? ORDER BY page,id',(meta['version'],)).fetchall()
            typed=results.comparable_facts(results.extract(meta,rows)['tables'])
            if typed:quarterly_facts.extend(typed);quarterly_sources.append(meta)
        progress['stage']='Comparing report wording and retaining management commitments'
        from .narrative import build as narrative_view
        narrative=await narrative_view(docs,progress)
        if narrative.get('status')=='unavailable' and previous and previous.get('narrative',{}).get('observations'):
            from .narrative import sanitise
            versions={d['version'] for d in docs}
            earlier=previous['narrative']
            if all(s['evidence'].get('version') in versions for item in earlier['observations'] for s in item['sources']):
                narrative={**sanitise(earlier),'retained_selection':True,'selection_checked_at':previous['checked_at'],
                    'refresh_error':narrative.get('error'),'limitation':'Using the previous dated selection from the same immutable sources. No fresh model conclusion was generated.'}
        result={'narrative':narrative,'company':company,'documents':docs,'gaps':gaps,'sections':sections,'facts':facts,
                'report_changes':compare_reports(docs),'commitments':commitment_ledger(docs,[*statement_facts,*quarterly_facts]),
                'quarterly_actual_sources':quarterly_sources,
                'financials':statements.compact(statements.analyse(statement_facts)),
                'revenue_mix':segments.latest(mixes),
                'checked_at':now(),'policy':POLICY,'is_demo_seed':False,'annual_reports_requested':annual_count,
                'coverage_note':f'{sum(d["kind"]=="annual" for d in docs)} reports and {sum(d["kind"]=="transcript" for d in docs)} calls read. Readable documents do not guarantee five comparable years. Source-summary values retain their disclosed basis; unknown scope is never consolidated.'}
        repository.save('_public','research_packs',key(symbol),result)
        progress.update(status='complete',stage='Sources indexed',result=result)
        return result


def get(symbol):
    current=repository.get('_public','research_packs',key(symbol))
    if current:
        if current.get('narrative'):
            from .narrative import sanitise
            current={**current,'narrative':sanitise(current['narrative'])}
        return current
    previous=repository.get('_public','research_packs',LEGACY_POLICY+'-'+symbol)
    return {**previous,'update_available':True} if previous else None


FACT_FIELDS=('metric','reported_label','crore','scope','scope_basis','period_start','period_end','quote','evidence_id','headers')


def slim(pack):
    """Response shape for the phone: one copy of each header citation set, no
    unused fact fields, and no legacy summary facts once statements cover it.
    Stored packs are unchanged."""
    if not pack:return pack
    financials=pack.get('financials')
    if not financials or not financials.get('facts'):return pack
    sets={};facts={}
    for fid,fact in financials['facts'].items():
        headers=fact.get('headers') or []
        signature=json.dumps(headers,sort_keys=True)
        hid=sets.setdefault(signature,'h'+str(len(sets)))
        facts[fid]={**{k:fact[k] for k in FACT_FIELDS if k in fact and k!='headers'},'header_set':hid}
    header_sets={hid:json.loads(signature) for signature,hid in sets.items()}
    out={**pack,'financials':{**financials,'facts':facts,'header_sets':header_sets}}
    if financials.get('trajectory'):out['facts']=[]
    return out
