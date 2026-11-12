import json,sys,collections,re
R=json.load(open(sys.argv[1]));S=R['S'];T,E,N=S['T'],S['E'],S['N'];fr=R['out'];W=1080
issues=collections.OrderedDict()
# 1 missing words
miss=[]
for j in range(N):
    words=set(w['tx'].strip().upper() for w in S['ws'][j] if not w['ad'] and w['tx'].strip())
    seen=set()
    for f in fr:
        if T[j]-.01<=f['t']<=(E[j] if E and E[j] is not None else T[j]+3)+1.5:
            for q in f['r']:
                if q['a']>.3: seen.add(q['t'].strip().upper())
    if words-seen: miss.append((j,sorted(words-seen)[:3]))
issues['missing words']=miss
# 2 overflow
issues['overflow']=sorted(set((round(f['t']),q['t'][:10]) for f in fr for q in f['r'] if q['a']>.3 and (q['x0']<W*.03 or q['x1']>W*.97) and len(q['t'])<30))[:10]
# 3 jitter: lyric word moves >3px between frames, not within .4s after a line start
def trans(t): return any(-0.05<=t-x<0.4 for x in T)
mv=collections.Counter()
lyr=set(w['tx'].strip() for j in range(N) for w in S['ws'][j])
for a,b in zip(fr,fr[1:]):
    if trans(b['t']): continue
    def M(f):
        d={}
        for q in f['r']:
            if q['a']>.5 and q['t'].strip() in lyr: d.setdefault(q['t'],[]).append(q)
        return d
    A=M(a);B=M(b)
    for k in A:
        if k in B and len(A[k])==len(B[k]):
            for qa,qb in zip(sorted(A[k],key=lambda q:(q['y'],q['x0'])),sorted(B[k],key=lambda q:(q['y'],q['x0']))):
                if max(abs(qa['x0']-qb['x0']),abs(qa['y']-qb['y']),abs(qa['x1']-qa['x0']-(qb['x1']-qb['x0'])))>3: mv[round(b['t'])]+=1
issues['shaking (seconds)']=[k for k,v in mv.items() if v>=3]
# 4 labels shown
lab=re.compile(r'^\s*[\(\[]\s*(rap|hook|chorus|v\.?\s*\d|verse|intro|outro|bridge)',re.I)
issues['label lines']=[S['LN'][j]['t'] for j in range(N) if lab.search(S['LN'][j]['t'])]
# 5 live stale flash: a line index reappears after being gone >1s
gone={};fl=[]
prev=set()
for s in R['live']:
    v=set(s['vis'])
    for i in v-prev:
        if i in gone and s['t']-gone[i]>1.0: fl.append((s['t'],int(i)))
    for i in prev-v: gone[i]=s['t']
    prev=v
issues['live stale flashes']=fl[:10]
# 6 live line count toggles per second
tg=0
for a,b in zip(R['live'],R['live'][1:]):
    if set(a['vis'])!=set(b['vis']) and len(a['vis'])==len(b['vis'])==0: pass
c=collections.Counter()
for a,b in zip(R['live'],R['live'][1:]):
    if set(a['vis'])!=set(b['vis']): c[int(b['t'])]+=1
issues['live flicker (secs with >3 changes)']=[k for k,v in c.items() if v>3]
issues['page errors']=R['errs'][:3]
bad=sum(1 for v in issues.values() if v)
print(('PASS' if not bad else 'FAIL'),sys.argv[1].split('/')[-1],json.dumps(issues,ensure_ascii=False))
