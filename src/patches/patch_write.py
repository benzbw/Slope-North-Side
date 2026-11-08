import sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
def R(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: sys.exit('count %d %r'%(c,a[:80]))
    s=s.replace(a,b)
X=open('/tmp/w/xdata.js',encoding='utf-8').read()
# songPool: mood songs from every genre come right after the artist's own songs
R('''function songPool(inp){var gk=wGen(inp),ak=artKey(inp.artist),P=[];
 if(ak)ART[ak][1].forEach(function(t){P.push({artist:ak,title:t,own:1})});''','''function songPool(inp){var gk=wGen(inp),ak=artKey(inp.artist),P=[];
 if(ak)ART[ak][1].forEach(function(t){P.push({artist:ak,title:t,own:1})});
 if(window.SNSData&&inp.mood&&inp.mood.length)SNSData.moodSongs(inp.mood).forEach(function(x){if(!P.some(function(y){return y.title==x.title}))P.push({artist:x.artist,title:x.title,mood:x.mood,genre:x.genre})});''')
R('''function whyFor(x,gk){''','''function whyFor(x,gk){if(x.mood)return"เข้ากับอารมณ์ "+x.mood+" · "+x.genre+" — ฟังว่าเขาสื่ออารมณ์นี้ด้วยเสียง/คำ/ดนตรียังไง";''')
R('''var ref=pick(G.ref,Math.min(4,G.ref.length),rnd).map(function(x){return{artist:x[0],title:x[1],why:"ฟัง"+(rnd()<.5?"วิธีวางฮุค":"การเล่าเรื่องและซาวด์")+"ของแนว "+G.n}});''',
  '''var ref=pick(G.ref,Math.min(inp.mood.length?3:4,G.ref.length),rnd).map(function(x){return{artist:x[0],title:x[1],why:"ฟัง"+(rnd()<.5?"วิธีวางฮุค":"การเล่าเรื่องและซาวด์")+"ของแนว "+G.n}});
 if(window.SNSData&&inp.mood.length){var ms=SNSData.moodSongs(inp.mood,3).map(function(x){return{artist:x.artist,title:x.title,why:"เข้ากับอารมณ์ "+x.mood+" · "+x.genre+" (คนละแนวก็ได้ เอาวิธีสื่ออารมณ์มาใช้)"}});ref=ms.concat(ref)}''')
R('2) แนะนำเพลงที่มีอยู่จริง 6 เพลงให้ฟังเป็นแรงบันดาลใจ: 2 เพลงของศิลปินที่อิน (ถ้ามี) และ 4 เพลงแนวใกล้กัน บอกว่าฟังเพื่อเรียนรู้อะไร (ฮุค ฟลว์ ทิศทางทำนอง โครงเพลง)',
  '2) แนะนำเพลงที่มีอยู่จริง 6 เพลงให้ฟังเป็นแรงบันดาลใจ: 2 เพลงของศิลปินที่อิน (ถ้ามี), 2 เพลงที่ดนตรี/แนวคล้ายเพลงที่อิน และ 2 เพลงที่สื่อสารเรื่องเดียวกันหรือเข้ากับอารมณ์ตอนนี้ แนวไหนก็ได้ ไม่จำเป็นต้องเป็นฮิปฮอป (ป๊อป ร็อก อินดี้ R&B เพลงไทยก็ได้) ใน why บอกว่าคล้ายตรงไหน (ดนตรี/แนว/สื่อสาร/อารมณ์) และฟังเพื่อเรียนรู้อะไร (ฮุค ฟลว์ ทิศทางทำนอง โครงเพลง)')
# slang / hot words in the lyric notebook
R('<div class="sw-stat" id="sw-stt"></div></div>\'+','<div class="sw-stat" id="sw-stt"></div><div class="sw-box" id="sw-slang"></div></div>\'+')
# bug: ปุ่มค้นหาบีตส่ง event เข้ามาแทนคำค้น → (extra||[]).slice พัง
R('$("sw-bgo").onclick=beatSearch;','$("sw-bgo").onclick=function(){beatSearch()};')
R('function beatSearch(extra){','function beatSearch(extra){extra=Array.isArray(extra)?extra:(typeof extra=="string"&&extra?[extra]:[]);')
R('function padEditor(){var n=W.note;','function padEditor(){window.SNSW={W:W,can:function(){return!!ST.sample},ai:function(q){return aiJSON(q)}};setTimeout(slangUI,0);var n=W.note;')
SL0=r'''<script>/* คำฮิต & สแลง: เลือกให้เข้ากับคอนเซปต์เพลงที่กำลังเขียนเองอัตโนมัติ (ชื่อเพลง คอนเซปต์ อารมณ์ เนื้อ) + AI คิดเฉพาะเพลงนี้ */
var SLERA="now",SLSIG="",SLT0=0,SLAI={busy:0,last:0};
function slangMine(){try{return JSON.parse(localStorage.getItem("sns:slang:mine")||"[]")}catch(e){return[]}}
function slCtx(){var S=window.SNSW,n=S&&S.W&&S.W.note||{},ti=document.getElementById("sw-ti"),tx=document.getElementById("sw-tx");
 return{id:n.id||"x",title:(ti&&ti.value)||n.title||"",concept:(n.idea&&n.idea.concept)||"",moods:(S&&S.W&&S.W.mood)||[],lyrics:((tx&&tx.value)||n.body||"").replace(/\[[^\]]*\]/g," ").slice(-1500)}}
function slHash(t){var h=0;for(var i=0;i<t.length;i++)h=(h*31+t.charCodeAt(i))|0;return(h>>>0).toString(36)}
function slChips(L){return L.map(function(w){return'<button class="sw-chip" data-w="'+esc(w[0])+'" data-p="'+esc(w[2]||"")+'" data-x="'+esc(w[3]||"")+'" title="'+esc(w[1]||"")+'" style="height:auto;padding:6px 12px;text-align:left;line-height:1.25'+(w.fit?';border-color:var(--sx-red,#ff3347)':'')+'">'+esc(w[0])+(w[2]?' <span style="font-size:11.5px;opacity:.8;font-weight:400">['+esc(w[2])+']</span>':'')+(w[1]?'<small style="display:block;font-size:11px;opacity:.72;font-weight:400">'+esc(w[1])+'</small>':'')+'</button>'}).join("")}
function slBind(box){box.querySelectorAll("[data-w]").forEach(function(b){b.onclick=function(){var w=b.dataset.w,ex=b.dataset.x,m=document.getElementById("sw-slm");document.querySelectorAll("#sw-slang [data-w]").forEach(function(x){x.setAttribute("aria-pressed",x==b)});
  var pr=b.dataset.p,en=!/[฀-๿]/.test(w);m.innerHTML='<b style="color:var(--sx-fg);font-size:15px">'+esc(w)+'</b>'+(pr?' · อ่านว่า <b style="color:var(--sx-fg)">'+esc(pr)+'</b>':'')+' — '+esc(b.title||"คำของคุณ")+(ex?'<div style="margin-top:4px">ตัวอย่างในเพลงนี้: “'+esc(ex)+'”</div>':'')+'<div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap">'+(en&&window.speechSynthesis?'<button class="sw-ghost" id="sw-slsay" style="min-height:34px">🔊 ฟังเสียง</button>':'')+'<button class="sw-ghost" id="sw-slput" style="min-height:34px">+ ใส่คำในเนื้อ</button>'+(ex?'<button class="sw-ghost" id="sw-slputx" style="min-height:34px">+ ใส่ทั้งประโยค</button>':'')+'</div>';
  var sy=document.getElementById("sw-slsay");if(sy)sy.onclick=function(){try{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(w.replace(/\./g,""));u.lang="en-US";u.rate=.85;var v=speechSynthesis.getVoices().filter(function(x){return/^en(-|_)US/i.test(x.lang)})[0];if(v)u.voice=v;speechSynthesis.speak(u)}catch(x){}};
  var put=function(t,nl){var tx=document.getElementById("sw-tx");if(!tx)return;var a=tx.selectionStart||tx.value.length,e=tx.selectionEnd||a,pre=tx.value.slice(0,a),sp=nl?(pre&&!/\n$/.test(pre)?"\n":""):(pre&&!/\s$/.test(pre)?" ":"");tx.value=pre+sp+t+(nl?"\n":" ")+tx.value.slice(e);tx.focus();var c=a+sp.length+t.length+1;try{tx.setSelectionRange(c,c)}catch(x){}tx.dispatchEvent(new Event("input"));m.textContent="ใส่ “"+t+"” ในเนื้อแล้ว"};
  document.getElementById("sw-slput").onclick=function(){put(w)};var px=document.getElementById("sw-slputx");if(px)px.onclick=function(){put(ex,1)}}})}
function slAI(ctx,th,force){var el=document.getElementById("sw-slai"),S=window.SNSW;if(!el)return;
 if(!S||!S.can()){el.innerHTML='<p class="sw-note" style="margin:6px 0 0">AI คิดสแลงเฉพาะเพลงนี้ ใช้ได้ในลิงก์ claude.ai (ตอนนี้แอปเลือกจากคลังคำให้ตามคอนเซปต์แล้ว)</p>';return}
 var enough=(ctx.title+ctx.concept).trim().length>1||ctx.lyrics.trim().length>40;if(!enough){el.innerHTML="";return}
 var sig=slHash([ctx.title,ctx.concept,th.map(function(x){return x.t}).join(","),ctx.moods.join(",")].join("|")),key="sns:slang:ai:"+ctx.id+":"+sig,c=null;
 try{c=JSON.parse(localStorage.getItem(key)||"null")}catch(e){}
 var show=function(r){var L=function(a){return(a||[]).slice(0,8).map(function(x){var y=[x.w,x.m,x.p,x.ex];y.fit=1;return y})};
  el.innerHTML='<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:10px"><p class="sw-note" style="margin:0"><b style="color:var(--sx-fg)">AI คิดให้เพลงนี้</b>'+(r.why?' · '+esc(r.why):'')+'</p><button class="sw-ghost" id="sw-slaire" style="min-height:32px">↻ คิดใหม่</button></div><div class="sw-chips" style="margin-top:4px">'+slChips(L(r.th).concat(L(r.en)))+'</div>';
  slBind(el);document.getElementById("sw-slaire").onclick=function(){slAI(slCtx(),th,1)}};
 if(c&&!force){show(c);return}
 if(SLAI.busy)return;if(!force&&Date.now()-SLAI.last<45000){if(!el.innerHTML)el.innerHTML='<p class="sw-note" style="margin:6px 0 0">AI จะคิดสแลงให้เข้ากับเพลงนี้อีกสักครู่…</p>';clearTimeout(SLAI.t);SLAI.t=setTimeout(function(){slAI(slCtx(),SNSData.slangThemes(slCtx()))},45000-(Date.now()-SLAI.last));return}
 SLAI.busy=1;SLAI.last=Date.now();el.innerHTML='<p class="sw-note" style="margin:8px 0 0">AI กำลังคิดสแลงให้เข้ากับคอนเซปต์เพลงนี้…</p>';
 S.ai("คุณเป็นนักแต่งเพลงฮิปฮอป/R&B ไทยที่ตามภาษาวัยรุ่นทันสมัย ช่วยศิลปินเลือกคำแสลงให้เข้ากับเพลงที่เขากำลังเขียน\nชื่อเพลง: "+(ctx.title||"-")+"\nคอนเซปต์: "+(ctx.concept||"-")+"\nอารมณ์: "+(ctx.moods.join(", ")||"-")+"\nธีมที่แอปจับได้: "+(th.map(function(x){return x.n}).join(", ")||"-")+"\nเนื้อที่เขียนแล้ว (ท้ายสุด):\n"+(ctx.lyrics.slice(-900)||"-")+
  "\n\nงาน: เสนอคำแสลง/คำฮิตที่คนใช้จริงตอนนี้ และเข้ากับเรื่องของเพลงนี้ ไทย 6 คำ อังกฤษ (สายแร็ปเปอร์ฝรั่ง) 6 คำ ห้ามคำหยาบรุนแรงหรือเหยียด แต่ละคำให้ความหมายสั้น คำอ่านภาษาไทย (สำหรับคำอังกฤษ) และประโยคตัวอย่าง 1 บรรทัดที่เข้ากับเรื่องเพลงนี้ (แต่งใหม่ ห้ามยกเนื้อเพลงคนอื่น)\nตอบเป็น JSON อย่างเดียว: {\"why\":\"สรุปคอนเซปต์ที่จับได้ ไม่เกิน 12 คำ\",\"th\":[{\"w\":\"\",\"m\":\"\",\"ex\":\"\"}],\"en\":[{\"w\":\"\",\"m\":\"\",\"p\":\"\",\"ex\":\"\"}]}")
  .then(function(r){SLAI.busy=0;if(!r||!(r.th||r.en))throw{code:"parse"};try{localStorage.setItem(key,JSON.stringify(r))}catch(e){}show(r)})
  .catch(function(e){SLAI.busy=0;el.innerHTML='<p class="sw-note" style="margin:8px 0 0">'+esc(e&&e.code=="not_granted"?"ยังไม่ได้อนุญาตให้แอปถาม AI":e&&e.code=="rate_limited"?"ถาม AI ถี่ไป เดี๋ยวลองใหม่ให้เอง":"AI ไม่ตอบตอนนี้ ใช้คำที่แอปเลือกตามคอนเซปต์ด้านบนไปก่อน")+'</p>'})}
function slangUI(force){var box=document.getElementById("sw-slang");if(!box||!window.SNSData)return;var D=SNSData,M=slangMine(),ctx=slCtx(),th=D.slangThemes?D.slangThemes(ctx):[],
  pick=function(l,ex){return D.slangFor&&th.length?D.slangFor(l,SLERA,10,th,ex):D.slangPick(l,SLERA,10,ex)},
  T=pick("th",M.filter(function(w){return/[฀-๿]/.test(w[0])})),E=pick("en",M.filter(function(w){return!/[฀-๿]/.test(w[0])}));
 SLSIG=th.map(function(x){return x.t}).join(",");
 box.innerHTML='<div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><h3 style="font-size:15px;margin:0">คำฮิต & สแลง</h3><button class="sw-ghost" id="sw-slre">↻ สุ่มใหม่</button></div>'+
  '<p class="sw-note" style="margin:6px 0 0">'+(th.length?'เข้ากับคอนเซปต์: '+th.map(function(x){return'<b style="color:var(--sx-fg)">'+esc(x.n)+'</b>'}).join(" · ")+' <span style="opacity:.75">(แอปอ่านจากชื่อเพลง คอนเซปต์ อารมณ์ และเนื้อที่เขียน เปลี่ยนตามเองระหว่างเขียน)</span>':'ยังจับคอนเซปต์ไม่ได้ ใส่ชื่อเพลงหรือเขียนเนื้อสักท่อน แอปจะเลือกคำให้เข้ากับเพลงเอง')+'</p>'+
  '<div class="sw-chips" style="margin:8px 0 4px">'+[["now","ตอนนี้"],["old","ยุคก่อน"],["mix","ผสม"]].map(function(e){return'<button class="sw-chip" data-era="'+e[0]+'" aria-pressed="'+(SLERA==e[0])+'">'+e[1]+'</button>'}).join("")+'</div>'+
  '<p class="sw-note" style="margin:6px 0 2px">ไทย</p><div class="sw-chips">'+slChips(T)+'</div><p class="sw-note" style="margin:8px 0 2px">อังกฤษ / แร็ปเปอร์ฝรั่ง</p><div class="sw-chips">'+slChips(E)+'</div>'+
  '<div id="sw-slai"></div>'+
  '<div id="sw-slm" class="sw-note" style="min-height:18px;margin:8px 0 0">ขอบแดง = เข้ากับเพลงนี้ · คำอ่านอยู่ใน [ ] ความหมายอยู่ใต้คำ · แตะคำเพื่อฟังเสียงอ่าน แล้วกด "ใส่ในเนื้อ"</div>'+
  '<div style="display:flex;gap:6px;margin-top:6px"><input class="sw-in" id="sw-slin" maxlength="40" placeholder="เพิ่มคำของคุณ เช่น คำที่ฮิตในกลุ่ม" style="flex:1;min-width:0"><button class="sw-ghost" id="sw-sladd">+ เก็บ</button></div>';
 box.querySelectorAll("[data-era]").forEach(function(b){b.onclick=function(){SLERA=b.dataset.era;slangUI()}});
 document.getElementById("sw-slre").onclick=function(){slangUI()};slBind(box);
 document.getElementById("sw-sladd").onclick=function(){var v=document.getElementById("sw-slin").value.trim();if(!v)return;var L=slangMine();if(!L.some(function(w){return w[0]==v})){L.push([v,"คำของคุณ"]);try{localStorage.setItem("sns:slang:mine",JSON.stringify(L.slice(-60)))}catch(e){}}slangUI();document.getElementById("sw-slm").textContent="เก็บ “"+v+"” ไว้ในคลังคำแล้ว"};
 slAI(ctx,th,0);
 ["sw-tx","sw-ti"].forEach(function(id){var e=document.getElementById(id);if(e&&!e.dataset.sl){e.dataset.sl=1;e.addEventListener("input",function(){clearTimeout(SLT0);SLT0=setTimeout(function(){var c=slCtx(),t=SNSData.slangThemes?SNSData.slangThemes(c).map(function(x){return x.t}).join(","):"";if(t!=SLSIG)slangUI()},1500)})}})}
</script>
'''
SL=SL0[:SL0.index('/* คำฮิต')]+SL0[SL0.index('/* คำฮิต'):].replace('esc(','slEsc(').replace('var SLERA="now",','function slEsc(t){return String(t==null?"":t).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",\'"\':"&quot;"}[c]})}var SLERA="now",',1)
i=s.rindex('</body>')
s=s[:i]+'<script>'+X+'</script>\n'+SL+s[i:]
open(p,'w',encoding='utf-8').write(s);print('ok')
