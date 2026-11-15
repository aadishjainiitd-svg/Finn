import {test,expect,type Page} from '@playwright/test';
const date=new Date().toISOString();
const evidence={id:'fixture-p1-c0',hash:'fixturehash',symbol:'TCS',name:'Fixture issuer',kind:'filing',title:'Director appointment',period:'Fixture date',page:1,text:'The board approved the appointment of a director for one year.',url:'https://example.com/filing.pdf',original_url:'https://example.com/filing.pdf',fetched_at:date};
const event={id:'fixture-event',revision:'r1',symbol:'TCS',name:'Fixture issuer',kind:'filing',tier:0,assessment:'assessed',title:'Director appointed for one year',description:'Fixture disclosure',reason:'Board change; review the terms.',published_at:date,checked_at:date,url:evidence.url,evidence:[evidence]};
const brief={events:[event],coverage:Array.from({length:15},(_,i)=>({symbol:i===0?'TCS':'TEST'+i,price:{status:'live',session:date.slice(0,10),close:100},filings:{status:'live',checked_at:date}})),checked_at:date,filing_checked_at:date,source_status:'live',is_demo_seed:false,counts:{fetched_filings:1,distinct_filings:1,exact_duplicates:0,pending:0,routine:0}};
const answer=(symbol:string)=>({status:'supported',company:{symbol,name:symbol+' fixture issuer'},question:'What does this company do?',claims:[{text:symbol+' fixture answer',nature:'reported',citations:[]}],evidence:[],documents:[],gaps:[],answered_at:date,cache_hit:false,limitation:'Controlled browser fixture'});
export async function fixture(page:Page,returning=false){
 const review={reviewed:{} as Record<string,string>,pins:{} as Record<string,boolean>,feedback:{},promotions:[],eligible:{[event.id]:event.revision},visit:{opened_at:Date.now()/1000,active_at:Date.now()/1000,cutoff:Date.now()/1000-(returning?3:1)*86400,first:!returning,returning},_version:1};
 await page.route('**/api/history',r=>r.fulfill({json:{items:[]}}));await page.route('**/api/active-jobs',r=>r.fulfill({json:{items:[]}}));
 await page.route('**/api/session',r=>r.fulfill({json:{book:{holdings:brief.coverage.map(c=>({symbol:c.symbol,weight:null,thesis:'',inputs:[],sector:''})),is_demo:true,_version:1,label:'Fixture'},review,storage:{mode:'fixture',recovery:'Fixture isolation'},telegram:{configured:false,connected:false}}}));
 await page.route('**/api/review',r=>{const body=r.request().postDataJSON();if(body.action==='review')review.reviewed[body.event_id]=body.revision;if(body.action==='undo')delete review.reviewed[body.event_id];if(body.action==='pin'){if(body.value)review.pins[body.event_id]=true;else delete review.pins[body.event_id];}return r.fulfill({json:review});});
 await page.route('**/api/today',r=>r.fulfill({json:brief}));await page.route('**/api/evidence/**',r=>r.fulfill({json:evidence}));
}

test('mobile review persists, nested evidence opening does not acknowledge, Escape returns focus',async({page})=>{
 await fixture(page);await page.goto('/');const open=page.getByRole('button',{name:/TCS.*Director appointed/});await open.click();
 await expect(page.getByRole('dialog')).toBeVisible();await page.getByRole('button',{name:'Inspect supporting evidence'}).click();
 await expect(page.locator('[role=dialog]')).toHaveCount(2);await expect(page.getByRole('dialog')).toHaveCount(1);await expect(page.locator('blockquote')).toHaveText(evidence.text);
 await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:'Inspect supporting evidence'})).toBeFocused();
 await page.keyboard.press('Escape');await expect(open).toBeFocused();
 await page.getByRole('button',{name:'Mark done'}).click();await expect(page.getByRole('heading',{name:'0 things need you'})).toBeVisible();await page.getByRole('button',{name:'Undo last review'}).click();await expect(page.getByRole('button',{name:'Mark done'})).toBeVisible();await page.getByRole('button',{name:'Mark done'}).click();
 await page.reload();await page.getByLabel('Digest period').selectOption('14');await page.getByRole('button',{name:'Reviewed · Undo'}).click();await expect(page.getByRole('button',{name:'Mark done'})).toBeVisible();
 for(const width of [390,360,430]){await page.setViewportSize({width,height:844});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);}
});

