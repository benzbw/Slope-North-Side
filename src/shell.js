/* ===== Slope North Side · ระบบบัญชี โปรเจกต์ หน้าแรก ผู้ช่วย ===== */
(function(){
"use strict";
var S=window.SNS,$=function(i){return document.getElementById(i)};
var BRAND="Slopenorthside44",LOCALHOST=/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname)||location.protocol=="file:";
var ST={mode:"local",uid:null,owner:false,acct:null,db:null,user:null,assets:null,sample:null,ready:false};
var LOGO=(document.querySelector(".brand img")||{}).src||"";
function esc(t){return String(t==null?"":t).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function cp(o){return o==null?o:JSON.parse(JSON.stringify(o))}
function J(k,d){try{var v=S.raw.get(k);return v?JSON.parse(v):d}catch(e){return d}}
function JS(k,v){return S.raw.set(k,JSON.stringify(v))}
function rid(){return (Date.now().toString(36)+Math.random().toString(36).slice(2,6)).toLowerCase()}
function now(){return Date.now()}
function h(html){var d=document.createElement("div");d.innerHTML=html.trim();return d.firstChild}
function ago(t){if(!t)return"";var s=(now()-t)/1000;if(s<60)return"เมื่อสักครู่";if(s<3600)return Math.floor(s/60)+" นาทีที่แล้ว";if(s<86400)return Math.floor(s/3600)+" ชม.ที่แล้ว";if(s<86400*7)return Math.floor(s/86400)+" วันที่แล้ว";return new Date(t).toLocaleDateString("th-TH",{day:"numeric",month:"short",year:"2-digit"})}
function toastS(m){try{if(typeof window.toast=="function")return window.toast(m)}catch(e){}var t=h('<div class="sx-busy" style="background:none;pointer-events:none;place-items:start center;padding-top:80px"><span style="background:#fff;color:#111;padding:10px 16px;border-radius:12px">'+esc(m)+'</span></div>');document.body.appendChild(t);setTimeout(function(){t.remove()},2600)}
function busy(m){var b=$("sx-busy");if(!m){if(b)b.remove();return}if(!b){b=h('<div class="sx-busy" id="sx-busy"></div>');document.body.appendChild(b)}b.textContent=m}

/* ---------- รหัสผ่าน (PBKDF2) ---------- */
var SHA=(function(){var K=[],H0=[],p=2,n=0;function fr(x){return(x-Math.floor(x))*4294967296|0}
while(n<64){var q=true;for(var d=2;d*d<=p;d++)if(p%d==0){q=false;break}if(q){if(n<8)H0[n]=fr(Math.pow(p,1/2));K[n]=fr(Math.pow(p,1/3));n++}p++}
var W=new Int32Array(64);
function comp(st,b,o){for(var i=0;i<16;i++)W[i]=b[o+i*4]<<24|b[o+i*4+1]<<16|b[o+i*4+2]<<8|b[o+i*4+3];
 for(i=16;i<64;i++){var x=W[i-15],y=W[i-2];W[i]=((x>>>7|x<<25)^(x>>>18|x<<14)^(x>>>3))+W[i-7]+((y>>>17|y<<15)^(y>>>19|y<<13)^(y>>>10))+W[i-16]|0}
 var a=st[0],bb=st[1],c=st[2],dd=st[3],e=st[4],f=st[5],g=st[6],h=st[7];
 for(i=0;i<64;i++){var t1=h+((e>>>6|e<<26)^(e>>>11|e<<21)^(e>>>25|e<<7))+(e&f^~e&g)+K[i]+W[i]|0,t2=((a>>>2|a<<30)^(a>>>13|a<<19)^(a>>>22|a<<10))+(a&bb^a&c^bb&c)|0;h=g;g=f;f=e;e=dd+t1|0;dd=c;c=bb;bb=a;a=t1+t2|0}
 st[0]=st[0]+a|0;st[1]=st[1]+bb|0;st[2]=st[2]+c|0;st[3]=st[3]+dd|0;st[4]=st[4]+e|0;st[5]=st[5]+f|0;st[6]=st[6]+g|0;st[7]=st[7]+h|0}
function hash(msg,st0,pre){var st=st0?Int32Array.from(st0):Int32Array.from(H0),L=msg.length,tot=L+(pre||0),nb=((L+9+63)>>6)<<6,b=new Uint8Array(nb);b.set(msg);b[L]=128;
 var bits=tot*8;for(var i=0;i<4;i++)b[nb-1-i]=bits/Math.pow(2,8*i)&255;for(var o=0;o<nb;o+=64)comp(st,b,o);return st}
function bytes(st){var o=new Uint8Array(32);for(var i=0;i<8;i++){o[i*4]=st[i]>>>24;o[i*4+1]=st[i]>>>16&255;o[i*4+2]=st[i]>>>8&255;o[i*4+3]=st[i]&255}return o}
function pbkdf2(pw,salt,it){var key=pw.length>64?bytes(hash(pw)):pw,ip=new Uint8Array(64),op=new Uint8Array(64);for(var i=0;i<64;i++){ip[i]=(key[i]||0)^54;op[i]=(key[i]||0)^92}
 var si=Int32Array.from(H0),so=Int32Array.from(H0);comp(si,ip,0);comp(so,op,0);
 function hm(m){return bytes(hash(bytes(hash(m,si,64)),so,64))}
 var s1=new Uint8Array(salt.length+4);s1.set(salt);s1[salt.length+3]=1;var u=hm(s1),t=u.slice();for(var k=1;k<it;k++){u=hm(u);for(var j=0;j<32;j++)t[j]^=u[j]}return t}
return{pbkdf2:pbkdf2,hash:function(m){return bytes(hash(m))}}})();
async function hashPw(pw,salt){var enc=new TextEncoder();
 if(!(window.crypto&&crypto.subtle)){await new Promise(function(r){setTimeout(r,30)});return Array.prototype.map.call(SHA.pbkdf2(enc.encode(pw),enc.encode(salt),150000),function(b){return("0"+b.toString(16)).slice(-2)}).join("")}
 var key=await crypto.subtle.importKey("raw",enc.encode(pw),"PBKDF2",false,["deriveBits"]);
 var bits=await crypto.subtle.deriveBits({name:"PBKDF2",hash:"SHA-256",salt:enc.encode(salt),iterations:150000},key,256);
 return Array.prototype.map.call(new Uint8Array(bits),function(b){return("0"+b.toString(16)).slice(-2)}).join("")}

/* ---------- ไฟล์เสียงในเครื่อง (IndexedDB) ---------- */
var IDB={p:null,open:function(){if(!this.p)this.p=new Promise(function(res,rej){try{var r=indexedDB.open("sns",1);r.onupgradeneeded=function(){r.result.createObjectStore("audio")};r.onsuccess=function(){res(r.result)};r.onerror=function(){rej(r.error)}}catch(e){rej(e)}});return this.p},
 tx:function(mode,fn){return this.open().then(function(d){return new Promise(function(res,rej){var t=d.transaction("audio",mode),q=fn(t.objectStore("audio"));t.oncomplete=function(){res(q&&q.result)};t.onerror=function(){rej(t.error)}})})},
 put:function(k,v){return this.tx("readwrite",function(s){return s.put(v,k)})},get:function(k){return this.tx("readonly",function(s){return s.get(k)})},del:function(k){return this.tx("readwrite",function(s){return s.delete(k)})}};

/* ---------- ที่เก็บข้อมูล: cloud (บัญชี claude) หรือ local (เครื่องนี้) ---------- */
function pCol(){return "data/users/"+ST.uid+"/account/projects"}
function lKey(){return "sns:proj:"+ST.uid}
function stateOf(pid){var o={},pre="p:"+pid+":";S.raw.keys().forEach(function(k){if(k&&k.indexOf(pre)==0){var kk=k.slice(pre.length),v=S.raw.get(k);if(kk=="bwcvhist"||(v&&v.length>200000))return;o[kk]=v}});
 var keep={bwraw:1,bwraw0:1,bw3:1,bw3s57l:1,bwsec:1,bwsing:1};for(var g=0;g<20&&JSON.stringify(o).length>235000;g++){var big=null;Object.keys(o).forEach(function(k){if(!keep[k]&&(!big||o[k].length>o[big].length))big=k});if(!big)break;delete o[big]}return o}
function infoOf(st){var r={synced:false,theme:0,lines:0};try{var b=JSON.parse(st.bw3||st.bw3s57l||"null");if(b&&b.s)r.synced=true}catch(e){}r.theme=+(st.bwtheme||0)||0;
 try{if(st.bwraw)r.lines=st.bwraw.split("\n").filter(function(x){return x.trim()}).length}catch(e){}return r}
var Store={
 acctGet:async function(){if(ST.mode=="cloud"){var s=await ST.db.doc("data/users/"+ST.uid+"/account").get();return s.exists?cp(s.data()):null}var a=J("sns:accts",{});return null},
 list:async function(){var L;
  if(ST.mode=="cloud"){var q=await ST.db.collection(pCol()).get();L=q.docs.map(function(d){var x=cp(d.data())||{};x.id=d.id;x.info=infoOf(x.state||{});if(x.baked)x.info.synced=true;delete x.state;return x})}
  else{var m=J(lKey(),{});L=Object.keys(m).map(function(id){var x=m[id];x.id=id;x.info=infoOf(stateOf(id));if(x.baked)x.info.synced=true;return x})}
  L.sort(function(a,b){return(b.updated||0)-(a.updated||0)});JS("sns:cache:"+ST.uid,L);return L},
 create:async function(meta,state){var id=meta.id||rid();meta.id=id;meta.created=meta.created||now();meta.updated=now();
  Object.keys(state||{}).forEach(function(k){S.raw.set("p:"+id+":"+k,state[k])});
  if(ST.mode=="cloud"){var d=Object.assign({},meta);delete d.id;d.state=stateOf(id);await ST.db.doc(pCol()+"/"+id).set(d)}
  else{var m=J(lKey(),{});var d2=Object.assign({},meta);delete d2.id;m[id]=d2;JS(lKey(),m)}
  S.raw.set("sns:t:"+id,String(meta.updated));return id},
 patch:async function(id,fields){fields.updated=now();
  if(ST.mode=="cloud")await ST.db.doc(pCol()+"/"+id).update(fields);
  else{var m=J(lKey(),{});if(m[id]){Object.assign(m[id],fields);JS(lKey(),m)}}},
 push:async function(id){var t=now();if(ST.mode=="cloud"){await ST.db.doc(pCol()+"/"+id).update({state:stateOf(id),updated:t})}else{var m=J(lKey(),{});if(m[id]){m[id].updated=t;JS(lKey(),m)}}S.raw.set("sns:t:"+id,String(t))},
 pull:async function(id){if(ST.mode!="cloud")return true;var s=await ST.db.doc(pCol()+"/"+id).get();if(!s.exists)return false;var d=cp(s.data())||{},lt=+(S.raw.get("sns:t:"+id)||0);
  if((d.updated||0)>lt&&d.state){var pre="p:"+id+":";S.raw.keys().forEach(function(k){if(k&&k.indexOf(pre)==0&&k!=pre+"bwcvhist")S.raw.rm(k)});Object.keys(d.state).forEach(function(k){S.raw.set(pre+k,d.state[k])});S.raw.set("sns:t:"+id,String(d.updated||now()))}return d},
 meta:async function(id){if(ST.mode=="cloud"){var s=await ST.db.doc(pCol()+"/"+id).get();if(!s.exists)return null;var d=cp(s.data());delete d.state;d.id=id;return d}var m=J(lKey(),{});return m[id]?Object.assign({id:id},m[id]):null},
 remove:async function(id,meta){var pre="p:"+id+":";S.raw.keys().forEach(function(k){if(k&&k.indexOf(pre)==0)S.raw.rm(k)});S.raw.rm("sns:t:"+id);try{await IDB.del(id)}catch(e){}
  if(ST.mode=="cloud"){await ST.db.doc(pCol()+"/"+id).delete();if(meta&&meta.audio&&meta.audio.aid&&ST.assets)try{await ST.assets.delete(meta.audio.aid)}catch(e){}}
  else{var m=J(lKey(),{});delete m[id];JS(lKey(),m)}
  if(id=="dangerous")S.raw.set("sns:nodangerous:"+ST.uid,"1")},
 saveAudio:async function(id,file){var a={name:file.name||"เพลง",size:file.size||0};try{await IDB.put(id,{blob:file,name:a.name})}catch(e){}
  if(ST.mode=="cloud"&&ST.assets){try{var old=await Store.meta(id);var up=await ST.assets.upload(file);a.url=up.url;a.aid=up.id;if(old&&old.audio&&old.audio.aid&&old.audio.aid!=up.id)try{await ST.assets.delete(old.audio.aid)}catch(e){}}catch(e){a.localOnly=true;a.err=e&&e.code||String(e)}}
  else if(ST.mode=="cloud")a.localOnly=true;
  await Store.patch(id,{audio:a});return a},
 loadAudio:async function(id,meta){try{var r=await IDB.get(id);if(r&&r.blob)return{url:URL.createObjectURL(r.blob),name:r.name}}catch(e){}
  if(meta&&meta.audio&&meta.audio.url)return{url:meta.audio.url,name:meta.audio.name};return null},
 log:function(kind,data){try{var e=Object.assign({k:kind,t:now(),p:S.pid||"home",ua:navigator.userAgent.slice(0,140),m:ST.mode},data);
  var L=J("sns:log",[]);L.push(e);if(L.length>60)L=L.slice(-60);JS("sns:log",L);
  if(ST.mode=="cloud"&&ST.db){var base=kind=="ticket"?"tickets/":"logs/";ST.db.collection(base+ST.uid+"/items").add(e).catch(function(){})}
  else if(LOCALHOST&&location.protocol!="file:")fetch("/api/report",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(e)}).catch(function(){})}catch(x){}}
};
S.onErr=function(e){Store.log("error",{msg:e.m,src:e.s})};

/* ---------- บัญชี ---------- */
async function detect(){
 if(!LOCALHOST&&window.claude&&typeof claude.use=="function"){
  try{var u=await claude.use("user");if(u){var id=await u.id();if(id){var db=await claude.use("db");if(db){ST.mode="cloud";ST.user=u;ST.db=db;ST.uid=id;ST.owner=await u.isOwner();
   claude.use("assets").then(function(a){ST.assets=a}).catch(function(){});claude.use("sample").then(function(s){ST.sample=s}).catch(function(){});return}}}}catch(e){}
 }
 ST.mode="local";
}
function isBrand(handle){return ST.mode=="cloud"?ST.owner:String(handle||"").toLowerCase()==BRAND.toLowerCase()}
async function getAcct(){if(ST.mode=="cloud"){var s=await ST.db.doc("data/users/"+ST.uid+"/account").get();return s.exists?cp(s.data()):null}
 var A=J("sns:accts",{}),sess=S.raw.get("sns:sess");return sess&&A[sess]?A[sess]:null}
async function findLocal(handle){var A=J("sns:accts",{});return A[String(handle).toLowerCase()]||null}
async function saveAcct(a){if(ST.mode=="cloud"){await ST.db.doc("data/users/"+ST.uid+"/account").set(a)}else{var A=J("sns:accts",{});A[a.handle.toLowerCase()]=a;JS("sns:accts",A)}}
function sessOn(handle){S.raw.set("sns:sess",ST.mode=="cloud"?ST.uid:String(handle).toLowerCase())}
function sessOk(acct){var s=S.raw.get("sns:sess");if(!s||!acct)return false;return ST.mode=="cloud"?s==ST.uid:s==acct.handle.toLowerCase()}
function logout(){S.raw.rm("sns:sess");if(ST.mode=="cloud")S.raw.set("sns:out:"+ST.uid,"1");location.hash="";location.reload()}

/* ---------- โครงหน้า ---------- */
var root;
function mount(){root=$("sx");if(!root){root=h('<div id="sx" role="main"></div>');document.body.appendChild(root)}root.hidden=false;return root}
function frame(inner){return '<div class="sx-amb" aria-hidden="true"></div><div class="sx-wrap">'+inner+'</div>'}
function splash(msg){mount().innerHTML=frame('<div class="sx-splash"><div><img src="'+LOGO+'" alt="" width="56" height="56" style="border-radius:50%"><div class="sx-word">Slope <span>North</span> Side</div><div>'+esc(msg||"กำลังเปิดสตูดิโอ…")+'</div></div></div>')}

/* ---------- ล็อกอิน / สมัคร ---------- */
async function loginView(mode,existing){
 var brandSetup=mode=="setup";var cloudHas=ST.mode=="cloud"&&existing;
 var title=mode=="login"?"เข้าสู่ระบบ":brandSetup?"ตั้งรหัสบัญชีหลักของแบรนด์":"สมัครบัญชีใหม่";
 var preId=cloudHas?existing.handle:(brandSetup?BRAND:(S.raw.get("sns:lastid")||""));
 mount().innerHTML=frame('<div class="sx-login"><div class="sx-lbox">'+
  '<img src="'+LOGO+'" alt="" width="46" height="46" style="border-radius:50%">'+
  '<div class="sx-word">Slope <span>North</span> Side</div>'+
  '<p>สตูดิโอทำวิดีโอเนื้อเพลง ปก มิกซ์ และปล่อยเพลง ในที่เดียว</p>'+
  (brandSetup?'<div class="sx-tag" style="margin-bottom:14px">บัญชีหลักของแบรนด์</div>':'')+
  '<form class="sx-f" id="sx-lf" autocomplete="on"><b style="font-size:17px">'+title+'</b>'+
  '<label class="sx-lab">ID<input class="sx-in" id="sx-id" name="username" autocomplete="username" value="'+esc(preId)+'" '+(cloudHas?'readonly':'')+' required minlength="3" maxlength="32"></label>'+
  '<label class="sx-lab">รหัสผ่าน<input class="sx-in" id="sx-pw" name="password" type="password" autocomplete="'+(mode=="login"?"current-password":"new-password")+'" required minlength="4"></label>'+
  (mode!="login"?'<label class="sx-lab">ยืนยันรหัสผ่าน<input class="sx-in" id="sx-pw2" type="password" autocomplete="new-password" required minlength="4"></label>':'')+
  '<div class="sx-err" id="sx-le" role="alert"></div>'+
  '<button class="sx-btn" id="sx-lgo" type="submit">'+(mode=="login"?"เข้าสู่ระบบ":"สร้างบัญชีและเข้าใช้")+'</button>'+
  '<div class="sx-note">'+(mode=="login"?'เข้าแล้วระบบจะจำไว้ จนกว่าจะกด "ออกจากระบบ"':'รหัสถูกเก็บแบบเข้ารหัส ไม่มีใครเห็นรหัสจริง รวมถึงทีมงาน')+'</div>'+
  (ST.mode=="local"&&!brandSetup?'<div class="sx-note">'+(mode=="login"?'ยังไม่มีบัญชี? <button type="button" class="sx-link" id="sx-sw">สมัครบัญชีใหม่</button>':'มีบัญชีแล้ว? <button type="button" class="sx-link" id="sx-sw">เข้าสู่ระบบ</button>')+'</div>':'')+
  (ST.mode=="local"?'<div class="sx-note" style="margin-top:4px">โหมดเครื่องนี้: บัญชีและโปรเจกต์เก็บในเครื่องนี้</div>':'')+
  '</form></div></div>');
 var sw=$("sx-sw");if(sw)sw.onclick=function(){loginView(mode=="login"?"signup":"login")};
 setTimeout(function(){var f=$(preId?"sx-pw":"sx-id");if(f)f.focus()},50);
 $("sx-lf").onsubmit=async function(ev){ev.preventDefault();var id=$("sx-id").value.trim(),pw=$("sx-pw").value,er=$("sx-le"),btn=$("sx-lgo");er.textContent="";
  if(!/^[A-Za-z0-9_.-]{3,32}$/.test(id)){er.textContent="ID ใช้ได้เฉพาะ a-z 0-9 _ . - ยาว 3–32 ตัว";return}
  btn.disabled=true;try{
  if(mode=="login"){
   var a=ST.mode=="cloud"?existing:await findLocal(id);
   if(!a||a.handle.toLowerCase()!=id.toLowerCase()){if(ST.mode=="cloud"){er.textContent="ID ไม่ตรงกับบัญชีนี้";btn.disabled=false;return}
    S.raw.set("sns:lastid",id);loginView("signup");setTimeout(function(){var f=$("sx-id"),p1=$("sx-pw"),p2=$("sx-pw2"),e2=$("sx-le");if(f)f.value=id;if(p1)p1.value=pw;if(e2)e2.textContent="ยังไม่มีบัญชีนี้ในเครื่องนี้ พิมพ์รหัสอีกครั้งในช่องยืนยัน แล้วกดสร้างบัญชี";if(p2)p2.focus()},80);return}
   var hh=await hashPw(pw,a.salt);if(hh!==a.hash){er.textContent="รหัสผ่านไม่ถูกต้อง";btn.disabled=false;Store.log("login_fail",{id:id});return}
   ST.acct=a;sessOn(a.handle);S.raw.set("sns:lastid",a.handle);afterLogin();return}
  if(pw.length<4){er.textContent="รหัสผ่านอย่างน้อย 4 ตัว";btn.disabled=false;return}
  if($("sx-pw2").value!==pw){er.textContent="รหัสผ่านสองช่องไม่ตรงกัน";btn.disabled=false;return}
  if(/^slopenorthside/i.test(id)&&!(brandSetup||(ST.mode=="local"&&id.toLowerCase()==BRAND.toLowerCase()))){er.textContent="ID นี้สงวนไว้สำหรับแบรนด์ Slope North Side";btn.disabled=false;return}
  if(ST.mode=="local"&&await findLocal(id)){er.textContent="มี ID นี้ในเครื่องแล้ว กดเข้าสู่ระบบแทน";btn.disabled=false;return}
  var salt=rid()+rid(),acct={handle:id,salt:salt,hash:await hashPw(pw,salt),created:now(),brand:isBrand(id)};
  await saveAcct(acct);ST.acct=acct;sessOn(id);S.raw.set("sns:lastid",id);Store.log("signup",{id:id});afterLogin()
  }catch(e){er.textContent="ทำรายการไม่สำเร็จ: "+(e&&e.message||e);btn.disabled=false}};
}

/* ---------- เข้าใช้ด้วยบัญชี Claude (ลิงก์ claude.ai): ไม่ต้องตั้งรหัส ---------- */
function cloudView(existing){var brand=ST.owner,h0=existing?existing.handle:(brand?BRAND:(S.raw.get("sns:lastid")||""));
 mount().innerHTML=frame('<div class="sx-login"><div class="sx-lbox"><img src="'+LOGO+'" alt="" width="46" height="46" style="border-radius:50%">'+
  '<div class="sx-word">Slope <span>North</span> Side</div><p>สตูดิโอทำวิดีโอเนื้อเพลง ปก มิกซ์ และปล่อยเพลง ในที่เดียว</p>'+
  (brand?'<div class="sx-tag" style="margin-bottom:14px">บัญชีหลักของแบรนด์</div>':'')+
  '<form class="sx-f" id="sx-cf">'+(existing||brand?'<div class="sx-lab">เข้าใช้ในชื่อ<b style="font:700 20px var(--sx-lab);color:var(--sx-fg);letter-spacing:0">'+esc(h0)+'</b></div>':
  '<label class="sx-lab">ตั้ง ID ของคุณ<input class="sx-in" id="sx-cid" autocomplete="nickname" value="'+esc(h0)+'" required minlength="3" maxlength="32" placeholder="เช่น ชื่อศิลปิน"></label>')+
  '<div class="sx-err" id="sx-ce" role="alert"></div><button class="sx-btn" id="sx-cgo" type="submit">'+(existing?"เข้าใช้งาน":"เริ่มใช้งาน")+'</button>'+
  '<div class="sx-note">ยืนยันตัวตนด้วยบัญชี Claude ที่ล็อกอินอยู่แล้ว ไม่ต้องจำรหัส งานทั้งหมดเก็บในบัญชีนี้ เปิดจากมือถือหรือคอมก็เห็นเหมือนกัน</div></form></div></div>');
 $("sx-cf").onsubmit=async function(ev){ev.preventDefault();var er=$("sx-ce"),btn=$("sx-cgo");er.textContent="";btn.disabled=true;
  try{var a=existing;if(!a){var id=brand?BRAND:$("sx-cid").value.trim();
    if(!/^[A-Za-z0-9_.-]{3,32}$/.test(id)){er.textContent="ID ใช้ได้เฉพาะ a-z 0-9 _ . - ยาว 3–32 ตัว";btn.disabled=false;return}
    if(!brand&&/^slopenorthside/i.test(id)){er.textContent="ID นี้สงวนไว้สำหรับแบรนด์ Slope North Side";btn.disabled=false;return}
    a={handle:id,created:now(),brand:brand,via:"claude"};await saveAcct(a);Store.log("signup",{id:id})}
   ST.acct=a;sessOn(a.handle);S.raw.rm("sns:out:"+ST.uid);S.raw.set("sns:lastid",a.handle);afterLogin()}catch(e){er.textContent="ทำรายการไม่สำเร็จ: "+(e&&(e.message||e.code)||e)+(e&&e.code=="not_granted"?" (กดอนุญาตให้แอปเก็บข้อมูลก่อน)":"");btn.disabled=false}};
 if(existing||brand)setTimeout(function(){var b=$("sx-cgo");if(b)b.focus()},50)}

/* ---------- หลังล็อกอิน ---------- */
var BRANDED=false;
async function seedDangerous(){if(!BRANDED)return;if(S.raw.get("sns:nodangerous:"+ST.uid))return;
 var have=await Store.meta("dangerous").catch(function(){return null});if(have)return;
 /* ย้ายงานเดิม (ก่อนมีระบบโปรเจกต์) เข้ามาเป็นโปรเจกต์ Dangerous */
 var st={};S.raw.keys().forEach(function(k){if(k&&k.slice(0,2)=="bw"&&!S.GL[k]&&k!="bwcvhist")st[k]=S.raw.get(k)});
 await Store.create({id:"dangerous",name:"Dangerous",artist:"Bedupbiw",feat:"Killmonker",baked:true,audio:{name:"Dangerous (มากับแอป)",embedded:true}},st)}
async function afterLogin(){BRANDED=isBrand(ST.acct&&ST.acct.handle);ST.uid=ST.uid||ST.acct.handle.toLowerCase();
 if(ST.mode=="local")ST.uid=ST.acct.handle.toLowerCase();
 try{await seedDangerous()}catch(e){Store.log("error",{msg:"seed: "+e})}
 if(S.pid){enterProject();return}
 home()}

/* ---------- ปกเพลงแบบสร้างเอง ---------- */
function hashN(s){var x=2166136261;for(var i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)}return x>>>0}
function artFor(cv,p){var TH=(window.THEMES||[])[p.info&&p.info.theme||0]||{hot:"#ff3347",b1:"74,11,23",b2:"122,15,30"};
 var W=480,c=cv.getContext("2d"),r=hashN(p.id+p.name),rnd=function(){r=(Math.imul(r,1664525)+1013904223)>>>0;return r/4294967296};
 cv.width=W;cv.height=W;c.fillStyle="#0b0709";c.fillRect(0,0,W,W);
 var g=c.createRadialGradient(W*(.2+rnd()*.6),W*(.15+rnd()*.4),10,W/2,W/2,W*.8);g.addColorStop(0,"rgba("+TH.b2+",1)");g.addColorStop(.55,"rgba("+TH.b1+",.85)");g.addColorStop(1,"rgba(6,4,6,1)");c.fillStyle=g;c.fillRect(0,0,W,W);
 c.globalCompositeOperation="screen";for(var i=0;i<3;i++){var gx=W*rnd(),gy=W*rnd(),gr=W*(.15+rnd()*.3),g2=c.createRadialGradient(gx,gy,0,gx,gy,gr);g2.addColorStop(0,TH.hot+"55");g2.addColorStop(1,TH.hot+"00");c.fillStyle=g2;c.fillRect(0,0,W,W)}
 c.globalCompositeOperation="source-over";c.strokeStyle="rgba(255,255,255,.07)";c.lineWidth=1;for(var k=0;k<5;k++){c.beginPath();c.arc(W*.78,W*.24,30+k*26,0,Math.PI*2);c.stroke()}
 var im=c.getImageData(0,0,W,W),d=im.data;for(var j=0;j<d.length;j+=4){var n=(rnd()-.5)*26;d[j]+=n;d[j+1]+=n;d[j+2]+=n}c.putImageData(im,0,0);
 var t=String(p.name||"UNTITLED").toUpperCase(),fs=t.length>14?44:t.length>9?58:76;c.fillStyle="#fff";c.textBaseline="alphabetic";
 var words=t.split(/\s+/),lines;for(;;){c.font="400 "+fs+"px Anton, Impact, 'Noto Sans Thai', sans-serif";lines=[];var cur="";words.forEach(function(w){var tt=cur?cur+" "+w:w;if(c.measureText(tt).width>W-60&&cur){lines.push(cur);cur=w}else cur=tt});lines.push(cur);lines=lines.slice(-3);
 var mw=Math.max.apply(null,lines.map(function(L){return c.measureText(L).width}));if(mw<=W-60||fs<=22)break;fs-=4}
 lines.forEach(function(L,i){c.fillText(L,30,W-48-(lines.length-1-i)*fs*1.02)});
 c.font="600 13px Montserrat, 'Noto Sans Thai', sans-serif";c.fillStyle="rgba(255,255,255,.75)";var ar=(p.artist||"")+(p.feat?" ft. "+p.feat:"");c.fillText(ar.toUpperCase().split("").join(" "),30,W-24);
 c.fillStyle=TH.hot;c.fillRect(30,30,26,4);c.font="700 10px Montserrat, sans-serif";c.fillStyle="rgba(255,255,255,.6)";c.fillText("SLOPE NORTH SIDE",64,35)}

