# เว็บแอปสาธารณะ (GitHub Pages) — ไม่ฝังไฟล์เพลง, ติดตั้งเป็นแอปได้ (PWA)
import re,os,sys,shutil,json
src=sys.argv[1]; out=sys.argv[2]; swv=sys.argv[3] if len(sys.argv)>3 else 'web-v1'
z=open(src+'/synced/slope-north-side-synced.html',encoding='utf-8').read()
z,n=re.subn(r'window\.SNS_AUDIO="data:audio/mpeg;base64,[^"]*"','window.SNS_AUDIO="data:audio/mpeg;base64,"',z); assert n==1
M='<link rel="manifest" href="manifest.json"><meta name="theme-color" content="#050305"><link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="icon-192.png"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Slope North Side">\n'
W='<script>if("serviceWorker" in navigator)navigator.serviceWorker.register("sw.js").catch(function(){})</script>\n'
assert z.count('</head>')==1 and z.count('</script>\n</body>')==1
z=z.replace('</head>',M+'</head>').replace('</script>\n</body>','</script>\n'+W+'</body>')
os.makedirs(out,exist_ok=True)
open(out+'/index.html','w',encoding='utf-8').write(z)
open(out+'/sw.js','w').write(open('/home/claude/app/sw.js').read().replace('__V__',swv))
m=json.load(open('/home/claude/app/manifest.json')); m.update({"name":"Slope North Side","short_name":"Slope North Side","description":"สตูดิโอทำวิดีโอเนื้อเพลง ปก มิกซ์ และปล่อยเพลง","id":"./","lang":"th"})
json.dump(m,open(out+'/manifest.json','w'),ensure_ascii=False)
for f in ('icon-192.png','icon-512.png'): shutil.copy('/home/claude/app/'+f,out+'/'+f)
open(out+'/.nojekyll','w').write('')
WR=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','write.html')
if os.path.exists(WR): shutil.copy(WR,out+'/write.html')  # หน้าแต่งเพลง & หาบีต (ในแอปเดียวกัน)
print('web ok',len(z))
