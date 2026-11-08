import sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
def R(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: sys.exit('count %d %r'%(c,a[:80]))
    s=s.replace(a,b)
# 1) cover: photo templates
R('<div class="chips" id="cv-t"><button data-t="studio">','<div class="chips" id="cv-t"><button data-t="ph_cine">รูปคุณ · ซีเนม่า<small>หน้า/ชุดไม่เพี้ยน</small></button><button data-t="ph_frame">รูปคุณ · กรอบ<small>ไม่ครอปรูป</small></button><button data-t="ph_poster">รูปคุณ · โปสเตอร์<small>ชื่อยักษ์</small></button><button data-t="ph_mag">รูปคุณ · นิตยสาร<small>ขอบกระดาษ</small></button><button data-t="studio">')
R('var CTIP={studio:','var CTIP={ph_cine:"ใช้รูปที่คุณถ่ายจริง ปรับแค่แสงสีแบบหนัง ใส่แถบดำและเกรน หน้าตา ชุด ทรงผม ไม่ถูกวาดใหม่",ph_frame:"วางรูปเต็มทั้งรูปไม่ครอป บนพื้นหลังที่เบลอจากรูปเดียวกัน เหมาะกับรูปแนวตั้ง",ph_poster:"รูปเต็มจอ ไล่สีธีมด้านล่าง ชื่อเพลงตัวใหญ่แบบโปสเตอร์",ph_mag:"ขอบกระดาษแบบปกนิตยสาร ชื่อเพลงตัวเอียง",studio:')
R('function drawCover(c,S){if(drawCoverPro(c,S))return;drawCover0(c,S)}','''/* ปกจากรูปถ่ายของผู้ใช้: ไม่วาดคนใหม่ ใช้พิกเซลจริง ปรับแค่สี/กรอบ/ตัวหนังสือ จึงไม่เพี้ยน */
function drawCoverPhoto(c,S){var tp=CV.tpl;if(!/^ph_/.test(tp))return false;var x=c.getContext("2d"),im=CV.photo,T1=String(CV.title||" "),A1=String(CV.artist||" "),hot=(typeof TH!="undefined"&&TH.hot)||"#ff3347";
 x.setTransform(1,0,0,1,0,0);x.globalAlpha=1;x.globalCompositeOperation="source-over";x.filter="none";x.shadowBlur=0;x.textBaseline="alphabetic";x.fillStyle="#060406";x.fillRect(0,0,S,S);
 var TF="Anton,'Noto Sans Thai',sans-serif",MF="Montserrat,'Noto Sans Thai',sans-serif";
 function fit(t,maxW,base,wt,fam){var z=base;x.font=wt+" "+z+"px "+fam;while(z>S*.03&&x.measureText(t).width>maxW){z*=.92;x.font=wt+" "+z+"px "+fam}return z}
 function sp(t,X,Y,g,al){var L=Array.from(t),W=0;L.forEach(function(ch){W+=x.measureText(ch).width+g});W-=g;var cx=al=="center"?X-W/2:al=="right"?X-W:X;x.textAlign="left";L.forEach(function(ch){x.fillText(ch,cx,Y);cx+=x.measureText(ch).width+g})}
 if(!im){try{x.drawImage(cvSource(Math.min(S,1200)),0,0,S,S)}catch(e){}x.fillStyle="rgba(0,0,0,.6)";x.fillRect(0,0,S,S);x.fillStyle="#fff";x.textAlign="center";x.font="700 "+Math.round(S*.045)+"px 'Noto Sans Thai',sans-serif";x.fillText("แตะ “ใส่รูปของคุณ” ด้านล่าง",S/2,S*.49);x.font="400 "+Math.round(S*.03)+"px 'Noto Sans Thai',sans-serif";x.fillText("แบบนี้ใช้รูปจริง หน้า ชุด ทรงผม ไม่เพี้ยน",S/2,S*.55);return true}
 var w=im.naturalWidth||im.width,h=im.naturalHeight||im.height;
 function cover(X,Y,W,H){var r=Math.max(W/w,H/h);x.save();x.beginPath();x.rect(X,Y,W,H);x.clip();x.drawImage(im,X+(W-w*r)/2,Y+(H-h*r)/2,w*r,h*r);x.restore()}
 function grain(a){try{if(typeof noiseTile!="undefined"&&noiseTile){x.save();x.globalAlpha=a;x.fillStyle=x.createPattern(noiseTile,"repeat");x.fillRect(0,0,S,S);x.restore()}}catch(e){}}
 function vig(a){var g=x.createRadialGradient(S/2,S*.45,S*.25,S/2,S/2,S*.75);g.addColorStop(0,"rgba(0,0,0,0)");g.addColorStop(1,"rgba(0,0,0,"+a+")");x.fillStyle=g;x.fillRect(0,0,S,S)}
 if(tp=="ph_cine"){x.filter="contrast(1.08) saturate(1.05)";cover(0,0,S,S);x.filter="none";
  x.globalCompositeOperation="soft-light";x.fillStyle="rgba(10,70,95,.42)";x.fillRect(0,0,S,S);x.globalCompositeOperation="overlay";x.fillStyle="rgba(255,150,80,.07)";x.fillRect(0,0,S,S);x.globalCompositeOperation="source-over";
  vig(.55);grain(.07);x.fillStyle="#000";x.fillRect(0,0,S,S*.085);x.fillRect(0,S*.915,S,S*.085);
  var g2=x.createLinearGradient(0,S*.55,0,S*.915);g2.addColorStop(0,"rgba(0,0,0,0)");g2.addColorStop(1,"rgba(0,0,0,.65)");x.fillStyle=g2;x.fillRect(0,S*.55,S,S*.365);
  x.fillStyle="rgba(255,255,255,.82)";x.font="500 "+Math.round(S*.024)+"px "+MF;sp(A1.toUpperCase(),S*.07,S*.775,S*.008,"left");
  x.fillStyle="#fff";fit(T1.toUpperCase(),S*.86,S*.12,"400",TF);x.textAlign="left";x.fillText(T1.toUpperCase(),S*.065,S*.885);
  x.fillStyle=hot;x.fillRect(S*.07,S*.795,S*.06,S*.006);
  if(CV.logo){x.fillStyle="rgba(255,255,255,.7)";x.font="600 "+Math.round(S*.016)+"px "+MF;sp("SLOPE NORTH SIDE",S*.93,S*.055,S*.006,"right")}}
 else if(tp=="ph_frame"){x.filter="blur("+Math.round(S*.035)+"px) brightness(.45) saturate(1.25)";cover(-S*.08,-S*.08,S*1.16,S*1.16);x.filter="none";vig(.5);grain(.05);
  var bx=S*.1,by=S*.08,bw=S*.8,bh=S*.66,r=Math.min(bw/w,bh/h),dw=w*r,dh=h*r,dx=bx+(bw-dw)/2,dy=by+(bh-dh)/2;
  x.save();x.shadowColor="rgba(0,0,0,.6)";x.shadowBlur=S*.04;x.shadowOffsetY=S*.012;x.fillStyle="#000";x.fillRect(dx,dy,dw,dh);x.restore();x.drawImage(im,dx,dy,dw,dh);
  x.strokeStyle="rgba(255,255,255,.85)";x.lineWidth=Math.max(2,S*.004);x.strokeRect(dx,dy,dw,dh);
  x.fillStyle="#fff";fit(T1.toUpperCase(),S*.84,S*.095,"400",TF);x.textAlign="center";x.fillText(T1.toUpperCase(),S/2,S*.86);
  x.fillStyle="rgba(255,255,255,.75)";x.font="500 "+Math.round(S*.024)+"px "+MF;sp(A1.toUpperCase(),S/2,S*.915,S*.01,"center");
  if(CV.logo){x.fillStyle=hot;x.font="600 "+Math.round(S*.015)+"px "+MF;sp("SLOPE NORTH SIDE",S/2,S*.955,S*.008,"center")}}
 else if(tp=="ph_poster"){cover(0,0,S,S);var g3=x.createLinearGradient(0,S*.4,0,S);g3.addColorStop(0,"rgba(0,0,0,0)");g3.addColorStop(.55,"rgba(0,0,0,.55)");g3.addColorStop(1,"rgba(0,0,0,.92)");x.fillStyle=g3;x.fillRect(0,S*.4,S,S*.6);
  x.globalCompositeOperation="soft-light";var g4=x.createLinearGradient(0,S*.5,0,S);g4.addColorStop(0,"rgba(0,0,0,0)");g4.addColorStop(1,hot);x.fillStyle=g4;x.globalAlpha=.6;x.fillRect(0,S*.5,S,S*.5);x.globalAlpha=1;x.globalCompositeOperation="source-over";grain(.06);
  x.fillStyle="#fff";var z=fit(T1.toUpperCase(),S*.92,S*.26,"400",TF);x.textAlign="center";x.fillText(T1.toUpperCase(),S/2,S*.955);
  x.fillStyle="rgba(255,255,255,.9)";x.font="600 "+Math.round(S*.026)+"px "+MF;sp(A1.toUpperCase(),S/2,S*.955-z*.95,S*.012,"center");
  if(CV.logo){x.fillStyle="rgba(255,255,255,.8)";x.font="600 "+Math.round(S*.016)+"px "+MF;sp("SLOPE NORTH SIDE",S*.05,S*.06,S*.006,"left")}}
 else{x.fillStyle="#efe9e1";x.fillRect(0,0,S,S);cover(S*.06,S*.2,S*.88,S*.66);x.strokeStyle="#111";x.lineWidth=Math.max(1,S*.002);x.strokeRect(S*.06,S*.2,S*.88,S*.66);
  x.fillStyle="#111";var z2=fit(T1,S*.88,S*.13,"italic 700","'Playfair Display','Noto Sans Thai',serif");x.textAlign="left";x.fillText(T1,S*.055,S*.17);
  x.font="500 "+Math.round(S*.022)+"px "+MF;sp(A1.toUpperCase(),S*.06,S*.925,S*.008,"left");x.fillStyle=hot;x.fillRect(S*.06,S*.94,S*.08,S*.006);
  x.fillStyle="#111";x.font="600 "+Math.round(S*.016)+"px "+MF;sp((CV.logo?"SLOPE NORTH SIDE · ":"")+new Date().getFullYear(),S*.94,S*.925,S*.006,"right");grain(.04)}
 return true}
function drawCover(c,S){if(drawCoverPhoto(c,S))return;if(drawCoverPro(c,S))return;drawCover0(c,S)}''')
R('$("cv-photo").onchange=function(){var f=this.files[0];if(!f)return;var im=new Image();im.onload=function(){CV.photo=im;cvRender()};','$("cv-photo").onchange=function(){var f=this.files[0];if(!f)return;var im=new Image();im.onload=function(){CV.photo=im;if(!/^ph_/.test(CV.tpl)){CV.tpl="ph_cine";try{cvSave()}catch(e){}toast("ใช้แบบ \\"รูปคุณ\\" ให้แล้ว หน้าและชุดไม่ถูกวาดใหม่")}cvRender()};')
# 2) shorts
R('<button data-l="30">ฮุค 30 วิ<small>Reels/Shorts</small></button></div>','<button data-l="30">ฮุค 30 วิ<small>Reels/Shorts</small></button><button data-l="30" data-shorts="1">YouTube Shorts<small>9:16 · AI เลือกท่อนเด่น</small></button></div>')
R('<div id="vclip" hidden>','''<div id="vshorts" hidden style="margin-top:8px;padding:12px;border-radius:14px;border:1px solid rgba(255,51,71,.35);background:rgba(255,51,71,.06)">
     <b style="font-size:14px">ลง YouTube Shorts</b>
     <p class="mut" id="vs-why" style="font-size:12.5px;margin:4px 0 8px">AI ฟังทั้งเพลงแล้วเลือกท่อนที่พลังสูงสุด + ฮุคที่ร้องซ้ำ (เปลี่ยนท่อนเองได้ด้านล่าง) · ส่งออกแนวตั้ง 9:16 แล้วอัปโหลดตามขั้นตอนนี้</p>
     <div style="display:flex;gap:6px;flex-wrap:wrap"><button class="cta alt" id="vs-ct" style="width:auto;min-height:40px;padding:0 14px;font-size:13px">คัดลอกชื่อ Shorts</button><button class="cta alt" id="vs-cd" style="width:auto;min-height:40px;padding:0 14px;font-size:13px">คัดลอกคำอธิบาย</button><a class="cta alt" href="https://www.youtube.com/upload" target="_blank" rel="noopener" style="width:auto;min-height:40px;padding:0 14px;font-size:13px;text-decoration:none">เปิดหน้าอัปโหลด YouTube ↗</a></div>
     <p class="mut" style="font-size:11.5px;margin:8px 0 0">ในมือถือ: แอป YouTube › ปุ่ม + › สร้าง Short › เลือกวิดีโอที่บันทึกไว้ · แอปอัปโหลดแทนคุณเองไม่ได้ เพราะต้องล็อกอินช่อง YouTube ของคุณ</p>
    </div>
    <div id="vclip" hidden>''')
R("document.querySelectorAll(\"#vlen button\").forEach(function(b){b.onclick=function(){VLEN=+b.dataset.l;$(\"vclip\").hidden=!VLEN;if(VLEN)vsecFill();document.querySelectorAll(\"#vlen button\").forEach(function(x){x.classList.toggle(\"on\",x==b)});if(b.dataset.reel){",
  "document.querySelectorAll(\"#vlen button\").forEach(function(b){b.onclick=function(){VLEN=+b.dataset.l;$(\"vclip\").hidden=!VLEN;$(\"vshorts\").hidden=!b.dataset.shorts;if(VLEN){vsecFill();bestSec()}document.querySelectorAll(\"#vlen button\").forEach(function(x){x.classList.toggle(\"on\",x==b)});if(b.dataset.reel||b.dataset.shorts){")
R('var VLEN=0,VSEC=-1,VEND="auto";','''var VLEN=0,VSEC=-1,VEND="auto",VBEST=-1,VBWHY="";
/* หาท่อนเด่นสำหรับคลิปสั้น: ความดังจริงของเพลง + ฮุค + ประโยคที่ร้องซ้ำ */
async function bestSec(){try{var L=secList();if(!L.length)return;var buf=await getBuf(),ch=buf.getChannelData(0),sr=buf.sampleRate,len=VLEN||30,best=-1,bs=-1e9,why="";
 var txt={};for(var q=0;q<N;q++){var k=LN[q].t.replace(/\\(.*?\\)/g,"").trim().toLowerCase();txt[k]=(txt[k]||0)+1}
 L.forEach(function(o){var s0=Math.max(0,T[o.i]-off),a=Math.floor(s0*sr),b=Math.min(ch.length,Math.floor((s0+len)*sr)),e=0,n=0;for(var j=a;j<b;j+=16){e+=ch[j]*ch[j];n++}if(!n)return;var db=10*Math.log10(e/n+1e-12),rep=0;
  for(var q2=o.i;q2<N&&LN[q2].g==LN[o.i].g;q2++){var k2=LN[q2].t.replace(/\\(.*?\\)/g,"").trim().toLowerCase();if(txt[k2]>1)rep++}
  var sc=db+(LN[o.i].h?2.5:0)+Math.min(2,rep*.5)-(o.i==0?1:0);if(sc>bs){bs=sc;best=o.i;why=o.label.split(" · ")[0]+(LN[o.i].h?" (ฮุค":" (")+"ดังสุด "+(rep?"· มีท่อนร้องซ้ำ":"")+")"}});
 VBEST=best;VBWHY=why;vsecFill();var w=$("vs-why");if(w&&why)w.textContent="AI เลือก: "+why+" · ฟังทั้งเพลงแล้วเลือกท่อนที่พลังสูงสุด + ฮุคที่ร้องซ้ำ (เปลี่ยนเองได้ด้านล่าง) · ส่งออกแนวตั้ง 9:16 แล้วอัปโหลดตามขั้นตอนนี้"}catch(e){}}
function shortsText(){var R0=(typeof RL!="undefined"&&RL)||{},ti=R0.title||CV.title||"",ar=R0.artist||CV.artist||"",hk="";for(var i=0;i<N;i++)if(LN[i].h){hk=LN[i].t.replace(/\\(.*?\\)/g,"").trim();break}
 return{t:(ar+" - "+ti).trim()+" #Shorts",d:(hk?"“"+hk+"”\\n\\n":"")+ar+" - "+ti+"\\nฟังเต็มเพลงบนช่องนี้ 🔗\\n\\n#Shorts #"+String(ar).replace(/\\s+/g,"")+" #เพลงใหม่ #ฮิปฮอปไทย"}}''')
R('var i,h=-1;if(VSEC>=0&&VSEC<N)h=VSEC;else for(','var i,h=-1;if(VSEC>=0&&VSEC<N)h=VSEC;else if(VBEST>=0&&VBEST<N)h=VBEST;else for(')
R('''el.innerHTML='<option value="-1">AI เลือกท่อนเด่น (ฮุคแรก)</option>'+''','''el.innerHTML='<option value="-1">AI เลือกท่อนเด่น'+(VBEST>=0&&VBWHY?" · "+esc2(VBWHY):" (ฮุคแรก)")+'</option>'+''')
R('$("vsec").onchange=function(){VSEC=+this.value};','$("vsec").onchange=function(){VSEC=+this.value};$("vs-ct").onclick=function(){var t=shortsText().t;try{navigator.clipboard.writeText(t);toast("คัดลอกแล้ว: "+t)}catch(e){prompt("คัดลอก",t)}};$("vs-cd").onclick=function(){var t=shortsText().d;try{navigator.clipboard.writeText(t);toast("คัดลอกคำอธิบายแล้ว")}catch(e){prompt("คัดลอก",t)}};')
# 3) release radar placeholder
R('<input class="inp" id="rl-date" type="date"></div>','<input class="inp" id="rl-date" type="date"></div>\n    <div id="rl-radar"></div>')
# 4) genre card out of the mix tab -> link to explore page
i=s.index(' <section class="card" id="gnr">');j=s.index('</section>',i)+len('</section>')
s=s[:i]+s[j+1:] if s[j]=='\n' else s[:i]+s[j:]
R('มีไฟล์ที่มิกซ์แล้ว? <button type="button" class="lnkb" id="mx-skip">ข้ามไปใส่เพลง →</button></p>','มีไฟล์ที่มิกซ์แล้ว? <button type="button" class="lnkb" id="mx-skip">ข้ามไปใส่เพลง →</button> · อยากรู้ว่าเพลงนี้แนวอะไร? <button type="button" class="lnkb" onclick="window.SNSExplore&&SNSExplore.open()">หน้าค้นหาแนวเพลง →</button></p>')
R('ทำเสียงให้เสร็จก่อนเพราะ AI ต้องใช้เพลงตัวจริงไปซิงค์เนื้อ หาจังหวะตัดภาพ MV และดูแนวเพลง','ทำเสียงให้เสร็จก่อนเพราะ AI ต้องใช้เพลงตัวจริงไปซิงค์เนื้อ และหาจังหวะตัดภาพ MV')
open(p,'w',encoding='utf-8').write(s);print('ok')
