var C="web-v36",F=["./","index.html","manifest.json","icon-192.png","icon-512.png"];
self.addEventListener("install",function(e){e.waitUntil(caches.open(C).then(function(c){return c.addAll(F)}));self.skipWaiting()});
self.addEventListener("activate",function(e){e.waitUntil(caches.keys().then(function(k){return Promise.all(k.filter(function(x){return x!=C}).map(function(x){return caches.delete(x)}))}));self.clients.claim()});
self.addEventListener("fetch",function(e){if(e.request.method!="GET"||new URL(e.request.url).origin!=location.origin)return;
 var u=new URL(e.request.url);if(u.pathname.indexOf("/api/")>=0)return;
 if(e.request.mode=="navigate"||/\/(index\.html)?$/.test(u.pathname)){
  /* หน้าแอป: เอาเวอร์ชันล่าสุดจากเครื่อง/เน็ตก่อน ถ้าออฟไลน์ค่อยใช้ที่เก็บไว้ */
  e.respondWith(fetch(u.href,{cache:"no-cache",credentials:"same-origin"}).then(function(r){var cp=r.clone();caches.open(C).then(function(c){c.put(e.request,cp)});return r}).catch(function(){return caches.match(e.request).then(function(r){return r||caches.match("index.html")})}));return}
 e.respondWith(caches.match(e.request).then(function(r){return r||fetch(e.request)}))});
