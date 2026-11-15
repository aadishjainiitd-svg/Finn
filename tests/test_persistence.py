import asyncio
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from backend import repository,portfolio,store
from backend.main import app


@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.delenv('FINN_DATABASE_URL',raising=False)
    monkeypatch.setattr(repository,'DATA',tmp_path)
    monkeypatch.setattr(store,'DATA',tmp_path)
    repository.init();store.init()


def test_concurrent_compare_and_swap_has_one_winner():
    original=repository.save('alice','state','book',{'holdings':[]},expected=0)
    def writer(i):
        try:repository.save('alice','state','book',{'winner':i},expected=original['_version']);return True
        except repository.Conflict:return False
    with ThreadPoolExecutor(max_workers=8) as pool:assert sum(pool.map(writer,range(8)))==1
    assert repository.get('alice','state','book')['_version']==2
    assert repository.get('bob','state','book') is None


def test_quota_reservation_is_atomic_and_survives_restart():
    from backend.admission import reserve
    from backend.network import SourceError
    def writer(_):
        try:reserve('test-day',7600,at=10000);return True
        except SourceError:return False
    with ThreadPoolExecutor(max_workers=8) as pool:assert sum(pool.map(writer,range(8)))==1
    repository.init()
    with pytest.raises(SourceError):reserve('test-day',7600,at=10030)
    next=reserve('test-day',7600,at=10062)
    assert next['requests']==2 and next['reserved_tokens']==15200


def test_immutable_evidence_survives_reinitialisation_and_replacement():
    first={'version':'bytes1-parser1','hash':'bytes1','symbol':'TCS','period':'FY2026'}
    repository.retain_document(first,[{'id':'bytes1-p1','page':1,'text':'Revenue was 100 crore.'}])
    repository.init()
    repository.retain_document({**first,'version':'bytes2-parser1','hash':'bytes2'},
                               [{'id':'bytes2-p1','page':1,'text':'Restated revenue was 99 crore.'}])
    assert repository.evidence('bytes1-p1')['text']=='Revenue was 100 crore.'
    assert repository.evidence('bytes2-p1')['text']=='Restated revenue was 99 crore.'
    assert repository.evidence('unknown') is None


def test_two_browsers_are_isolated_and_cross_origin_mutation_rejected():
    with TestClient(app) as alice,TestClient(app) as bob:
        a=alice.get('/api/session');b=bob.get('/api/session')
        assert a.status_code==b.status_code==200
        assert 'httponly' in a.headers['set-cookie'].lower()
        mutation={'action':'pin','event_id':'event','value':True}
        assert alice.post('/api/review',json=mutation).status_code==403
        assert alice.post('/api/review',json=mutation,headers={'X-Finn-Request':'1','Origin':'https://evil.invalid'}).status_code==403
        assert alice.post('/api/review',json=mutation,headers={'X-Finn-Request':'1'}).status_code==200
        assert bob.get('/api/session').json()['review']['pins']=={}
        assert alice.get('/api/session').json()['review']['pins']=={'event':True}


def test_private_answers_and_completed_jobs_survive_memory_loss_without_cross_owner_access():
    import hashlib
    from backend import research
    from backend.owners import COOKIE
    with TestClient(app) as alice,TestClient(app) as bob:
        alice.get('/api/session');bob.get('/api/session')
        token=alice.cookies.get(COOKIE)
        identity=repository.get('_system','sessions',hashlib.sha256(token.encode()).hexdigest())['owner']
        repository.save(identity,'history','answer',{'question':'Private research question','answer':{'status':'partial'}})
        repository.save(identity,'jobs','completed-private',{'owner':identity,'id':'completed-private','status':'complete','result':{'status':'partial'}})
        research.jobs.pop('completed-private',None)
        assert alice.get('/api/jobs/completed-private').status_code==200
        assert bob.get('/api/jobs/completed-private').status_code==410
        assert len(alice.get('/api/history').json()['items'])==1
        assert bob.get('/api/history').json()['items']==[]
        assert 'owner' not in alice.get('/api/jobs/completed-private').json()


def test_visit_freezes_cutoff_and_new_revision_reopens_without_losing_pin(monkeypatch):
    monkeypatch.setattr(portfolio.time,'time',lambda:100000)
    first=portfolio.update_review('a','visit')['visit']
    monkeypatch.setattr(portfolio.time,'time',lambda:100001)
    assert portfolio.update_review('a','visit')['visit']['cutoff']==first['cutoff']
    portfolio.update_review('a','review','e','v1')
    portfolio.update_review('a','pin','e',value=True)
    monkeypatch.setattr(portfolio.time,'time',lambda:103000)
    state=portfolio.update_review('a','visit')
    assert state['visit']['cutoff']==100000
    assert state['reviewed']['e']!='v2' and state['pins']['e']


def test_critical_floor_and_unknown_inputs_are_explained():
    event={'id':'e','symbol':'TCS','tier':0,'assessment':'assessed','kind':'filing',
           'reason':'Auditor resigned.','published_at':'2026-11-15','evidence':[]}
    state={'feedback':{'e':'noise'},'promotions':[]}
    ranked=portfolio.rank([event],[{'symbol':'TCS','weight':'0','thesis':''}],state)[0]
    assert ranked['tier']==0 and ranked['thesis_status']=='unknown'
    assert any(r['label']=='Your feedback' for r in ranked['ranking_reasons'])