/* ---------- หน้าแรก ---------- */
var STEPS=[["เช็กเทรนด์ & วางแนว","ดูชาร์ตไทย/โลก Top 10 ทั้งทุกแนวและฮิปฮอป แนวที่กำลังมา และประเมินโอกาสแมสตามสไตล์ศิลปิน","ทุกเครื่อง"],["สร้างโปรเจกต์","ตั้งชื่อเพลง ใส่ไฟล์เพลงและเนื้อเพลง แยกท่อนร้อง/ฮุค และคนร้อง","ทุกเครื่อง"],
 ["ซิงค์เนื้อกับเสียง","AI จับจังหวะคำร้องทีละคำ แล้วปรับเองได้ทีละบรรทัด","แม่นสุดบนคอม"],
 ["สไตล์ · ปก · MV","เลือกสไตล์ 60 แบบ ธีมสี เอฟเฟกต์ ภาพวาดอินโทร ปกเพลง และฉาก MV","ปก/MV ด้วย AI บนคอม"],
 ["ส่งออกวิดีโอ","YouTube 16:9, Reels/TikTok 9:16 ทั้งเพลงหรือท่อนฮุค 15–30 วิ","ทุกเครื่อง"],
 ["ปล่อยเพลง & โปรโมท","สิทธิ์บีต ชื่อเพลงมาตรฐาน แคปชันทุกช่องทาง และวัน-เวลาปล่อย","ทุกเครื่อง"]];
