#!/usr/bin/env python3
"""ซิงค์เนื้อเพลงอัตโนมัติ (ฟังเสียงร้อง -> จับเวลาทุกบรรทัด -> สร้างหน้า lyric video ที่ซิงค์แล้ว)

ติดตั้งครั้งเดียว:   pip install faster-whisper
ใช้งาน:            python align.py 10747.mp4 bedupbiw-lyric.html
ถ้าบีตกลบเสียงร้อง:  pip install demucs   แล้วเพิ่ม --separate
ถ้าเครื่องช้า:       เพิ่ม --model small   (แม่นสุด: --model large-v3)
ผลลัพธ์:           bedupbiw-lyric-synced.html  และ timings.json
"""
import sys, re, json, argparse, subprocess, difflib, unicodedata, bisect, pathlib


def keep(c):
    return c.isalnum() or unicodedata.category(c).startswith("M")


def load_lines(html):
    raw = json.loads(re.search(r'RAW=("(?:[^"\\]|\\.)*")', html).group(1))
    out = []
    for g in raw.split("\n\n"):
        while True:                      # ตัดเครื่องหมาย § และ @2 หน้าท่อนออก
            m = re.match(r"(§|@[1-4])[ \t]*", g)
            if not m: break
            g = g[m.end():]
        out += [l for l in g.split("\n") if l.strip()]
    return out


def lcs_pairs(a, b):
    import array
    n, m = len(a), len(b)
    W = m + 1
    D = array.array("H", bytes(2 * (n + 1) * W))
    for i in range(1, n + 1):
        ai = a[i - 1]; row = i * W; prev = (i - 1) * W
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                D[row + j] = D[prev + j - 1] + 1
            else:
                x = D[prev + j]; y = D[row + j - 1]
                D[row + j] = x if x >= y else y
    i, j, P = n, m, []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            P.append((i - 1, j - 1)); i -= 1; j -= 1
        elif D[(i - 1) * W + j] >= D[i * W + j - 1]:
            i -= 1
        else:
            j -= 1
    return P[::-1]


def run_pairs(a, b, op=1, cont=5):
    """จับคู่รักษาลำดับ ให้คะแนนตัวที่ตรงต่อเนื่องสูงกว่าตัวที่ตรงกระจาย (กันพยางค์ซ้ำในท่อนอื่นมาแย่ง)"""
    import array
    n, m = len(a), len(b)
    W = m + 1
    M = array.array("i", [-1]) * ((n + 1) * W)      # จบด้วยการตรงที่ (i,j)
    X = array.array("i", bytes(4 * (n + 1) * W))     # ดีที่สุดถึง (i,j)
    for i in range(1, n + 1):
        ai = a[i - 1]; row = i * W; prev = (i - 1) * W
        for j in range(1, m + 1):
            best = X[prev + j]
            y = X[row + j - 1]
            if y > best: best = y
            if ai == b[j - 1]:
                pm = M[prev + j - 1]
                v = pm + cont if pm >= 0 else -1
                w = X[prev + j - 1] + op
                mm = v if v > w else w
                M[row + j] = mm
                if mm > best: best = mm
            X[row + j] = best
    i, j, P, inm = n, m, [], False
    while i > 0 and j > 0:
        row = i * W; prev = (i - 1) * W
        if not inm:
            if X[row + j] == X[prev + j]: i -= 1; continue
            if X[row + j] == X[row + j - 1]: j -= 1; continue
            inm = True
        P.append((i - 1, j - 1))
        pm = M[prev + j - 1]
        inm = pm >= 0 and M[row + j] == pm + cont
        i -= 1; j -= 1
    return P[::-1]


