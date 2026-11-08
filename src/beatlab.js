/* ===== Slope North Side · Beat Lab: AI ทำบีตในเครื่อง (ฟรี) =====
   สังเคราะห์เสียงเองทั้งหมดด้วย Web Audio (ไม่ใช้แซมเปิลของใคร ทำนองแต่งใหม่ทุกครั้ง)
   AI (Claude บน claude.ai / Puter บนเว็บ) ช่วยวาง "สูตรบีต" ให้คล้ายแนวศิลปิน/เพลงที่อิน
   window.SNSBeat.render(recipe) → {buffer, wav(), meta} */
(function(){
"use strict";
var SR=44100;
function rng(seed){var a=seed>>>0||1;return function(){a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function pick(R,a){return a[Math.floor(R()*a.length)]}
function mtof(m){return 440*Math.pow(2,(m-69)/12)}
var NN=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];
var SC={minor:[0,2,3,5,7,8,10],harm:[0,2,3,5,7,8,11],phryg:[0,1,3,5,7,8,10],dor:[0,2,3,5,7,9,10],major:[0,2,4,5,7,9,11]};
var SCN={minor:"ไมเนอร์",harm:"ฮาร์โมนิกไมเนอร์",phryg:"ฟริเจียน (มืด)",dor:"โดเรียน",major:"เมเจอร์"};
/* ---------- แนว (ตรงกับ GEN ในหน้าแต่งเพลง) ---------- */
var STY={
 trap:{n:"Melodic Trap",bpm:[136,156],half:1,scale:["minor","harm"],progs:[[1,6,3,7],[1,4,6,5],[1,7,6,7],[6,4,1,5],[1,6,4,5]],cb:1,ext:3,drum:"trap",keys:["pad","pluck"],lead:["bell","pluck","flute"],bass:"808g",swing:0,len:[120,160]},
 drill:{n:"UK Drill",bpm:[140,145],half:1,scale:["harm","minor","phryg"],progs:[[1,6,4,5],[1,6,3,5],[1,2,6,5],[1,4,6,5]],cb:2,ext:3,drum:"drill",keys:["strings","piano"],lead:["piano","strings","bell"],bass:"808g",swing:0,len:[120,155]},
 rnb:{n:"Dark R&B",bpm:[64,76],half:0,scale:["minor","dor"],progs:[[1,6,3,7],[1,4,7,3],[6,7,1,1],[1,7,6,5],[4,5,1,6]],cb:1,ext:5,drum:"rnb",keys:["pad","ep"],lead:["vox","flute","ep"],bass:"808",swing:.08,len:[150,180]},
 lofi:{n:"Lo-fi อบอุ่น",bpm:[74,88],half:0,scale:["major","dor"],progs:[[2,5,1,6],[4,3,2,1],[1,6,2,5],[4,5,3,6]],cb:1,ext:5,drum:"lofi",keys:["ep","piano"],lead:["ep","flute"],bass:"sub",swing:.16,len:[120,150],crackle:1},
 rap:{n:"Boom bap",bpm:[86,96],half:0,scale:["minor","dor"],progs:[[1,4,1,5],[1,6,4,5],[1,1,4,4],[1,7,6,5]],cb:1,ext:4,drum:"boombap",keys:["piano","ep"],lead:["piano","flute","strings"],bass:"sub",swing:.14,len:[130,170],crackle:1},
 thai:{n:"ป๊อป/R&B ไทย",bpm:[78,100],half:0,scale:["major","minor"],progs:[[1,5,6,4],[6,4,1,5],[1,6,4,5],[4,5,3,6]],cb:1,ext:4,drum:"pop",keys:["ep","pad","piano"],lead:["pluck","vox","bell"],bass:"808",swing:.06,len:[150,180]},
 emo:{n:"Emo/Rock rap",bpm:[140,160],half:1,scale:["minor","major"],progs:[[1,6,3,7],[6,4,1,5],[1,5,6,4]],cb:1,ext:3,drum:"trap",keys:["guitar","pad"],lead:["guitar","bell"],bass:"808g",swing:0,len:[120,150]},
 phonk:{n:"Phonk",bpm:[124,140],half:1,scale:["phryg","minor"],progs:[[1,2,1,7],[1,6,2,1],[1,1,6,7]],cb:2,ext:3,drum:"phonk",keys:["pad","strings"],lead:["cowbell"],bass:"808d",swing:0,len:[110,140]},
 pop:{n:"Pop R&B",bpm:[88,110],half:0,scale:["major","minor"],progs:[[1,5,6,4],[4,1,5,6],[6,4,1,5],[2,5,1,6]],cb:1,ext:4,drum:"pop",keys:["ep","pad"],lead:["pluck","vox","bell"],bass:"808",swing:.05,len:[140,180]}};
var MOODLEN={"เศร้า":170,"อกหัก":170,"เหงา":165,"คิดถึง":165,"รัก/หวาน":160,"มืด/หม่น":160,"สำนึกผิด/ขอโทษ":170,"ครอบครัว":165,"ขับรถกลางคืน":165,"ฝัน/ล่องลอย":160,
 "ปาร์ตี้":125,"โกรธ":120,"แค้น/ดิส":120,"มั่นใจ/โชว์ของ":135,"สู้/ฮึกเหิม":140,"ธุรกิจ/หาเงิน":140,"ภูมิใจ/ฉลอง":130,"สายถนน":130,"ตลก/กวน":115,"ชิล":150,"อิสระ/ปล่อยวาง":150,"หลอน":140};
/* ---------- สูตรบีต ---------- */
function recipe(o){o=o||{};var seed=(o.seed>>>0)||((Math.random()*4294967295)>>>0),R=rng(seed),k=STY[o.style]?o.style:"trap",S=STY[k];
 var bpm=o.bpm?Math.max(60,Math.min(170,Math.round(o.bpm))):Math.round(S.bpm[0]+R()*(S.bpm[1]-S.bpm[0]));
 var sc=SC[o.scale]?o.scale:pick(R,S.scale),key=o.key!=null&&o.key>=0&&o.key<12?o.key|0:Math.floor(R()*12);
 var prog=(o.prog&&o.prog.length>=2&&o.prog.every(function(d){return d>=1&&d<=7}))?o.prog.slice(0,8):pick(R,S.progs);
 var len=o.len?Math.max(110,Math.min(180,o.len)):(function(){var m=(o.moods||[]).map(function(x){return MOODLEN[x]}).filter(Boolean);var b=m.length?m.reduce(function(a,b){return a+b},0)/m.length:(S.len[0]+S.len[1])/2;return Math.max(110,Math.min(180,Math.round(b+(R()-.5)*24)))})();
 return{seed:seed,style:k,bpm:bpm,key:key,scale:sc,prog:prog,len:len,keys:o.keys&&/^(ep|pad|piano|pluck|strings|guitar)$/.test(o.keys)?o.keys:pick(R,S.keys),
  lead:o.lead&&/^(bell|pluck|flute|piano|cowbell|guitar|vox|ep|strings)$/.test(o.lead)?o.lead:pick(R,S.lead),swing:o.swing!=null?Math.max(0,Math.min(.25,+o.swing)):S.swing,
  dark:o.dark!=null?+o.dark:.5,energy:o.energy!=null?+o.energy:.6,why:o.why||"",ref:o.ref||""}}
function keyName(r){return NN[r.key]+" "+SCN[r.scale]}
/* ---------- ทฤษฎี ---------- */
function chord(r,deg,ext,oct){var s=SC[r.scale],out=[];for(var i=0;i<ext;i++){var d=deg-1+i*2,o=Math.floor(d/7);out.push(12*(oct+o)+r.key+s[d%7])}
 if(r.style=="drill"&&deg==5&&r.scale!="major")out[1]=12*oct+r.key+11-12*(out[1]<12*oct+r.key+7?1:0); /* V เมเจอร์ในไมเนอร์ */
 return out}
function scaleNotes(r,lo,hi){var s=SC[r.scale],out=[];for(var m=lo;m<=hi;m++){if(s.indexOf(((m-r.key)%12+12)%12)>=0)out.push(m)}return out}
/* ---------- เสียงพื้นฐาน ---------- */
var NOISE=null;function noise(c){if(NOISE&&NOISE.sampleRate==c.sampleRate)return NOISE;var b=c.createBuffer(1,c.sampleRate*2,c.sampleRate),d=b.getChannelData(0);for(var i=0;i<d.length;i++)d[i]=Math.random()*2-1;NOISE=b;return b}
function env(g,t,a,peak,d,sus,rel,end){g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(peak,t+a);g.gain.setTargetAtTime(peak*sus,t+a,d/3);g.gain.setTargetAtTime(0,end,rel/3)}
function osc(c,type,f,t,end,det){var o=c.createOscillator();o.type=type;o.frequency.setValueAtTime(f,t);if(det)o.detune.value=det;o.start(t);o.stop(end+.05);return o}
function nsrc(c,t,dur){var s=c.createBufferSource();s.buffer=noise(c);s.loop=true;s.start(t,Math.random()*1.5);s.stop(t+dur+.05);return s}
function shaper(c,amt){var w=c.createWaveShaper(),n=2048,cv=new Float32Array(n);for(var i=0;i<n;i++){var x=i*2/n-1;cv[i]=Math.tanh(x*amt)/Math.tanh(amt)}w.curve=cv;w.oversample="2x";return w}
/* ---------- กลอง ---------- */
var DR={
 kick:function(c,o,t,v,p){var g=c.createGain(),f=osc(c,"sine",p&&p.hard?190:160,t,t+.5);f.frequency.exponentialRampToValueAtTime(p&&p.hard?48:52,t+.11);f.connect(g);g.connect(o);
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v*1.05,t+.003);g.gain.exponentialRampToValueAtTime(.001,t+(p&&p.long?.55:.38));
  var kn=osc(c,"triangle",260,t,t+.12),kg=c.createGain();kn.frequency.exponentialRampToValueAtTime(120,t+.035);kn.connect(kg);kg.connect(o);kg.gain.setValueAtTime(v*.55,t);kg.gain.exponentialRampToValueAtTime(.001,t+.07);
  var ng=c.createGain(),hp=c.createBiquadFilter();hp.type="highpass";hp.frequency.value=3000;var s=nsrc(c,t,.02);s.connect(hp);hp.connect(ng);ng.connect(o);ng.gain.setValueAtTime(v*.6,t);ng.gain.exponentialRampToValueAtTime(.001,t+.015)},
 snare:function(c,o,t,v,p){var bp=c.createBiquadFilter();bp.type="bandpass";bp.frequency.value=p&&p.tune?p.tune:1900;bp.Q.value=.8;var g=c.createGain(),s=nsrc(c,t,.3);s.connect(bp);bp.connect(g);g.connect(o);
  g.gain.setValueAtTime(v*.9,t);g.gain.exponentialRampToValueAtTime(.001,t+(p&&p.long?.32:.19));
  var tg=c.createGain(),tn=osc(c,"triangle",200,t,t+.2);tn.frequency.exponentialRampToValueAtTime(150,t+.08);tn.connect(tg);tg.connect(o);tg.gain.setValueAtTime(v*.55,t);tg.gain.exponentialRampToValueAtTime(.001,t+.11)},
 clap:function(c,o,t,v){var bp=c.createBiquadFilter();bp.type="bandpass";bp.frequency.value=1250;bp.Q.value=1.1;var g=c.createGain(),s=nsrc(c,t,.4);s.connect(bp);bp.connect(g);g.connect(o);
  g.gain.setValueAtTime(0,t);[0,.011,.022].forEach(function(d){g.gain.setValueAtTime(v,t+d);g.gain.exponentialRampToValueAtTime(v*.18,t+d+.009)});g.gain.setValueAtTime(v*.8,t+.031);g.gain.exponentialRampToValueAtTime(.001,t+.26)},
 snap:function(c,o,t,v){var hp=c.createBiquadFilter();hp.type="bandpass";hp.frequency.value=2600;hp.Q.value=1.6;var g=c.createGain(),s=nsrc(c,t,.12);s.connect(hp);hp.connect(g);g.connect(o);g.gain.setValueAtTime(v*1.2,t);g.gain.exponentialRampToValueAtTime(.001,t+.07)},
 hat:function(c,o,t,v,p){var hp=c.createBiquadFilter();hp.type="highpass";hp.frequency.value=p&&p.open?6500:7800;var g=c.createGain(),s=nsrc(c,t,.5);s.connect(hp);hp.connect(g);g.connect(o);
  g.gain.setValueAtTime(v*.75,t);g.gain.exponentialRampToValueAtTime(.001,t+(p&&p.open?.28:.05))},
 shaker:function(c,o,t,v){var bp=c.createBiquadFilter();bp.type="bandpass";bp.frequency.value=5800;bp.Q.value=.9;var g=c.createGain(),s=nsrc(c,t,.1);s.connect(bp);bp.connect(g);g.connect(o);g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v*.25,t+.012);g.gain.exponentialRampToValueAtTime(.001,t+.06)},
 rim:function(c,o,t,v){var g=c.createGain(),a=osc(c,"square",1720,t,t+.06),bp=c.createBiquadFilter();bp.type="bandpass";bp.frequency.value=1700;bp.Q.value=4;a.connect(bp);bp.connect(g);g.connect(o);g.gain.setValueAtTime(v*.5,t);g.gain.exponentialRampToValueAtTime(.001,t+.04)},
 crash:function(c,o,t,v){var hp=c.createBiquadFilter();hp.type="highpass";hp.frequency.value=4500;var g=c.createGain(),s=nsrc(c,t,2);s.connect(hp);hp.connect(g);g.connect(o);g.gain.setValueAtTime(v*.35,t);g.gain.exponentialRampToValueAtTime(.001,t+1.8)},
 impact:function(c,o,t,v){var g=c.createGain(),a=osc(c,"sine",90,t,t+1.2);a.frequency.exponentialRampToValueAtTime(38,t+.6);a.connect(g);g.connect(o);g.gain.setValueAtTime(v*.8,t);g.gain.exponentialRampToValueAtTime(.001,t+1.1)},
 riser:function(c,o,t,v,p){var d=p&&p.d||2,bp=c.createBiquadFilter();bp.type="bandpass";bp.Q.value=1.2;bp.frequency.setValueAtTime(300,t);bp.frequency.exponentialRampToValueAtTime(9000,t+d);var g=c.createGain(),s=nsrc(c,t,d+.1);s.connect(bp);bp.connect(g);g.connect(o);g.gain.setValueAtTime(.001,t);g.gain.exponentialRampToValueAtTime(v*.5,t+d*.95);g.gain.linearRampToValueAtTime(0,t+d)},
 perc:function(c,o,t,v,p){var g=c.createGain(),a=osc(c,"sine",p&&p.f||420,t,t+.2);a.frequency.exponentialRampToValueAtTime((p&&p.f||420)*.7,t+.15);a.connect(g);g.connect(o);g.gain.setValueAtTime(v*.5,t);g.gain.exponentialRampToValueAtTime(.001,t+.16)}};
/* ---------- เบส ---------- */
function bass808(c,o,t,dur,m,v,p){var f=mtof(m),g=c.createGain(),a=osc(c,"sine",f*1.7,t,t+dur+.4),h=osc(c,"triangle",f*2,t,t+dur+.4),hg=c.createGain();hg.gain.value=.12;
 a.frequency.exponentialRampToValueAtTime(f,t+.04);h.frequency.exponentialRampToValueAtTime(f*2,t+.04);
 if(p&&p.glide){a.frequency.setValueAtTime(f,t+dur-.09);a.frequency.exponentialRampToValueAtTime(mtof(p.glide),t+dur);h.frequency.setValueAtTime(f*2,t+dur-.09);h.frequency.exponentialRampToValueAtTime(mtof(p.glide)*2,t+dur)}
 var sh=shaper(c,p&&p.drive||1.8),lp=c.createBiquadFilter();lp.type="lowpass";lp.frequency.value=p&&p.drive>3?1400:620;
 a.connect(sh);h.connect(hg);hg.connect(sh);sh.connect(lp);lp.connect(g);g.connect(o);
 g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v,t+.006);g.gain.setTargetAtTime(v*.75,t+.006,.25);g.gain.setTargetAtTime(0,t+dur,.05)}
