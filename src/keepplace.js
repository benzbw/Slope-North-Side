/* ===== Slope North Side · จำตำแหน่งในโปรเจกต์ =====
   มือถือมักปิดหน้าเว็บตอนสลับไปแอปอื่น พอกลับมาหน้าโหลดใหม่ → พากลับไปขั้นเดิม แท็บย่อยเดิม ตำแหน่งเลื่อนเดิม */
(function(){
"use strict";
var K="sns:place",S=window.SNS||{},pid=S.pid;if(!pid)return;
function get(){try{return JSON.parse(localStorage.getItem(K)||"null")}catch(e){return null}}
function page(){var best=null;["pg1","sheet","sx"].map(function(i){return document.getElementById(i)}).concat([].slice.call(document.querySelectorAll("main,section,.pn"))).forEach(function(e){if(!e||!e.getClientRects().length)return;var cs=getComputedStyle(e);if(!/(auto|scroll)/.test(cs.overflowY)||e.scrollHeight<=e.clientHeight+10)return;if(!best||e.clientHeight>best.clientHeight)best=e});return best}
function subBar(){return[].slice.call(document.querySelectorAll(".sx-sub")).filter(function(x){return x.getClientRects().length})[0]||null}
function now(){var pg=page();var sb=subBar(),sub=null;if(sb){var bs=[].slice.call(sb.querySelectorAll("button"));bs.forEach(function(b,i){if(b.getAttribute("aria-selected")=="true"||/\bon\b|\bact\b/.test(b.className))sub=i})}
 var y=pg?pg.scrollTop:0,e=document.scrollingElement||document.documentElement;if(!y&&e)y=e.scrollTop||window.scrollY||0;var ab=document.querySelector("#dock nav button.act[data-s]")||document.querySelector("#dock nav button[aria-current][data-s]");return{pid:pid,s:ab?ab.dataset.s:"1",sub:sub,y:y,sc:pg?pg.id:"",t:Date.now()}}
var ready=false;function save(){if(!ready)return;var o=now();if(o)try{localStorage.setItem(K,JSON.stringify(o))}catch(e){}}
var T=0;function later(){clearTimeout(T);T=setTimeout(save,400)}
document.addEventListener("scroll",later,true);document.addEventListener("click",function(){setTimeout(save,500)},true);
document.addEventListener("visibilitychange",function(){if(document.visibilityState=="hidden")save()});window.addEventListener("pagehide",save);
/* คืนตำแหน่ง */
var want=get(),ok=want&&want.pid===pid&&Date.now()-want.t<864e5*2&&want.s;
var tries=0,iv=setInterval(function(){tries++;var b=document.querySelector('#dock nav button[data-s="'+(ok?want.s:"1")+'"]');if(!b){if(tries>80){clearInterval(iv);ready=true}return}clearInterval(iv);
 if(!ok){setTimeout(function(){ready=true},800);return}
 setTimeout(function(){if(!/\bact\b/.test(b.className))try{b.click()}catch(e){}
  setTimeout(function(){var sb=subBar();if(want.sub!=null&&sb){var bt=sb.querySelectorAll("button")[want.sub];if(bt&&bt.getAttribute("aria-selected")!="true")try{bt.click()}catch(e){}}
   [250,800,1500].forEach(function(d){setTimeout(function(){var p2=(want.sc&&document.getElementById(want.sc))||page();if(want.y&&p2&&p2.scrollTop<20)p2.scrollTop=want.y;else if(want.y&&!p2)window.scrollTo(0,want.y)},d)});
   setTimeout(function(){ready=true},1700)},350)},400)},150);
})();