var PROJ=[];
async function home(){if(S.crashed){toastS("เปิดโปรเจกต์ไม่สำเร็จ 2 ครั้ง เลยพากลับหน้าแรกก่อน ลองกด ⋯ > ซ่อมโปรเจกต์");Store.log("crash",{pid:S.crashed})}
 var a=ST.acct,ini=(a.handle||"?").slice(0,1).toUpperCase();
 PROJ=J("sns:cache:"+ST.uid,[]);
 mount().innerHTML=frame(
 '<div class="sx-top"><div class="sx-mark"><img src="'+LOGO+'" alt=""><div>Slope North Side<small>MUSIC STUDIO</small></div></div>'+
  '<div class="sx-acts"><button class="sx-pill" id="sx-guide">วิธีใช้</button><button class="sx-pill" id="sx-help">ผู้ช่วย</button>'+
  '<button class="sx-pill" id="sx-me" aria-haspopup="true" aria-label="บัญชี '+esc(a.handle)+'"><span class="sx-ava">'+esc(ini)+'</span><span class="sx-hn">'+esc(a.handle)+'</span></button></div></div>'+
 '<div class="sx-hello"><div style="min-width:0"><div class="sx-eyebrow">'+(BRANDED?"บัญชีหลักของแบรนด์":"สตูดิโอของคุณ")+'</div>'+
  '<h1 class="sx-h1">โปรเจกต์เพลง</h1><p class="sx-sub">แต่ละเพลงเก็บเป็นโปรเจกต์ของตัวเอง กดเข้าไปถึงจะแก้ไขได้ '+(ST.mode=="cloud"?"บันทึกในบัญชีอัตโนมัติ เปิดจากมือถือหรือคอมก็เห็นงานเดียวกัน":"บันทึกในเครื่องนี้อัตโนมัติ")+'</p>'+
  '<div class="sx-stats" id="sx-stats"></div></div>'+
  '<div style="display:flex;gap:8px;flex-wrap:wrap"><a class="sx-btn ghost" id="sx-wtop" target="_blank" rel="noopener" style="text-decoration:none">✎ แต่งเพลง & หาบีต</a><button class="sx-btn" id="sx-new">+ เพลงใหม่</button></div></div>'+
 '<section class="sx-sec"><div class="sx-sech"><h2>เพลงทั้งหมด</h2><span id="sx-cnt"></span></div><div class="sx-grid" id="sx-grid"></div></section>'+
 (BRANDED?'':'<section class="sx-sec"><div class="sx-sech"><h2>ตัวอย่างผลงานจากแอป</h2><span>เปิดดูได้ แก้ได้ แต่ไม่บันทึก</span></div><div class="sx-grid" id="sx-demo"></div></section>')+
 '<section class="sx-sec"><div class="sx-sech"><h2>เทรนด์ & โอกาสแมส</h2><span>ชาร์ตไทย/โลก · ฮิปฮอป · แนวที่กำลังมา</span></div><p class="sx-sub" style="margin:0 0 12px">เลือกศิลปิน แอปจำสไตล์ไว้ แล้วบอกว่าเพลงมีโอกาสแมสกี่ % เพราะอะไร และควรปรับตรงไหน</p><button class="sx-btn" type="button" onclick="window.SNSTrend&&SNSTrend.open()">เปิดหน้าเทรนด์</button></section>'+
 '<section class="sx-sec" id="sx-write"></section>'+'<section class="sx-sec" id="sx-lan"></section>'+
 '<section class="sx-sec"><div class="sx-sech"><h2>ขั้นตอนทำเพลง 1 เพลง</h2><span>เรียงตามลำดับในแอป</span></div><div class="sx-steps">'+
  STEPS.map(function(s){return'<div class="sx-step"><b>'+s[0]+'</b><p>'+s[1]+'</p><em>'+s[2]+'</em></div>'}).join("")+'</div></section>'+
 '<div class="sx-foot"><span>© Slope North Side</span><span>'+(ST.mode=="cloud"?"ซิงค์กับบัญชี claude.ai":"โหมดเครื่องนี้ · ฟีเจอร์ AI ใช้ได้เมื่อเปิดเซิร์ฟเวอร์บนคอม")+'</span></div>');
 $("sx-new").onclick=newDialog;$("sx-guide").onclick=guide;$("sx-help").onclick=function(){bot.open()};
 $("sx-me").onclick=function(ev){menuAt(ev.currentTarget,[["ออกจากระบบ",logout]].concat(BRANDED?[["ดูปัญหาที่แจ้งเข้ามา",function(){bot.open();bot.say("ai","รายการแจ้งปัญหาและข้อผิดพลาดทั้งหมดถูกเก็บไว้ในระบบ Claude จะเข้ามาตรวจและแก้ให้ตามรอบตรวจอัตโนมัติ หรือสั่งในแชทว่า \"ตรวจปัญหาที่แจ้งเข้ามา\" ได้เลย")}]]:[]),true)};
 if(!BRANDED){var dg=$("sx-demo");var dp={id:"demo",name:"Dangerous",artist:"Bedupbiw",feat:"Killmonker",info:{theme:0,synced:true}};dg.appendChild(card(dp,true))}
 renderGrid();lanCard();writeCard();
 try{PROJ=await Store.list();renderGrid()}catch(e){Store.log("error",{msg:"list: "+(e&&e.message||e)});$("sx-cnt").textContent="โหลดรายการไม่สำเร็จ ลองรีเฟรช"}}
