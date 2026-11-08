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
R('function padEditor(){var n=W.note;','function padEditor(){setTimeout(slangUI,0);var n=W.note;')
SL0=r'''<script>/* คำฮิต & สแลง: ไทย 10 + อังกฤษ 10 สุ่มใหม่ได้ แตะเพื่อใส่ในเนื้อ */
var SLERA="now";
function slangMine(){try{return JSON.parse(localStorage.getItem("sns:slang:mine")||"[]")}catch(e){return[]}}
function slangUI(){var box=document.getElementById("sw-slang");if(!box||!window.SNSData)return;var M=slangMine(),th=SNSData.slangPick("th",SLERA,10,M.filter(function(w){return/[฀-๿]/.test(w[0])})),en=SNSData.slangPick("en",SLERA,10,M.filter(function(w){return!/[฀-๿]/.test(w[0])}));
 var col=function(L){return L.map(function(w){return'<button class="sw-chip" data-w="'+esc(w[0])+'" title="'+esc(w[1]||"")+'" style="height:auto;padding:6px 12px;text-align:left;line-height:1.25">'+esc(w[0])+(w[1]?'<small style="display:block;font-size:11px;opacity:.72;font-weight:400">'+esc(w[1])+'</small>':'')+'</button>'}).join("")};
 box.innerHTML='<div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><h3 style="font-size:15px;margin:0">คำฮิต & สแลง</h3><button class="sw-ghost" id="sw-slre">↻ สุ่มใหม่</button></div>'+
  '<div class="sw-chips" style="margin:8px 0 4px">'+[["now","ตอนนี้"],["old","ยุคก่อน"],["mix","ผสม"]].map(function(e){return'<button class="sw-chip" data-era="'+e[0]+'" aria-pressed="'+(SLERA==e[0])+'">'+e[1]+'</button>'}).join("")+'</div>'+
  '<p class="sw-note" style="margin:6px 0 2px">ไทย</p><div class="sw-chips">'+col(th)+'</div><p class="sw-note" style="margin:8px 0 2px">อังกฤษ / แร็ปเปอร์ฝรั่ง</p><div class="sw-chips">'+col(en)+'</div>'+
  '<div id="sw-slm" class="sw-note" style="min-height:18px;margin:8px 0 0">ความหมายภาษาไทยอยู่ใต้แต่ละคำ · แตะคำเพื่อดูคำแปลเต็ม แล้วกด "ใส่ในเนื้อ"</div>'+
  '<div style="display:flex;gap:6px;margin-top:6px"><input class="sw-in" id="sw-slin" maxlength="40" placeholder="เพิ่มคำของคุณ เช่น คำที่ฮิตในกลุ่ม" style="flex:1;min-width:0"><button class="sw-ghost" id="sw-sladd">+ เก็บ</button></div>';
 box.querySelectorAll("[data-era]").forEach(function(b){b.onclick=function(){SLERA=b.dataset.era;slangUI()}});
 document.getElementById("sw-slre").onclick=slangUI;
 box.querySelectorAll("[data-w]").forEach(function(b){b.onclick=function(){var w=b.dataset.w,m=document.getElementById("sw-slm");box.querySelectorAll("[data-w]").forEach(function(x){x.setAttribute("aria-pressed",x==b)});
  m.innerHTML='<b style="color:var(--sx-fg);font-size:15px">'+esc(w)+'</b> — '+esc(b.title||"คำของคุณ")+' <button class="sw-ghost" id="sw-slput" style="min-height:34px;margin-left:6px">+ ใส่ในเนื้อ</button>';
  document.getElementById("sw-slput").onclick=function(){var tx=document.getElementById("sw-tx");if(!tx)return;var a=tx.selectionStart||tx.value.length,e=tx.selectionEnd||a,pre=tx.value.slice(0,a),sp=pre&&!/\s$/.test(pre)?" ":"";tx.value=pre+sp+w+" "+tx.value.slice(e);tx.focus();var c=a+sp.length+w.length+1;try{tx.setSelectionRange(c,c)}catch(x){}tx.dispatchEvent(new Event("input"));m.textContent="ใส่ “"+w+"” ในเนื้อแล้ว"}}});
 document.getElementById("sw-sladd").onclick=function(){var v=document.getElementById("sw-slin").value.trim();if(!v)return;var L=slangMine();if(!L.some(function(w){return w[0]==v})){L.push([v,"คำของคุณ"]);try{localStorage.setItem("sns:slang:mine",JSON.stringify(L.slice(-60)))}catch(e){}}slangUI();document.getElementById("sw-slm").textContent="เก็บ “"+v+"” ไว้ในคลังคำแล้ว"}}
</script>
'''
SL=SL0[:SL0.index('/* คำฮิต')]+SL0[SL0.index('/* คำฮิต'):].replace('esc(','slEsc(').replace('var SLERA="now";','var SLERA="now";function slEsc(t){return String(t==null?"":t).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",\'"\':"&quot;"}[c]})}',1)
i=s.rindex('</body>')
s=s[:i]+'<script>'+X+'</script>\n'+SL+s[i:]
open(p,'w',encoding='utf-8').write(s);print('ok')
