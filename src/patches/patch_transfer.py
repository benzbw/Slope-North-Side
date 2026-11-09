# ย้ายเพลงไปมาได้ทั้งสองทาง (claude.ai ⇄ เว็บแอป): เมนู ⋯ "คัดลอกเพลงนี้ไปอีกที่" + ปุ่ม "วางเพลงที่คัดลอก" ในรายการเพลง
# ข้อมูลที่ย้าย: ชื่อ เนื้อ ลิงก์บีต BPM บรีฟเพลง บีตที่เลือก · ใช้: python3 patch_transfer.py <write.html>
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
if 'snsSongCode(' in s: print('transfer already'); sys.exit(0)
def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
R('var Notes={\n', r'''function snsSongCode(n){var o={t:n.title||"",b:n.body||"",l:n.link||"",bpm:n.bpm||0,br:n.brief||null,bp:n.beatPick||null,g:n.genre||""};try{return"SNSSONG:"+btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"")}catch(e){return""}}
function snsSongParse(t){var m=/SNSSONG:([\w-]+)|#import=([\w-]+)/.exec(String(t||""));if(!m)return null;try{return JSON.parse(decodeURIComponent(escape(atob((m[1]||m[2]).replace(/-/g,"+").replace(/_/g,"/")))))}catch(e){return null}}
async function snsSongImport(o){var L0=[];try{L0=await Notes.list()}catch(e){}var nn=L0.filter(function(x){return o.t&&x.title==o.t})[0]||newNote({title:o.t||""});
 if(o.b)nn.body=o.b;if(o.l)nn.link=o.l;if(o.bpm)nn.bpm=o.bpm;if(o.br)nn.brief=o.br;if(o.bp)nn.beatPick=o.bp;if(o.g)nn.genre=o.g;W.note=nn;W.dirty=true;try{await wSaveNow()}catch(e){}return nn}
var Notes={
''')
R('menuAt($("sw-more"),[["คัดลอกเนื้อทั้งหมด",function(){copyTxt(tx.value)}],',
  'menuAt($("sw-more"),[["คัดลอกเนื้อทั้งหมด",function(){copyTxt(tx.value)}],["ย้ายเพลงนี้ไปอีกที่ (claude.ai ⇄ เว็บแอป)",function(){n.body=tx.value;var c=snsSongCode(n),m=modal(\'<button class="sx-x" aria-label="ปิด">×</button><h3>ย้ายเพลงนี้ไปอีกที่</h3><p class="sx-note">คัดลอกรหัสนี้ แล้วไปเปิดหน้าแต่งเพลงอีกที่ (claude.ai หรือเว็บแอป) › ③ สมุดเนื้อเพลง › กด \\u201cวางเพลงที่คัดลอก\\u201d · ได้ชื่อ เนื้อ บีต และบรีฟเพลงไปครบ</p><textarea class="sx-in" readonly id="sw-tc" style="min-height:90px;font-size:12px"></textarea><div class="sx-row2" style="margin-top:12px"><button class="sx-btn" id="sw-tcc">คัดลอกรหัส</button><a class="sx-btn ghost" id="sw-tco" target="_blank" rel="noopener">เปิดในเว็บแอป ↗</a></div>\');$("sw-tc").value=c;$("sw-tco").href="https://benzbw.github.io/Slope-North-Side/write.html#import="+c.slice(8);if(!/claude\\.ai|claudeusercontent/.test(location.hostname))$("sw-tco").remove();$("sw-tcc").onclick=function(){copyTxt(c)}}],')
R('$("sw-nn").onclick=function(){W.note=newNote();W.dirty=true;wSaveNow();padEditor()};',
  '''$("sw-nn").onclick=function(){W.note=newNote();W.dirty=true;wSaveNow();padEditor()};
 (function(){var bx=$("sw-nn").parentNode,pb=document.createElement("button");pb.className="sw-ghost";pb.id="sw-np";pb.textContent="วางเพลงที่คัดลอก";pb.style.marginLeft="6px";$("sw-nn").insertAdjacentElement("afterend",pb);
  pb.onclick=function(){var m=modal('<button class="sx-x" aria-label="ปิด">×</button><h3>วางเพลงที่คัดลอก</h3><p class="sx-note">วางรหัสที่ขึ้นต้นด้วย SNSSONG: จากเมนู ⋯ › ย้ายเพลงนี้ไปอีกที่</p><textarea class="sx-in" id="sw-ti2" placeholder="SNSSONG:..." style="min-height:90px"></textarea><button class="sx-btn" id="sw-tig" style="margin-top:12px;width:100%">เพิ่มเพลงนี้</button>');
   $("sw-tig").onclick=async function(){var o=snsSongParse($("sw-ti2").value);if(!o){toastS("รหัสไม่ถูกต้อง ลองคัดลอกใหม่");return}m.remove();await snsSongImport(o);padEditor();toastS("เพิ่มเพลงแล้ว")}}})();''')
# #import in web build should also carry brief/beatPick when present
s = s.replace('if(o.b)nn.body=o.b;if(o.l)nn.link=o.l;if(o.bpm)nn.bpm=o.bpm;W.note=nn;', 'if(o.b)nn.body=o.b;if(o.l)nn.link=o.l;if(o.bpm)nn.bpm=o.bpm;if(o.br)nn.brief=o.br;if(o.bp)nn.beatPick=o.bp;W.note=nn;')
open(p, 'w', encoding='utf-8').write(s); print('transfer ok')
