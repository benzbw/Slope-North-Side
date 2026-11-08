# จำหน้าเดิม: สลับแอปแล้วกลับมา (มือถือโหลดหน้าใหม่) ให้อยู่แท็บเดิม เพลงเดิม ช่องที่กรอก ไอเดียที่ได้ และตำแหน่งเลื่อนเดิม
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
if 'sns:wsess' in s: print('session already'); sys.exit(0)
a = 'writer(t=="beat"||t=="pad"?t:"idea")}'
assert s.count(a) == 1, 'boot anchor'
NEW = r'''(async function(){var Ss=null,rs=false;try{Ss=JSON.parse(localStorage.getItem("sns:wsess")||"null")}catch(e){}
 if(!(t=="beat"||t=="pad")&&Ss&&now()-(Ss.t||0)<864e5*2){rs=true;t=Ss.tab||"idea";if(Ss.lastIdeas&&!W.lastIdeas)W.lastIdeas=Ss.lastIdeas;if(Ss.mood&&Ss.mood.length)W.mood=Ss.mood;
  if(t=="pad"&&Ss.note){try{var L=await Notes.list();W.note=L.filter(function(x){return x.id==Ss.note})[0]||null}catch(e){}}}
 var _w=writer;writer=function(tab){_w(tab);setTimeout(snsSave,80)};
 writer(t=="beat"||t=="pad"?t:"idea");
 if(rs&&Ss.y)[250,800,1600].forEach(function(d){setTimeout(function(){var r=$("sx");if(r&&r.scrollTop<20)r.scrollTop=Ss.y},d)})})();
 function snsSave(){try{var r=$("sx");localStorage.setItem("sns:wsess",JSON.stringify({tab:W.tab,note:W.tab=="pad"&&W.note?W.note.id:null,y:r?r.scrollTop:0,lastIdeas:W.lastIdeas||null,mood:W.mood||[],t:now()}))}catch(e){}}
 var snsT=0;function snsLater(){clearTimeout(snsT);snsT=setTimeout(snsSave,400)}
 document.addEventListener("scroll",snsLater,true);document.addEventListener("click",snsLater,true);
 document.addEventListener("input",function(e){var id=e.target&&e.target.id;if(/^sw-(art|song|story)$/.test(id)){var P=J("sns:wprefs",{}),k=id=="sw-art"?"art":id=="sw-song"?"song":"story";P[k]=e.target.value;JS("sns:wprefs",P)}snsLater()},true);
 document.addEventListener("change",function(e){var id=e.target&&e.target.id;if(id=="sw-g"||id=="sw-lang"){var P=J("sns:wprefs",{});P[id=="sw-g"?"g":"lang"]=e.target.value;JS("sns:wprefs",P)}},true);
 var snsHide=function(){snsSave();try{var P=J("sns:wprefs",{});P.mood=W.mood;JS("sns:wprefs",P)}catch(e){}if(W.note&&W.dirty)try{wSaveNow()}catch(e){}};
 document.addEventListener("visibilitychange",function(){if(document.visibilityState=="hidden")snsHide()});window.addEventListener("pagehide",snsHide);}'''
s = s.replace(a, NEW)
open(p, 'w', encoding='utf-8').write(s); print('session ok')