function renderGrid(){var g=$("sx-grid");if(!g)return;g.innerHTML="";
 PROJ.forEach(function(p){g.appendChild(card(p))});
 var nw=h('<div class="sx-card" tabindex="0" role="button" aria-label="สร้างเพลงใหม่"><div class="sx-new"><span>+</span><b>เพลงใหม่</b><small>ใส่ชื่อ เนื้อ และไฟล์เพลง</small></div></div>');nw.onclick=newDialog;nw.onkeydown=function(e){if(e.key=="Enter")newDialog()};g.appendChild(nw);
 if(!PROJ.length)g.insertBefore(h('<div class="sx-empty"><b>ยังไม่มีเพลงในบัญชีนี้</b><br>เริ่มจากกด "+ เพลงใหม่" ใส่ชื่อเพลง ไฟล์เพลง และเนื้อเพลง แล้วแอปจะพาไปซิงค์ ทำสไตล์ และส่งออกวิดีโอ'+(BRANDED?'':' หรือดูตัวอย่างผลงานด้านล่างก่อนก็ได้')+'</div>'),g.firstChild);
 var syn=PROJ.filter(function(p){return p.info&&p.info.synced}).length;
 $("sx-stats").innerHTML='<div><b>'+PROJ.length+'</b>เพลง</div><div><b>'+syn+'</b>ซิงค์แล้ว</div><div><b>'+(PROJ[0]?esc(ago(PROJ[0].updated)):"–")+'</b>แก้ล่าสุด</div>';
 $("sx-cnt").textContent=PROJ.length?PROJ.length+" โปรเจกต์":""}
