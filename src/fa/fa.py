# -*- coding: utf-8 -*-
"""จับเวลาเนื้อแบบบังคับ (forced alignment): รู้เนื้ออยู่แล้ว ให้โมเดลหาว่าแต่ละตัวอักษรร้องตอนไหน
ใช้เสียงร้องที่แยกแล้ว (cache/*_vocals16k.npy) + โมเดล MMS forced aligner (รองรับไทยและอังกฤษ)"""
import json, os, sys, time, glob, re, traceback
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def log(*a):
    print(*a, flush=True)

def romanizer(kind=None):
    kind = kind or os.environ.get("FA_ROM", "royin")
    if kind in ("royin", "thai2rom", "tltk"):
        try:
            from pythainlp.transliterate import romanize
            romanize("ทดสอบ", engine=kind)
            def f(s):
                out = []
                for w in re.findall(r"[\u0E00-\u0E7F]+|[^\u0E00-\u0E7F]+", s):
                    out.append(romanize(w, engine=kind) if re.match(r"[\u0E00-\u0E7F]", w) else w)
                return " ".join(out)
            return f, kind
        except Exception as e:
            log("pythainlp", kind, "ใช้ไม่ได้:", e)
    try:
        import uroman as ur
        u = ur.Uroman()
        return lambda s: u.romanize_string(s), "uroman"
    except Exception as e:
        log("uroman ใช้ไม่ได้:", e)
    from pythainlp.transliterate import romanize
    return lambda s: " ".join(romanize(w) if re.search("[฀-๿]", w) else w for w in s.split()), "pythainlp"

def units_of(line):
    """แบ่งบรรทัดเป็นคำย่อย (ไทยใช้ตัดคำ, อังกฤษแบ่งตามช่องว่าง) คืน [(offset, text)]"""
    try:
        from pythainlp.tokenize import word_tokenize
        toks = word_tokenize(line, engine="newmm", keep_whitespace=True)
    except Exception:
        toks = re.findall(r"\S+|\s+", line)
    out, o = [], 0
    for t in toks:
        if t.strip(): out.append((o, t))
        o += len(t)
    return out

def emissions(model, x, dev, torch, sr=16000, chunk=15.0, ctx=1.0):
    fps = 50.0
    nfr = int(len(x) / sr * fps)
    out = None
    s = 0.0
    dur = len(x) / sr
    while s < dur:
        a = max(0.0, s - ctx); b = min(dur, s + chunk + ctx)
        seg = x[int(a * sr):int(b * sr)].astype(np.float32)
        seg = (seg - seg.mean()) / (seg.std() + 1e-7)
        with torch.inference_mode():
            lg = model(torch.from_numpy(seg)[None].to(dev)).logits[0]
            lp = torch.log_softmax(lg.float(), -1).cpu().numpy()
        if out is None: out = np.full((nfr + 5, lp.shape[1]), -1e4, np.float32)
        f0 = int(round(a * fps)); c0 = int(round(s * fps)); c1 = int(round(min(dur, s + chunk) * fps))
        for f in range(c0, min(c1, nfr)):
            k = f - f0
            if 0 <= k < len(lp): out[f] = lp[k]
        s += chunk
    return out[:nfr]

def viterbi(lp, toks, blank):
    """CTC forced alignment: คืนเฟรมเริ่ม/จบของแต่ละ token"""
    T, L = len(lp), len(toks)
    S = 2 * L + 1
    lab = np.full(S, blank, np.int64); lab[1::2] = toks
    allow2 = np.zeros(S, bool)
    for s in range(3, S, 2):
        allow2[s] = lab[s] != lab[s - 2]
    NEG = -1e30
    al = np.full(S, NEG); al[0] = lp[0, blank]; al[1] = lp[0, lab[1]]
    bp = np.zeros((T, S), np.int8)
    for t in range(1, T):
        a0 = al
        a1 = np.r_[NEG, al[:-1]]
        a2 = np.r_[NEG, NEG, al[:-2]]; a2 = np.where(allow2, a2, NEG)
        st = np.stack([a0, a1, a2]); k = st.argmax(0)
        al = st[k, np.arange(S)] + lp[t, lab]
        bp[t] = k
    s = S - 1 if al[S - 1] >= al[S - 2] else S - 2
    path = np.zeros(T, np.int64)
    for t in range(T - 1, -1, -1):
        path[t] = s
        s -= int(bp[t, s])
    st = np.full(L, -1); en = np.full(L, -1); sc = np.zeros(L)
    for t in range(T):
        s = path[t]
        if s % 2 == 1:
            j = s // 2
            if st[j] < 0: st[j] = t
            en[j] = t; sc[j] = max(sc[j], lp[t, lab[s]]) if st[j] != t else lp[t, lab[s]]
    return st, en, sc