def align(lines, words):
    """words = [(text, start, end)] -> (starts, ends, ratio, conf) conf = ความมั่นใจ 0-1 ต่อบรรทัด"""
    lc, li = [], []
    for i, l in enumerate(lines):
        for c in l.lower():
            if keep(c):
                lc.append(c); li.append(i)
    tc, tt = [], []
    for w, s, e in words:
        cs = [c for c in w.lower() if keep(c)]
        for k, c in enumerate(cs):
            tc.append(c); tt.append(s + (e - s) * (k + .5) / len(cs))
    pairs = run_pairs(lc, tc)                         # จับคู่แบบรักษาลำดับทั้งเพลง (ท่อนฮุคซ้ำจะไม่ไปจับผิดท่อน)
    if not pairs:
        sys.exit("จับคำที่ตรงกับเนื้อเพลงไม่ได้เลย ลองใส่ --separate หรือ --model ที่ใหญ่ขึ้น")
    runs, cur = [], [pairs[0]]                       # เก็บเฉพาะช่วงที่ตรงติดกัน >= 3 ตัว ตัดตัวที่บังเอิญตรง
    for p in pairs[1:]:
        if p[0] == cur[-1][0] + 1 and p[1] == cur[-1][1] + 1: cur.append(p)
        else: runs.append(cur); cur = [p]
    runs.append(cur)
    kept = [p for r in runs if len(r) >= 3 for p in r]
    if len(kept) < 5: kept = pairs
    ratio = len(kept) / max(1, len(lc))
    xs = [p[0] for p in kept]; ys = [p[1] for p in kept]

    def tpos(a):
        j = bisect.bisect_left(xs, a)
        if j < len(xs) and xs[j] == a: return ys[j]
        if j == 0: return ys[0]
        if j == len(xs): return ys[-1]
        x0, x1, y0, y1 = xs[j-1], xs[j], ys[j-1], ys[j]
        return y0 + (y1 - y0) * (a - x0) / (x1 - x0)

    def tm(p):
        p = min(max(p, 0), len(tt) - 1); f = int(p)
        return tt[f] if f + 1 >= len(tt) else tt[f] + (tt[f+1] - tt[f]) * (p - f)

    first, last = {}, {}
    for a, i in enumerate(li):
        first.setdefault(i, a); last[i] = a
    n = len(lines)
    S = [tm(tpos(first[i])) - .1 for i in range(n)]
    E = [tm(tpos(last[i])) + .3 for i in range(n)]
    S0 = S[:]
    # บรรทัดที่จับได้บางส่วน: นับย้อนจากพยางค์แรกที่จับได้ตามจังหวะร้องจริง แทนการเดาข้ามช่วงยาว
    gaps = sorted(tt[k + 1] - tt[k] for k in range(len(tt) - 1) if 0 < tt[k + 1] - tt[k] < .5)
    rate = gaps[len(gaps) // 2] if gaps else .12
    kin = {}
    for a, b in kept:
        kin.setdefault(li[a], []).append((a, b))
    nch = {}
    for i in li: nch[i] = nch.get(i, 0) + 1
    kin = {i: ab for i, ab in kin.items() if len(ab) >= max(6, .4 * nch[i])}   # ใช้เป็นหมุดเฉพาะบรรทัดที่จับได้ชัด
    for i, ab in kin.items():
        a0, b0 = ab[0]; a1, b1 = ab[-1]
        S[i] = tt[b0] - (a0 - first[i]) * rate - .1
        E[i] = tt[b1] + (last[i] - a1) * rate + .3
    # บรรทัดที่ไม่มีคำจับได้: กระจายระหว่างบรรทัดที่จับได้ตามความยาวเนื้อ (ไม่ไปดันบรรทัดที่จับได้)
    anc = sorted(kin)
    if anc:
        L = [last[i] - first[i] + 1 for i in range(n)]
        for k in range(len(anc) + 1):
            p_ = anc[k - 1] if k > 0 else None
            q_ = anc[k] if k < len(anc) else None
            lo = p_ + 1 if p_ is not None else 0
            hi = q_ if q_ is not None else n
            if hi <= lo: continue
            seg = S0[lo:hi]
            okint = all(seg[k + 1] > seg[k] + .1 for k in range(len(seg) - 1))
            if p_ is not None: okint = okint and seg[0] > S[p_] + .1
            if q_ is not None: okint = okint and seg[-1] < S[q_] - .1
            if okint and (p_ is not None or q_ is not None) and len(tt) > 2 * len(lc) * .2:
                S[lo:hi] = seg; continue                  # มีคำในช่วงนั้นจริง: ใช้เวลาจากคำที่ได้ยิน
            if p_ is not None and q_ is not None:
                t0, t1 = E[p_], S[q_]
                tot = sum(L[lo:hi]) or 1
                if t1 - t0 < .3 * (hi - lo): t0 = t1 - .3 * (hi - lo)
                acc = 0
                for i in range(lo, hi):
                    S[i] = t0 + (t1 - t0) * acc / tot; acc += L[i]
            elif q_ is not None:                       # ก่อนบรรทัดแรกที่จับได้: นับย้อนตามจังหวะร้อง
                t1 = S[q_]; need = sum(L[i] * rate * 1.6 + .4 for i in range(lo, hi))
                t0 = max(0.0, t1 - need); tot = sum(L[lo:hi]) or 1; acc = 0
                for i in range(lo, hi):
                    S[i] = t0 + (t1 - .3 - t0) * acc / tot; acc += L[i]
            else:                                     # หลังบรรทัดสุดท้ายที่จับได้
                t = E[p_]
                for i in range(lo, hi):
                    S[i] = t; t += L[i] * rate * 1.6 + .4
    for i in range(1, n):
        if S[i] < S[i-1] + .15 and i not in kin: S[i] = S[i-1] + .15
    for i in range(n):
        E[i] = max(E[i], S[i] + .8)
        if i + 1 < n: E[i] = max(S[i] + .2, min(E[i], S[i+1] - .05))
    cnt, nc = [0] * n, [0] * n
    for i in li: nc[i] += 1
    for a in xs: cnt[li[a]] += 1
    conf = [min(1.0, cnt[i] / nc[i]) if nc[i] else 0.0 for i in range(n)]
    return S, E, ratio, conf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("html")
    ap.add_argument("--model", default="medium")
    ap.add_argument("--separate", action="store_true")
    ap.add_argument("--out", default="bedupbiw-lyric-synced.html")
    a = ap.parse_args()
    html = pathlib.Path(a.html).read_text(encoding="utf-8")
    lines = load_lines(html)
    audio = a.audio
    if a.separate:
        print("แยกเสียงร้องออกจากบีต (ช้าหน่อย)...")
        subprocess.run([sys.executable, "-m", "demucs", "--two-stems", "vocals", "-o", "sep", a.audio], check=True)
        audio = str(max(pathlib.Path("sep").glob("*/*/vocals.wav"), key=lambda p: p.stat().st_mtime))
    from faster_whisper import WhisperModel
    print("ฟังเสียงร้อง (ครั้งแรกจะโหลดโมเดลก่อน)...")
    model = WhisperModel(a.model, device="auto", compute_type="int8")
    segs, _ = model.transcribe(audio, language="th", word_timestamps=True, beam_size=5,
                               condition_on_previous_text=False, initial_prompt=" ".join(lines)[:600])
    words = [(w.word, w.start, w.end) for s in segs for w in s.words]
    print("ถอดเสียงได้", len(words), "คำ")
    S, E, ratio, conf = align(lines, words)
    print("จับคู่กับเนื้อได้ %.0f%%" % (ratio * 100))
    if ratio < .3:
        print("!! ต่ำมาก ผลอาจเหลื่อม ลองใส่ --separate หรือ --model large-v3")
    S = [round(x, 2) for x in S]; E = [round(x, 2) for x in E]
    pathlib.Path("timings.json").write_text(json.dumps({"starts": S, "ends": E, "conf": [round(c, 2) for c in conf], "lines": lines}, ensure_ascii=False, indent=1), encoding="utf-8")
    old = "var T=EST.slice(),E=null,off=0,synced=false,"
    if old not in html:
        sys.exit("ใช้ไฟล์ bedupbiw-lyric.html เวอร์ชันล่าสุดที่ผมส่งให้ (หาจุดฝังเวลาไม่เจอ)")
    html = html.replace(old, "var T=%s,E=%s,off=0,synced=true," % (json.dumps(S), json.dumps(E))).replace('"bw3"', '"bw3auto"')
    pathlib.Path(a.out).write_text(html, encoding="utf-8")
    print("เสร็จ ->", a.out, "(เปิดด้วย Chrome แล้วกด เล่น)")


if __name__ == "__main__":
    main()