function subBass(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),a=osc(c,"sine",f,t,t+dur+.2),b=osc(c,"triangle",f,t,t+dur+.2),bg=c.createGain();bg.gain.value=.25;
 var lp=c.createBiquadFilter();lp.type="lowpass";lp.frequency.value=380;a.connect(g);b.connect(bg);bg.connect(lp);lp.connect(g);g.connect(o);env(g,t,.008,v,.3,.6,.08,t+dur)}
/* ---------- คีย์/เมโลดี้ ---------- */
var INS={
 ep:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),car=osc(c,"sine",f,t,t+dur+1.2),mod=osc(c,"sine",f,t,t+dur+1.2),mg=c.createGain(),c2=osc(c,"sine",f*2,t,t+dur+1.2),g2=c.createGain();
  mg.gain.setValueAtTime(f*2.2,t);mg.gain.exponentialRampToValueAtTime(f*.25,t+.5);mod.connect(mg);mg.connect(car.frequency);g2.gain.value=.12;c2.connect(g2);g2.connect(g);car.connect(g);g.connect(o);
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v*.5,t+.004);g.gain.setTargetAtTime(v*.18,t+.004,.6);g.gain.setTargetAtTime(0,t+dur,.25)},
 piano:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),a=osc(c,"triangle",f,t,t+dur+2),b=osc(c,"sine",f*2,t,t+dur+2,3),bg=c.createGain(),cc=osc(c,"sine",f,t,t+dur+2,-4),lp=c.createBiquadFilter();
  bg.gain.value=.22;lp.type="lowpass";lp.frequency.setValueAtTime(Math.min(9000,f*9),t);lp.frequency.exponentialRampToValueAtTime(Math.max(500,f*2.5),t+1.2);
  a.connect(lp);cc.connect(lp);b.connect(bg);bg.connect(lp);lp.connect(g);g.connect(o);
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v*.42,t+.003);g.gain.setTargetAtTime(v*.12,t+.003,.5);g.gain.setTargetAtTime(0,t+dur,.18)},
 pad:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),lp=c.createBiquadFilter();lp.type="lowpass";lp.frequency.setValueAtTime(700,t);lp.frequency.linearRampToValueAtTime(1500,t+Math.min(dur,1.5));lp.Q.value=.4;
  [-9,0,8].forEach(function(d){var a=osc(c,"sawtooth",f,t,t+dur+1.2,d);a.connect(lp)});lp.connect(g);g.connect(o);env(g,t,.35,v*.075,.6,.85,.7,t+dur)},
 strings:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),lp=c.createBiquadFilter();lp.type="lowpass";lp.frequency.value=2200;var lfo=osc(c,"sine",5.2,t,t+dur+1.2),lg=c.createGain();lg.gain.value=6;lfo.connect(lg);
  [-12,0,11].forEach(function(d){var a=osc(c,"sawtooth",f,t,t+dur+1.2,d);lg.connect(a.detune);a.connect(lp)});lp.connect(g);g.connect(o);env(g,t,.22,v*.08,.5,.9,.45,t+dur)},
 pluck:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),lp=c.createBiquadFilter(),a=osc(c,"sawtooth",f,t,t+dur+.6),b=osc(c,"square",f,t,t+dur+.6,7),bg=c.createGain();bg.gain.value=.35;
  lp.type="lowpass";lp.Q.value=2;lp.frequency.setValueAtTime(5200,t);lp.frequency.exponentialRampToValueAtTime(500,t+.25);a.connect(lp);b.connect(bg);bg.connect(lp);lp.connect(g);g.connect(o);
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v*.2,t+.003);g.gain.exponentialRampToValueAtTime(.001,t+Math.min(.9,dur+.35))},
 bell:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain();[[1,1],[2.76,.32],[5.4,.12],[2,.18]].forEach(function(p){var a=osc(c,"sine",f*p[0],t,t+2.2),gg=c.createGain();gg.gain.value=p[1];a.connect(gg);gg.connect(g)});g.connect(o);
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v*.26,t+.002);g.gain.exponentialRampToValueAtTime(.001,t+Math.max(.7,Math.min(2,dur*2.5)))},
 flute:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),a=osc(c,"sine",f,t,t+dur+.4),b=osc(c,"triangle",f*2,t,t+dur+.4),bg=c.createGain(),lfo=osc(c,"sine",5.5,t,t+dur+.4),lg=c.createGain();
  bg.gain.value=.08;lg.gain.setValueAtTime(0,t);lg.gain.linearRampToValueAtTime(f*.012,t+.35);lfo.connect(lg);lg.connect(a.frequency);
  var br=nsrc(c,t,dur+.3),bp=c.createBiquadFilter(),ng=c.createGain();bp.type="bandpass";bp.frequency.value=f*2;bp.Q.value=3;ng.gain.value=.05;br.connect(bp);bp.connect(ng);ng.connect(g);
  a.connect(g);b.connect(bg);bg.connect(g);g.connect(o);env(g,t,.06,v*.22,.3,.8,.12,t+dur)},
 vox:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),a=osc(c,"sawtooth",f,t,t+dur+.5),lfo=osc(c,"sine",5,t,t+dur+.5),lg=c.createGain();lg.gain.setValueAtTime(0,t);lg.gain.linearRampToValueAtTime(f*.015,t+.3);lfo.connect(lg);lg.connect(a.frequency);
  var f1=c.createBiquadFilter(),f2=c.createBiquadFilter(),g1=c.createGain(),g2=c.createGain();f1.type=f2.type="bandpass";f1.frequency.value=700;f2.frequency.value=1150;f1.Q.value=f2.Q.value=6;g2.gain.value=.6;
  a.connect(f1);a.connect(f2);f1.connect(g1);f2.connect(g2);g1.connect(g);g2.connect(g);g.connect(o);env(g,t,.05,v*.5,.3,.8,.15,t+dur)},
 cowbell:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),bp=c.createBiquadFilter();bp.type="bandpass";bp.frequency.value=f*1.2;bp.Q.value=1.4;
  [1,1.48].forEach(function(r){var a=osc(c,"square",f*r,t,t+.6);a.connect(bp)});bp.connect(g);g.connect(o);g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v*.3,t+.002);g.gain.exponentialRampToValueAtTime(v*.08,t+.06);g.gain.exponentialRampToValueAtTime(.001,t+Math.min(.45,dur+.2))},
 guitar:function(c,o,t,dur,m,v){var f=mtof(m),g=c.createGain(),lp=c.createBiquadFilter(),sh=shaper(c,2.5),a=osc(c,"sawtooth",f,t,t+dur+.8,-5),b=osc(c,"sawtooth",f,t,t+dur+.8,6);
  lp.type="lowpass";lp.frequency.setValueAtTime(3200,t);lp.frequency.exponentialRampToValueAtTime(900,t+.5);a.connect(sh);b.connect(sh);sh.connect(lp);lp.connect(g);g.connect(o);
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v*.1,t+.004);g.gain.setTargetAtTime(v*.04,t+.004,.4);g.gain.setTargetAtTime(0,t+dur,.12)}};
/* ---------- รูปแบบกลอง (16 สเต็ป/ห้อง) ---------- */
function P(s){var a=[];for(var i=0;i<s.length;i++)if(s[i]!=".")a.push(i);return a}
var KICK={trap:["x.........x.....","x......x..x.....","x.....x...x..x..","x..x......x.....","x.......x.x....x"],drill:["x.........x.....","x.....x.........","x.......x.....x.","x.........x..x.."],
 boombap:["x......x..x.....","x.x....x..x.....","x......x.x...x.."],rnb:["x.......x.x.....","x......x........","x.........x..x.."],lofi:["x......x..x.....","x.....x...x.x..."],
 pop:["x.......x.x.....","x.....x.x.......","x..x....x.x....."],phonk:["x.....x...x.....","x..x..x...x....."]};
