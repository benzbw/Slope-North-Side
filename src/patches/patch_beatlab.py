# ใส่ Beat Lab (AI ทำบีต) ในหน้าแต่งเพลง · ใช้: python3 patch_beatlab.py <write.html>
import os, sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
BF = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'beatfind.js'), encoding='utf-8').read()
SNAP = os.environ.get('BEATS_SNAPSHOT')
if SNAP and os.path.isfile(SNAP): BF = 'window.SNS_BEATS=' + open(SNAP, encoding='utf-8').read().strip() + ';\n' + BF
BL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'beatlab.js'), encoding='utf-8').read()
def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
if 'window.SNSBeat=' in s:
    i = s.index('/* ===== Slope North Side · Beat Lab'); a = s.rfind('<script>', 0, i); b = s.index('</script>', s.index('B.mount=mount;')) + 9
    s = s[:a] + '<script>' + BL + '</script>' + s[b:]
else:
    R('function beatTab(){', 'function beatTab(){setTimeout(function(){window.SNSBeat&&SNSBeat.mount&&SNSBeat.mount();window.SNSBeatFind&&SNSBeatFind.hook()},0);')
    a = 'var t=(location.hash||"").replace("#","");writer(t=="beat"'
    R(a, 'window.SNSWX={W:W,IDB:IDB,save:wSaveNow,writer:writer,newNote:newNote,wGen:wGen,ST:ST,can:function(){return!!ST.sample&&(!window.SNSFreeAI||ST.sample!==SNSFreeAI.sample||SNSFreeAI.signedIn())},ai:function(q){return aiJSON(q)}};' + a)
    i = s.rindex('</body>'); s = s[:i] + '<script>' + BL + '</script>\n' + s[i:]
if '/* ===== Slope North Side · บีตจริงจาก YouTube' in s:
    i = s.index('/* ===== Slope North Side · บีตจริงจาก YouTube'); a = s.rfind('<script>', 0, i); b = s.index('</script>', i) + 9
    a2 = s.rfind('<script>', 0, a-1) if 'window.SNS_BEATS=' in s[a:i] else a
    s = s[:a] + '<script>' + BF + '</script>' + s[b:]
else:
    i = s.rindex('</body>'); s = s[:i] + '<script>' + BF + '</script>\n' + s[i:]
if 'savedList:function' not in s:
    s = s.replace('window.SNSWX={W:W,', 'window.SNSWX={savedList:function(){try{savedList()}catch(e){}},W:W,', 1)
if 'SNSBeatFind.hook()' not in s:
    s = s.replace('window.SNSBeat&&SNSBeat.mount&&SNSBeat.mount()},0);', 'window.SNSBeat&&SNSBeat.mount&&SNSBeat.mount();window.SNSBeatFind&&SNSBeatFind.hook()},0);', 1)
open(p, 'w', encoding='utf-8').write(s); print('beatlab ok')