function card(p,demo){var inf=p.info||{},el=h('<div class="sx-card" tabindex="0" role="button"><div class="sx-art"><canvas width="480" height="480" aria-hidden="true"></canvas><span class="sx-play"></span></div>'+
 '<div class="sx-meta"><b></b><i></i><div class="sx-chips"></div></div></div>');
 el.setAttribute("aria-label","เปิด "+p.name);el.querySelector("b").textContent=p.name;el.querySelector("i").textContent=(p.artist||"")+(p.feat?" ft. "+p.feat:"")+(demo?"":(p.updated?" · "+ago(p.updated):""));
 var ch=el.querySelector(".sx-chips");ch.innerHTML=(demo?'<span class="sx-chip hot">ตัวอย่าง</span>':'')+(inf.synced?'<span class="sx-chip ok">ซิงค์แล้ว</span>':'<span class="sx-chip warn">ยังไม่ซิงค์</span>')+(!demo&&p.audio&&p.audio.localOnly?'<span class="sx-chip">เสียงอยู่ในเครื่องนี้</span>':'')+(!demo&&!p.audio?'<span class="sx-chip warn">ยังไม่มีไฟล์เพลง</span>':'');
 var cv=el.querySelector("canvas");try{artFor(cv,p)}catch(e){}
 if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){try{artFor(cv,p)}catch(e){}});
 el.onclick=function(ev){if(ev.target.closest(".sx-more,.sx-menu"))return;openProject(p.id)};el.onkeydown=function(e){if(e.key=="Enter")openProject(p.id)};
 if(!demo){var mb=h('<button class="sx-more" aria-label="ตัวเลือก">⋯</button>');el.querySelector(".sx-art").appendChild(mb);
  mb.onclick=function(ev){ev.stopPropagation();menuAt(mb,[["เปิด",function(){openProject(p.id)}],["เปลี่ยนชื่อ",function(){renameDialog(p)}],["ซ่อมโปรเจกต์ (ล้างการซิงค์)",function(){repairDialog(p)}],["ลบโปรเจกต์",function(){delDialog(p)},"del"]])}}
 return el}
function menuAt(anchor,items,top){closeMenus();var m=h('<div class="sx-menu" role="menu"></div>');items.forEach(function(it){var b=h('<button role="menuitem"></button>');b.textContent=it[0];if(it[2])b.className=it[2];b.onclick=function(ev){ev.stopPropagation();closeMenus();it[1]()};m.appendChild(b)});
 if(top){m.style.position="fixed";var r=anchor.getBoundingClientRect();m.style.top=(r.bottom+6)+"px";m.style.right=Math.max(12,innerWidth-r.right)+"px";document.body.appendChild(m);m.style.zIndex=90}else anchor.parentNode.appendChild(m);
 setTimeout(function(){document.addEventListener("click",closeMenus,{once:true})},0)}
function closeMenus(){document.querySelectorAll(".sx-menu").forEach(function(m){m.remove()})}
function modal(html){var m=h('<div class="sx-modal" role="dialog" aria-modal="true"><div class="sx-sheet">'+html+'</div></div>');document.body.appendChild(m);
 m.onclick=function(e){if(e.target==m)m.remove()};var x=m.querySelector(".sx-x");if(x)x.onclick=function(){m.remove()};
 document.addEventListener("keydown",function k(e){if(e.key=="Escape"){m.remove();document.removeEventListener("keydown",k)}});return m}

function newDialog(){var defA=BRANDED?"Bedupbiw":ST.acct.handle;
 var m=modal('<button class="sx-x" aria-label="ปิด">×</button><h3>เพลงใหม่</h3><p class="sx-note" style="margin:0 0 14px">ใส่แค่ชื่อเพลงก็เริ่มได้ ที่เหลือเติมทีหลังในโปรเจกต์</p>'+
 '<form class="sx-f" id="sx-nf"><label class="sx-lab">ชื่อเพลง *<input class="sx-in" id="sx-nn" required maxlength="60" placeholder="เช่น Dangerous"></label>'+
 '<div class="sx-row2"><label class="sx-lab">ศิลปินหลัก<input class="sx-in" id="sx-na" maxlength="40" value="'+esc(defA)+'"></label><label class="sx-lab">feat. (ถ้ามี)<input class="sx-in" id="sx-nft" maxlength="60" placeholder="เช่น Killmonker"></label></div>'+
 '<label class="sx-file" id="sx-nfl"><input type="file" id="sx-nfi" accept="audio/*,video/*,.mp3,.m4a,.wav,.mp4"><span>♪</span><span id="sx-nfn">เลือกไฟล์เพลง (mp3, m4a, wav)</span></label>'+
 '<label class="sx-lab">เนื้อเพลง (วางทั้งเพลงได้ เว้นบรรทัดว่างคั่นท่อน)<textarea class="sx-in" id="sx-nl" placeholder="ท่อนที่ 1&#10;บรรทัดที่สอง&#10;&#10;§ ท่อนฮุค (ใส่ § นำหน้าท่อนฮุค)&#10;&#10;@2 ท่อนคน feat (ใส่ @2 นำหน้า)"></textarea></label>'+
 '<div class="sx-err" id="sx-ne"></div><button class="sx-btn" type="submit" id="sx-ngo">สร้างโปรเจกต์</button></form>');
 var file=null;$("sx-nfi").onchange=function(){file=this.files[0]||null;$("sx-nfn").textContent=file?file.name:"เลือกไฟล์เพลง";if(file&&!$("sx-nn").value)$("sx-nn").value=file.name.replace(/\.[^.]+$/,"").replace(/[_-]+/g," ").slice(0,60)};
 setTimeout(function(){$("sx-nn").focus()},60);
 $("sx-nf").onsubmit=async function(ev){ev.preventDefault();var name=$("sx-nn").value.trim(),ar=$("sx-na").value.trim()||defA,ft=$("sx-nft").value.trim(),ly=$("sx-nl").value.replace(/\r/g,"").trim();
  if(!name){$("sx-ne").textContent="ใส่ชื่อเพลงก่อน";return}$("sx-ngo").disabled=true;busy("กำลังสร้างโปรเจกต์…");
  try{var raw0=ly||"วางเนื้อเพลงท่อนแรกที่นี่\nแล้วกด บันทึกเนื้อเพลงและนักร้อง";var st={bwraw:raw0,bwraw0:raw0,
   bwsing:JSON.stringify([{n:ar,c:"auto"},{n:ft||"ศิลปิน 2",c:"#5ec8ff"},{n:"ศิลปิน 3",c:"#ffd24a"},{n:"ศิลปิน 4",c:"#7ee2a0"}]),
   bwend:JSON.stringify({on:true,title:name,artist:ar+(ft?" ft. "+ft:"")}),bwstudio:JSON.stringify({title:name}),
   bwcover:JSON.stringify({tpl:"dark",title:name.toUpperCase(),artist:ar}),bwrel:JSON.stringify({artist:ar,title:name,feat:ft})};
   var id=await Store.create({name:name,artist:ar,feat:ft},st);
   if(file){busy("กำลังอัปโหลดไฟล์เพลง…");await Store.saveAudio(id,file)}
   Store.log("create",{pid:id});openProject(id)}catch(e){busy();$("sx-ngo").disabled=false;$("sx-ne").textContent="สร้างไม่สำเร็จ: "+(e&&e.message||e.code||e)}}}