function drumBar(R,kind,bar,sec,half){var ev=[],st=function(s,i,v,p){ev.push({s:s,i:i,v:v,p:p})},kp=pick(R,KICK[kind=="lofi"?"lofi":kind]||KICK.trap);
 var lastBar=sec.last&&bar==sec.bars-1,fill=lastBar&&sec.next=="hook";
 P(kp).forEach(function(s){if(fill&&s>=12)return;st(s,"kick",.95)});
 if(kind=="trap"||kind=="phonk"){st(8,"clap",.85);if(R()<.25)st(8,"snare",.4);
  for(var s=0;s<16;s+=2){if(R()<.18&&s>=4){var n=pick(R,[3,4,6]);for(var k=0;k<n;k++)st(s+k*2/n,"hat",.5+.3*(k%2))}else st(s,"hat",s%4?.55:.75)}
  if(R()<.35)st(pick(R,[6,14]),"hat",.6,{open:1});if(kind=="phonk"&&R()<.5)st(14,"snare",.5)}
 else if(kind=="drill"){st(8,"snare",.9,{tune:2300});if(bar%2==1)st(R()<.5?13:15,"snare",.65,{tune:2300});else if(R()<.3)st(5,"snare",.35,{tune:2300});
  [0,3,6,8,11,14].forEach(function(s){st(s,"hat",s==0||s==8?.7:.5)});if(R()<.4){st(12+2/3,"hat",.45);st(13+1/3,"hat",.45)}if(R()<.3)st(10,"perc",.4,{f:pick(R,[380,520,640])})}
 else if(kind=="boombap"||kind=="lofi"){st(4,"snare",.9,{long:kind=="boombap"});st(12,"snare",.9,{long:kind=="boombap"});if(R()<.4)st(15,"snare",.25);
  for(var s2=0;s2<16;s2+=2)st(s2,"hat",s2%4?.45:.65);if(R()<.5)st(pick(R,[7,11,13]),"hat",.3);if(kind=="lofi"&&R()<.4)st(pick(R,[3,10]),"rim",.4)}
 else if(kind=="rnb"){st(4,"snap",.85);st(12,"snap",.85);if(R()<.4)st(12,"clap",.4);for(var s3=0;s3<16;s3++)if(s3%2==0||R()<.25)st(s3,"hat",s3%4==0?.45:.3);if(R()<.4)st(14,"hat",.45,{open:1})}
 else{st(4,"clap",.85);st(12,"clap",.85);st(4,"snare",.45);st(12,"snare",.45);for(var s4=0;s4<16;s4+=2)st(s4,"hat",.5);for(var s5=1;s5<16;s5+=2)st(s5,"shaker",.5);if(R()<.4)st(14,"hat",.5,{open:1})}
 if(fill){for(var q=12;q<16;q+=.5)st(q,kind=="boombap"||kind=="lofi"?"snare":"hat",.3+(q-12)*.12)}
 return ev}