_MODEL = {}
def align(lines, x, vs, ve, ef, name="MahmoudAshraf/mms-300m-1130-forced-aligner", rom_kind=None):
    """จับเวลาเนื้อแบบบังคับ คืน [{S,E,conf,units:[[offset,คำ,เริ่ม,จบ],...]}] ต่อบรรทัด"""
    a = max(0.0, vs - 1.0); b = min(len(x) / 16000, ve + 1.0)
    if os.path.exists(ef):
        z = np.load(ef, allow_pickle=True); lp = z["lp"]; voc = dict(z["voc"].item()); log("ใช้ผลฟังเสียงที่เก็บไว้", ef)
    else:
        import torch
        from transformers import AutoModelForCTC, AutoTokenizer
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        if name not in _MODEL:
            log("โหลดโมเดล", name, "(ครั้งแรกดาวน์โหลด ~1.2GB)")
            _MODEL[name] = (AutoTokenizer.from_pretrained(name), AutoModelForCTC.from_pretrained(name).eval())
        tok, model = _MODEL[name]
        voc = tok.get_vocab()
        seg = x[int(a * 16000):int(b * 16000)]
        t0 = time.time(); lp = emissions(model, seg, "cpu", torch); log("emissions", lp.shape, round(time.time() - t0, 1), "วิ")
        np.savez_compressed(ef, lp=lp.astype(np.float16), voc=np.array(voc, dtype=object))
    lp = lp.astype(np.float32)
    blank = voc.get("<blank>", 0)
    rom, rname = romanizer(rom_kind)
    toks, owner, U = [], [], []
    for i, l in enumerate(lines):
        us = units_of(l); U.append(us)
        for k, (o, w) in enumerate(us):
            r = rom(w).lower()
            ids = [voc[c] for c in r if c in voc and c not in (" ", "|")]
            for c in ids: toks.append(c); owner.append((i, k))
    if not toks: return None
    st, en, sc = viterbi(lp, np.array(toks), blank)
    fps = 50.0
    out = []
    for i, l in enumerate(lines):
        idx = [j for j, ow in enumerate(owner) if ow[0] == i]
        units = []
        for k, (o, w) in enumerate(U[i]):
            jj = [j for j in idx if owner[j][1] == k]
            if jj: units.append([o, w, round(a + st[jj[0]] / fps, 2), round(a + (en[jj[-1]] + 1) / fps, 2)])
        conf = float(np.mean([sc[j] for j in idx])) if idx else -9
        out.append({"S": units[0][2] if units else None, "E": units[-1][3] if units else None, "conf": round(conf, 3), "units": units})
    try: refine(out, x)
    except Exception: traceback.print_exc()
    return out

def refine(out, x, sr=16000):
    """แก้คำแรกของบรรทัดที่ถูกดึงไปติดหางเสียงของบรรทัดก่อน:
    1) ถ้ามีช่วงเงียบ (>=0.18 วิ) หลังจุดเริ่ม และยังห่างคำที่ 2 พอ (>=0.22 วิ) ให้เริ่มหลังช่วงเงียบ
    2) ไม่งั้น ขยับไปจุดเริ่มพยางค์ที่ใกล้ที่สุดหลังจุดเดิม (ไม่เกิน 0.1 วิ)"""
    hop = 160; n = len(x) // hop
    e = 10 * np.log10((x[:n * hop].reshape(n, hop).astype(np.float64) ** 2).mean(1) + 1e-9)
    e = np.convolve(e, np.ones(3) / 3, "same"); floor = np.percentile(e, 20)
    quiet = e < floor + 10
    d = e - np.r_[np.full(4, e[0]), e[:-4]]
    pk = np.where((d[1:-1] > 4.5) & (d[1:-1] >= d[:-2]) & (d[1:-1] >= d[2:]) & (e[1:-1] > floor + 12))[0] + 1
    syl = pk / 100.0 - .02
    for q in out:
        u = q.get("units") or []
        if not u: continue
        w0 = str(u[0][1]).strip().lower()
        if re.match(r"^[fshzvc]|^th|^[สซศษฟฝหฮ]", w0): continue   # เสียงลม (ฟ ส ซ ห) เบาโดยธรรมชาติ อย่าเข้าใจว่าเงียบ
        s0 = u[0][2]; nxt = u[1][2] if len(u) > 1 else u[0][3]
        lim = min(s0 + 1.3, nxt)
        a, b = int(s0 * 100), int(lim * 100)
        best = None; k = a
        while k < b:
            if quiet[k]:
                j = k
                while j < n and quiet[j]: j += 1
                if (j - k) >= 18 and j < b + 5 and j / 100.0 <= nxt - .22 and k <= a + 25: best = j / 100.0; break
                if k > a + 25: break   # มีเสียงร้องต่อจากจุดเริ่มแล้ว แปลว่าจุดเดิมน่าจะถูก (เช่น ฮุคที่ร้องซ้ำ "if you, if you")
                k = j
            else: k += 1
        if best is None:
            c = syl[(syl >= s0 - .02) & (syl <= s0 + .1) & (syl <= nxt - .15)]
            if len(c): best = float(c[0])
        if best is not None and abs(best - s0) > .05:
            u[0][2] = round(best, 2); q["S"] = u[0][2]; q["moved"] = round(best - s0, 2)
    return out

def main():
    t_start = time.time()
    J = json.load(open(os.path.join(HERE, "lines.json"), encoding="utf-8"))
    lines = J["lines"]
    vf = J.get("vocals") or sorted(glob.glob(os.path.join(HERE, "..", "cache", "*_vocals16k.npy")))[-1]
    log("เสียงร้อง:", vf)
    x = np.load(vf).astype(np.float32)
    vs, ve = J.get("vs", 0), J.get("ve", len(x) / 16000)
    a = max(0.0, vs - 1.0); b = min(len(x) / 16000, ve + 1.0)
    ef = vf.replace("_vocals16k.npy", "_mms_%d_%d.npz" % (int(a * 100), int(b * 100)))
    for kind in (sys.argv[1:] or ["royin"]):
        out = align(lines, x, vs, ve, ef, rom_kind=kind)
        log("==", kind)
        for i, l in enumerate(lines): log(i + 1, out[i]["S"], out[i]["E"], out[i]["conf"], l[:40])
        json.dump({"lines": out, "rom": kind, "secs": round(time.time() - t_start, 1)}, open(os.path.join(HERE, "fa_result_%s.json" % kind), "w", encoding="utf-8"), ensure_ascii=False)
    log("เสร็จ", round(time.time() - t_start, 1), "วิ")

if __name__ == "__main__":
    try: main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