for(const order of ['old-first','new-first'])test('late research response cannot replace selected company: '+order,async({page})=>{
 await fixture(page);let finishOld:()=>void=()=>{},finishNew:()=>void=()=>{};let oldSeen=false,newSeen=false;
 await page.route('**/api/research',async r=>{const symbol=r.request().postDataJSON().symbol;await new Promise<void>(resolve=>{if(symbol==='TCS'){finishOld=resolve;oldSeen=true;}else{finishNew=resolve;newSeen=true;}});await r.fulfill({json:{id:symbol,status:'complete',result:answer(symbol)}});});
 await page.goto('/');await page.getByRole('button',{name:'Ask',exact:true}).click();await page.getByLabel('NSE company symbol').fill('TCS');await page.getByRole('button',{name:'Investigate company'}).click();await expect.poll(()=>oldSeen).toBe(true);
 await page.getByLabel('NSE company symbol').fill('INFY');await page.getByRole('button',{name:'Investigate company'}).click();await expect.poll(()=>newSeen).toBe(true);
 if(order==='old-first'){finishOld();await page.waitForTimeout(50);finishNew();}else{finishNew();await expect(page.getByText('INFY fixture answer')).toBeVisible();finishOld();}
 await expect(page.getByText('INFY fixture answer')).toBeVisible();await expect(page.getByText('TCS fixture answer')).toHaveCount(0);
});

test('generation failure retains document coverage, missing-source gap and evidence',async({page})=>{
 await fixture(page);await page.route('**/api/research',r=>r.fulfill({json:{id:'quota',status:'error',stage:'Could not complete',error:{code:'daily_quota',message:'Shared answer allowance reached.'},documents:[{...evidence,kind:'transcript',period:'Q2 FY27'}],evidence:[evidence],gaps:[{kind:'annual',message:'Document processing exceeded the hosting memory budget.'}]}}));
 await page.goto('/');await page.getByRole('button',{name:'Ask',exact:true}).click();await page.getByLabel('NSE company symbol').fill('TEST');await page.getByRole('button',{name:'Investigate company'}).click();
 await expect(page.getByText('Shared answer allowance reached.')).toBeVisible();await expect(page.getByText('Earnings call · Q2 FY27')).toBeVisible();await expect(page.getByText(/Annual report: Document processing exceeded/)).toBeVisible();await expect(page.getByText('The sources are still here')).toBeVisible();
});

test('coverage loss is visible without events being reordered',async({page})=>{
 await fixture(page);await page.clock.install();let reads=0;await page.route('**/api/today',r=>r.fulfill({json:++reads===1?brief:{...brief,source_status:'unavailable',coverage:brief.coverage.map(c=>({...c,filings:{...c.filings,status:'unavailable'}}))}}));
 await page.goto('/');await expect(page.getByRole('button',{name:'Coverage 15/15'})).toBeVisible();await page.clock.fastForward(61000);await expect(page.getByRole('button',{name:'Coverage 0/15'})).toBeVisible();await expect(page.getByRole('button',{name:/TCS.*Director appointed/})).toBeVisible();
});

test('lost source version retains saved quote and explicitly marks unavailable',async({page})=>{
 await fixture(page);await page.route('**/api/evidence/**',r=>r.fulfill({status:410,json:{error:{code:'version_unavailable'}}}));await page.goto('/');await page.getByRole('button',{name:/TCS.*Director appointed/}).click();await page.getByRole('button',{name:'Inspect supporting evidence'}).click();
 await expect(page.getByText(/Version unavailable on the server/)).toBeVisible();await expect(page.locator('blockquote')).toHaveText(evidence.text);await expect(page.getByRole('link',{name:/Open original/})).toHaveAttribute('href',evidence.url+'#page=1');
});

