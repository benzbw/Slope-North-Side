# เปิดบีต YouTube ในเครื่องเล่นของสมุดเนื้อ (ไม่ต้องออกไปแอป YouTube) + แก้สีหน้าต่างบรีฟเพลง/โมดัล · ใช้: python3 patch_ytplay.py <write.html>
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
OLD = 'function snsYT(' in s
def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
HELP = r'''<style>
.sx-modal label{display:block}
.sx-modal .sw-lab{display:block;font:600 12px var(--sx-lab,system-ui);letter-spacing:.04em;color:var(--sx-mut,#a9989e);margin:12px 0 6px}
.sx-modal .sx-in,.sx-modal .sw-in{display:block;width:100%;box-sizing:border-box;min-height:46px;padding:10px 13px;border-radius:12px;border:1px solid var(--sx-line2,rgba(255,232,238,.16));background:rgba(0,0,0,.35);color:var(--sx-fg,#f6eff1);font:15px/1.5 var(--sx-body,system-ui);outline:none;-webkit-text-fill-color:var(--sx-fg,#f6eff1)}
.sx-modal textarea.sx-in{min-height:110px;resize:vertical}
.sx-modal .sx-in::placeholder,.sx-modal .sw-in::placeholder{color:var(--sx-dim,#6f6168);-webkit-text-fill-color:var(--sx-dim,#6f6168)}
.sx-modal .sx-in:focus,.sx-modal .sw-in:focus{border-color:var(--sx-hot,#ff3347)}
.sx-modal select.sw-in option{background:#120d12;color:#f6eff1}
</style><script>/* บีตจาก YouTube เล่นในแอป: ทำตัวให้เหมือน <audio> เพื่อให้ปุ่มเดิมทั้งหมดใช้ได้ */
function snsYtId(u){var m=/(?:youtu\.be\/|[?&]v=|embed\/|shorts\/)([\w-]{11})/.exec(u||"");return m?m[1]:null}
var SNS_WEB="https://benzbw.github.io/Slope-North-Side/write.html";
function snsPack(o){try{return btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"")}catch(e){return""}}
function snsYT(id,n){var A={paused:true,_t:0,_r:1,duration:0,loop:true,src:"",el:null};
 if(/claude\.ai|claudeusercontent/.test(location.hostname)){var d=document.createElement("div"),u="https://www.youtube.com/watch?v="+id,tx=document.getElementById("sw-tx"),ti=document.getElementById("sw-ti");
  var pk=snsPack({t:(ti&&ti.value)||n&&n.title||"",b:(tx&&tx.value)||n&&n.body||"",l:(n&&n.link)||u,bpm:n&&n.bpm||0});
  d.style.cssText="border:1px solid var(--sx-line2);border-radius:12px;padding:12px;margin:0 0 10px;background:rgba(255,51,71,.06)";
  d.innerHTML='<b style="display:block;font-size:14px">claude.ai ไม่ให้เล่นคลิป YouTube ในหน้า</b><p class="sw-note" style="margin:4px 0 8px">เปิดเพลงนี้ในเว็บแอป (ลิงก์ GitHub) จะได้ชื่อเพลง เนื้อ และบีตเดิมไปด้วย แล้วกดเล่นบีตในสมุดได้เลย หรือฟังใน YouTube แล้วกลับมาเขียน</p><div class="sw-acts" style="margin-top:0"><a class="sx-btn" target="_blank" rel="noopener" href="'+SNS_WEB+'#import='+pk+'">เปิดเพลงนี้ในเว็บแอป ↗</a><a class="sw-ghost" target="_blank" rel="noopener" href="'+u+'">▶ ฟังใน YouTube</a></div>';
  A.el=d;A.blocked=true;A.play=function(){window.open(SNS_WEB+"#import="+pk,"_blank");return Promise.resolve()};A.pause=function(){};A.kill=function(){};
  Object.defineProperty(A,"currentTime",{get:function(){return 0},set:function(){}});return A}
 var fr=document.createElement("iframe");
 fr.src="https://www.youtube-nocookie.com/embed/"+id+"?enablejsapi=1&playsinline=1&rel=0&modestbranding=1&origin="+encodeURIComponent(location.origin);
 fr.allow="autoplay; encrypted-media";fr.setAttribute("allowfullscreen","");fr.title="บีตจาก YouTube";fr.style.cssText="width:100%;aspect-ratio:16/9;border:0;border-radius:10px;margin:0 0 10px;display:block;background:#000";A.el=fr;
 var send=function(o){try{fr.contentWindow.postMessage(JSON.stringify(o),"*")}catch(e){}},cmd=function(f,a){send({event:"command",func:f,args:a||[]})};
 var listen=function(){send({event:"listening",id:1,channel:"widget"})};fr.addEventListener("load",function(){listen();setTimeout(listen,600);setTimeout(listen,1800)});
 var state=function(st){if(st==1&&A.paused){A.paused=false;if(A.onplay)A.onplay()}else if((st==2||st==0)&&!A.paused){A.paused=true;if(A.onpause)A.onpause()}if(st==0&&A.loop){cmd("seekTo",[0,true]);cmd("playVideo")}};
 var on=function(e){if(e.source!==fr.contentWindow)return;var d;try{d=typeof e.data=="string"?JSON.parse(e.data):e.data}catch(x){return}if(!d)return;
  if(d.event=="infoDelivery"&&d.info){var f=d.info;if(f.duration){var first=!A.duration;A.duration=f.duration;if(first&&A.onloadedmetadata)A.onloadedmetadata()}if(f.currentTime!=null){A._t=f.currentTime;if(A.ontimeupdate)A.ontimeupdate()}if(f.playerState!=null)state(f.playerState)}
  else if(d.event=="onStateChange")state(d.info);else if(d.event=="onReady")listen()};
 window.addEventListener("message",on);
 Object.defineProperty(A,"currentTime",{get:function(){return A._t},set:function(v){A._t=v;cmd("seekTo",[v,true])}});
 Object.defineProperty(A,"playbackRate",{get:function(){return A._r},set:function(v){A._r=v;cmd("setPlaybackRate",[v])}});
 A.play=function(){cmd("playVideo");return Promise.resolve()};A.pause=function(){cmd("pauseVideo")};A.kill=function(){window.removeEventListener("message",on)};return A}
</script>
'''
if OLD:
    a = s.index('<style>\n.sx-modal label{display:block}'); b = s.index('</script>', s.index('function snsYT(')) + 10
    s = s[:a] + HELP + s[b:]
    s = s.replace('A=W.audio=W.ytA=snsYT(YID);', 'A=W.audio=W.ytA=snsYT(YID,n);')
    s = s.replace('$("sw-bh").textContent=YID?"เล่นบีตจาก YouTube ในแอป · ปุ่มวน/A-B/−5 วิใช้ได้ · ถ้าภาพไม่ขึ้นให้กดเปิด ↗ หรือใส่ไฟล์บีต":', '$("sw-bh").textContent=YID?(A.blocked?"หรือโหลดไฟล์บีตที่โปรดิวเซอร์แจก แล้วกด ♪ ใส่ไฟล์บีต เพื่อเปิดวนในหน้านี้":"เล่นบีตจาก YouTube ในแอป · ปุ่มวน/A-B/−5 วิใช้ได้ · ถ้าภาพไม่ขึ้นให้กดเปิด ↗ หรือใส่ไฟล์บีต"):')
    open(p, 'w', encoding='utf-8').write(s); print('ytplay updated'); sys.exit(0)
