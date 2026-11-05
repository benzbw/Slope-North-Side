/* Slope North Side · boot: เลือกโปรเจกต์จาก #p-<id> และแยกข้อมูลแต่ละโปรเจกต์ออกจากกัน */
(function(){
var h=(location.hash||"").replace(/^#/,""),m=/^p-([a-z0-9_-]{1,40})$/i.exec(h);
var S=window.SNS={pid:m?m[1].toLowerCase():null,mem:{}};
S.demo=S.pid=="demo";S.baked=S.pid=="dangerous"||S.demo;
var GL={bwalbums:1,bwkey:1,bwlite:1};S.GL=GL;
var P=Storage.prototype,g=P.getItem,st=P.setItem,rm=P.removeItem,LS=null;
try{LS=window.localStorage}catch(e){}
function own(o,k){return o===LS&&typeof k=="string"&&k.slice(0,2)=="bw"&&!GL[k]}
function ns(k){return "p:"+(S.pid||"_home")+":"+k}
P.getItem=function(k){if(own(this,k)){if(S.demo)return S.mem.hasOwnProperty(k)?S.mem[k]:null;return g.call(this,ns(k))}return g.call(this,k)};
P.setItem=function(k,v){if(own(this,k)){if(S.demo){S.mem[k]=String(v);return}S.dirty=Date.now();return st.call(this,ns(k),v)}return st.call(this,k,v)};
P.removeItem=function(k){if(own(this,k)){if(S.demo){delete S.mem[k];return}S.dirty=Date.now();return rm.call(this,ns(k))}return rm.call(this,k)};
S.raw={get:function(k){try{return g.call(LS,k)}catch(e){return null}},set:function(k,v){try{st.call(LS,k,v);return true}catch(e){return false}},rm:function(k){try{rm.call(LS,k)}catch(e){}},
 keys:function(){var o=[];try{for(var i=0;i<LS.length;i++)o.push(LS.key(i))}catch(e){}return o}};
/* กันแอปค้างตอนเปิดโปรเจกต์: เปิดพังติดกัน 2 ครั้ง → กลับหน้าแรกแบบปลอดภัย */
if(S.pid&&!S.demo){var bk="sns:boot:"+S.pid,n=+(S.raw.get(bk)||0);
 if(n>=2){S.raw.set(bk,"0");S.crashed=S.pid;S.pid=null;S.baked=false;try{history.replaceState(null,"",location.pathname+location.search)}catch(e){}}
 else{S.raw.set(bk,String(n+1));window.addEventListener("load",function(){setTimeout(function(){S.raw.set(bk,"0")},4000)})}}
/* จดข้อผิดพลาดไว้ให้ระบบตรวจ */
S.errs=[];function lg(msg,src){if(S.errs.length>40)return;var e={m:String(msg||"").slice(0,400),s:String(src||"").slice(0,600),p:S.pid||"home",t:Date.now()};S.errs.push(e);if(S.onErr)try{S.onErr(e)}catch(x){}}
window.addEventListener("error",function(ev){lg(ev.message,(ev.filename||"")+":"+(ev.lineno||0)+" "+(ev.error&&ev.error.stack||""))});
window.addEventListener("unhandledrejection",function(ev){var r=ev.reason;lg("promise: "+(r&&r.message||r),r&&r.stack)});
})();
