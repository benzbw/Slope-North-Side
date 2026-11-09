# สร้างหน้าแต่งเพลงสำหรับเว็บ GitHub จากตัวเดียวกับ claude.ai (มีบรีฟเพลง ฯลฯ ครบ) + AI ฟรี (Puter) + รับเพลงจาก claude.ai (#import=)
# ใช้: python3 make_web_write.py <write-artifact.html> <out write.html>
import os, sys
src, out = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()
D = os.path.dirname(os.path.abspath(__file__))
FA = open(os.path.join(D, '..', 'freeai.js'), encoding='utf-8').read()
def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
if 'SNSFreeAI={' not in s:
    i = s.index('<script>(function(){\n"use strict";'); s = s[:i] + '<script>' + FA + '</script>\n' + s[i:]
    R('var t=(location.hash||"").replace("#","");', 'if(!ST.sample&&window.SNSFreeAI)ST.sample=SNSFreeAI.sample;document.addEventListener("sns:freeai",function(){if(document.getElementById("sw-slang")&&window.slangUI)slangUI()});var t=(location.hash||"").replace("#","");')
if 'var IM=/^#import=' not in s:
    R('try{Ss=JSON.parse(localStorage.getItem("sns:wsess")||"null")}catch(e){}', 'try{Ss=JSON.parse(localStorage.getItem("sns:wsess")||"null")}catch(e){}\n var IM=/^#import=([\\w-]+)/.exec(location.hash||"");if(IM){try{var o=JSON.parse(decodeURIComponent(escape(atob(IM[1].replace(/-/g,"+").replace(/_/g,"/")))));var L0=[];try{L0=await Notes.list()}catch(e){}\n  var nn=L0.filter(function(x){return o.t&&x.title==o.t})[0]||newNote({title:o.t||""});if(o.b)nn.body=o.b;if(o.l)nn.link=o.l;if(o.bpm)nn.bpm=o.bpm;if(o.br)nn.brief=o.br;if(o.bp)nn.beatPick=o.bp;W.note=nn;W.dirty=true;try{await wSaveNow()}catch(e){}t="pad";Ss=null;try{history.replaceState(null,"","#pad")}catch(e){}}catch(e){}}')
open(out, 'w', encoding='utf-8').write(s); print('web write ok', len(s))
