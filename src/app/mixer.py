# -*- coding: utf-8 -*-
"""มิกซ์ + มาสเตอร์อัตโนมัติ: เสียงร้อง (ยังไม่มิกซ์) + บีต -> ไฟล์พร้อมลงสตรีม
หลักการ: เสียงไม่แตก (true peak <= -1 dBTP), ดังระดับสตรีม, เสียงร้องชัดลอยอยู่บนบีต ตามคอนเซปต์ที่เลือก"""
import json, os, sys, time, math, subprocess
import numpy as np
from scipy import signal

SR = 44100
CONCEPTS = {
 "dark-rnb":  {"n": "Dark R&B · ฟีล The Weeknd", "tags": "weeknd,the weeknd,rnb,r&b,dark,synth,daniel caesar,brent,6lack,partynextdoor,giveon", "hpf": 95, "mud": 2.5, "pres": 2.0, "air": 3.0, "sat": .12, "c1": 4, "c2": 2.5, "rev": -14, "rt": 2.4, "pre": 30, "dly": -18, "div": .25, "fb": .35, "dbl": -16, "vbal": -.5, "carve": 2.5, "lo": 1.0, "hi": .8, "lufs": -9.5},
 "uk-drill":  {"n": "UK Drill · ฟีล Central Cee", "tags": "central cee,drill,uk,pop smoke,dave,headie,digga", "hpf": 110, "mud": 3.0, "pres": 3.5, "air": 2.0, "sat": .18, "c1": 5, "c2": 3, "rev": -26, "rt": .8, "pre": 10, "dly": -28, "div": .125, "fb": .2, "dbl": -22, "vbal": 1.5, "carve": 3.5, "lo": .5, "hi": 1.0, "lufs": -8.5},
 "melodic-trap": {"n": "Melodic Trap · ฟีล Travis Scott / Juice WRLD", "tags": "travis,juice,trap,melodic,future,uzi,young thug,gunna,metro,rage,carti", "hpf": 100, "mud": 2.0, "pres": 2.5, "air": 2.5, "sat": .25, "c1": 4, "c2": 3, "rev": -16, "rt": 1.8, "pre": 20, "dly": -19, "div": .125, "fb": .3, "dbl": -15, "vbal": 0, "carve": 3, "lo": 1.5, "hi": .5, "lufs": -8.5},
 "lofi-warm": {"n": "Lo-fi อบอุ่น · ฟีล Mac Miller", "tags": "mac miller,lofi,lo-fi,joji,keshi,warm,jazz,chill,circles,swimming", "hpf": 90, "mud": 1.5, "pres": 1.0, "air": 0.0, "sat": .35, "c1": 3, "c2": 2, "rev": -18, "rt": 1.2, "pre": 15, "dly": -24, "div": .25, "fb": .25, "dbl": -24, "vbal": 0, "carve": 2, "lo": 1.5, "hi": -2.0, "lufs": -11},
 "clean-rap": {"n": "Rap ชัดสะอาด · ฟีล Drake / Kendrick", "tags": "drake,kendrick,j cole,cole,eminem,nf,rap,hiphop,hip-hop,conscious,kanye", "hpf": 100, "mud": 2.5, "pres": 2.5, "air": 2.0, "sat": .15, "c1": 4, "c2": 2.5, "rev": -22, "rt": 1.0, "pre": 15, "dly": -24, "div": .25, "fb": .25, "dbl": -24, "vbal": 1.0, "carve": 3, "lo": 1.0, "hi": .5, "lufs": -9},
 "thai-pop":  {"n": "ป๊อป/R&B ไทย ใสชัด", "tags": "thai,ไทย,pop,ป๊อป,ballad,บัลลาด,indie,อินดี้", "hpf": 90, "mud": 2.0, "pres": 2.0, "air": 2.5, "sat": .1, "c1": 3.5, "c2": 2.5, "rev": -17, "rt": 1.6, "pre": 25, "dly": -22, "div": .25, "fb": .3, "dbl": -20, "vbal": .5, "carve": 2.5, "lo": .5, "hi": 1.0, "lufs": -10},
 "emo-wide":  {"n": "Emo / Rock กว้างหนา · ฟีล Lil Peep", "tags": "peep,emo,rock,xxxtentacion,xxx,grunge,pop punk", "hpf": 110, "mud": 2.0, "pres": 3.0, "air": 1.5, "sat": .3, "c1": 5, "c2": 3, "rev": -18, "rt": 1.5, "pre": 20, "dly": -22, "div": .25, "fb": .3, "dbl": -10, "vbal": .5, "carve": 3, "lo": 1.0, "hi": .5, "lufs": -9},
}

