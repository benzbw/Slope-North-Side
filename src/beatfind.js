/* ===== Slope North Side · บีตจริงจาก YouTube (ฟรี ไม่ใช้ key) =====
   ข้อมูลจาก data/beats.json ที่ GitHub Actions ดึงทุกวันด้วย yt-dlp · โชว์รูปปก เล่นฟังในแอป เก็บ หรือใช้แต่งเพลง */
(function(){
"use strict";
var $=function(i){return document.getElementById(i)},DATA=null,LP=null,SHOW=8;
function esc(t){return String(t==null?"":t).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function mmss(s){return Math.floor(s/60)+":"+("0"+s%60).slice(-2)}
function nf(n){return n>=1e6?(n/1e6).toFixed(1)+"M":n>=1e3?Math.round(n/100)/10+"K":String(n)}
function load(){if(DATA)return Promise.resolve(DATA);if(LP)return LP;
 var urls=["data/beats.json","https://benzbw.github.io/Slope-North-Side/data/beats.json","https://raw.githubusercontent.com/benzbw/Slope-North-Side/main/data/beats.json"];
 LP=(async function(){for(var i=0;i<urls.length;i++){try{var r=await fetch(urls[i],{cache:"no-cache"});if(r.ok){var j=await r.json();if(j&&j.artists){DATA=j;return j}}}catch(e){}}
  if(window.SNS_BEATS){DATA=window.SNS_BEATS;return DATA}throw new Error("no data")})();LP.catch(function(){LP=null});return LP}
var GK={rnb:"rnb",drill:"drill",trap:"trap",lofi:"lofi",rap:"rap",thai:"thai",emo:"emo",phonk:"phonk",pop:"pop"};
function pickList(D,inp){var a=(inp.artist||"").toLowerCase().trim(),out=[],seen={},src=[];
 var add=function(L,why){(L||[]).forEach(function(x){if(!seen[x.id]){seen[x.id]=1;out.push(Object.assign({why:why},x))}})};
 if(a){Object.keys(D.artists).forEach(function(k){if(k==a||k.indexOf(a)>=0||a.indexOf(k)>=0){add(D.artists[k],"ฟีล "+k.replace(/\b\w/g,function(c){return c.toUpperCase()}));src.push(k)}})}
 var g=GK[inp.genre]||null;if(g&&D.genres[g])add(D.genres[g],"แนวเดียวกัน");
 if(inp.budget=="free")out=out.filter(function(x){return x.free});else if(inp.budget=="paid")out=out.filter(function(x){return!x.free});
 return{list:out,src:src,updated:D.updated}}
function card(x,i){var u="https://www.youtube.com/watch?v="+x.id;
 return'<div class="sw-beat" data-bf="'+i+'"><div class="th"><img loading="lazy" alt="" src="https://i.ytimg.com/vi/'+x.id+'/mqdefault.jpg" onerror="this.style.display=\'none\'"></div><div class="bd"><b>'+esc(x.t)+'</b>'+
  '<small>'+esc(x.ch)+(x.d?' · '+mmss(x.d):'')+(x.v?' · '+nf(x.v)+' วิว':'')+'</small><div class="tg">'+(x.free?'<span class="sw-tag">มีคำว่า FREE</span>':'<span class="sw-tag paid">ดูราคาในคำอธิบาย</span>')+'<span class="sw-tag" style="background:rgba(255,255,255,.06);color:var(--sx-mut)">'+esc(x.why)+'</span></div>'+
  '<div class="ac"><button class="sw-ghost" data-play="'+i+'">▶ ฟัง</button><a class="sw-ghost" target="_blank" rel="noopener" href="'+u+'">YouTube ↗</a><button class="sw-ghost" data-keep="'+i+'">★ เก็บ</button><button class="sw-ghost" data-use="'+i+'">✎ ใช้แต่ง</button></div><div class="pl"></div></div></div>'}
var CUR=[],N=SHOW;
async function render(inp){var host=$("bf");if(!host)return;host.innerHTML='<div class="sw-box"><h3>บีตจริงแนวคล้ายเพลงที่อิน</h3><p class="sw-note">กำลังโหลดบีต…</p></div>';
 try{var D=await load()}catch(e){host.innerHTML='<div class="sw-box"><h3>บีตจริงแนวคล้ายเพลงที่อิน</h3><p class="sw-note">โหลดรายการบีตไม่ได้ในลิงก์นี้ ลองเปิดหน้าแต่งเพลงจากลิงก์ GitHub หรือใช้ปุ่มค้นหาด้านล่าง</p></div>';return}
 var R=pickList(D,inp);CUR=R.list;N=SHOW;
 if(!CUR.length){host.innerHTML='<div class="sw-box"><h3>บีตจริงแนวคล้ายเพลงที่อิน</h3><p class="sw-note">ยังไม่มีบีตของ "'+esc(inp.artist||"")+'" ในคลัง (มี '+Object.keys(D.artists).length+' ศิลปิน อัปเดต '+esc(D.updated)+') ลองเลือก "แนว" ให้ตรง แล้วกดค้นหาอีกครั้ง หรือใช้ลิงก์ค้นหาด้านล่าง</p></div>';return}
 draw(R,inp)}
function draw(R,inp){var host=$("bf");
 host.innerHTML='<div class="sw-box"><h3>บีตจริงแนวคล้ายเพลงที่อิน</h3><p class="sw-note">'+CUR.length+' บีตจาก YouTube'+(R.src.length?' · ฟีล '+esc(R.src.join(", "))+' + แนวเดียวกัน':' · แนวเดียวกัน')+' · อัปเดต '+esc(R.updated)+' · <b style="color:var(--sx-fg)">ก่อนใช้ลงสตรีม เปิดดูเงื่อนไขในคำอธิบายคลิปทุกครั้ง</b> (คำว่า FREE ในชื่อ ไม่ได้แปลว่าหารายได้ได้เสมอ)</p>'+
  '<div class="sw-beats">'+CUR.slice(0,N).map(card).join("")+'</div>'+(CUR.length>N?'<div class="sw-acts"><button class="sw-ghost" id="bf-more">ดูเพิ่ม ('+(CUR.length-N)+')</button></div>':'')+'</div>';
 var m=$("bf-more");if(m)m.onclick=function(){N+=SHOW;draw(R,inp)}}
document.addEventListener("click",function(e){var t=e.target&&e.target.closest&&e.target.closest("#bf [data-play],#bf [data-keep],#bf [data-use]");if(!t)return;
 var i=+(t.dataset.play||t.dataset.keep||t.dataset.use),x=CUR[i];if(!x)return;var X=window.SNSWX||{},u="https://www.youtube.com/watch?v="+x.id;
 if(t.dataset.play!=null){var pl=t.closest(".bd").querySelector(".pl");if(pl.innerHTML){pl.innerHTML="";t.textContent="▶ ฟัง";return}
  document.querySelectorAll("#bf .pl").forEach(function(p){p.innerHTML=""});document.querySelectorAll("#bf [data-play]").forEach(function(b){b.textContent="▶ ฟัง"});
  pl.innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/'+x.id+'?autoplay=1&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen style="width:100%;aspect-ratio:16/9;border:0;border-radius:10px;margin-top:6px"></iframe>';t.textContent="■ ปิด";return}
 var uid=X.ST&&X.ST.uid||"local",K="sns:beats:"+uid,L=[];try{L=JSON.parse(localStorage.getItem(K)||"[]")}catch(er){}
 var b={id:(Date.now().toString(36)+Math.random().toString(36).slice(2,6)),url:u,name:x.t.slice(0,80),lic:x.free?"ffp":"mp3",usd:0,t:Date.now()};
 if(t.dataset.keep!=null){if(!L.some(function(y){return y.url==u})){L.unshift(b);try{localStorage.setItem(K,JSON.stringify(L.slice(0,60)))}catch(er){}}t.textContent="✓ เก็บแล้ว";if(X.savedList)X.savedList();try{window.toast&&toast("เก็บบีตแล้ว ดูได้ที่ บีตที่เก็บไว้")}catch(er){}return}
 if(t.dataset.use!=null){var W=X.W;if(!W||!X.writer)return;var n=W.note||(X.newNote&&X.newNote({title:""}));if(!n)return;n.beatPick={name:b.name,url:u,buy:"",lic:b.lic,usd:0};if(!n.link)n.link=u;W.note=n;W.dirty=true;
  Promise.resolve(X.save&&X.save()).then(function(){X.writer("pad");try{window.toast&&toast("ใส่ลิงก์บีตในเพลงแล้ว โหลดไฟล์บีตมาใส่เพื่อเปิดวนตอนเขียน")}catch(er){}})}});
function hook(){var go=$("sw-bgo");if(!go||go.dataset.bf)return;go.dataset.bf=1;var host=$("bf");if(!host){host=document.createElement("div");host.id="bf";var res=$("sw-bres");if(res)res.parentNode.insertBefore(host,res)}
 var run=function(){var bud=document.querySelector("#sw-bud [aria-pressed=true]");render({artist:($("sw-ba")||{}).value||"",song:($("sw-bs")||{}).value||"",genre:($("sw-bg")||{}).value||"",budget:bud?bud.dataset.b:"both"})};
 go.addEventListener("click",function(){setTimeout(run,50)});if(($("sw-ba")||{}).value)run()}
window.SNSBeatFind={hook:hook,load:load,render:render};
})();
