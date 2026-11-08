# เพิ่มอารมณ์ (15 แบบ) + ช่องพิมพ์อารมณ์เอง ให้หน้าแต่งเพลง · ใช้: python3 patch_moods.py <write.html>
import json, os, sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
if 'sw-mown' in s: print('already'); sys.exit(0)
NEW = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moods.json'), encoding='utf-8'))
J = lambda o: json.dumps(o, ensure_ascii=False)
def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
R('"สู้/ฮึกเหิม","ชิล","หลอน"];', '"สู้/ฮึกเหิม","ชิล","หลอน",' + ','.join(J(m[0]) for m in NEW) + '];'
  '(function(){try{(JSON.parse(localStorage.getItem("sns:moods:mine")||"[]")||[]).forEach(function(m){if(MOODS.indexOf(m)<0)MOODS.push(m)})}catch(e){}})();')
R('var MOODGEN={', 'var MOODGEN={' + ''.join(J(m[0]) + ':' + J(m[1]) + ',' for m in NEW))
R('var HOOKS={', 'var HOOKS={' + ''.join(J(m[0]) + ':' + J(m[4]) + ',' for m in NEW))
i = s.index('var SEED={') + len('var SEED={')
s = s[:i] + ''.join(J(m[0]) + ':' + J(m[3]) + ',' for m in NEW) + s[i:]
# อารมณ์ที่พิมพ์เอง: หาอารมณ์ใกล้เคียงในคลังไว้คิดไอเดียแบบไม่ใช้เน็ต (AI ใช้คำที่พิมพ์ตรงๆ)
R('function offlineIdeas(inp,seed){', '''function moodKey(m){if(SEED[m])return m;var t=String(m||""),K=[[/เศร้า|ร้องไห้|น้ำตา|sad/i,"เศร้า"],[/เลิก|ทิ้ง|อกหัก|เท/i,"อกหัก"],[/โกรธ|เดือด|แค้น/i,"แค้น/ดิส"],[/รัก|หวาน|ชอบ|love/i,"รัก/หวาน"],[/เงิน|รวย|ธุรกิจ|งาน|business/i,"ธุรกิจ/หาเงิน"],[/สู้|ฝัน|ไต่|ขยัน/i,"สู้/ฮึกเหิม"],[/เหงา|คนเดียว/i,"เหงา"],[/ชิล|สบาย|โล่ง|ว่าง/i,"อิสระ/ปล่อยวาง"],[/ปาร์ตี้|มันส์|เต้น|ฉลอง/i,"ภูมิใจ/ฉลอง"],[/เพื่อน|แก๊ง/i,"เพื่อน/แก๊ง"],[/บ้าน|พ่อ|แม่|ครอบครัว/i,"ครอบครัว"],[/กลัว|หลอน|ผี/i,"หลอน"],[/ขำ|ตลก|กวน/i,"ตลก/กวน"]];
 for(var i=0;i<K.length;i++)if(K[i][0].test(t))return K[i][1];return"สู้/ฮึกเหิม"}
function offlineIdeas(inp,seed){''')
R('pick(SEED[m],1,rnd)[0]', 'pick(SEED[moodKey(m)],1,rnd)[0]')
R('hk=pick(HOOKS[m],1,rnd)[0]', 'hk=pick(HOOKS[moodKey(m)]||HOOKS["สู้/ฮึกเหิม"],1,rnd)[0]')
R('return MOODGEN[inp.mood[0]]||"rnb"}', 'return MOODGEN[moodKey(inp.mood[0])]||"rnb"}')
# ช่องพิมพ์อารมณ์เอง ใต้ชิป
R('''+m+'</button>'}).join("")+'</div>'+''', '''+m+'</button>'}).join("")+'</div><div style="display:flex;gap:6px;margin-top:8px"><input class="sw-in" id="sw-mown" maxlength="24" placeholder="อารมณ์อื่น พิมพ์เอง เช่น โล่งใจ, หมดไฟ, อยากแก้แค้น" style="flex:1;min-width:0"><button class="sw-ghost" id="sw-madd" type="button">+ เพิ่ม</button></div>'+''')
R('''$("sw-moods").querySelectorAll("button").forEach(function(b){b.onclick=function(){var m=b.textContent,i=W.mood.indexOf(m);if(i>=0)W.mood.splice(i,1);else W.mood.push(m);b.setAttribute("aria-pressed",i<0)}});''',
  '''var mBind=function(b){b.onclick=function(){var m=b.textContent,i=W.mood.indexOf(m);if(i>=0)W.mood.splice(i,1);else W.mood.push(m);b.setAttribute("aria-pressed",i<0)}};$("sw-moods").querySelectorAll("button").forEach(mBind);
 var mAdd=function(){var e=$("sw-mown"),v=e.value.trim().replace(/[<>"]/g,"");if(!v)return;e.value="";if(MOODS.indexOf(v)<0){MOODS.push(v);try{var L=JSON.parse(localStorage.getItem("sns:moods:mine")||"[]");L.push(v);localStorage.setItem("sns:moods:mine",JSON.stringify(L.slice(-20)))}catch(x){}var b=document.createElement("button");b.className="sw-chip";b.textContent=v;$("sw-moods").appendChild(b);mBind(b)}
  if(W.mood.indexOf(v)<0)W.mood.push(v);[].forEach.call($("sw-moods").querySelectorAll("button"),function(b){if(b.textContent==v)b.setAttribute("aria-pressed","true")})};
 $("sw-madd").onclick=mAdd;$("sw-mown").onkeydown=function(e){if(e.key=="Enter"){e.preventDefault();mAdd()}};''')
open(p, 'w', encoding='utf-8').write(s); print('ok', s.count('moodKey('))