test('failed first check is not called quiet, and slow filing cannot open over Research',async({page})=>{
 await fixture(page);await page.route('**/api/today',r=>r.fulfill({status:503,json:{error:{message:'Fixture exchange unavailable'}}}));await page.goto('/');await expect(page.getByText('Fixture exchange unavailable')).toBeVisible();await expect(page.getByText('Nothing needs you in this view.')).toHaveCount(0);
 await page.unroute('**/api/today');await fixture(page);await page.route('**/api/today',r=>r.fulfill({json:{...brief,events:[{...event,evidence:[]}]}}));await page.reload();let finish:()=>void=()=>{};
 await page.route('**/api/filings/**/assess',async r=>{await new Promise<void>(resolve=>finish=resolve);await r.fulfill({json:{id:'slow',status:'complete',result:{evidence:[evidence]}}});});
 await page.getByRole('button',{name:/TCS.*Director appointed/}).click();await page.getByRole('button',{name:'Inspect supporting evidence'}).click();await expect(page.getByText('Reading the attachment…')).toBeVisible();await page.keyboard.press('Escape');await page.getByRole('button',{name:'Research',exact:true}).click();finish();await page.waitForTimeout(100);await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.getByRole('heading',{name:'Understand the business.'})).toBeVisible();
});

test('Research keeps scope warning and five-year source headers inspectable',async({page})=>{
 await fixture(page);
 const source={...evidence,kind:'annual',version:'fixture-v1',period:'Annual summary 2025',text:'FIVE-YEAR SUMMARY (INR in Crore) 2025 2024 2023 2022 2021 Revenue 100 90 80 70 60'};
 await page.route('**/api/research-pack/TEST',r=>r.fulfill({json:{pack:{company:{symbol:'TEST',name:'Fixture issuer'},documents:[source],gaps:[],sections:[],checked_at:date,coverage_note:'Fixture only; accounting basis unspecified.',facts:[2025,2024,2023,2022,2021].map((year,i)=>({metric:'revenue',reported_label:'Revenue',year:String(year),crore:String(100-i*10),scope:'unspecified',qualification:'Fixture only',comparison_status:'No verified fiscal dates',evidence:source,quote:source.text,header_quote:'FIVE-YEAR SUMMARY'}))}}}));
 await page.goto('/');await page.getByRole('button',{name:'Research',exact:true}).click();await page.getByLabel('Research any NSE ticker').fill('TEST');await page.getByRole('button',{name:'Open saved research'}).click();
 await expect(page.getByText(/Accounting scope not specified/)).toBeVisible();await expect(page.getByRole('img',{name:/2021: 60 crore/})).toBeVisible();
 await page.getByRole('button',{name:/Inspect header, row/}).click();await expect(page.locator('blockquote')).toHaveText(source.text);
 await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:/Inspect header, row/})).toBeFocused();
});


test('installed production shell reloads offline without acknowledging an item',async({page,context})=>{
 test.skip(!process.env.FINN_E2E_URL,'Requires a production preview with the actual service worker.');
 await fixture(page);await page.goto('/');
 await expect(page.getByRole('button',{name:'Mark done'})).toBeVisible();
 await page.evaluate(async()=>{await navigator.serviceWorker.ready;});
 await expect.poll(()=>page.evaluate(()=>!!navigator.serviceWorker.controller)).toBe(true);
 await expect.poll(()=>page.evaluate(()=>!!localStorage.getItem('finn.offline.v1'))).toBe(true);
 const keys=await page.evaluate(async()=>{const names=await caches.keys();return (await Promise.all(names.map(async n=>(await (await caches.open(n)).keys()).map(r=>new URL(r.url).pathname)))).flat();});
 expect(keys.some(k=>k.startsWith('/api/'))).toBe(false);
 await context.setOffline(true);await page.reload();
 await expect(page.getByText(/Offline · read-only saved snapshot/)).toBeVisible();
 await page.getByRole('button',{name:'Mark done'}).click();
 await expect(page.getByText(/Offline. Reconnect before changing saved state/)).toBeVisible();
 await expect(page.getByRole('button',{name:'Mark done'})).toBeVisible();
 await context.setOffline(false);
 await expect(page.getByText(/Back online. This view is still the saved snapshot/)).toBeVisible();
 await page.getByRole('button',{name:'Reload stored data'}).click();
 await expect(page.getByText(/Back online. This view/)).toHaveCount(0);
});