function renameDialog(p){var m=modal('<button class="sx-x" aria-label="ปิด">×</button><h3>เปลี่ยนชื่อ</h3><form class="sx-f" id="sx-rf"><label class="sx-lab">ชื่อเพลง<input class="sx-in" id="sx-rn" maxlength="60"></label><button class="sx-btn" type="submit">บันทึก</button></form>');
 $("sx-rn").value=p.name;$("sx-rf").onsubmit=async function(e){e.preventDefault();var n=$("sx-rn").value.trim();if(!n)return;await Store.patch(p.id,{name:n});p.name=n;m.remove();renderGrid();toastS("เปลี่ยนชื่อแล้ว")}}
function delDialog(p){var m=modal('<h3>ลบ "'+esc(p.name)+'" ?</h3><p class="sx-note">ลบเนื้อเพลง การซิงค์ ธีม และไฟล์เพลงของโปรเจกต์นี้ ย้อนกลับไม่ได้</p><div class="sx-row2" style="margin-top:14px"><button class="sx-btn ghost" id="sx-dn">ยกเลิก</button><button class="sx-btn" id="sx-dy">ลบถาวร</button></div>');
 $("sx-dn").onclick=function(){m.remove()};$("sx-dy").onclick=async function(){busy("กำลังลบ…");try{await Store.remove(p.id,p);PROJ=PROJ.filter(function(x){return x.id!=p.id});renderGrid();toastS("ลบแล้ว")}catch(e){toastS("ลบไม่สำเร็จ")}busy();m.remove()}}
function repairDialog(p){var m=modal('<h3>ซ่อมโปรเจกต์</h3><p class="sx-note">ใช้เมื่อเปิดเพลงนี้แล้วค้างหรือเนื้อขึ้นเพี้ยน: ล้างข้อมูลการซิงค์ แต่เก็บเนื้อเพลง ธีม และไฟล์เพลงไว้ จากนั้นซิงค์ใหม่ในขั้นที่ 2</p><div class="sx-row2" style="margin-top:14px"><button class="sx-btn ghost" id="sx-rpn">ยกเลิก</button><button class="sx-btn" id="sx-rpy">ล้างการซิงค์</button></div>');
 $("sx-rpn").onclick=function(){m.remove()};$("sx-rpy").onclick=async function(){["bw3","bw3s57l"].forEach(function(k){S.raw.rm("p:"+p.id+":"+k)});S.raw.set("sns:boot:"+p.id,"0");try{await Store.push(p.id)}catch(e){}m.remove();toastS("ล้างการซิงค์แล้ว");Store.log("repair",{pid:p.id})}}

async function openProject(id){busy("กำลังเปิดโปรเจกต์…");try{if(id!="demo"){var d=await Store.pull(id);if(d===false){busy();toastS("ไม่พบโปรเจกต์นี้");return}}}catch(e){Store.log("error",{msg:"pull: "+(e&&e.message||e)})}
 location.hash="p-"+id;location.reload()}
function goHome(){var fin=function(){location.hash="";location.reload()};if(S.pid&&!S.demo&&ST.acct){busy("กำลังบันทึก…");Store.push(S.pid).then(fin,fin)}else fin()}

/* ---------- วิธีใช้ ---------- */
function guide(){modal('<button class="sx-x" aria-label="ปิด">×</button><h3>วิธีใช้ Slope North Side</h3>'+
 '<div class="sx-steps" style="grid-template-columns:1fr;margin-top:12px">'+STEPS.map(function(s){return'<div class="sx-step"><b>'+s[0]+'</b><p>'+s[1]+'</p><em>'+s[2]+'</em></div>'}).join("")+'</div>'+
 '<h3 style="margin-top:18px;font-size:16px">มือถือ กับ คอม ต่างกันยังไง</h3><p class="sx-note" style="font-size:13.5px;line-height:1.7">'+
 '<b style="color:var(--sx-fg)">มือถือ (ลิงก์นี้):</b> สร้าง/แก้โปรเจกต์ เนื้อเพลง สไตล์ ธีม ปกแบบลาย ส่งออกวิดีโอ และหน้าปล่อยเพลง<br>'+
 '<b style="color:var(--sx-fg)">คอม (ดับเบิลคลิก start.bat แล้วเปิด localhost:8790):</b> ซิงค์ด้วย AI แม่นสุด, มิกซ์/มาสเตอร์เสียง, AI วาดปกและฉาก MV, ไฟล์ WAV</p>'+
 '<h3 style="margin-top:14px;font-size:16px">ทิป</h3><p class="sx-note" style="font-size:13.5px;line-height:1.7">• ใส่ § หน้าท่อนฮุค และ @2 หน้าท่อนคน feat ตอนวางเนื้อ<br>• ทุกอย่างบันทึกอัตโนมัติ กด "‹ โปรเจกต์" มุมบนเพื่อกลับหน้าแรก<br>• ติดตั้งเป็นแอป: Chrome ⋮ › เพิ่มลงในหน้าจอหลัก<br>• ติดปัญหาอะไร กด "ผู้ช่วย" ถามได้เลย</p>')}

/* ---------- ผู้ช่วย (บอท) ---------- */
var FAQ=[
 [/ซิงค์|ไม่ตรง|เร็วไป|ช้าไป|เพี้ยน|sync/i,"ถ้าเนื้อขึ้นไม่ตรง:\n1) ขั้น 2 กด \"ตรวจทีละบรรทัด\" แล้วใช้ปุ่ม −/+ ขยับบรรทัดที่เพี้ยน (+ = ให้เนื้อขึ้นช้าลง)\n2) ถ้าทั้งเพลงเลื่อนเท่ากัน ใช้ปุ่มเลื่อนทั้งเพลง\n3) ซิงค์ที่แม่นสุดต้องทำบนคอม (start.bat) เพราะใช้ AI ตัวใหญ่\nถ้าเพี้ยนมากจนแก้ไม่ไหว กดปุ่ม \"ล้างการซิงค์\" แล้วซิงค์ใหม่",["resync"]],
 [/ไม่มีเสียง|เสียงไม่|เล่นไม่|ไม่ดัง|audio/i,"เช็กตามนี้:\n1) โปรเจกต์มีไฟล์เพลงหรือยัง (ขั้น 1 › อัปโหลด/เปลี่ยนเพลง)\n2) มือถือปิดโหมดเงียบ และกดเล่นเองหนึ่งครั้ง (เบราว์เซอร์ไม่ให้เล่นเสียงเองอัตโนมัติ)\n3) ถ้าอัปไฟล์จากคอม แต่เปิดในมือถือแล้วไม่มีเสียง ให้เลือกไฟล์เพลงในมือถืออีกครั้ง",["reload"]],
 [/ส่งออก|export|วิดีโอ|ดาวน์โหลด|บันทึกไฟล์|mp4|webm/i,"ส่งออกวิดีโอ: ขั้น 3 › เลือกขนาด (16:9 / 9:16 / ฮุค) › บันทึกวิดีโอ แล้วเปิดหน้าจอค้างไว้จนเสร็จ\nเสร็จแล้วกด \"ดาวน์โหลด\" จะมีหน้าต่างให้ยืนยันบันทึกไฟล์\nถ้าเครื่องกระตุก เปิดโหมดประหยัดเครื่องก่อน",["lite"]],
 [/ช้า|กระตุก|ค้าง|หน่วง|lag/i,"ลองเปิด \"โหมดประหยัดเครื่อง\" (ลดเอฟเฟกต์) แล้วโหลดแอปใหม่ ถ้ายังค้างที่โปรเจกต์เดิม ใช้ ⋯ › ซ่อมโปรเจกต์ ที่หน้าแรก",["lite","reload"]],
 [/รหัส|ลืม|password|ล็อกอิน|login/i,"รหัสผ่านถูกเก็บแบบเข้ารหัส ระบบดูรหัสเดิมไม่ได้ ถ้าลืม ให้แจ้งทีมเพื่อรีเซ็ตบัญชี (ห้ามพิมพ์รหัสในแชทนี้)",["ticket"]],
 [/มือถือ|คอม|ติดตั้ง|แอป|install/i,"ติดตั้งเป็นแอป: เปิดลิงก์ใน Chrome › ⋮ › เพิ่มลงในหน้าจอหลัก\nมือถือ: แก้โปรเจกต์ สไตล์ ส่งออกวิดีโอ\nคอม: ซิงค์ AI, มิกซ์, AI วาดปก/MV (ต้องเปิด start.bat)",[]],
 [/บีต|beat|ลิขสิทธิ์|หารายได้|monet/i,"ดูตารางราคาบีตและสิทธิ์ได้ที่ขั้น 3 › ปล่อยเพลง & โปรโมท เลือกประเภทบีตที่ใช้ แอปจะบอกว่าลงสตรีม/หารายได้ได้ไหม",[]],
 [/ปก|cover|mv|ภาพ/i,"ปกแบบลายทำได้ทุกเครื่องในหัวข้อปกเพลง ส่วน AI วาดปกและฉาก MV ต้องเปิดเซิร์ฟเวอร์บนคอม (start.bat) แล้วใช้แอปที่ localhost:8790",[]]];
