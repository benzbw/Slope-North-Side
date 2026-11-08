import sys,re
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
def R(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: sys.exit('count %d %r'%(c,a[:80]))
    s=s.replace(a,b)
R('''<div style="display:flex;gap:8px;flex-wrap:wrap"><a class="sx-btn ghost" id="sx-wtop" target="_blank" rel="noopener" style="text-decoration:none">✎ แต่งเพลง & หาบีต</a><button class="sx-btn" id="sx-new">+ เพลงใหม่</button></div></div>'+''',
 '''<div style="display:flex;gap:8px;flex-wrap:wrap"><button class="sx-btn" id="sx-new">+ เพลงใหม่</button></div></div>'+
 '<section class="sx-sec"><div class="sx-sech"><h2>เครื่องมือ</h2><span>ใช้ได้ทันที ไม่ต้องเข้าโปรเจกต์</span></div><div class="sx-tools">'+
  '<a class="sx-tool" id="sx-wtop" target="_blank" rel="noopener"><i>✎</i><b>แต่งเพลง & หาบีต</b><small>แรงบันดาลใจตามอารมณ์ · บีต · สมุดเนื้อ · คำฮิต/สแลง</small></a>'+
  '<button class="sx-tool" type="button" onclick="window.SNSExplore&&SNSExplore.open()"><i>◎</i><b>ค้นหาแนวเพลง</b><small>เพลง/ศิลปินนี้แนวอะไร เล่าอะไร เพลงคล้าย · % คนฟัง</small></button>'+
  '<button class="sx-tool" type="button" onclick="window.SNSTrend&&SNSTrend.open()"><i>↗</i><b>เทรนด์ & เพลงมาแรง</b><small>ท็อป 20 ไทย/โลก · มาแรง · ฮิปฮอป · Gen Z · กดฟังได้</small></button>'+
  '<button class="sx-tool" type="button" id="sx-new2"><i>+</i><b>เริ่มเพลงใหม่</b><small>มิกซ์เสียง → เนื้อ → ซิงค์ → MV/ปก → ปล่อยเพลง</small></button>'+
 '</div></section>'+''')
R(''' '<section class="sx-sec"><div class="sx-sech"><h2>เทรนด์ & โอกาสแมส</h2>''',''' (0?'<section class="sx-sec"><div class="sx-sech"><h2>เทรนด์ & โอกาสแมส</h2>''')
R('''<button class="sx-btn" type="button" onclick="window.SNSTrend&&SNSTrend.open()">เปิดหน้าเทรนด์</button></section>'+''','''<button class="sx-btn" type="button" onclick="window.SNSTrend&&SNSTrend.open()">เปิดหน้าเทรนด์</button></section>':'')+''')
R(''''<section class="sx-sec" id="sx-write"></section>'+''','')
R('$("sx-new").onclick=newDialog;','$("sx-new").onclick=newDialog;if($("sx-new2"))$("sx-new2").onclick=newDialog;')
R('function writeCard(){var host=$("sx-write");if(!host)return;var url=writeUrl();','function writeCard(){var host=$("sx-write"),url=writeUrl(),wt0=$("sx-wtop");if(wt0){wt0.href=url;if(url=="write.html"){wt0.removeAttribute("target");wt0.removeAttribute("rel")}}if(!host)return;')
R('{k:"mix",n:"เสียง & แนว",d:"ทำก่อน: มิกซ์เสียงร้อง+บีต จูนเสียงนิดๆ หาคีย์ เทียบกับเพลงที่ชอบ แล้วดูว่าเพลงเป็นแนวอะไร",m:/^(สตูดิโอมิกซ์|แนวเพลง)/}','{k:"mix",n:"เสียง (มิกซ์)",d:"ทำก่อน: ใส่เสียงร้อง+บีตแยกไฟล์ มิกซ์ จูนเสียงนิดๆ หาคีย์ เทียบกับเพลงที่อยากให้เสียงออกมาแบบนั้น",m:/^สตูดิโอมิกซ์/}')
R('"ขั้น 1 › เสียง & แนว › กด \\"เพลงนี้แนวอะไร\\" ระบบฟังเพลงจริง','"หน้าแรก › เครื่องมือ › ค้นหาแนวเพลง: พิมพ์ชื่อเพลง/ศิลปิน หรือใส่ไฟล์เพลง ระบบฟังเพลงจริง')
R('และลิงก์ Spotify/YouTube/Apple Music"]','ลิงก์ Spotify/YouTube ไอเดียคอนเซปต์ และ % คนฟังแนวนี้ในไทย/ทั่วโลก"]')
R('["มิกซ์ & ดูแนวเพลง","ใส่เสียงร้อง+บีต ให้มิกซ์ จูนนิดๆ หาคีย์ เทียบกับเพลงที่ชอบ แล้วบอกว่าเพลงแนวอะไร ฟังแนวเดียวกันที่ไหน","ทุกเครื่อง"]','["มิกซ์เสียงก่อน","ขั้น 1 › เสียง: ใส่เสียงร้อง+บีตแยกไฟล์ ให้มิกซ์ จูนนิดๆ หาคีย์ เทียบกับเพลงที่ชอบ แล้วใช้เป็นเพลงของโปรเจกต์","ทุกเครื่อง"]')
R('มิกซ์อยู่ขั้น 1 › แท็บ \\"เสียง & แนว\\"','มิกซ์อยู่ขั้น 1 › แท็บ \\"เสียง (มิกซ์)\\"')
open(p,'w',encoding='utf-8').write(s);print('ok')