test('book Ask uses an explicit saved scope and shows missing-company coverage',async({page})=>{
 await fixture(page);let payload:any=null;
 await page.route('**/api/research',r=>{payload=r.request().postDataJSON();return r.fulfill({json:{id:'book-answer',status:'complete',result:{...answer('BOOK'),status:'partial',gaps:[{kind:'coverage',message:'INFY: no readable retained primary documents.'}]}}});});
 await page.goto('/');await page.getByRole('button',{name:'Ask',exact:true}).click();
 await page.getByLabel('Question scope').selectOption('portfolio');
 await page.getByLabel('What do you want to understand?').fill('What risks are disclosed across my book?');
 await page.getByRole('button',{name:'Investigate book'}).click();
 await expect(page.getByText('BOOK fixture answer')).toBeVisible();
 await expect(page.getByText('INFY: no readable retained primary documents.')).toBeVisible();
 expect(payload.scope).toBe('portfolio');expect(payload.filing_id).toBeUndefined();
 await expect(page.getByRole('button',{name:'Create a watch'})).toHaveCount(0);
 await page.getByLabel('Question scope').selectOption('company');
 await expect(page.getByLabel('NSE company symbol')).toBeVisible();
 await expect(page.getByText('BOOK fixture answer')).toHaveCount(0);
});

test('browser Back closes only the top sheet and retains the underlying item',async({page})=>{
 await fixture(page);await page.goto('/');const open=page.getByRole('button',{name:/TCS.*Director appointed/});await open.click();
 const inspect=page.getByRole('button',{name:'Inspect supporting evidence'});await inspect.click();
 await expect(page.locator('[role=dialog]')).toHaveCount(2);await page.goBack();
 await expect(page.locator('[role=dialog]')).toHaveCount(1);await expect(inspect).toBeFocused();
 await page.goBack();await expect(page.locator('[role=dialog]')).toHaveCount(0);await expect(open).toBeFocused();
 await expect(page.getByRole('button',{name:'Mark done'})).toBeVisible();
 await open.click();await page.getByRole('button',{name:'Ask about this event'}).click();
 await expect(page.getByRole('heading',{name:'Ask what matters.'})).toBeVisible();
 await page.goBack();await expect(page.locator('[role=dialog]')).toHaveCount(0);
});

test('return recap groups real event dates without acknowledging them',async({page})=>{
 await fixture(page,true);await page.goto('/');await page.getByText('Review changes by day').click();
 await expect(page.getByText(/Missing days are not proof/)).toBeVisible();
 await page.getByRole('button',{name:/1 event.*TCS.*1 to review/}).click();
 await expect(page.getByLabel('Digest period')).toHaveValue('custom');
 await expect(page.getByRole('button',{name:'Mark done'})).toBeVisible();
});