/* ---------- เมโลดี้ (โมทีฟ 2 ห้อง แล้วแปรผัน) ---------- */
var RHY=[[0,3,6,8,10,14],[0,2,4,7,10,12],[0,4,6,10,12],[0,3,6,10,12,14],[2,4,6,8,11,14],[0,6,8,12],[0,2,3,6,8,11,12,14]];
function motif(R,r,chords,lo){var notes=scaleNotes(r,lo,lo+19),out=[],idx=Math.floor(notes.length*.45);
 for(var b=0;b<2;b++){var rh=pick(R,RHY),ch=chords[b%chords.length];rh.forEach(function(s,j){
  var strong=s%4==0,cand;if(strong){cand=notes.filter(function(n){return ch.some(function(c){return((n-c)%12+12)%12==0})});var cur=notes[idx];cand.sort(function(a,b){return Math.abs(a-cur)-Math.abs(b-cur)});var nn=cand[Math.min(cand.length-1,Math.floor(R()*2))];idx=notes.indexOf(nn)}
  else idx=Math.max(0,Math.min(notes.length-1,idx+pick(R,[-2,-1,-1,1,1,2,0])));
  var nx=rh[j+1]!=null?rh[j+1]:16,dur=Math.max(1,Math.min(nx-s,4));out.push({s:b*16+s,m:notes[idx],d:dur,v:strong?.95:.75})})}
 return out}
