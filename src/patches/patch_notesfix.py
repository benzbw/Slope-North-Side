# แก้สมุดเนื้อ: (1) ลบแล้วไม่ฟื้น (รอลบเสร็จ + จำรายการที่ลบ) (2) ไม่บันทึกเพลงว่าง + เก็บกวาดเพลงว่างเก่า
# (3) จำหน้า/เพลงที่เปิดไว้ในบัญชีด้วย (claude.ai อาจล้างความจำในเครื่องตอนโหลดใหม่) · ใช้: python3 patch_notesfix.py <write.html>
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
if 'snsEmpty(' in s: print('notesfix already'); sys.exit(0)
def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
# helpers before Notes
R('var Notes={\n', '''function snsEmpty(n){return!n||(!String(n.title||"").trim()&&!String(n.body||"").replace(/\\[[^\\]]*\\]|\\/\\/[^\\n]*/g,"").trim()&&!n.beat&&!n.beatPick&&!n.link&&!(n.takes&&n.takes.length)&&!n.brief&&!n.idea)}
function snsDelKey(){return"sns:notes:del:"+ST.uid}
var Notes={
''')
# list: drop tombstoned + clean up old empty notes (not the one open)
R('L.sort(function(a,b){return(b.updated||0)-(a.updated||0)});JS(nKey(),L);return L},',
  '''var DEL=J(snsDelKey(),[]),cur=W.note&&W.note.id,old=now()-6e5;L=L.filter(function(x){if(DEL.indexOf(x.id)>=0){if(ST.mode=="cloud"&&ST.db)ST.db.doc(nCol()+"/"+x.id).delete().catch(function(){});return false}
   if(x.id!=cur&&snsEmpty(x)&&(x.updated||0)<old){if(ST.mode=="cloud"&&ST.db)ST.db.doc(nCol()+"/"+x.id).delete().catch(function(){});return false}return true});
  L.sort(function(a,b){return(b.updated||0)-(a.updated||0)});JS(nKey(),L);return L},''')
# save: skip empty
R('save:async function(n){n.updated=now();', 'save:async function(n){if(snsEmpty(n)){JS(nKey(),J(nKey(),[]).filter(function(x){return x.id!=n.id}));return}n.updated=now();')
# del: tombstone
R('del:async function(n){JS(nKey(),J(nKey(),[]).filter(function(x){return x.id!=n.id}));',
  'del:async function(n){var DL=J(snsDelKey(),[]);if(DL.indexOf(n.id)<0){DL.push(n.id);JS(snsDelKey(),DL.slice(-300))}JS(nKey(),J(nKey(),[]).filter(function(x){return x.id!=n.id}));')
# delete button: wait for delete before reloading list
R('$("sw-dy").onclick=function(){m.remove();Notes.del(n).catch(function(){});W.note=null;W.dirty=false;wStop();padTab();toastS("ลบแล้ว")}',
  '$("sw-dy").onclick=async function(){m.remove();W.note=null;W.dirty=false;wStop();try{await Notes.del(n)}catch(e){}padTab();toastS("ลบแล้ว")}')
# session in account (cloud)
R('try{Ss=JSON.parse(localStorage.getItem("sns:wsess")||"null")}catch(e){}',
  'try{Ss=JSON.parse(localStorage.getItem("sns:wsess")||"null")}catch(e){}\n if(ST.mode=="cloud"&&ST.db){try{var qs=await ST.db.collection("data/users/"+ST.uid+"/account/wsess").get();qs.docs.forEach(function(d){if(d.id=="cur"){var cs=cp(d.data());if(cs&&cs.t&&(!Ss||cs.t>(Ss.t||0)))Ss=cs}})}catch(e){}}')
R('function snsSave(){try{var r=$("sx");localStorage.setItem("sns:wsess",JSON.stringify({tab:W.tab,note:W.tab=="pad"&&W.note?W.note.id:null,y:r?r.scrollTop:0,lastIdeas:W.lastIdeas||null,mood:W.mood||[],t:now()}))}catch(e){}}',
  'var snsCT=0,snsLast="";function snsSave(){try{var r=$("sx"),o={tab:W.tab,note:W.tab=="pad"&&W.note&&!snsEmpty(W.note)?W.note.id:null,y:r?r.scrollTop:0,lastIdeas:W.lastIdeas||null,mood:W.mood||[],t:now()};localStorage.setItem("sns:wsess",JSON.stringify(o));\n  var key=[o.tab,o.note,Math.round(o.y/200)].join("|");if(ST.mode=="cloud"&&ST.db&&key!=snsLast){snsLast=key;clearTimeout(snsCT);snsCT=setTimeout(function(){ST.db.doc("data/users/"+ST.uid+"/account/wsess/cur").set(cp(o)).catch(function(){})},1200)}}catch(e){}}')
open(p, 'w', encoding='utf-8').write(s); print('notesfix ok')
