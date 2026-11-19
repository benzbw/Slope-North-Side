"""Map Whisper char stream (with times) onto lyric words by consonant-skeleton alignment.
usage: python3 walign.py project.json result.json  -> prints per-line proposal"""
import json, sys, re

TH_CONS = set(chr(c) for c in range(0x0E01, 0x0E2F))
TH_VOW = set('ะาำิีึืุูเแโใไๅ')


def skel(s):
    out = []
    for ch in s.lower():
        if ch in TH_CONS or ch in TH_VOW or ch.isascii() and ch.isalnum():
            out.append(ch)
    return out


EQ = [set('ขคฆ'), set('ทธฑฒถฐ'), set('สศษซ'), set('พภผ'), set('ฟฝ'), set('ตฏ'), set('ดฎ'), set('ชฌฉ'), set('นณ'), set('ลฬร'), set('ยญ'), set('ฮห'), set('ใไ'), set('aeiou')]


def sim(a, b):
    if a == b: return 2
    for g in EQ:
        if a in g and b in g: return 1
    return -1


def align(A, B):
    """global-local: A lyric chars, B whisper chars; return map iA->iB"""
    n, m = len(A), len(B)
    G = -1
    import numpy as np
    S = np.zeros((n + 1, m + 1), dtype=np.int32)
    P = np.zeros((n + 1, m + 1), dtype=np.int8)
    for i in range(1, n + 1): S[i, 0] = S[i - 1, 0] + G; P[i, 0] = 1
    for j in range(1, m + 1): S[0, j] = 0; P[0, j] = 2  # free leading whisper junk
    for i in range(1, n + 1):
        a = A[i - 1]
        for j in range(1, m + 1):
            d = S[i - 1, j - 1] + sim(a, B[j - 1]); u = S[i - 1, j] + G; l = S[i, j - 1] + G
            if d >= u and d >= l: S[i, j] = d; P[i, j] = 0
            elif u >= l: S[i, j] = u; P[i, j] = 1
            else: S[i, j] = l; P[i, j] = 2
    j = int(S[n].argmax()); i = n; mp = {}
    while i > 0 and j > 0:
        p = P[i, j]
        if p == 0:
            if sim(A[i - 1], B[j - 1]) > 0: mp[i - 1] = j - 1
            i -= 1; j -= 1
        elif p == 1: i -= 1
        else: j -= 1
    return mp


def main():
    d = json.load(open(sys.argv[1])); st = d['state']; b = json.loads(st['bw3s57l'])
    r = json.load(open(sys.argv[2])); ww = r['whisper']
    B = []; BT = []
    for w, s, e, p in ww:
        cs = skel(w)
        for k, ch in enumerate(cs):
            B.append(ch); BT.append(s + (e - s) * k / max(1, len(cs)))
    A = []; AW = []
    for j, line in enumerate(b['U']):
        for wi, w in enumerate(line):
            for ch in skel(w[1]): A.append(ch); AW.append((j, wi))
    mp = align(A, B)
    first = {}
    for ia, ib in mp.items():
        k = AW[ia]
        first.setdefault(k, []).append(BT[ib])
    out = []
    for j, line in enumerate(b['U']):
        row = []
        for wi, w in enumerate(line):
            ts = first.get((j, wi))
            row.append((w[1], w[2], round(min(ts), 2) if ts else None, len(ts or []), len(skel(w[1]))))
        out.append(row)
    json.dump(out, open('walign.json', 'w'), ensure_ascii=False)
    for j, row in enumerate(out):
        hit = sum(1 for x in row if x[2] is not None)
        dif = [round(x[2] - x[1], 2) for x in row if x[2] is not None]
        print(j, f"hit {hit}/{len(row)}", 'dt', dif[:12])


if __name__ == '__main__':
    main()
