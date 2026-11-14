import {test,expect,type Page} from '@playwright/test';
const date=new Date().toISOString();
const evidence={id:'fixture-p1-c0',hash:'fixturehash',symbol:'TCS',name:'Fixture issuer',kind:'filing',title:'Director appointment',period:'Fixture date',page:1,text:'The board approved the appointment of a director for one year.',url:'https://example.com/filing.pdf',original_url:'https://example.com/filing.pdf',fetched_at:date};
const event={id:'fixture-event',revision:'r1',symbol:'TCS',name:'Fixture issuer',kind:'filing',tier:0,assessment:'assessed',title:'Director appointed for one year',description:'Fixture disclosure',reason:'Board change; review the terms.',published_at:date,checked_at:date,url:evidence.url,evidence:[evidence]};
const brief={events:[event],coverage:Array.from({length:15},(_,i)=>({symbol:'TEST'+i,price:{status:'live',session:date.slice(0,10),close:100},filings:{status:'live',checked_at:date}})),checked_at:date,filing_checked_at:date,source_status:'live',is_demo_seed:false,counts:{fetched_filings:1,distinct_filings:1,exact_duplicates:0,pending:0,routine:0}};
const answer=(symbol:string)=>({status:'supported',company:{symbol,name:symbol+' fixture issuer'},question:'What does this company do?',claims:[{text:symbol+' fixture answer',nature:'reported',citations:[]}],evidence:[],documents:[],gaps:[],answered_at:date,cache_hit:false,limitation:'Controlled browser fixture'});
async function fixture(page:Page){await page.route('**/api/brief',r=>r.fulfill({json:brief}));await page.route('**/api/evidence/**',r=>r.fulfill({json:evidence}));}

test('mobile review persists, evidence opening does not acknowledge, Escape returns focus',async({page})=>{
 await fixture(page);await page.goto('/');const open=page.getByRole('button',{name:'Evidence',exact:true});await open.click();
 await expect(page.getByRole('dialog')).toBeVisible();await expect(page.getByRole('button',{name:'Close evidence'})).toBeFocused();
 await page.keyboard.press('Tab');await expect(page.getByText('Show surrounding context')).toBeFocused();await page.keyboard.press('Tab');await expect(page.getByRole('link',{name:/Open original/})).toBeFocused();await page.keyboard.press('Escape');await expect(open).toBeFocused();
 await expect(page.getByRole('button',{name:'Mark reviewed'})).toBeVisible();await page.getByRole('button',{name:'Mark reviewed'}).click();await expect(page.getByText('0 to review')).toBeVisible();
 await page.reload();await expect(page.getByText('A quieter review window')).toBeVisible();await page.getByLabel('Review window').selectOption('14');await page.getByRole('button',{name:/Reviewed Undo/}).click();await expect(page.getByRole('button',{name:'Mark reviewed'})).toBeVisible();
 for(const width of [390,360]){await page.setViewportSize({width,height:844});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);}
});

for(const order of ['old-first','new-first'])test('late research response cannot replace selected company: '+order,async({page})=>{
 await fixture(page);let finishOld:()=>void=()=>{},finishNew:()=>void=()=>{};let oldSeen=false,newSeen=false;
 await page.route('**/api/research',async r=>{const symbol=r.request().postDataJSON().symbol;await new Promise<void>(resolve=>{if(symbol==='TCS'){finishOld=resolve;oldSeen=true;}else{finishNew=resolve;newSeen=true;}});await r.fulfill({json:{id:symbol,status:'complete',result:answer(symbol)}});});
 await page.goto('/');await page.getByRole('button',{name:'Research',exact:true}).click();await page.getByLabel('NSE company symbol').fill('TCS');await page.getByRole('button',{name:'Investigate company'}).click();await expect.poll(()=>oldSeen).toBe(true);
 await page.getByLabel('NSE company symbol').fill('INFY');await page.getByRole('button',{name:'Investigate company'}).click();await expect.poll(()=>newSeen).toBe(true);
 if(order==='old-first'){finishOld();await page.waitForTimeout(50);finishNew();}else{finishNew();await expect(page.getByText('INFY fixture answer')).toBeVisible();finishOld();}
 await expect(page.getByText('INFY fixture answer')).toBeVisible();await expect(page.getByText('TCS fixture answer')).toHaveCount(0);
});

test('generation failure retains document coverage, missing-source gap and evidence',async({page})=>{
 await fixture(page);await page.route('**/api/research',r=>r.fulfill({json:{id:'quota',status:'error',stage:'Could not complete',error:{code:'daily_quota',message:'Shared answer allowance reached.'},documents:[{...evidence,kind:'transcript',period:'Q2 FY27'}],evidence:[evidence],gaps:[{kind:'annual',message:'Document processing exceeded the hosting memory budget.'}]}}));
 await page.goto('/');await page.getByRole('button',{name:'Research',exact:true}).click();await page.getByLabel('NSE company symbol').fill('TEST');await page.getByRole('button',{name:'Investigate company'}).click();
 await expect(page.getByText('Shared answer allowance reached.')).toBeVisible();await expect(page.getByText('Earnings call · Q2 FY27')).toBeVisible();await expect(page.getByText(/Annual report: Document processing exceeded/)).toBeVisible();await expect(page.getByText('The sources are still here')).toBeVisible();
});

test('coverage loss is visible without events being reordered',async({page})=>{
 await page.clock.install();let reads=0;await page.route('**/api/brief',r=>r.fulfill({json:++reads===1?brief:{...brief,source_status:'unavailable',coverage:brief.coverage.map(c=>({...c,filings:{...c.filings,status:'unavailable'}}))}}));
 await page.goto('/');await expect(page.getByRole('button',{name:/15\/15 filings/})).toBeVisible();await page.clock.fastForward(61000);await expect(page.getByRole('button',{name:/0\/15 filings/})).toBeVisible();await expect(page.getByRole('button',{name:event.title})).toBeVisible();
});

test('lost source version retains saved quote and explicitly marks unavailable',async({page})=>{
 await fixture(page);await page.route('**/api/evidence/**',r=>r.fulfill({status:410,json:{error:{code:'version_unavailable'}}}));await page.goto('/');await page.getByRole('button',{name:'Evidence',exact:true}).click();
 await expect(page.getByText(/Version unavailable on the server/)).toBeVisible();await expect(page.locator('blockquote')).toHaveText(evidence.text);await expect(page.getByRole('link',{name:/Open original/})).toHaveAttribute('href',evidence.url+'#page=1');
});

test('failed first check is not called quiet, and slow filing cannot open over Research',async({page})=>{
 await page.route('**/api/brief',r=>r.fulfill({status:503,json:{error:{message:'Fixture exchange unavailable'}}}));await page.goto('/');await expect(page.getByText('Could not check your portfolio')).toBeVisible();await expect(page.getByText('A quieter review window')).toHaveCount(0);
 await page.unroute('**/api/brief');await page.route('**/api/brief',r=>r.fulfill({json:{...brief,events:[{...event,evidence:[]}]}}));await page.reload();let finish:()=>void=()=>{};
 await page.route('**/api/filings/**/assess',async r=>{await new Promise<void>(resolve=>finish=resolve);await r.fulfill({json:{id:'slow',status:'complete',result:{evidence:[evidence]}}});});
 await page.getByRole('button',{name:'Evidence',exact:true}).click();await expect(page.getByText('Reading attachment…')).toBeVisible();await page.getByRole('button',{name:'Research',exact:true}).click();finish();await page.waitForTimeout(100);await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.getByRole('heading',{name:'Look closer.'})).toBeVisible();
});
