# สร้าง index.html (PWA) และไฟล์ซิงค์ฝังเวลา จาก /tmp/w/new.html
import json,os,sys
def rep(s,o,n):
    assert s.count(o)==1,(s.count(o),o[:60]); return s.replace(o,n)
out=sys.argv[1]; key=sys.argv[2] if len(sys.argv)>2 else 'bw3s57l'
b=open('/tmp/w/audio.b64').read().strip()
s=open('/tmp/w/new.html',encoding='utf-8').read().replace('__AUDIO__',b)
BOOT=open('/tmp/w/shell_boot.js',encoding='utf-8').read();SCSS=open('/tmp/w/shell.css',encoding='utf-8').read();SJS=open('/tmp/w/shell.js',encoding='utf-8').read()
s=rep(s,'<title>Slope North Side</title>','<title>Slope North Side</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<script>'+BOOT+'</script>')
s=rep(s,'</head>','<style>'+SCSS+'</style></head>')
s=rep(s,'</script>\n</body>','</script>\n<script>'+SJS+'</script>\n</body>')
M='<link rel="manifest" href="manifest.json"><meta name="theme-color" content="#050305"><link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="icon-192.png">\n'
W='<script>if("serviceWorker" in navigator)navigator.serviceWorker.register("sw.js").catch(function(){})</script>\n'
app=rep(s,'</style>\n','</style>\n'+M); app=rep(app,'</script>\n</body>','</script>\n'+W+'</body>')
sw=open('/home/claude/app/sw.js').read().replace('__V__',os.environ.get('SWV','bw-v28'))
for x in ('pc','space'):
    os.makedirs(out+'/'+x,exist_ok=True)
    open(out+'/'+x+'/index.html','w',encoding='utf-8').write(app); open(out+'/'+x+'/sw.js','w').write(sw)
f=json.load(open(os.environ.get('FUSED','/tmp/w/al/fused.json')))
z=rep(s,'var T=EST.slice(),E=null,off=0,synced=false,','var T=SNS.baked?%s:EST.slice(),E=SNS.baked?%s:null,off=0,synced=!!SNS.baked,'%(json.dumps(f['S']),json.dumps(f['E'])))
z=rep(z,'var VSEG=null,SYL=null,UT=null,WTC={},CONF=null,VER=[]','var VSEG=SNS.baked?%s:null,SYL=SNS.baked?%s:null,UT=SNS.baked?%s:null,WTC={},CONF=SNS.baked?%s:null,VER=[]'%(json.dumps(f.get('Q')),json.dumps(f.get('Y')),json.dumps(f.get('U'),ensure_ascii=False),json.dumps(f['C'])))
z=rep(z,'localStorage.getItem("bw3")','localStorage.getItem("%s")'%key)
z=rep(z,'localStorage.setItem("bw3",','localStorage.setItem("%s",'%key)
os.makedirs(out+'/synced',exist_ok=True)
open(out+'/synced/slope-north-side-synced.html','w',encoding='utf-8').write(z)
print('built',out)
# เวอร์ชันเว็บถาวร (Artifact) — ใช้ลิงก์เดิมตลอด ดาวน์โหลดไฟล์ผ่านระบบของ claude.ai
SHIM='''<script>(function(){var D=null;try{if(window.claude&&claude.use)claude.use("downloads").then(function(d){D=d}).catch(function(){})}catch(e){}
var oc=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){var a=this;if(D&&a.download&&/^(blob:|data:)/.test(a.href)){var fn=a.download;if(/\\.wav$/i.test(fn)){try{toast("ไฟล์ WAV ดาวน์โหลดได้ในแอปบนคอม (localhost) เท่านั้น")}catch(e){}return}fetch(a.href).then(function(r){return r.blob()}).then(function(b){return D.save({filename:fn,data:b})}).catch(function(e){if(e&&e.code&&e.code!="declined")try{toast("บันทึกไฟล์ไม่ได้: "+(e.message||e.code))}catch(x){}});return}return oc.call(this)}})()</script>
'''
art=rep(z,'</script>\n</body>','</script>\n'+SHIM+'</body>')
os.makedirs(out+'/artifact',exist_ok=True)
open(out+'/artifact/slope-north-side.html','w',encoding='utf-8').write(art)
print('artifact ok')
# ไฟล์ต้นทางของลิงก์ถาวร https://claude.ai/artifact/8AxN6jBbSnhs5148EB2CeK — ต้อง publish จาก path นี้เสมอ
FIX='/mnt/user-data/outputs/fresh37/artifact/slope-north-side.html'
if out.rstrip('/')!='/mnt/user-data/outputs/fresh37':
    open(FIX,'w',encoding='utf-8').write(art); print('artifact ->',FIX)
