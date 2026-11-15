/* Cache the app shell only. Private API data never enters shared CacheStorage. */
const CACHE='finn-shell-__BUILD_ID__';
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);const response=await fetch('/');
 if(!response.ok)throw new Error('App shell unavailable');
 const html=await response.clone().text();await cache.put('/',response);
 const assets=[...html.matchAll(/(?:src|href)="(\/assets\/[^"<>]+)"/g)].map(m=>m[1]);
 await cache.addAll([...assets,'/manifest.webmanifest','/icon.svg','/fonts/HankenGrotesk.ttf']);
 await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 await Promise.all((await caches.keys()).filter(key=>key.startsWith('finn-shell-')&&key!==CACHE).map(key=>caches.delete(key)));
 await self.clients.claim();
})()));
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url);
 if(request.method!=='GET'||url.origin!==location.origin||url.pathname.startsWith('/api/'))return;
 if(request.mode==='navigate'){
  event.respondWith(fetch(request).catch(()=>caches.match('/')));return;
 }
 if(!/^\/(assets\/|fonts\/|icon\.svg$|manifest\.webmanifest$)/.test(url.pathname))return;
 event.respondWith((async()=>{
  // Public, same-origin immutable assets can differ only in CORS response
  // headers. Precache fetches have no Origin; module loads do. No API enters
  // this branch, so ignoring Vary cannot expose a personalised response.
  const cached=await caches.match(request,{ignoreVary:true});if(cached)return cached;
  const response=await fetch(request);if(response.ok){const cache=await caches.open(CACHE);await cache.put(request,response.clone());}
  return response;
 })());
});
