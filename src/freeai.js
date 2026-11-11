/* ===== Slope North Side · AI ฟรีบนเว็บ GitHub (นอก claude.ai) =====
   ใช้ Puter.js แบบ "ผู้ใช้จ่ายเอง": เว็บเราไม่มี API key ไม่มีค่าใช้จ่าย
   คนใช้ล็อกอิน Puter (ฟรี) ครั้งเดียว แล้วใช้ AI ด้วยโควตาฟรีของบัญชีเขาเอง
   บน claude.ai ไม่ทำอะไร (ใช้ AI ของ Claude ตามเดิม) */
(function(){
"use strict";
if(/claude\.ai|claudeusercontent/.test(location.hostname))return;
var SRC="https://js.puter.com/v2/",LP=null,K="sns:freeai:off";
function load(){if(window.puter&&puter.ai)return Promise.resolve(window.puter);if(LP)return LP;
 LP=new Promise(function(res,rej){var s=document.createElement("script");s.src=SRC;s.async=true;s.onload=function(){window.puter?res(window.puter):rej({code:"load"})};s.onerror=function(){LP=null;rej({code:"load"})};document.head.appendChild(s)});return LP}
function signedIn(){try{return!!(window.puter&&puter.auth&&puter.auth.isSignedIn())}catch(e){return false}}
function active(){try{return!navigator.userActivation||navigator.userActivation.isActive}catch(e){return true}}
async function signIn(){var p=await load();if(signedIn())return true;await p.auth.signIn();upd();return signedIn()}
function textOf(r){if(r==null)return"";if(typeof r=="string")return r;var c=r.message&&r.message.content;
 if(Array.isArray(c))c=c.map(function(x){return x&&(x.text||"")||""}).join("");if(typeof c=="string")return c;try{return String(r)}catch(e){return""}}
/* หน้าตาเหมือน sample ของ claude.ai: sample(messages,{onText}) → {text} */
async function sample(msgs,opt){opt=opt||{};var p;try{p=await load()}catch(e){throw{code:"unavailable",message:"โหลดบริการ AI ฟรีไม่ได้ (เช็กเน็ต)"}}
 if(!signedIn()){/* ไม่เด้งหน้าสมัคร Puter เอง: ใช้คลังในแอปแทน จนกว่าผู้ใช้จะกดปุ่ม "เปิดใช้ AI ฟรี" เอง */upd(true);throw{code:"not_granted",message:"ใช้คลังในแอปแทน (AI ฟรีต้องกดปุ่ม เปิดใช้ AI ฟรี ก่อน)"}}
 var M=(msgs||[]).map(function(m){return{role:m.role||"user",content:typeof m.content=="string"?m.content:textOf({message:{content:m.content}})}});
 var r;try{r=await p.ai.chat(M)}catch(e){var m=String(e&&(e.message||e.error&&e.error.message||e)||"");throw{code:/limit|quota|credit|insufficient|funds/i.test(m)?"rate_limited":"error",message:m}}
 var t=textOf(r);if(typeof opt.onText=="function")try{opt.onText({text:t})}catch(e){}return{text:t}}
sample.sample=sample;
/* ปุ่มเล็ก "เปิดใช้ AI ฟรี" มุมล่างซ้าย หายไปเมื่อล็อกอินแล้ว */
var btn=null;
function upd(force){if(signedIn()){if(btn)btn.remove();btn=null;return}
 var off=false;try{off=localStorage.getItem(K)=="1"}catch(e){}if(off&&!force)return;if(btn||!document.body)return;
 btn=document.createElement("div");btn.id="sns-freeai";
 btn.innerHTML='<button type="button" class="go">✦ เปิดใช้ AI ฟรี</button><button type="button" class="x" aria-label="ซ่อน">×</button>';
 btn.style.cssText="position:fixed;left:max(12px,env(safe-area-inset-left,0px));bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:9990;display:flex;align-items:center;gap:2px;background:rgba(18,13,18,.94);border:1px solid rgba(255,51,71,.55);border-radius:99px;padding:3px;box-shadow:0 10px 30px -10px #000;font:600 13px 'Noto Sans Thai',system-ui,sans-serif";
 var go=btn.querySelector(".go"),x=btn.querySelector(".x");
 go.style.cssText="min-height:36px;padding:0 14px;border:0;border-radius:99px;background:#ff3347;color:#fff;font:inherit;cursor:pointer";
 x.style.cssText="width:32px;height:32px;border:0;background:none;color:#a9989e;font-size:18px;cursor:pointer";
 go.title="ใช้ AI ฟรีผ่าน Puter: ล็อกอินหรือสมัคร Puter ฟรีครั้งเดียว ใช้โควตาฟรีของบัญชีคุณเอง";
 go.onclick=function(){go.textContent="กำลังเชื่อมต่อ…";signIn().then(function(ok){if(ok){toast("เปิดใช้ AI แล้ว ลองกดปุ่ม AI ได้เลย");try{document.dispatchEvent(new CustomEvent("sns:freeai"))}catch(e){}}else go.textContent="✦ เปิดใช้ AI ฟรี"}).catch(function(){go.textContent="✦ เปิดใช้ AI ฟรี";toast("เชื่อมต่อไม่สำเร็จ ลองใหม่อีกครั้ง")})};
 x.onclick=function(){try{localStorage.setItem(K,"1")}catch(e){}btn.remove();btn=null};
 document.body.appendChild(btn)}
function toast(m){try{if(window.toast)return window.toast(m)}catch(e){}var t=document.createElement("div");t.textContent=m;t.style.cssText="position:fixed;left:50%;top:80px;transform:translateX(-50%);z-index:9999;background:#fff;color:#111;padding:10px 16px;border-radius:12px;font:500 14px system-ui";document.body.appendChild(t);setTimeout(function(){t.remove()},2400)}
window.SNSFreeAI={sample:sample,load:load,signIn:signIn,signedIn:signedIn,provider:"Puter (ฟรี · ผู้ใช้ล็อกอินเอง)"};
/* แอปหลัก: ใส่ให้ SNSX.ST.sample เมื่อแอปพร้อม (บน claude.ai ไม่แตะ) */
var tries=0,iv=setInterval(function(){tries++;var X=window.SNSX;if(X&&X.ST){if(!X.ST.sample)X.ST.sample=sample;clearInterval(iv)}else if(tries>120)clearInterval(iv)},250);
/* โหลด Puter ไว้ก่อนเงียบๆ เพื่อรู้ว่าล็อกอินอยู่ไหม แล้วค่อยโชว์ปุ่ม */
function boot(){load().then(function(){setTimeout(upd,600)}).catch(function(){})}
if(document.readyState=="loading")document.addEventListener("DOMContentLoaded",boot);else boot();
})();
