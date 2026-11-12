const {chromium}=require('playwright');const http=require('http'),fs=require('fs'),path=require('path');const ROOT=process.env.ROOT;
const file=process.argv[2],name=process.argv[3],out=process.argv[4];
const srv=http.createServer((q,r)=>{let f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));if(f.endsWith('/'))f+='index.html';if(!fs.existsSync(f)){r.writeHead(404);return r.end()}r.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html; charset=utf-8':f.endsWith('.js')?'text/javascript':'application/octet-stream'});fs.createReadStream(f).pipe(r)}).listen(0,async()=>{
const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.addInitScript(()=>{try{localStorage.setItem('sns:tsz','1.19')}catch(e){}});
await p.goto('http://127.0.0.1:'+srv.address().port+'/');await p.waitForTimeout(1500);
if(await p.isVisible('#sx-id')){await p.fill('#sx-id','ci-tester');await p.fill('#sx-pw','ci-pass-123');if(await p.isVisible('#sx-pw2'))await p.fill('#sx-pw2','ci-pass-123');await p.click('#sx-lgo');await p.waitForTimeout(1500)}
const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('#sx-imp')]);await fc.setFiles(file);
for(let i=0;i<120;i++){await p.waitForTimeout(500);if(await p.$(`.sx-card[aria-label="เปิด ${name}"]`))break}
await p.click(`.sx-card[aria-label="เปิด ${name}"]`);await p.waitForTimeout(6000);
let F=null;for(const fr of p.frames()){try{if(await fr.evaluate(()=>!!window.__df)){F=fr;break}}catch(e){}}
const W=1080,H=1920;
const res=await F.evaluate(async([W,H])=>{const S=window.__ln();const c=document.createElement('canvas');c.width=W;c.height=H;const x=c.getContext('2d');let rec=[];
 const of=x.fillText.bind(x);x.fillText=function(t,X,Y){try{const w=x.measureText(t).width,al=x.textAlign;let x0=al=='center'?X-w/2:al=='right'||al=='end'?X-w:X;const m=x.getTransform();const p0=[m.a*x0+m.c*Y+m.e,m.b*x0+m.d*Y+m.f],p1=[m.a*(x0+w)+m.c*Y+m.e];rec.push({t:String(t),a:+x.globalAlpha.toFixed(2),x0:Math.round(Math.min(p0[0],p1[0])),x1:Math.round(Math.max(p0[0],p1[0])),y:Math.round(p0[1]),sz:parseFloat((x.font.match(/([\d.]+)px/)||[0,0])[1])})}catch(e){}return of(t,X,Y)};
 const outF=[];const D=S.D;for(let t=0;t<D;t+=1/30){rec=[];window.__df(c,W,H,t);outF.push({t:+t.toFixed(3),r:rec.filter(q=>q.a>0.05)})}
 return {S:{T:S.T,E:S.E,N:S.N,LN:S.LN.map(l=>({t:l.t,g:l.g})),ws:S.LN.map((l,j)=>S.ws(j)),D:S.D,FIXED:S.FIXED},out:outF}},[W,H]);
// live: play, sample visible lines every 100ms
await F.evaluate(()=>window.__go());await p.waitForTimeout(800);
await F.evaluate(()=>{const a=document.querySelector('audio');a.muted=true;a.playbackRate=2;a.currentTime=0;return a.play().catch(e=>String(e))});
const live=[];const dur=await F.evaluate(()=>document.querySelector('audio').duration);
for(let k=0;k<Math.min(900,dur*5+10);k++){await p.waitForTimeout(100);const s=await F.evaluate(()=>{const a=document.querySelector('audio');return {t:+a.currentTime.toFixed(2),vis:[...document.querySelectorAll('#stage .l')].filter(e=>e.style.display!='none'&&e.offsetParent).map(e=>e.dataset.i)}});live.push(s);if(s.t>=dur-0.2)break}
res.live=live;res.errs=errs;fs.writeFileSync(out,JSON.stringify(res));console.log('ok',name,res.out.length,'live',live.length,'errs',errs.length);await b.close();srv.close()})