i = s.index('<script>(function(){\n"use strict";')
s = s[:i] + HELP + s[i:]
R('if(!src&&n.beat.url)src=n.beat.url}',
  'if(!src&&n.beat.url)src=n.beat.url}\n if(W.ytA){try{W.ytA.kill()}catch(e){}W.ytA=null}var YID=!src&&snsYtId(n.link||(n.beatPick&&n.beatPick.url)||"");if(YID){A=W.audio=W.ytA=snsYT(YID,n);src="yt"}')
R('$("sw-bn").textContent=n.beat?n.beat.name:"ยังไม่มีบีต";',
  'if(YID)pl.insertBefore(A.el,pl.firstChild);\n $("sw-bn").textContent=n.beat?n.beat.name:YID?((n.beatPick&&n.beatPick.name)||"บีตจาก YouTube"):"ยังไม่มีบีต";')
R('$("sw-bh").textContent=src?"":',
  '$("sw-bh").textContent=YID?(A.blocked?"หรือโหลดไฟล์บีตที่โปรดิวเซอร์แจก แล้วกด ♪ ใส่ไฟล์บีต เพื่อเปิดวนในหน้านี้":"เล่นบีตจาก YouTube ในแอป · ปุ่มวน/A-B/−5 วิใช้ได้ · ถ้าภาพไม่ขึ้นให้กดเปิด ↗ หรือใส่ไฟล์บีต"):src?"":')
R('if(src)A.src=src;A.loop=true;', 'if(src&&!YID)A.src=src;A.loop=true;')
R('bl.onchange=function(){n.link=bl.value.trim();upd();W.dirty=true;wSaveNow()};',
  'bl.onchange=function(){var was=snsYtId(n.link||"");n.link=bl.value.trim();upd();W.dirty=true;wSaveNow();if(!n.beat&&snsYtId(n.link)!=was)player()};')
open(p, 'w', encoding='utf-8').write(s); print('ytplay ok')