function vary(R,m,r,lo){var notes=scaleNotes(r,lo,lo+19);return m.map(function(n,i){var x=Object.assign({},n);if(n.s>=24&&R()<.5){var k=notes.indexOf(n.m);if(k>=0)x.m=notes[Math.max(0,Math.min(notes.length-1,k+pick(R,[-2,-1,1,2])))]}return x})}
/* ---------- โครงเพลง ---------- */
function form(r){var target=Math.max(24,Math.round(r.len*r.bpm/240)),slow=r.bpm<100,best=null;
 /* หาโครงที่ยาวใกล้เป้าที่สุด (เพลงช้าใช้ท่อนสั้นลงได้) */
 [4,8].forEach(function(intro){[4,8].forEach(function(hk){[4,8,16].forEach(function(v1){[4,8,16].forEach(function(v2){[0,4,8].forEach(function(br){[0,8,16].forEach(function(v3){[4,8].forEach(function(out){
  var S=[["intro",intro],["hook",hk],["verse",v1],["hook",hk],["verse",v2]];if(br)S.push(["bridge",br]);S.push(["hook",hk]);if(v3){S.push(["verse",v3]);S.push(["hook",hk])}S.push(["outro",out]);
  var tot=S.reduce(function(a,x){return a+x[1]},0),pen=Math.abs(tot-target)*4+(hk==4?(slow?3:12):0)+(v1==4||v2==4?(slow?4:14):0)+(v3?2:0)+(intro==8?1:0)+(out==8?1:0)+(br==4?2:0)+Math.abs(v1-v2)/8;
  if(!best||pen<best.pen)best={S:S,pen:pen}})})})})})})});
 var S=best.S,out=[],t=0;S.forEach(function(x,i){out.push({name:x[0],bars:x[1],start:t,next:S[i+1]?S[i+1][0]:"",last:1});t+=x[1]});return out}
/* ---------- ตัวเรนเดอร์ ---------- */
function impulse(c,sec,decay){var n=Math.floor(c.sampleRate*sec),b=c.createBuffer(2,n,c.sampleRate);for(var ch=0;ch<2;ch++){var d=b.getChannelData(ch);for(var i=0;i<n;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/n,decay)}return b}
/* เรนเดอร์แบบ "อัดเสียงทีละชิ้นครั้งเดียว แล้วเรียง+ผสมเอง" → เร็วพอสำหรับมือถือ */
var CACHE={};
function bake(key,len,fn){if(CACHE[key])return CACHE[key];var C=window.OfflineAudioContext||window.webkitOfflineAudioContext,c=new C(1,Math.max(1,Math.ceil(len*SR)),SR);fn(c,c.destination);
 CACHE[key]=c.startRendering().then(function(b){return b.getChannelData(0)});return CACHE[key]}