var bot={el:null,hist:[],open:function(){if(this.el){this.el.hidden=false;return}var b=this.el=h('<div class="sx-bot" role="dialog" aria-label="ผู้ช่วย Slope"><div class="sx-both"><div><b>ผู้ช่วย Slope</b><small>'+(ST.sample?"ตอบด้วย AI · แก้ปัญหาเบื้องต้นให้ได้":"ตอบจากคู่มือ · แจ้งทีมได้")+'</small></div><button aria-label="ปิด">×</button></div>'+
  '<div class="sx-msgs" id="sx-msgs"></div><div class="sx-quick">'+["ซิงค์ไม่ตรง","ส่งออกวิดีโอไม่ได้","ไม่มีเสียง","แอปช้า/ค้าง","ใช้ในมือถือได้แค่ไหน","แจ้งปัญหาให้ทีม"].map(function(q){return'<button>'+q+'</button>'}).join("")+'</div>'+
  '<form class="sx-bin" id="sx-bf"><input id="sx-bq" placeholder="พิมพ์ปัญหาหรือคำถาม…" maxlength="500" autocomplete="off"><button type="submit">ส่ง</button></form></div>');
  document.body.appendChild(b);b.querySelector(".sx-both button").onclick=function(){b.hidden=true};
  b.querySelectorAll(".sx-quick button").forEach(function(x){x.onclick=function(){if(x.textContent=="แจ้งปัญหาให้ทีม"){bot.ticketForm();return}bot.ask(x.textContent)}});
  $("sx-bf").onsubmit=function(e){e.preventDefault();var q=$("sx-bq").value.trim();if(!q)return;$("sx-bq").value="";bot.ask(q)};
  this.say("ai","สวัสดีครับ ติดปัญหาอะไรในแอป พิมพ์มาได้เลย ถ้าแก้เองได้ผมจะมีปุ่มให้กดแก้ทันที ถ้าต้องให้ทีมดู ผมจะส่งเรื่องให้")},
 say:function(who,t,fixes){var box=$("sx-msgs");if(!box)return;var m=h('<div class="sx-m '+(who=="me"?"me":"ai")+'"></div>');m.textContent=t;
  if(fixes&&fixes.length){var f=h('<div class="sx-fixes"></div>');fixes.forEach(function(k){var F=FIX[k];if(!F)return;var bt=h('<button></button>');bt.textContent=F[0];bt.onclick=function(){F[1]()};f.appendChild(bt)});m.appendChild(f)}
  box.appendChild(m);box.scrollTop=box.scrollHeight;this.hist.push({role:who=="me"?"user":"assistant",content:t});return m},
 ask:async function(q){this.say("me",q);var hit=null;FAQ.forEach(function(f){if(!hit&&f[0].test(q))hit=f});
  if(ST.sample){var w=this.say("ai","…");try{var ctx="คุณคือผู้ช่วยในแอป Slope North Side (แอปทำวิดีโอเนื้อเพลง ปก มิกซ์ ปล่อยเพลง ของศิลปินไทย) ตอบภาษาไทย สั้น ทำตามได้ทันที ไม่เกิน 6 บรรทัด\n"+
   "ความรู้ของแอป:\n"+STEPS.map(function(s,i){return(i+1)+". "+s[0]+": "+s[1]+" ("+s[2]+")"}).join("\n")+"\n"+FAQ.map(function(f){return"- "+f[1].replace(/\n/g," ")}).join("\n")+
   "\nสถานะตอนนี้: เปิดอยู่ที่ "+(S.pid?"โปรเจกต์ "+S.pid:"หน้าแรก")+" · โหมด "+ST.mode+" · ข้อผิดพลาดล่าสุด: "+(S.errs.slice(-3).map(function(e){return e.m}).join(" | ")||"ไม่มี")+
   "\nถ้าแนะนำให้กดแก้ ใส่แท็กท้ายคำตอบได้: [[fix:reload]] โหลดใหม่, [[fix:lite]] โหมดประหยัด, [[fix:resync]] ล้างการซิงค์เพลงนี้, [[fix:home]] กลับหน้าแรก, [[fix:ticket]] ส่งเรื่องให้ทีมแบรนด์ (ใช้เมื่อเป็นบั๊กของระบบ เซิร์ฟเวอร์ บัญชี หรือขอฟีเจอร์ใหม่) ห้ามขอรหัสผ่าน";
   var msgs=[{role:"user",content:ctx+"\n\nคำถาม: "+q}];var r=await ST.sample(msgs,{modelTier:"quick",cache:false,onText:function(x){w.textContent=x.text.replace(/\[\[fix:\w+\]\]/g,"")}});
   var txt=r.text||"",fx=[];txt.replace(/\[\[fix:(\w+)\]\]/g,function(_,k){fx.push(k)});w.remove();this.hist.pop();this.say("ai",txt.replace(/\[\[fix:\w+\]\]/g,"").trim(),fx);return}catch(e){w.remove();this.hist.pop()}}
  if(hit)this.say("ai",hit[1],hit[2]);else this.say("ai","ยังไม่มีคำตอบสำเร็จรูปสำหรับเรื่องนี้ ส่งเรื่องให้ทีมแบรนด์ดูได้เลย ระบบจะแนบข้อผิดพลาดล่าสุดไปให้ด้วย",["ticket","reload"])},
 ticketForm:function(){var t=this.say("ai","อธิบายสั้นๆ ว่าเกิดอะไรขึ้น ทำอะไรอยู่ตอนนั้น แล้วกดส่ง");var f=h('<form class="sx-bin" style="border:0;padding:8px 0 0"><input placeholder="เช่น กดส่งออก 9:16 แล้วค้างที่ 80%" maxlength="400"><button>ส่ง</button></form>');t.appendChild(f);
  f.onsubmit=function(e){e.preventDefault();var v=f.querySelector("input").value.trim();if(!v)return;Store.log("ticket",{msg:v,chat:bot.hist.slice(-6),errs:S.errs.slice(-5)});f.remove();
   bot.say("ai",ST.mode=="cloud"?"ส่งเรื่องให้ทีมแล้ว Claude จะเห็นตอนตรวจระบบรอบถัดไป ระหว่างนี้ลองปุ่มด้านล่างดูก่อนได้":(LOCALHOST&&location.protocol!="file:"?"บันทึกเรื่องไว้ในคอมแล้ว (โฟลเดอร์ reports) Claude จะเห็นตอนตรวจระบบ":"บันทึกไว้ในเครื่องนี้แล้ว บอก Claude ในแชทด้วยนะ เพราะโหมดนี้ส่งเรื่องออกนอกเครื่องไม่ได้"),["reload"])}}};
var FIX={reload:["โหลดแอปใหม่",function(){location.reload()}],
 lite:["เปิดโหมดประหยัดเครื่อง",function(){var c=$("litechk");if(c&&!c.checked){c.click()}bot.say("ai","เปิดโหมดประหยัดเครื่องแล้ว")}],
 resync:["ล้างการซิงค์เพลงนี้",function(){if(!S.pid||S.demo){bot.say("ai","เปิดโปรเจกต์ที่ต้องการก่อน แล้วค่อยกดปุ่มนี้");return}var m=bot.say("ai","ยืนยันล้างการซิงค์ของเพลงนี้? เนื้อเพลงและธีมยังอยู่");var f=h('<div class="sx-fixes"><button>ยืนยัน ล้างเลย</button></div>');m.appendChild(f);f.firstChild.onclick=function(){localStorage.removeItem("bw3");localStorage.removeItem("bw3s57l");Store.log("repair",{pid:S.pid});Store.push(S.pid).finally(function(){location.reload()})}}],
 home:["กลับหน้าแรก",function(){goHome()}],ticket:["ส่งเรื่องให้ทีม",function(){bot.ticketForm()}]};

/* ---------- ในหน้าแก้โปรเจกต์ ---------- */
var META=null,lastPush=0,saveEl=[];
function setSave(t){saveEl.forEach(function(e){e.textContent=t})}
function addBar(host){if(!host||host.querySelector(".sx-back"))return;var b=h('<button class="sx-back" type="button"></button>');b.textContent="‹ "+(META?META.name:(S.demo?"ตัวอย่าง":"โปรเจกต์"));b.title="กลับหน้าโปรเจกต์ทั้งหมด";b.onclick=goHome;host.insertBefore(b,host.firstChild);
 var q=h('<button class="sx-back" type="button" style="margin:0 0 0 6px">?</button>');q.title="ผู้ช่วย";q.onclick=function(){bot.open()};var chip=host.querySelector("#chip");if(chip)chip.parentNode.insertBefore(q,chip);else host.appendChild(q);
 var s=h('<span class="sx-save"></span>');b.after(s);saveEl.push(s)}