def log(*a): print(*a, flush=True)

# ---------- IO ----------
def load(path):
    try:
        import soundfile as sf
        x, sr = sf.read(path, dtype="float32", always_2d=True)
    except Exception:
        raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy(); sr = SR
    if x.shape[1] == 1: x = np.repeat(x, 2, 1)
    x = x[:, :2]
    if sr != SR:
        g = math.gcd(SR, sr); x = signal.resample_poly(x, SR // g, sr // g, axis=0).astype(np.float32)
    return x

def save_wav24(path, x):
    x = np.clip(x, -1, 1)
    try:
        import soundfile as sf
        sf.write(path, x, SR, subtype="PCM_24"); return
    except Exception:
        pass
    import wave
    y = (x * 8388607).astype(np.int32)
    b = np.zeros((y.shape[0], 2, 3), np.uint8)
    for k in range(3): b[:, :, k] = (y >> (8 * k)) & 255
    w = wave.open(path, "wb"); w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(b.tobytes()); w.close()

# ---------- filters (RBJ biquads) ----------
def biquad(kind, f, q=.707, g=0.0):
    A = 10 ** (g / 40); w = 2 * math.pi * f / SR; c, s = math.cos(w), math.sin(w); al = s / (2 * q)
    if kind == "hp": b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == "lp": b = [(1 - c) / 2, 1 - c, (1 - c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == "bp": b = [al, 0, -al]; a = [1 + al, -2 * c, 1 - al]
    elif kind == "peak": b = [1 + al * A, -2 * c, 1 - al * A]; a = [1 + al / A, -2 * c, 1 - al / A]
    elif kind in ("ls", "hs"):
        sq = 2 * math.sqrt(A) * al; sgn = 1 if kind == "ls" else -1
        b = [A * ((A + 1) - sgn * (A - 1) * c + sq), sgn * 2 * A * ((A - 1) - sgn * (A + 1) * c), A * ((A + 1) - sgn * (A - 1) * c - sq)]
        a = [(A + 1) + sgn * (A - 1) * c + sq, -sgn * 2 * ((A - 1) + sgn * (A + 1) * c), (A + 1) + sgn * (A - 1) * c - sq]
    return np.array(b) / a[0], np.array(a) / a[0]
def filt(x, kind, f, q=.707, g=0.0):
    b, a = biquad(kind, f, q, g); return signal.lfilter(b, a, x, axis=0).astype(np.float32)

# ---------- loudness (BS.1770 / LUFS) ----------
def kweight(x):
    y = filt(x, "hs", 1681.97, .7072, 4.0); return filt(y, "hp", 38.13, .5003)
def lufs(x):
    y = kweight(x); n = int(.4 * SR); h = int(.1 * SR)
    if len(y) < n: return -70.0
    p = np.array([np.mean(np.sum(y[i:i + n] ** 2, 1)) for i in range(0, len(y) - n, h)]) + 1e-12
    l = -.691 + 10 * np.log10(p); p = p[l > -70]
    if not len(p): return -70.0
    rel = -.691 + 10 * np.log10(p.mean()) - 10; p2 = p[(-.691 + 10 * np.log10(p)) > rel]
    return float(-.691 + 10 * np.log10(p2.mean()))
def true_peak(x):
    up = signal.resample_poly(x, 4, 1, axis=0); return float(20 * np.log10(np.max(np.abs(up)) + 1e-12))

# ---------- dynamics ----------
def env_db(x, att, rel, blk=64):
    """ระดับเสียง (dB) แบบมี attack/release คำนวณทีละบล็อกเล็ก"""
    m = np.max(np.abs(x), 1) if x.ndim > 1 else np.abs(x)
    n = len(m) // blk; pk = m[:n * blk].reshape(n, blk).max(1); db = 20 * np.log10(pk + 1e-9)
    ca = math.exp(-blk / (att * SR)); cr = math.exp(-blk / (rel * SR)); e = np.empty(n); v = db[0] if n else -90
    for i in range(n):
        d = db[i]; v = (ca * v + (1 - ca) * d) if d > v else (cr * v + (1 - cr) * d); e[i] = v
    return e, blk
def comp(x, thr, ratio, att, rel, knee=6.0, makeup=0.0):
    e, blk = env_db(x, att, rel); over = e - thr
    gr = np.where(over <= -knee / 2, 0, np.where(over >= knee / 2, over * (1 - 1 / ratio), (1 - 1 / ratio) * (over + knee / 2) ** 2 / (2 * knee)))
    g = 10 ** ((-gr + makeup) / 20); gi = np.interp(np.arange(len(x)), np.arange(len(g)) * blk + blk / 2, g).astype(np.float32)
    return x * gi[:, None], float(gr.max() if len(gr) else 0)
def rms_db(x):
    m = np.sqrt(np.mean(x ** 2, 1)); n = int(.4 * SR); act = []
    for i in range(0, len(m) - n, n):
        v = 20 * np.log10(np.sqrt(np.mean(m[i:i + n] ** 2)) + 1e-9)
        if v > -50: act.append(v)
    return float(np.median(act)) if act else -30.0

def deess(x, amount=6.0):
    band = filt(filt(x, "hp", 5500, .7), "lp", 10000, .7); rest = x - band
    e, blk = env_db(band, .002, .05); thr = np.percentile(e[e > -60], 80) if np.any(e > -60) else -30
    gr = np.clip(e - thr, 0, None) * .7; gr = np.minimum(gr, amount)
    g = 10 ** (-gr / 20); gi = np.interp(np.arange(len(x)), np.arange(len(g)) * blk + blk / 2, g).astype(np.float32)
    return rest + band * gi[:, None]

def make_ir(rt, pre_ms, seed=1):
    r = np.random.default_rng(seed); n = int(SR * min(4, rt * 1.2)); t = np.arange(n) / SR
    ir = r.standard_normal((n, 2)).astype(np.float32) * np.exp(-6.9 * t / rt)[:, None]
    ir = filt(filt(ir, "hp", 250), "lp", 7500); pre = np.zeros((int(SR * pre_ms / 1000), 2), np.float32)
    ir = np.vstack([pre, ir]); return ir / np.sqrt(np.sum(ir ** 2) / 2)

def bpm_of(x):
    m = np.mean(np.abs(x), 1); hop = 512; n = len(m) // hop; e = m[:n * hop].reshape(n, hop).mean(1)
    d = np.clip(np.diff(e), 0, None); d = d - d.mean()
    ac = np.correlate(d, d, "full")[len(d) - 1:]; fps = SR / hop
    lo, hi = int(fps * 60 / 180), int(fps * 60 / 60); k = lo + int(np.argmax(ac[lo:hi]))
    b = 60 * fps / k
    while b < 75: b *= 2
    while b > 165: b /= 2
    return round(b, 1)

def limiter(x, ceil_db=-1.0, look_ms=1.5, rel_ms=80):
    """ลิมิเตอร์มองล่วงหน้า + ตรวจ true peak (oversample 4 เท่า) กันเสียงแตก"""
    c = 10 ** (ceil_db / 20)
    up = np.abs(signal.resample_poly(x, 4, 1, axis=0)).max(1); pk = up.reshape(-1, 4).max(1)[:len(x)]
    if len(pk) < len(x): pk = np.pad(pk, (0, len(x) - len(pk)))
    need = np.minimum(1.0, c / (pk + 1e-12)); la = max(1, int(SR * look_ms / 1000))
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    g = minimum_filter1d(need, size=2 * la + 1, origin=0)
    blk = 32; n = len(g) // blk + 1; gb = np.ones(n); cr = math.exp(-blk / (SR * rel_ms / 1000)); v = 1.0
    gmin = np.array([g[i * blk:(i + 1) * blk].min() if i * blk < len(g) else 1 for i in range(n)])
    for i in range(n):
        t = gmin[i]; v = t if t < v else cr * v + (1 - cr) * t; gb[i] = v
    gs = np.interp(np.arange(len(x)), np.arange(n) * blk, gb)
    gs = np.minimum(gs, g); gs = uniform_filter1d(gs, la)
    gs = np.minimum(gs, minimum_filter1d(need, size=2 * la + 1))
    return (x * gs[:, None]).astype(np.float32), float(-20 * np.log10(gs.min() + 1e-12))

def softclip(x, knee_db=-4.0):
    """ตัดยอดแบบนุ่ม (oversample 4 เท่า กันเสียงแตก/aliasing) เฉพาะยอดที่เกิน knee ใช้เกลี่ยหัวกลองให้ดังขึ้นได้แบบใส"""
    u = signal.resample_poly(x, 4, 1, axis=0); t = 10 ** (knee_db / 20); a = np.abs(u)
    over = a > t; y = u.copy()
    y[over] = np.sign(u[over]) * (t + (1 - t) * np.tanh((a[over] - t) / (1 - t)))
    return signal.resample_poly(y, 1, 4, axis=0)[:len(x)].astype(np.float32)

# ---------- main ----------
def pick_concept(text):
    t = (text or "").lower(); best, bs = "clean-rap", 0
    for k, p in CONCEPTS.items():
        s = sum(1 for w in p["tags"].split(",") if w and w in t)
        if s > bs: best, bs = k, s
    return best

def mix(vocal_path, beat_path, concept="clean-rap", out_dir=".", name="mix", ref_path=None, over=None, progress=None):
    t0 = time.time(); P = dict(CONCEPTS.get(concept, CONCEPTS["clean-rap"])); P.update(over or {})
    pr = progress or (lambda m, p: log(m))
    pr("โหลดไฟล์", 5); v = load(vocal_path); b = load(beat_path)
    n = max(len(v), len(b)); v = np.pad(v, ((0, n - len(v)), (0, 0))); b = np.pad(b, ((0, n - len(b)), (0, 0)))
    vm = v.mean(1, keepdims=True); v = np.repeat(vm, 2, 1)               # เสียงร้องหลักไว้ตรงกลาง
    bpm = bpm_of(b); pr("จังหวะเพลง %.1f BPM · แต่งเสียงร้อง" % bpm, 15)
    # --- vocal chain
    x = filt(v, "hp", P["hpf"], .707); x = filt(x, "hp", P["hpf"] * .8, .707)
    x = filt(x, "peak", 300, 1.0, -P["mud"]); x = filt(x, "peak", 3500, .9, P["pres"]); x = filt(x, "hs", 11000, .7, P["air"])
    x = deess(x, 6)
    vr = rms_db(x); x, gr1 = comp(x, vr + 6, P["c1"], .004, .06); x, gr2 = comp(x, vr - 3, P["c2"], .02, .18)
    if P["sat"] > 0: d = 1 + 4 * P["sat"]; x = (1 - P["sat"]) * x + P["sat"] * np.tanh(x * d) / np.tanh(d)
    x = deess(x, 4)
    pr("ใส่มิติ (รีเวิร์บ ดีเลย์ เสียงซ้อน)", 35)
    wet = np.zeros_like(x)
    if P["rev"] > -40:
        ir = make_ir(P["rt"], P["pre"]); r = signal.fftconvolve(x.mean(1), ir[:, 0])[:n]; l = signal.fftconvolve(x.mean(1), ir[:, 1])[:n]
        wet += np.stack([r, l], 1).astype(np.float32) * 10 ** (P["rev"] / 20)
    if P["dly"] > -40:
        dt = int(SR * 60 / bpm * 4 * P["div"]); src = filt(filt(x, "hp", 400), "lp", 6000); dl = np.zeros_like(x)
        g = 1.0
        for k in range(1, 6):
            sh = dt * k
            if sh >= n: break
            tap = np.zeros_like(x); tap[sh:] = src[:n - sh] * g
            if k % 2: tap[:, 1] *= .6
            else: tap[:, 0] *= .6
            dl += tap; g *= P["fb"]
        wet += dl * 10 ** (P["dly"] / 20)
    if P["dbl"] > -40:
        d1, d2 = int(SR * .013), int(SR * .021); dbl = np.zeros_like(x)
        dbl[d1:, 0] = x[:n - d1, 0]; dbl[d2:, 1] = x[:n - d2, 1]; wet += filt(dbl, "hp", 200) * 10 ** (P["dbl"] / 20)
    xv = x + wet
    # --- beat chain + carve space for vocal
    pr("ทำที่ว่างในบีตให้เสียงร้อง", 50)
    y = filt(b, "hp", 28, .707)
    if P["carve"] > 0:
        band = filt(filt(y, "hp", 1200, .6), "lp", 5000, .6); e, blk = env_db(x, .01, .15)
        act = np.clip((e - (np.percentile(e, 50))) / 12, 0, 1); g = 10 ** (-P["carve"] * act / 20)
        gi = np.interp(np.arange(n), np.arange(len(g)) * blk + blk / 2, g).astype(np.float32); y = y - band + band * gi[:, None]
    # --- balance
    lv, lb = lufs(xv), lufs(y); gv = 10 ** ((lb + P["vbal"] - lv) / 20) if lv > -60 else 1.0
    m = xv * gv + y
    pr("มาสเตอร์ (EQ, กลู, ลิมิเตอร์)", 65)
    m = filt(m, "ls", 100, .7, P["lo"]); m = filt(m, "hs", 10000, .7, P["hi"])
    if ref_path:
        try:
            m = match_ref(m, load(ref_path)); pr("ปรับโทนให้ใกล้เพลงอ้างอิง", 72)
        except Exception as e: log("อ้างอิงใช้ไม่ได้", e)
    mr = rms_db(m); m, grg = comp(m, mr + 2, 2.0, .03, .25)
    m = m / (np.max(np.abs(m)) + 1e-9) * .5
    target = P["lufs"]; gain = 0.0; lim_gr = 0.0
    for it in range(4):
        cur = lufs(m * 10 ** (gain / 20)); gain += target - cur
        out, lim_gr = limiter(softclip(m * 10 ** (gain / 20)))
        if lim_gr > 6.0: gain -= (lim_gr - 6.0); out, lim_gr = limiter(softclip(m * 10 ** (gain / 20))); break   # ไม่บีบเกิน 6 dB กันเสียงแบน/แตก
        if abs(lufs(out) - target) < .3: break
    # ตรวจ true peak สุดท้าย
    tp = true_peak(out)
    if tp > -1.0: out = out * 10 ** ((-1.05 - tp) / 20); tp = true_peak(out)
    L = lufs(out)
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, name + ".wav"); save_wav24(wav, out)
    mp3 = os.path.join(out_dir, name + ".mp3")
    try: subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", wav, "-b:a", "320k", mp3], check=True)
    except Exception: mp3 = None
    rep = {"concept": concept, "concept_name": P["n"], "bpm": bpm, "lufs": round(L, 1), "true_peak": round(tp, 2), "limiter_gr": round(lim_gr, 1),
           "vocal_comp_gr": [round(gr1, 1), round(gr2, 1)], "glue_gr": round(grg, 1), "secs": round(time.time() - t0, 1), "wav": os.path.basename(wav), "mp3": os.path.basename(mp3) if mp3 else None,
           "settings": {k: P[k] for k in P if k not in ("n", "tags")}}
    pr("เสร็จ", 100); return rep

def match_ref(m, ref, maxdb=4.0):
    """ปรับโทนเสียงรวมให้ใกล้เพลงอ้างอิง (เฉลี่ยสเปกตรัม ปรับไม่เกิน ±4 dB แบบเรียบ)"""
    def spec(z):
        f, p = signal.welch(z.mean(1), SR, nperseg=8192); return f, 10 * np.log10(p + 1e-14)
    f, a = spec(m); _, r = spec(ref); d = (r - r[(f > 200) & (f < 4000)].mean()) - (a - a[(f > 200) & (f < 4000)].mean())
    bands = [60, 120, 250, 500, 1000, 2000, 4000, 8000, 12000]; out = m
    for fc in bands:
        sel = (f > fc / 1.41) & (f < fc * 1.41)
        if sel.any():
            g = float(np.clip(np.median(d[sel]) * .7, -maxdb, maxdb))
            if abs(g) > .3: out = filt(out, "peak", fc, 1.0, g)
    return out

if __name__ == "__main__":
    J = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    print(json.dumps(mix(J["vocal"], J["beat"], J.get("concept", "clean-rap"), J.get("out", "."), J.get("name", "mix"), J.get("ref")), ensure_ascii=False))