function q(x){return Math.round(x*50)/50}
async function render(r,onProg){var S=STY[r.style],R=rng(r.seed^0x9e3779b9),spb=60/r.bpm,st16=spb/4,F=form(r),bars=F.reduce(function(a,x){return a+x.bars},0),dur=bars*4*spb+3,N=Math.ceil(dur*SR);
 var EV=[],add=function(bus,key,len,fn,t,g){EV.push({bus:bus,key:key,len:len,fn:fn,t:t,g:g})};
 var D=function(name,t,v,p){var k="d:"+name+":"+JSON.stringify(p||{});add("drums",k,name=="crash"?2:name=="impact"?1.2:name=="riser"?(p.d+.2):name=="hat"&&p&&p.open?.35:name=="kick"?.6:.4,function(c,o){DR[name](c,o,0,1,p)},t,v)};
 var I=function(bus,name,t,d,m,v){d=q(Math.max(.05,d));var tail=name=="bell"?2.2:name=="piano"||name=="ep"?1.6:name=="pad"||name=="strings"?1.3:.8;add(bus,"i:"+name+":"+m+":"+d,d+tail,function(c,o){INS[name](c,o,0,d,m,1)},t,v)};
 var B8=function(t,d,m,v,p){d=q(Math.max(.1,d));add("bass","b:"+m+":"+d+":"+JSON.stringify(p),d+.45,function(c,o){bass808(c,o,0,d,m,1,p)},t,v)};
 var SB=function(t,d,m,v){d=q(Math.max(.1,d));add("bass","s:"+m+":"+d,d+.3,function(c,o){subBass(c,o,0,d,m,1)},t,v)};
 var progBars=[];r.prog.forEach(function(d){for(var i=0;i<S.cb;i++)progBars.push(d)});var CH=progBars.map(function(d){return chord(r,d,S.ext,4)});
 var leadLo=r.lead=="cowbell"?60:r.lead=="vox"||r.lead=="flute"?67:r.lead=="piano"||r.lead=="strings"?64:69;
 var hookM=motif(R,r,[CH[0],CH[1%CH.length]],leadLo),hookM2=vary(R,hookM,r,leadLo),verseM=motif(R,r,[CH[0],CH[1%CH.length]],leadLo-5).filter(function(n,i){return i%2==0});
 var PAT={},R0=rng(r.seed+77),hs32=function(t){var h=0;for(var i=0;i<t.length;i++)h=(h*31+t.charCodeAt(i))|0;return h};
 var sw=function(s){return(Math.floor(s)%2==1?r.swing*st16*2:0)},T=function(bar,s){return .05+(bar*16+s)*st16+sw(s)},kicks=[];
 F.forEach(function(sec){for(var b=0;b<sec.bars;b++){var bar=sec.start+b,ch=CH[bar%CH.length],nm=sec.name,
   drumsOn=nm=="hook"||nm=="verse"||(nm=="bridge"&&b>=sec.bars/2)||(nm=="outro"&&b<2),bassOn=nm=="hook"||nm=="verse"||(nm=="outro"&&b<2),lv=nm=="hook"?1:nm=="verse"?.8:.7,
   sb={bars:sec.bars,next:sec.next,last:b==sec.bars-1},kp=null;
  if(drumsOn){var lk=nm+":"+(b%4)+":"+(sb.last?"L":""),ev=PAT[lk]||(PAT[lk]=drumBar(rng((r.seed^hs32(nm=='bridge'?'verse':nm))+(b%4>=2&&R0()<.5?b%4:b%2)),S.drum,b,sb,S.half));ev.forEach(function(e){var t=T(bar,e.s)+(e.i=="hat"?0:(R()-.5)*.006);D(e.i,t,e.v*(nm=="verse"?.92:1)*(.92+R()*.12),e.p);if(e.i=="kick")kicks.push(t)});
   kp=ev.filter(function(e){return e.i=="kick"}).map(function(e){return e.s})}
  else if(nm=="intro"&&b>=sec.bars-2&&S.drum!="rnb"){for(var hs=0;hs<16;hs+=2)D("hat",T(bar,hs),.35+b*.05)}
  if(bassOn){var root=ch[0]%12+(r.style=="drill"||r.style=="phonk"?24:(ch[0]%12>7?24:36));
   if(S.bass=="sub"){var sp=P(pick(R,KICK.boombap));sp.forEach(function(s,i){var nx=sp[i+1]!=null?sp[i+1]:16;SB(T(bar,s),(nx-s)*st16*.9,root,.8)})}
   else{var kk=kp&&kp.length?kp:[0,8];kk.forEach(function(s,i){var nx=kk[i+1]!=null?kk[i+1]:16,glide=null;if(S.bass=="808g"&&R()<.3&&i==kk.length-1)glide=root+pick(R,[12,7,-5,5]);
     B8(T(bar,s),Math.max(.15,(nx-s)*st16*.95),root,.85,{glide:glide,drive:S.bass=="808d"?5:r.style=="drill"?2.6:1.8})})}}
  if(b==sec.bars-1&&sec.next=="hook")D("riser",T(bar,0),.9,{d:q(16*st16)});
  if(b==0&&nm=="hook"){D("crash",T(bar,0),.9);D("impact",T(bar,0),.8)}
  var kt=r.keys,kv=lv*(nm=="intro"||nm=="outro"?.85:nm=="verse"?.8:1);
  if(kt=="pad"||kt=="strings")ch.forEach(function(m){I("keys",kt,T(bar,0),16*st16,m,kv)});
  else if(kt=="guitar"){for(var g=0;g<8;g++)I("keys","guitar",T(bar,g*2),st16*2.2,ch[g%ch.length]+(g>=4?12:0),kv*.9)}
  else{var stabs=r.style=="rap"?[[0,6],[7,3],[10,6]]:r.style=="lofi"||r.style=="rnb"?[[0,14]]:r.style=="drill"?[[0,6],[8,8]]:[[0,7],[8,8]];
   stabs.forEach(function(x){ch.forEach(function(m,j){I("keys",kt,T(bar,x[0])+(kt=="ep"||kt=="piano"?j*.012:0),x[1]*st16,m,kv*.85)})})}
  var lm=null,lvv=1;if(nm=="hook")lm=(b%4<2?hookM:hookM2);else if(nm=="intro"||nm=="outro"){lm=hookM;lvv=.7}else if(nm=="verse"&&b%4>=2){lm=verseM;lvv=.55}else if(nm=="bridge"){lm=hookM2;lvv=.6}
  if(lm){var half=(b%2)*16;lm.forEach(function(n){if(n.s>=half&&n.s<half+16){var tt=T(bar,n.s-half),dd=n.d*st16*(r.lead=="cowbell"||r.lead=="bell"?.6:.95);I("lead",r.lead,tt,dd,n.m,n.v*lvv);
    if(nm=="hook"&&b>=sec.bars/2&&r.lead!="vox"&&r.lead!="cowbell")I("lead",r.lead=="guitar"?"bell":r.lead,tt,dd,n.m+12,n.v*.3)}})}
 }});
 /* 1) อัดเสียงที่ไม่ซ้ำกัน */
 var keys=Object.keys(EV.reduce(function(m,e){m[e.key]=e;return m},{})),byKey={};EV.forEach(function(e){byKey[e.key]=e});
 for(var i=0;i<keys.length;i+=12){if(onProg)onProg("กำลังสร้างเสียง "+Math.min(100,Math.round(i/keys.length*100))+"%");await Promise.all(keys.slice(i,i+12).map(function(k){var e=byKey[k];return bake(k,e.len,e.fn)}))}
 /* 2) วางลงแทร็ก (mono stems) */
 if(onProg)onProg("กำลังเรียงท่อน…");var ST={drums:new Float32Array(N),bass:new Float32Array(N),keys:new Float32Array(N),lead:new Float32Array(N)};
 for(var e2=0;e2<EV.length;e2++){var ev2=EV[e2],src=await CACHE[ev2.key],dst=ST[ev2.bus],o=Math.round(ev2.t*SR),g=ev2.g,L=Math.min(src.length,N-o);for(var x=0;x<L;x++)dst[o+x]+=src[x]*g}
 if(S.crackle){var dd=ST.drums;for(var ci=0;ci<dur*8;ci++){var p0=Math.floor(R()*N),a=(R()*.05+.01)*(R()<.5?-1:1);for(var y=0;y<40&&p0+y<N;y++)dd[p0+y]+=a*Math.exp(-y/6)}}
 /* 3) ปรับสมดุลแทร็กอัตโนมัติ: กลองนำ 808 รอง ดนตรีกับเมโลดี้ไม่กลบกลอง */
 var big0=r.style=="drill"||r.style=="trap"||r.style=="phonk"||r.style=="emo",soft=r.style=="rnb"||r.style=="lofi";
 var TG={drums:soft?.26:.3,bass:big0?.2:.16,keys:soft?.12:.095,lead:soft?.08:.085},rms0=function(x){var t=0,n=0;for(var i=0;i<x.length;i+=8){t+=x[i]*x[i];n++}return Math.sqrt(t/n)};
 Object.keys(TG).forEach(function(k){var v=rms0(ST[k]);if(v>1e-5){var g=TG[k]/v,a=ST[k];for(var i=0;i<a.length;i++)a[i]*=g}});
 /* 4) มิกซ์ + เอฟเฟกต์รอบเดียว */
 if(onProg)onProg("กำลังมิกซ์…");
 var C=window.OfflineAudioContext||window.webkitOfflineAudioContext,c=new C(2,N,SR);
 var srcOf=function(arr){var b=c.createBuffer(1,N,SR);b.copyToChannel?b.copyToChannel(arr,0):b.getChannelData(0).set(arr);var s=c.createBufferSource();s.buffer=b;s.start(0);return s};
 var master=c.createGain(),comp=c.createDynamicsCompressor(),lim=c.createDynamicsCompressor();
 comp.threshold.value=-16;comp.ratio.value=2.5;comp.attack.value=.025;comp.release.value=.2;lim.threshold.value=-3;lim.ratio.value=20;lim.attack.value=.002;lim.release.value=.08;master.connect(comp);comp.connect(lim);lim.connect(c.destination);
 var big=r.style=="drill"||r.style=="trap"||r.style=="phonk"||r.style=="emo";
 var dg=c.createGain();dg.gain.value=1;srcOf(ST.drums).connect(dg);dg.connect(master);
 var bg=c.createGain();bg.gain.value=1;srcOf(ST.bass).connect(bg);bg.connect(master);
 var duck=c.createGain();duck.connect(master);var mus=c.createGain();var tone=c.createBiquadFilter();tone.type="lowpass";tone.frequency.value=S.crackle?5200:16000;mus.connect(tone);tone.connect(duck);
 var kp2=c.createStereoPanner?c.createStereoPanner():c.createGain();if(kp2.pan)kp2.pan.value=-.15;var kg=c.createGain();kg.gain.value=1;srcOf(ST.keys).connect(kg);kg.connect(kp2);kp2.connect(mus);
 var lp2=c.createStereoPanner?c.createStereoPanner():c.createGain();if(lp2.pan)lp2.pan.value=.12;var lg=c.createGain();lg.gain.value=1;srcOf(ST.lead).connect(lg);lg.connect(lp2);lp2.connect(mus);
 var rev=c.createConvolver();rev.buffer=impulse(c,r.style=="rnb"||r.style=="drill"?3:2.2,3);var rs=c.createGain();rs.gain.value=r.style=="rnb"||r.style=="lofi"?.35:.25;mus.connect(rs);rs.connect(rev);var rg=c.createGain();rg.gain.value=.5;rev.connect(rg);rg.connect(master);
 var dl=c.createDelay(2),fb=c.createGain(),dgl=c.createGain(),dlp=c.createBiquadFilter();dl.delayTime.value=spb*.75;fb.gain.value=.28;dgl.gain.value=.16;dlp.type="lowpass";dlp.frequency.value=3000;lg.connect(dl);dl.connect(dlp);dlp.connect(fb);fb.connect(dl);dlp.connect(dgl);dgl.connect(duck);
 F.forEach(function(sec){if(sec.name=="intro"){var t0=T(sec.start,0),t1=T(sec.start+sec.bars,0);tone.frequency.setValueAtTime(900,t0);tone.frequency.exponentialRampToValueAtTime(S.crackle?5200:16000,t1)}
  if(sec.name=="outro"){var o0=T(sec.start+2,0),o1=T(sec.start+sec.bars,0)+2.5;master.gain.setValueAtTime(1,o0);master.gain.linearRampToValueAtTime(0,o1)}});
 if(r.style!="rnb"&&r.style!="lofi")kicks.forEach(function(t){duck.gain.setValueAtTime(1,Math.max(0,t-.002));duck.gain.linearRampToValueAtTime(.65,t+.01);duck.gain.linearRampToValueAtTime(1,t+Math.min(.22,spb*.45))});
 var buf=await c.startRendering();
 var pk=0;for(var ch2=0;ch2<2;ch2++){var d=buf.getChannelData(ch2);for(var i2=0;i2<d.length;i2+=2){var a2=Math.abs(d[i2]);if(a2>pk)pk=a2}}var gain=pk>0?.89/pk:1;
 for(var ch3=0;ch3<2;ch3++){var d2=buf.getChannelData(ch3);for(var j=0;j<d2.length;j++)d2[j]*=gain}
 if(Object.keys(CACHE).length>600)CACHE={};
 var rms=function(x){var t=0,n=0;for(var i=0;i<x.length;i+=8){t+=x[i]*x[i];n++}return Math.sqrt(t/n)};
 return{buffer:buf,form:F,dur:bars*4*spb,sounds:keys.length,stems:{drums:rms(ST.drums),bass:rms(ST.bass),keys:rms(ST.keys),lead:rms(ST.lead)}}}