async function enterProject(){var r=$("sx");if(r)r.hidden=true;lanPin();
 if(S.demo){META={name:"Dangerous (ตัวอย่าง)"};var bn=h('<div class="sx-demo"><span>ตัวอย่างผลงาน · '+(S.silent?'ไม่มีเสียงเพลงในเว็บสาธารณะ':'แก้ได้แต่ไม่บันทึก')+'</span><button>ทำเพลงของคุณ</button></div>');document.body.appendChild(bn);bn.querySelector("button").onclick=function(){goHome()}}
 else{try{META=await Store.meta(S.pid)}catch(e){META=null}if(!META){toastS("ไม่พบโปรเจกต์นี้ในบัญชี");setTimeout(function(){location.hash="";location.reload()},1200);return}}
 addBar($("top"));addBar(document.querySelector("#pg1 .pgh"));try{document.title=(META.name||"")+" · Slope North Side"}catch(e){}
 if(S.demo)return;
 if(S.silent){var au0=await Store.loadAudio(S.pid,META).catch(function(){return null});if(au0&&typeof window.snsSetAudio=="function"){window.snsSetAudio(au0.url,au0.name)}else{var fn0=$("fname");if(fn0)fn0.textContent="เว็บสาธารณะไม่ได้ฝังเพลงไว้ กดอัปโหลดไฟล์เพลง Dangerous ในเครื่องนี้ครั้งเดียว";needAudio()}}
 if(!S.baked){var au=await Store.loadAudio(S.pid,META).catch(function(){return null});
  if(au&&typeof window.snsSetAudio=="function")window.snsSetAudio(au.url,au.name);
  else{var fn=$("fname");if(fn)fn.textContent=META.audio&&META.audio.localOnly?"ไฟล์เพลงอยู่ในเครื่องที่อัปโหลด เลือกไฟล์อีกครั้งในเครื่องนี้":"ยังไม่มีไฟล์เพลง กดอัปโหลดด้านล่าง";needAudio()}}
 var fi=$("fi");if(fi)fi.addEventListener("change",function(){var f=this.files[0];if(!f)return;setSave("กำลังอัปโหลดเพลง…");Store.saveAudio(S.pid,f).then(function(a){META.audio=a;S.baked=false;setSave(a.localOnly?"เสียงเก็บในเครื่องนี้":"บันทึกแล้ว")},function(){setSave("อัปโหลดเพลงไม่สำเร็จ")})});
 lastPush=+(S.raw.get("sns:t:"+S.pid)||0);setSave("บันทึกแล้ว");
 setInterval(function(){if(S.dirty&&S.dirty>lastPush&&now()-S.dirty>1500){lastPush=now();setSave("กำลังบันทึก…");Store.push(S.pid).then(function(){setSave("บันทึกแล้ว")},function(e){setSave("ยังไม่ได้บันทึก (ออฟไลน์?)");Store.log("error",{msg:"push: "+(e&&e.message||e)})})}},2500);
 document.addEventListener("visibilitychange",function(){if(document.visibilityState=="hidden"&&S.dirty>lastPush){lastPush=now();Store.push(S.pid).catch(function(){})}})}

/* ---------- ใช้ในมือถือผ่าน Wi-Fi บ้าน ---------- */
var LANORIGIN=!LOCALHOST&&location.protocol=="http:";
async function lanPin(){if(!LANORIGIN)return;try{var j=await (await fetch("/api/ping")).json();if(!j||!j.lan)return;var k=S.raw.get("bwkey");
 if(k){var t=await fetch("/api/mixhist",{headers:{"X-Key":k}});if(t.ok)return}
 var m=modal('<h3>ใส่ PIN ของคอม</h3><p class="sx-note">ดู PIN 6 หลักได้ที่หน้าแรกของแอปบนคอม (การ์ด "ใช้ในมือถือ") หรือในหน้าต่างดำของ start.bat ใส่ครั้งเดียว ระบบจำไว้</p><form class="sx-f" id="sx-pf"><input class="sx-in" id="sx-pin" inputmode="numeric" maxlength="12" autocomplete="one-time-code" placeholder="PIN 6 หลัก"><div class="sx-err" id="sx-pe"></div><button class="sx-btn" type="submit">เชื่อมต่อคอม</button></form>');
 $("sx-pf").onsubmit=async function(e){e.preventDefault();var v=$("sx-pin").value.trim();var t=await fetch("/api/mixhist",{headers:{"X-Key":v}}).catch(function(){return{ok:false}});
  if(!t.ok){$("sx-pe").textContent="PIN ไม่ถูกต้อง";return}S.raw.set("bwkey",v);var ak=$("akey");if(ak)ak.value=v;m.remove();toastS("เชื่อมต่อคอมแล้ว ใช้ AI ได้")}}catch(e){}}
var WRITE_URL="https://claude.ai/artifact/5howytgf8NkaPtrVWWxH6n";
function writeCard(){var host=$("sx-write");if(!host)return;var url=ST.mode=="cloud"?WRITE_URL:(LOCALHOST||location.protocol=="http:")?"write.html":WRITE_URL;
 host.innerHTML='<div class="sx-sech"><h2>แต่งเพลง & หาบีต</h2><span>เริ่มเพลงใหม่ก่อนเข้าโปรเจกต์</span></div><a class="sx-lanc" id="sx-wl" target="_blank" rel="noopener" style="text-decoration:none;color:inherit"><div style="font:400 34px/1 var(--sx-disp);color:var(--sx-hot)">✎</div><div style="min-width:0;flex:1"><b style="font-size:16px">เปิดหน้าแต่งเพลง</b><p class="sx-note" style="margin:4px 0 0">หาแรงบันดาลใจ · หาบีตฟรี/เสียเงินพร้อมราคา · สมุดเนื้อเพลงพร้อมเล่นบีต แล้วส่งเนื้อเข้าแอปนี้</p></div><span class="sx-pill">เปิด ↗</span></a>';$("sx-wl").href=url;var wt=$("sx-wtop");if(wt)wt.href=url}
async function lanCard(){if(!LOCALHOST||location.protocol=="file:")return;try{var j=await (await fetch("/api/lan")).json();if(!j||!j.url)return;var host=$("sx-lan");if(!host)return;
 host.innerHTML='<div class="sx-sech"><h2>ใช้ในมือถือที่บ้าน (AI เต็มรูปแบบ)</h2><span>มือถือต่อ Wi-Fi เดียวกับคอมนี้</span></div><div class="sx-lanc"><div id="sx-qr" aria-hidden="true"></div><div style="min-width:0"><div class="sx-note">เปิดในมือถือ</div><div class="sx-big" id="sx-lu"></div><div class="sx-note" style="margin-top:8px">PIN</div><div class="sx-big" id="sx-lp"></div><p class="sx-note" style="margin-top:8px">มือถือจะใช้พลังคอมนี้วาด MV/ปก ซิงค์ และมิกซ์ได้ เปิด start.bat ค้างไว้ ถ้า Windows ถามเรื่อง Firewall ให้กด Allow</p></div></div>';
 $("sx-lu").textContent=j.url;$("sx-lp").textContent=j.pin;
 var sc=document.createElement("script");sc.src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js";sc.onload=function(){try{new QRCode($("sx-qr"),{text:j.url,width:132,height:132,colorDark:"#000",colorLight:"#fff"})}catch(e){}};document.head.appendChild(sc)}catch(e){}}

function needAudio(){if($("sx-na"))return;var bn=h('<div class="sx-demo" id="sx-na"><span>ยังไม่มีเสียงเพลงในเครื่องนี้</span><button>เลือกไฟล์เพลง</button></div>');document.body.appendChild(bn);
 bn.querySelector("button").onclick=function(){var fi=$("fi");if(fi)fi.click()};var fi2=$("fi");if(fi2)fi2.addEventListener("change",function(){if(this.files[0])bn.remove()})}
/* ---------- เริ่ม ---------- */
async function start(){if(S.pid)document.documentElement.classList.add("sx-inproj");
 if(!S.pid)splash();
 await detect();
 var acct=null;try{acct=await getAcct()}catch(e){Store.log("error",{msg:"acct: "+(e&&e.message||e)})}
 if(acct&&sessOk(acct)){ST.acct=acct;afterLogin();return}
 if(S.pid)splash("เข้าสู่ระบบก่อนเปิดโปรเจกต์");
 if(ST.mode=="cloud"){if(acct&&!acct.handle){acct=null}
  if(acct&&!S.raw.get("sns:out:"+ST.uid)){ST.acct=acct;sessOn(acct.handle);afterLogin();return}
  if(!acct&&ST.owner){try{acct={handle:BRAND,created:now(),brand:true,via:"claude"};await saveAcct(acct);ST.acct=acct;sessOn(BRAND);Store.log("signup",{id:BRAND,auto:1});afterLogin();return}catch(e){acct=null}}
  cloudView(acct)}
 else{var A=J("sns:accts",{});loginView(Object.keys(A).length?"login":"signup")}}
window.SNSX={Store:Store,ST:ST,bot:bot,home:home,goHome:goHome};
if(document.readyState=="loading")document.addEventListener("DOMContentLoaded",start);else start();
})();