test('stats direct route shows only the returned owner usage and closes to Today',async({page})=>{
 await fixture(page);await page.route('**/api/stats',r=>r.fulfill({json:{observed_tokens:37,unknown_usage_jobs:1,cached_answers:2,answered_questions:3,cost_note:'Fixture cost unknown',coverage_note:'Owner-only fixture',reports:[]}}));
 await page.goto('/stats');await expect(page.getByRole('heading',{name:'Behind FINN'})).toBeVisible();
 await expect(page.getByText('Observed model tokens')).toBeVisible();await expect(page.getByText('37',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Close Behind FINN'}).click();await expect(page).toHaveURL(/\/$/);await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('quarterly results distinguish current and comparator columns with nested source access',async({page})=>{
 await fixture(page);const source={quote:evidence.text,evidence};
 const results={tables:[{scope:'consolidated',industry_schema:'general',page:1,periods:['2026-09-30','2026-06-30','2025-09-30'],unit:'₹ crore',headers:[source,source,source,source,source],items:[{metric:'revenue',label:'Total revenue from operations',values:['120','100','80'],qoq:'20',yoy:'50',...source}],comparison_basis:'Controlled test fixture; not investment data'}],gaps:[]};
 await page.route('**/api/today',r=>r.fulfill({json:{...brief,events:[{...event,results}]}}));
 await page.goto('/');await page.getByRole('button',{name:/TCS.*Director appointed/}).click();await page.getByText('Results first cut · verified rows').click();
 await expect(page.getByRole('cell',{name:'20%',exact:true})).toBeVisible();await expect(page.getByRole('cell',{name:'50%',exact:true})).toBeVisible();
 await page.getByText('Inspect operands and filing pages').click();await page.getByRole('button',{name:'Inspect quarter column 2'}).click();
 await expect(page.locator('blockquote')).toHaveText(evidence.text);await page.goBack();await expect(page.getByRole('button',{name:'Inspect quarter column 2'})).toBeFocused();
});


test('tab navigation preserves input and scroll across browser Back',async({page})=>{
 await fixture(page);await page.goto('/');await page.getByRole('button',{name:'Book',exact:true}).click();
 await page.getByLabel('Find a holding').fill('TEST');await page.evaluate(()=>scrollTo(0,600));
 await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(500);
 await page.getByRole('button',{name:'Ask',exact:true}).click();
 await page.getByLabel('NSE company symbol').fill('ABB');
 await page.goBack();await expect(page.getByRole('button',{name:'Book',exact:true})).toHaveAttribute('aria-current','page');
 await expect(page.getByLabel('Find a holding')).toHaveValue('TEST');
 await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(500);
 await page.goForward();await expect(page.getByLabel('NSE company symbol')).toHaveValue('ABB');
});

test('pinning creates one separate unfinished card, done removes it and undo restores it',async({page})=>{
 await fixture(page);await page.goto('/');await page.getByRole('button',{name:'Pin TCS',exact:true}).click();
 const section=page.getByRole('region',{name:'Pinned unfinished'});
 await expect(section).toBeVisible();await expect(page.getByRole('button',{name:/TCS.*Director appointed/})).toHaveCount(1);
 await section.getByRole('button',{name:'Mark done'}).click();await expect(section).toHaveCount(0);
 await page.getByRole('button',{name:'Undo last review'}).click();await expect(section).toBeVisible();
 await section.getByRole('button',{name:'Unpin TCS'}).click();await expect(section).toHaveCount(0);
 await expect(page.getByRole('button',{name:/TCS.*Director appointed/})).toHaveCount(1);
});

test('return playback is the recap even when Today is filtered to another period',async({page})=>{
 await fixture(page,true);await page.goto('/');await page.getByLabel('Digest period').selectOption('custom');
 await page.getByLabel('From',{exact:true}).fill('2020-01-01');await page.getByLabel('To',{exact:true}).fill('2020-01-02');
 await page.getByRole('button',{name:'Listen to this recap'}).click();
 await expect(page.getByText(/FINN return recap/)).toContainText('Director appointed for one year');
 await expect(page.getByText(/Reads the same retained day-by-day return recap/)).toBeVisible();
});


test('thesis evidence retains contradiction and broken requires an explicit user judgement',async({page})=>{
 await fixture(page);const holding={symbol:'TCS',weight:null,thesis:'Demand stays resilient.',thesis_version:'v1',sector:'',inputs:[]};
 await page.route('**/api/session',r=>r.fulfill({json:{book:{holdings:[holding],is_demo:true,_version:1,label:'Fixture'},review:{reviewed:{},pins:{},feedback:{},promotions:[],visit:null,_version:1},storage:{mode:'fixture',recovery:'Fixture'},telegram:{configured:false}}}));
 let broken=false,confirmations=0;
 const record={thesis:holding.thesis,thesis_version:'v1',title:event.title,checked_at:date,observations:[{effect:'supports',sources:[{quote:'Controlled supporting fixture.',evidence}]},{effect:'weakens',sources:[{quote:'Controlled adverse fixture.',evidence}]}]};
 await page.route('**/api/holding/TCS',r=>r.fulfill({json:{holding,bars:[],read_across:[],checked_at:date,price_basis:'Fixture',thesis:{status:broken?'broken':'weakening',assessed:1,total:1,unknown:0,note:'Fixture interpretations, not investment data.',confirmation:broken?{broken,confirmed_at:date}:null,items:[{event_id:event.id,title:event.title,effect:'weakens',assessment:record}],versions:[{id:'v1',thesis:holding.thesis,created_at:date}],history:[]}}}));
 await page.route('**/api/thesis/judgement',r=>{const body=r.request().postDataJSON();expect(body.thesis_version).toBe('v1');broken=body.broken;confirmations++;return r.fulfill({json:{broken}});});
 await page.goto('/');await page.getByRole('button',{name:'Book',exact:true}).click();await page.getByRole('button',{name:/TCS.*NSE holding/}).click();
 await expect(page.getByRole('heading',{name:'Thesis evidence · weakening'})).toBeVisible();expect(confirmations).toBe(0);
 await page.getByText(event.title+' · weakens',{exact:true}).click();await expect(page.getByText('Controlled supporting fixture.')).toBeVisible();await expect(page.getByText('Controlled adverse fixture.')).toBeVisible();
 await page.getByText('Record my judgement',{exact:true}).click();await page.getByRole('button',{name:'I confirm this thesis is broken'}).click();
 await expect(page.getByRole('heading',{name:'Thesis evidence · broken'})).toBeVisible();expect(confirmations).toBe(1);
 await page.getByRole('button',{name:'Clear my broken-thesis judgement'}).click();await expect(page.getByRole('heading',{name:'Thesis evidence · weakening'})).toBeVisible();
});


test('follow-up retains event scope and new ticker clears the parent',async({page})=>{
 await fixture(page);const requests:any[]=[];
 await page.route('**/api/research',r=>{const body=r.request().postDataJSON();requests.push(body);return r.fulfill({json:{id:'answer-'+requests.length,status:'complete',result:{...answer(body.symbol),question:body.question,history_id:'answer-'+requests.length,filing_id:body.filing_id}}});});
 await page.goto('/');await page.getByRole('button',{name:/TCS.*Director appointed/}).click();await page.getByRole('button',{name:'Ask about this event'}).click();
 await page.getByRole('button',{name:'Investigate company'}).click();await page.getByRole('button',{name:'Ask a follow-up'}).click();
 await expect(page.getByText('Following up in this scope')).toBeVisible();await page.getByLabel('What do you want to understand?').fill('And what qualified that outlook?');await page.getByRole('button',{name:'Investigate company'}).click();
 await expect.poll(()=>requests.length).toBe(2);expect(requests[1].parent_id).toBe('answer-1');expect(requests[1].filing_id).toBe(event.id);
 await page.getByRole('button',{name:'Ask a follow-up'}).click();await page.getByLabel('NSE company symbol').fill('INFY');await page.getByLabel('What do you want to understand?').fill('What does the company disclose?');await page.getByRole('button',{name:'Investigate company'}).click();
 await expect.poll(()=>requests.length).toBe(3);expect(requests[2].parent_id).toBeUndefined();expect(requests[2].filing_id).toBeUndefined();
});


test('balanced research labels interpretation and keeps a missing adverse side explicit',async({page})=>{
 await fixture(page);const source={...evidence,kind:'annual',version:'fixture-v1',period:'2025'};
 await page.route('**/api/research-pack/TEST',r=>r.fulfill({json:{pack:{company:{symbol:'TEST',name:'Fixture issuer'},documents:[source],gaps:[],sections:[],facts:[],checked_at:date,coverage_note:'Fixture only',narrative:{status:'partial',observations:[{aspect:'favourable',nature:'interpretation',sources:[{quote:source.text,evidence:source}]}],missing:['business','adverse','accounting'],coverage:'Controlled narrative fixture.',limitation:'Not an exhaustive risk audit.'}}}}));
 await page.goto('/');await page.getByRole('button',{name:'Research',exact:true}).click();await page.getByLabel('Research any NSE ticker').fill('TEST');await page.getByRole('button',{name:'Open saved research'}).click();await page.getByRole('link',{name:'Bull & bear',exact:true}).click();
 await expect(page.getByText('FINN interpretation',{exact:true})).toBeVisible();await expect(page.getByText('No adverse point passed the source checks. This side of the case is incomplete.')).toBeVisible();await page.getByRole('button',{name:/Annual report · 2025 · p. 1/}).click();await expect(page.getByRole('dialog').locator('blockquote')).toHaveText(source.text);
});