function wav(buf){var ch=buf.numberOfChannels,n=buf.length,ab=new ArrayBuffer(44+n*ch*2),v=new DataView(ab),w=function(o,s){for(var i=0;i<s.length;i++)v.setUint8(o+i,s.charCodeAt(i))};
 w(0,"RIFF");v.setUint32(4,36+n*ch*2,true);w(8,"WAVE");w(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,ch,true);v.setUint32(24,buf.sampleRate,true);v.setUint32(28,buf.sampleRate*ch*2,true);v.setUint16(32,ch*2,true);v.setUint16(34,16,true);w(36,"data");v.setUint32(40,n*ch*2,true);
 var D=[];for(var c=0;c<ch;c++)D.push(buf.getChannelData(c));var o=44;for(var i=0;i<n;i++)for(var c2=0;c2<ch;c2++){var s=Math.max(-1,Math.min(1,D[c2][i]));v.setInt16(o,s<0?s*32768:s*32767,true);o+=2}
 return new Blob([ab],{type:"audio/wav"})}
window.SNSBeat={STY:STY,recipe:recipe,render:render,wav:wav,keyName:keyName,form:form,chordName:function(r,d){var s=SC[r.scale],root=(r.key+s[d-1])%12,third=(s[(d+1)%7]-s[d-1]+12)%12;return NN[root]+(third==3?"m":"")}};
})();
/* ===== หน้าตา: การ์ด "AI ทำบีตให้" ในขั้น ② หาบีต ===== */
(function(){
"use strict";
var $=function(i){return document.getElementById(i)},B=window.SNSBeat,LK="sns:beatlab:list",cur=null,url=null,busy=false;
function esc(t){return String(t==null?"":t).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function J(k,d){try{var v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function JS(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function X(){return window.SNSWX||{}}
function mmss(s){s=Math.round(s);return Math.floor(s/60)+":"+("0"+s%60).slice(-2)}
function toast(m){try{window.toast?window.toast(m):0}catch(e){}}
function inputs(){var W=X().W||{},a=($("bl-a")||{}).value||"",sg=($("bl-s")||{}).value||"";return{artist:a.trim(),song:sg.trim(),moods:(W.mood||[]).slice(0,4),style:($("bl-g")||{}).value||"auto",len:+(($("bl-l")||{}).value||0)}}
function autoStyle(inp){var x=X();try{if(x.wGen){var g=x.wGen({artist:inp.artist+" "+inp.song,song:inp.song,mood:inp.moods.length?inp.moods:[]});if(B.STY[g])return g}}catch(e){}return"trap"}
async function aiRecipe(inp,style){var x=X();if(!x.ai||!(x.can?x.can():true))return null;
 var q="คุณเป็นโปรดิวเซอร์ฮิปฮอป/R&B มือหนึ่ง ช่วยวาง \"สูตรบีต\" ให้ฟีลคล้ายเพลง/ศิลปินที่ผู้ใช้อิน แต่เป็นบีตใหม่ ห้ามลอกทำนองหรือคอร์ดเฉพาะตัวของเพลงต้นฉบับ\n"+
  "ศิลปินที่อิน: "+(inp.artist||"-")+"\nเพลงที่อิน: "+(inp.song||"-")+"\nอารมณ์: "+(inp.moods.join(", ")||"-")+"\nแนวที่แอปเดา: "+style+"\n\n"+
  "ตอบเป็น JSON อย่างเดียว: {\"style\":\"trap|drill|rnb|lofi|rap|thai|emo|phonk|pop\",\"bpm\":60-170,\"key\":0-11 (C=0),\"scale\":\"minor|harm|phryg|dor|major\",\"prog\":[เลขดีกรี 1-7 จำนวน 4 ตัว],\"keys\":\"ep|pad|piano|pluck|strings|guitar\",\"lead\":\"bell|pluck|flute|piano|cowbell|guitar|vox|ep|strings\",\"swing\":0-0.2,\"why\":\"อธิบายสั้นๆ ภาษาไทยว่าบีตนี้คล้ายฟีลเพลงที่อินตรงไหน ไม่เกิน 20 คำ\"}\n"+
  "เลือกให้ตรงฟีลจริงของศิลปิน เช่น ความเร็ว ความมืด/สว่าง เครื่องดนตรีเด่น ถ้าไม่รู้จักเพลงให้เดาจากศิลปินและอารมณ์";
 try{var r=await x.ai(q);return r&&r.style?r:null}catch(e){return null}}
var AIC={};
async function make(reroll){if(busy)return;busy=true;var inp=inputs(),st=$("bl-st"),go=$("bl-go"),re=$("bl-re");go.disabled=re.disabled=true;
 try{var style=inp.style!="auto"?inp.style:autoStyle(inp),ak=[inp.artist,inp.song,inp.moods.join(","),inp.style].join("|"),air=AIC[ak];
  if(air===undefined&&(inp.artist||inp.song)){st.textContent="AI กำลังวางสูตรบีตให้คล้ายฟีลเพลงที่อิน…";air=AIC[ak]=await aiRecipe(inp,style)}
  var o={style:style,moods:inp.moods,len:inp.len||0};
  if(air){o.style=B.STY[air.style]?(inp.style!="auto"?inp.style:air.style):style;if(!reroll||Math.random()<.6){o.bpm=air.bpm;o.scale=air.scale;o.keys=air.keys;o.lead=air.lead;o.swing=air.swing}
   if(!reroll){o.key=air.key;o.prog=air.prog}o.why=air.why}
  if(reroll&&cur&&cur.r.style==o.style&&o.bpm==null)o.bpm=cur.r.bpm+Math.round((Math.random()-.5)*8);
  var r=B.recipe(o);r.ref=[inp.artist,inp.song].filter(Boolean).join(" – ");
  st.textContent="กำลังทำบีต "+B.STY[r.style].n+" · "+r.bpm+" BPM …";
  var out=await B.render(r,function(m){st.textContent=m});
  var blob=B.wav(out.buffer);if(url)try{URL.revokeObjectURL(url)}catch(e){}url=URL.createObjectURL(blob);cur={r:r,blob:blob,dur:out.dur,form:out.form};show();
  var L=J(LK,[]);L.unshift({r:r,t:Date.now()});JS(LK,L.slice(0,12));saved()}
 catch(e){st.textContent="ทำบีตไม่สำเร็จ: "+(e&&e.message||e)+" ลองกดใหม่อีกครั้ง"}
 busy=false;go.disabled=false;re.disabled=!cur}
function show(){var r=cur.r,st=$("bl-st"),o=$("bl-out");st.textContent="";
 o.innerHTML='<div class="sw-li" style="flex-direction:column;align-items:stretch;gap:8px"><div><b style="font-size:15px">'+esc(B.STY[r.style].n)+' · '+r.bpm+' BPM · '+esc(B.keyName(r))+' · '+mmss(cur.dur)+'</b>'+
  '<small>คอร์ด '+r.prog.map(function(d){return B.chordName(r,d)}).join(" – ")+' · โครง '+cur.form.map(function(f){return({intro:"อินโทร",hook:"ฮุค",verse:"เวิร์ส",bridge:"บริดจ์",outro:"เอาท์โทร"})[f.name]+" "+f.bars}).join(" › ")+' ห้อง'+(r.why?'<br>'+esc(r.why):'')+(r.ref?'<br>ฟีลจาก: '+esc(r.ref):'')+'</small></div>'+
  '<audio controls src="'+url+'" style="width:100%"></audio>'+
  '<div class="sw-acts" style="margin-top:0"><button class="sx-btn" id="bl-use">✎ ใช้บีตนี้แต่งเพลง</button><a class="sw-ghost" id="bl-dl" download="'+esc(("SNS beat "+B.STY[r.style].n+" "+r.bpm+"bpm "+B.keyName(r).split(" ")[0]).replace(/[\\/:*?"<>|#]/g,""))+'.wav" href="'+url+'">⬇ WAV</a></div></div>';
 $("bl-use").onclick=use}
async function use(){var x=X();if(!x.W||!x.IDB){toast("เปิดสมุดเนื้อเพลงไม่ได้ในหน้านี้");return}
 var W=x.W,n=W.note;if(!n){n=x.newNote({title:""})}var name="AI beat · "+B.STY[cur.r.style].n+" "+cur.r.bpm+"bpm";
 try{await x.IDB.put("beat:"+n.id,{blob:cur.blob,name:name})}catch(e){}
 n.beat={name:name,size:cur.blob.size,localOnly:true};n.bpm=cur.r.bpm;W.note=n;W.dirty=true;try{await x.save()}catch(e){}x.writer("pad");toast("ใส่บีตในสมุดแล้ว เปิดวนแล้วเขียนได้เลย")}
function saved(){var box=$("bl-saved");if(!box)return;var L=J(LK,[]);if(!L.length){box.innerHTML="";return}
 box.innerHTML='<details><summary class="sw-note" style="cursor:pointer">บีตที่ทำล่าสุด ('+L.length+') · กดเพื่อทำซ้ำ</summary><div class="sw-list">'+L.map(function(x,i){var r=x.r;return'<button class="sw-li" data-i="'+i+'" style="text-align:left;color:var(--sx-fg);font:inherit;cursor:pointer;width:100%"><div class="b"><b>'+esc(B.STY[r.style].n)+' · '+r.bpm+' BPM · '+esc(B.keyName(r))+'</b><small>'+esc(r.ref||"")+' · '+mmss(r.len)+'</small></div></button>'}).join("")+'</div></details>';
 box.querySelectorAll("[data-i]").forEach(function(b){b.onclick=async function(){if(busy)return;busy=true;var r=J(LK,[])[+b.dataset.i].r,st=$("bl-st");st.textContent="กำลังทำบีตเดิมซ้ำ…";
  try{var out=await B.render(r,function(m){st.textContent=m}),blob=B.wav(out.buffer);if(url)URL.revokeObjectURL(url);url=URL.createObjectURL(blob);cur={r:r,blob:blob,dur:out.dur,form:out.form};show()}catch(e){st.textContent="ทำไม่สำเร็จ"}busy=false;$("bl-re").disabled=false}})}
function mount(){var body=$("sw-body");if(!body||$("bl"))return;var x=X(),W=x.W||{},R0=W.beatRef||{},P=J("sns:wbeat",{}),ar=R0.artist!=null?R0.artist:(P.a||""),sg=R0.song!=null?R0.song:(P.s||"");
 var d=document.createElement("div");d.className="sw-box";d.id="bl";
 d.innerHTML='<h3>AI ทำบีตให้ <span class="sw-tag">ฟรี</span></h3><p class="sw-note">บอกศิลปินหรือเพลงที่อิน แอปทำบีตแนวคล้ายกันให้ ยาว 1:50–3:00 ตามอารมณ์ ทำนองแต่งใหม่ทุกครั้ง ไม่ลอกเพลงใคร กดสุ่มใหม่ได้เรื่อยๆ</p>'+
  '<div class="sw-row"><label><span class="sw-lab">ศิลปินที่อิน</span><input class="sw-in" id="bl-a" maxlength="60" placeholder="เช่น Central Cee, The Weeknd" value="'+esc(ar)+'"></label><label><span class="sw-lab">เพลงที่อิน</span><input class="sw-in" id="bl-s" maxlength="80" placeholder="เช่น Doja" value="'+esc(sg)+'"></label></div>'+
  '<div class="sw-row"><label><span class="sw-lab">แนว</span><select class="sw-in" id="bl-g"><option value="auto">ให้แอปเลือกจากศิลปิน/อารมณ์</option>'+Object.keys(B.STY).map(function(k){return'<option value="'+k+'">'+B.STY[k].n+'</option>'}).join("")+'</select></label>'+
  '<label><span class="sw-lab">ความยาว</span><select class="sw-in" id="bl-l"><option value="0">อัตโนมัติตามอารมณ์</option><option value="110">1:50</option><option value="135">2:15</option><option value="150">2:30</option><option value="165">2:45</option><option value="180">3:00</option></select></label></div>'+
  '<p class="sw-note">อารมณ์ใช้ตามที่เลือกใน ① หาแรงบันดาลใจ'+((W.mood||[]).length?': <b style="color:var(--sx-fg)">'+esc(W.mood.join(", "))+'</b>':'')+'</p>'+
  '<div class="sw-acts"><button class="sx-btn" id="bl-go">♪ ทำบีต</button><button class="sw-ghost" id="bl-re" disabled>↻ สุ่มใหม่</button></div>'+
  '<p class="sw-note" id="bl-st" aria-live="polite"></p><div id="bl-out"></div><div id="bl-saved" style="margin-top:8px"></div>'+
  '<p class="sw-note" style="font-size:12px">เสียงทั้งหมดสังเคราะห์ในเครื่อง (ไม่ใช้แซมเปิลของใคร) ใช้ทำเพลงปล่อยได้ · ถ้าอยากได้เสียงอัดจริงระดับสตูดิโอ ต้องใช้บริการ AI ทำเพลงแบบเสียเงิน (ยังไม่เปิดใช้)</p>';
 body.insertBefore(d,body.firstChild);
 $("bl-go").onclick=function(){make(false)};$("bl-re").onclick=function(){make(true)};
 ["bl-a","bl-s"].forEach(function(id){$(id).addEventListener("change",function(){var P2=J("sns:wbeat",{});P2[id=="bl-a"?"a":"s"]=$(id).value.trim();JS("sns:wbeat",P2)})});
 if(cur){show();$("bl-re").disabled=false}saved()}
B.mount=mount;
})();