def test_two_tabs_freeze_independent_cutoffs_and_reload_keeps_its_own(monkeypatch):
    monkeypatch.setattr(portfolio.time,'time',lambda:100000)
    a=portfolio.update_review('owner','visit',visit_id='a'*32)
    monkeypatch.setattr(portfolio.time,'time',lambda:100010)
    b=portfolio.update_review('owner','visit',visit_id='b'*32)
    assert b['visit']['cutoff']==a['visit']['opened_at']
    assert a['visit']['cutoff']==13600
    monkeypatch.setattr(portfolio.time,'time',lambda:100020)
    reloaded=portfolio.update_review('owner','visit',visit_id='a'*32)
    assert reloaded['visit']['cutoff']==a['visit']['cutoff']
    assert portfolio.review('owner','b'*32)['visit']==b['visit']
    assert 'visits' not in reloaded
    shared=portfolio.update_review('owner','pin','filing',value=True,visit_id='a'*32)
    assert shared['visit']['cutoff']==a['visit']['cutoff']
    assert portfolio.review('owner','b'*32)['pins']['filing']
    monkeypatch.setattr(portfolio.time,'time',lambda:300000)
    returned=portfolio.update_review('owner','visit',visit_id='a'*32)
    assert returned['visit']['returning'] and returned['visit']['cutoff']==100010


def test_http_visit_header_projects_the_correct_tab_state():
    with TestClient(app) as client:
        a={'X-Finn-Request':'1','X-Finn-Visit':'a'*32};b={**a,'X-Finn-Visit':'b'*32}
        one=client.post('/api/review',json={'action':'visit'},headers=a).json()
        two=client.post('/api/review',json={'action':'visit'},headers=b).json()
        assert client.get('/api/session',headers=a).json()['review']['visit']==one['visit']
        assert client.get('/api/session',headers=b).json()['review']['visit']==two['visit']
        assert two['visit']['cutoff']==one['visit']['opened_at']


def test_category_promotion_is_reversible_and_does_not_rewrite_the_source():
    event={'id':'e','revision':'v','symbol':'TCS','tier':3,'assessment':'routine','kind':'filing','category':'Routine notice',
           'reason':'Routine notice.','published_at':'2026-11-15','description':'Routine notice','evidence':[]}
    promoted=portfolio.update_review('a','promote','e',value=True,events=[event])
    assert portfolio.rank([event],[{'symbol':'TCS','weight':None}],promoted)[0]['tier']==1
    undone=portfolio.update_review('a','promote','e',value=False,events=[event])
    assert portfolio.rank([event],[{'symbol':'TCS','weight':None}],undone)[0]['tier']==3
    assert event['tier']==3 and not undone['reviewed']


def test_import_is_atomic_and_does_not_normalise_or_execute(monkeypatch):
    async def identity(symbol):return {'symbol':symbol,'name':symbol,'isin':'TEST'}
    monkeypatch.setattr(portfolio,'identity',identity)
    original=portfolio.book('a')
    with pytest.raises(Exception):asyncio.run(portfolio.save_book('a',[{'symbol':'TCS','weight':80},{'symbol':'INFY','weight':30}],original['_version']))
    assert portfolio.book('a')==original
    with pytest.raises(Exception):asyncio.run(portfolio.validate_holdings(portfolio.parse_import('=HYPERLINK("evil")')))
    changed=asyncio.run(portfolio.save_book('a',[{'symbol':'TCS','weight':None,'thesis':'My thesis'}],original['_version']))
    assert changed['holdings'][0]['weight'] is None
    assert not changed['is_demo']


# Regression: same-origin HTTPS page behind a TLS-terminating proxy (Render).
# Found by gstack /review + /qa-only probe on 2026-11-15: the app sees http while
# the browser sends an https Origin, so every write was rejected with 403.
def test_same_origin_https_page_behind_tls_proxy_can_mutate_and_cookie_is_secure():
    host='finn.example'
    with TestClient(app,base_url='http://'+host) as page:
        headers={'X-Finn-Request':'1','Origin':'https://'+host,'X-Forwarded-Proto':'https'}
        response=page.post('/api/review',json={'action':'pin','event_id':'event','value':True},headers=headers)
        assert response.status_code==200
        assert 'secure' in response.headers['set-cookie'].lower()
        # A different host is still cross-origin, whatever the scheme.
        assert page.post('/api/review',json={'action':'pin','event_id':'e2','value':True},
            headers={**headers,'Origin':'https://evil.invalid'}).status_code==403


# Regression: adversarial review F8. Anonymous reads must not write a demo-book
# row per visitor; the first explicit save still inserts the book.
def test_anonymous_read_does_not_persist_default_book(monkeypatch):
    from backend import portfolio
    with TestClient(app) as page:
        assert page.get('/api/session').status_code==200
        owner_rows=[r for r in repository.listing('_system','sessions')]
        assert len(owner_rows)==1
        identity=owner_rows[0]['owner']
        assert repository.get(identity,'state','book') is None
        assert portfolio.book(identity)['_version']==0


def test_expired_session_rows_are_pruned_hourly_and_live_ones_kept(tmp_path,monkeypatch):
    import time
    from backend import repository,owners
    monkeypatch.setenv('FINN_DATABASE_URL','');monkeypatch.setattr(repository,'DATA',tmp_path);repository.init()
    repository.save('_system','sessions','old',{'owner':'a','expires':1})
    repository.save('_system','sessions','live',{'owner':'b','expires':time.time()+100})
    repository.save('owner-a','book','default',{'holdings':[]})
    with repository.transaction() as tx:tx.execute("UPDATE records SET updated=? WHERE id='old'",(time.time()-owners.LIFETIME-10,))
    monkeypatch.setattr(owners,'_pruned',0.0)
    assert owners.prune()==1
    assert repository.get('_system','sessions','old') is None and repository.get('_system','sessions','live')
    assert repository.get('owner-a','book','default')  # private state is not deleted here
    assert owners.prune()==0  # at most hourly
