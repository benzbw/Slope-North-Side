"""เปิดแอปบนคอม + ให้ปุ่ม 'ซิงค์อัตโนมัติ' ใช้ AI ในเครื่อง (เร็วกว่าในเบราว์เซอร์มาก)
ติดตั้งครั้งเดียว:  pip install faster-whisper      (ถ้าจะใช้ตัวเลือกแยกเสียงร้อง: pip install demucs และต้องมี ffmpeg)
รัน:  python start.py
"""
import http.server, os, sys, json, base64, tempfile, threading, uuid, pathlib, subprocess, traceback, webbrowser, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())
PORT = int(os.environ.get("PORT", "8790"))
HOST = os.environ.get("HOST", "0.0.0.0" if (os.environ.get("PORT") or os.environ.get("LAN", "1") == "1") else "127.0.0.1")   # เปิดให้มือถือใน Wi-Fi เดียวกันใช้ได้ (ปิดด้วย LAN=0)
def _pin():
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lan_pin.txt")
    try:
        p = open(fp).read().strip()
        if len(p) >= 6: return p
    except Exception: pass
    import secrets; p = "%06d" % secrets.randbelow(10 ** 6)
    try: open(fp, "w").write(p)
    except Exception: pass
    return p
PIN = _pin()                                      # รหัส 6 หลักสำหรับมือถือ (เครื่องอื่นในบ้าน) — คอมเครื่องนี้ไม่ต้องใส่
def lan_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close(); return ip
    except Exception: return ""
KEY = os.environ.get("APP_PASSWORD", "")          # ตั้งไว้ = ต้องใส่รหัสก่อนใช้ AI
DEFAULT_MODEL = os.environ.get("WHISPER_MODEL", "medium")
BEAM = int(os.environ.get("BEAM", "1"))           # 1 = เร็วกว่าหลายเท่าบนโน้ตบุ๊ก
MAX_BODY = int(os.environ.get("MAX_UPLOAD_MB", "40")) * 1048576
JOBS, MODELS = {}, {}
GATE = threading.Semaphore(1)                      # ทำทีละเพลง กัน RAM เต็ม คนอื่นรอคิว
MAXQ = int(os.environ.get("MAX_QUEUE", "20"))        # คิวเต็มแล้วตอบกลับทันที ไม่ให้เครื่องล่มเมื่อคนเข้าเยอะ
_QL = threading.Lock(); _Q = []                       # ลำดับคิว (id งาน)
class Slot:
    """เข้าคิวงานหนัก แสดงลำดับคิวให้ผู้ใช้เห็น"""
    def __init__(self, J=None): self.J = J; self.k = uuid.uuid4().hex
    def __enter__(self):
        with _QL: _Q.append(self.k)
        while not GATE.acquire(timeout=1.0):
            if self.J is not None:
                with _QL: pos = _Q.index(self.k) if self.k in _Q else 0
                self.J.update(msg="รอคิว อันดับที่ %d (มีคนใช้อยู่)" % pos)
        return self
    def __exit__(self, *a):
        GATE.release()
        with _QL:
            if self.k in _Q: _Q.remove(self.k)
def queue_full(): 
    with _QL: return len(_Q) >= MAXQ
def housekeeping():
    """ล้างงานเก่า/ไฟล์ชั่วคราว ทุก 10 นาที (กันแรมและดิสก์เต็มเมื่อเปิดทิ้งไว้หลายวัน)"""
    import time as _t
    while True:
        _t.sleep(600)
        try:
            now = _t.time()
            for k in list(JOBS):
                j = JOBS.get(k) or {}
                if j.get("status") != "run" and now - j.get("_t", now) > 3600: JOBS.pop(k, None)
                elif "_t" not in j: j["_t"] = now
            for k, f in list(UPL.items()):
                try:
                    if now - os.path.getmtime(f) > 7200: os.remove(f); UPL.pop(k, None)
                except Exception: UPL.pop(k, None)
        except Exception: traceback.print_exc()
threading.Thread(target=housekeeping, daemon=True).start()


def load_audio(path, rate=16000, layout="mono"):
    """อ่านไฟล์เสียงเอง (กัน PyAV รุ่นใหม่ที่ faster-whisper บางรุ่นใช้ไม่ได้) คืนค่า float32 รูป (n,) หรือ (ch, n)"""
    import numpy as np
    try:
        import av
        c = av.open(path)
        rs = av.AudioResampler(format="s16", layout=layout, rate=rate)
        parts = []

        def add(fr):
            if fr is None:
                return
            for f in (fr if isinstance(fr, list) else [fr]):
                parts.append(f.to_ndarray().reshape(-1))     # s16 แบบ packed: ช่องสลับกัน L R L R
        for fr in c.decode(c.streams.audio[0]):
            add(rs.resample(fr))
        try:
            add(rs.resample(None))
        except Exception:
            pass
        c.close()
        x = np.concatenate(parts).astype(np.float32) / 32768.0
        if layout == "stereo":
            x = x[: len(x) // 2 * 2].reshape(-1, 2).T.copy()
        return x
    except Exception:
        traceback.print_exc()
        from faster_whisper.audio import decode_audio
        x = decode_audio(path, sampling_rate=rate)
        return np.stack([x, x]) if layout == "stereo" else x


SEP = {}


def vocal_onsets(x, sr=16000, mindur=.18, depth=9):
    """หาจุดเริ่มร้องหลังจังหวะหายใจ จากเสียงร้องที่แยกแล้ว (ใช้วางบรรทัดที่ AI ฟังคำไม่ออก)"""
    import numpy as np
    fr=int(sr*.02);n=len(x)//fr
    e=np.sqrt((x[:n*fr].reshape(n,fr)**2).mean(1));db=20*np.log10(e+1e-7)
    db=np.convolve(db,np.ones(3)/3,'same')
    floor=np.percentile(db,5)
    thr=min(floor+15,np.percentile(db,50)-4)                  # แร็พแน่นๆ ทั้งเพลง (ช่วงดัง-เบาแคบ) ก็ยังหาเจอ
    on=db>thr
    run=np.convolve(on.astype(float),np.ones(15),'same')>=14   # มีเสียงต่อเนื่อง >=0.3 วิ
    v=np.where(run)[0]
    start,end=(v[0]*.02-.15,v[-1]*.02+.15) if len(v) else (0,n*.02)
    if end-start<min(5.0,n*.02*.5): start,end=0.0,n*.02         # หาช่วงร้องไม่ได้จริง: ใช้ทั้งเพลง ดีกว่าบีบเนื้อทั้งหมดไว้ใน 1 วิ
    start=max(0.0,start)
    W=40;ons=[];i=W
    while i<n-W:
        loc=np.percentile(db[i-W:i+W],80)
        if db[i]<loc-depth:
            k=i
            while k<n-1 and db[k]<loc-depth: k+=1
            if (k-i)*.02>=mindur and start<k*.02<end:
                ons.append((round(k*.02,2),round((k-i)*.02,2)))
            i=k+1
        else: i+=1
    return ons,round(start,2),round(end,2)


def voice_segments(x, k=2, sr=16000, t0=None, t1=None):
    """แยกว่าแต่ละช่วงเป็นเสียงของนักร้องคนไหน จากโทนเสียง (MFCC) ของเสียงร้องที่แยกแล้ว คืน [[เริ่ม,จบ,กลุ่ม],...]"""
    import numpy as np
    x = np.asarray(x, dtype=np.float32); n, h = 512, 320
    if len(x) < n * 4 or k < 2: return []
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::h] * np.hanning(n).astype(np.float32)
    P = np.abs(np.fft.rfft(fr)) ** 2
    f = np.fft.rfftfreq(n, 1 / sr)
    mel = lambda v: 2595 * np.log10(1 + v / 700)
    hz = 700 * (10 ** (np.linspace(mel(60), mel(7600), 42) / 2595) - 1)
    fb = np.zeros((40, len(f)), np.float32)
    for i in range(40):
        a, b, c = hz[i], hz[i + 1], hz[i + 2]
        fb[i] = np.clip(np.minimum((f - a) / (b - a), (c - f) / (c - b)), 0, None)
    L = np.log(P @ fb.T + 1e-8)
    D = np.cos(np.pi / 40 * (np.arange(40)[None] + .5) * np.arange(1, 14)[:, None])
    M = L @ D.T
    e = 10 * np.log10(P.sum(1) + 1e-9); v = e > np.percentile(e, 40)
    t = np.arange(len(e)) * h / sr
    t0 = t0 if t0 is not None else 0; t1 = t1 if t1 is not None else t[-1]
    W, T = [], []
    s0 = t0
    while s0 < t1 - 1:
        m = (t >= s0) & (t < s0 + 3) & v
        if m.sum() >= 40:
            W.append(np.r_[M[m].mean(0), M[m].std(0)]); T.append(s0)
        s0 += 1.5
    if len(W) < k * 4: return []
    W = np.array(W); W = (W - W.mean(0)) / (W.std(0) + 1e-6)
    best = None
    for seed in range(20):
        r = np.random.default_rng(seed); c = W[r.choice(len(W), k, replace=False)]
        for _ in range(60):
            lab = ((W[:, None] - c[None]) ** 2).sum(2).argmin(1)
            c = np.array([W[lab == j].mean(0) if (lab == j).any() else c[j] for j in range(k)])
        inert = ((W - c[lab]) ** 2).sum()
        if best is None or inert < best[0]: best = (inert, lab.copy())
    lab = best[1]
    for _ in range(2):                                 # ปัดช่วงสั้นๆ ที่หลุดกลุ่มทิ้ง (ต่ำกว่า 3 หน้าต่าง ≈ 4.5 วิ)
        runs, i = [], 0
        while i < len(lab):
            j = i
            while j < len(lab) and lab[j] == lab[i]: j += 1
            runs.append([i, j]); i = j
        for ri, (a, b) in enumerate(runs):
            if b - a < 3 and len(runs) > 1:
                nb = runs[ri - 1] if ri > 0 else runs[ri + 1]
                lab[a:b] = lab[nb[0]]
    seg, i = [], 0
    while i < len(lab):
        j = i
        while j < len(lab) and lab[j] == lab[i]: j += 1
        a = T[i] if i else t0
        b = T[j] + 1.5 if j < len(lab) else t1
        if i: a = T[i] + .75
        seg.append([round(float(a), 2), round(float(b), 2), int(lab[i])]); i = j
    for q in range(1, len(seg)): seg[q - 1][1] = seg[q][0]
    # ตรวจซ้ำทั้งช่วง: ช่วงสั้น (< 15 วิ) ให้เทียบโทนเสียงเฉลี่ยทั้งช่วงกับช่วงยาวของแต่ละคน แล้วเลือกคนที่ใกล้สุด
    def mfeat(a, b):
        m = (t >= a) & (t < b) & v
        return M[m].mean(0) if m.sum() >= 20 else None
    for _ in range(2):
        cen = {}
        for a, b, c in seg:
            if b - a >= 15:
                fm = mfeat(a, b)
                if fm is not None: cen.setdefault(c, []).append((fm, b - a))
        cen = {c: sum(f * w for f, w in L) / sum(w for _, w in L) for c, L in cen.items()}
        if len(cen) < 2: break
        for q in seg:
            if q[1] - q[0] < 15:
                fm = mfeat(q[0], q[1])
                if fm is not None: q[2] = min(cen, key=lambda c: float(np.linalg.norm(fm - cen[c])))
        out = []
        for q in seg:
            if out and out[-1][2] == q[2]: out[-1][1] = q[1]
            else: out.append(q)
        seg = out
    return seg

def syllables(x, sr=16000, hop=160, rise=4.5, gap=.08, t0=0, t1=1e9):
    """จุดเริ่มพยางค์ในเสียงร้อง (พลังงานพุ่งขึ้นเร็ว) ใช้จับเวลาขึ้นของแต่ละคำ"""
    import numpy as np
    x = np.asarray(x, dtype=np.float32); n = len(x) // hop
    if n < 10: return []
    e = 10 * np.log10((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-9)
    e = np.convolve(e, np.ones(3) / 3, "same")
    floor = np.percentile(e, 20); d = e - np.r_[np.full(4, e[0]), e[:-4]]
    pk = np.where((d[1:-1] > rise) & (d[1:-1] >= d[:-2]) & (d[1:-1] >= d[2:]) & (e[1:-1] > floor + 12))[0] + 1
    on, last = [], -1.0
    for i in pk:
        t = i * hop / sr - .02
        if t - last >= gap and t0 - .5 <= t <= t1 + .5: on.append(round(float(t), 2)); last = t
    return on


def run_fa(lines, x, vs, ve, cdir, hsh, J):
    """จับเวลาทีละคำแบบรู้เนื้อ (fa/fa.py) ถ้าติดตั้งไม่ครบจะคืน None แล้วใช้วิธีเดิม"""
    try:
        import importlib.util
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fa", "fa.py")
        if not os.path.exists(fp): return None
        spec = importlib.util.spec_from_file_location("fa_mod", fp); fa = importlib.util.module_from_spec(spec); spec.loader.exec_module(fa)
        a = max(0.0, vs - 1.0); b = min(len(x) / 16000, ve + 1.0)
        ef = os.path.join(cdir, "%s_mms_%d_%d.npz" % (hsh, int(a * 100), int(b * 100)))
        if not os.path.exists(ef): J.update(msg="จับเวลาทีละคำจากเนื้อเพลง (ครั้งแรกราว 5 นาที)", pct=90)
        return fa.align(lines, x, vs, ve, ef)
    except Exception:
        traceback.print_exc(); return None

def combine(lines, word_sets, align):
    """ซิงค์แยกทีละชุดคำที่ AI เคยฟัง แล้วเลือกบรรทัดที่มั่นใจที่สุดจากทุกชุด (เรียงลำดับเวลาให้ถูก)"""
    best = None
    for ws in word_sets:
        S, E, ratio, conf = align(lines, ws)
        if best is None:
            best = [S[:], E[:], ratio, conf[:]]; continue
        for i in range(len(lines)):
            if conf[i] > best[3][i]:
                best[0][i], best[1][i], best[3][i] = S[i], E[i], conf[i]
        best[2] = max(best[2], ratio)
    S, E, ratio, conf = best
    last = -1e9
    order = sorted(range(len(lines)))
    for i in order:                                   # ตัดหมุดที่เวลาสลับลำดับ
        if conf[i] >= .5:
            if S[i] <= last + .3: conf[i] = min(conf[i], .3)
            else: last = S[i]
    return S, E, ratio, conf


def vocals_16k(path, J):
    """แยกเสียงร้องออกจากบีตด้วย demucs (htdemucs) ในโปรแกรมนี้เลย ไม่ต้องใช้ ffmpeg แล้วคืนเสียงร้อง 16kHz mono"""
    import time
    import torch
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    t0 = time.time()
    if "m" not in SEP:
        J.update(msg="โหลดตัวแยกเสียงร้อง (ครั้งแรกดาวน์โหลด ~80MB)", pct=3)
        SEP["m"] = get_model("htdemucs")
        SEP["m"].eval()
    m = SEP["m"]
    torch.set_num_threads(os.cpu_count() or 4)
    wav = torch.from_numpy(load_audio(path, m.samplerate, "stereo"))
    ref = wav.mean(0)
    mu, sd = ref.mean(), ref.std() + 1e-8
    J.update(msg="แยกเสียงร้องออกจากบีต (บนโน้ตบุ๊กใช้ 5–12 นาที ครั้งต่อไปจะข้ามขั้นนี้)", pct=5)
    with torch.no_grad():
        out = apply_model(m, ((wav - mu) / sd)[None], device="cpu", split=True, overlap=0.1, segment=6, progress=False)[0]
    voc = out[m.sources.index("vocals")] * sd + mu
    mono = voc.mean(0)
    try:
        import julius                                  # มากับ demucs
        mono = julius.resample_frac(mono, m.samplerate, 16000)
    except Exception:
        n = int(mono.shape[-1] * 16000 / m.samplerate)
        mono = torch.nn.functional.interpolate(mono[None, None], size=n, mode="linear", align_corners=False)[0, 0]
    res = mono.numpy().astype("float32")
    del out, voc, wav, mono
    SEP.clear()                                       # คืนแรมก่อนโหลด AI ถอดเสียง
    import gc
    gc.collect()
    J.update(msg="แยกเสียงร้องเสร็จ (%d วิ)" % (time.time() - t0), pct=9)
    return res


UPL = {}
def mix_job(jid, body):
    """มิกซ์ + มาสเตอร์ (mixer.py) เสียงร้อง + บีต -> mixes/ พร้อมบันทึกประวัติ"""
    J = JOBS[jid]
    try:
        import importlib.util, datetime
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mixer.py")
        spec = importlib.util.spec_from_file_location("mixer_mod", fp); mx = importlib.util.module_from_spec(spec); spec.loader.exec_module(mx)
        voc, beat, ref = UPL.get(body.get("vocal")), UPL.get(body.get("beat")), UPL.get(body.get("ref"))
        if not voc or not beat: raise RuntimeError("ไม่พบไฟล์เสียงร้องหรือบีต อัปโหลดใหม่อีกครั้ง")
        concept = body.get("concept") or mx.pick_concept(body.get("hint", ""))
        out = os.path.join(os.getcwd(), "mixes"); stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        safe = "".join(c for c in (body.get("song") or "song") if c.isalnum() or c in "-_ ").strip().replace(" ", "_")[:40] or "song"
        name = "%s_%s_%s" % (safe, concept, stamp)
        with Slot(J):
            rep = mx.mix(voc, beat, concept, out, name, ref, body.get("over") or None, progress=lambda m, p: J.update(msg=m, pct=p))
        rec = dict(rep, song=body.get("song", ""), setname=body.get("setname", ""), hint=body.get("hint", ""), time=stamp, url="/mixes/" + rep["wav"], mp3url=("/mixes/" + rep["mp3"]) if rep.get("mp3") else None)
        hf = os.path.join(out, "history.json")
        try: H = json.load(open(hf, encoding="utf-8"))
        except Exception: H = []
        H.insert(0, rec); json.dump(H[:200], open(hf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        J.update(status="done", pct=100, result=rec)
    except Exception as e:
        traceback.print_exc(); J.update(status="error", err=str(e)[:300])
    finally:
        for k in ("vocal", "beat", "ref"):
            f = UPL.pop(body.get(k) or "", None)
            try:
                if f: os.remove(f)
            except Exception: pass

def scenes_job(jid, body):
    """สร้างภาพฉาก MV ทีละภาพ (สไตล์เดียวกันทั้งเรื่อง) ส่งผลทีละภาพให้แอปแสดงทันที"""
    J = JOBS[jid]
    try:
        import importlib.util
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img_gen.py")
        ig = sys.modules.get("img_gen")
        if ig is None:
            spec = importlib.util.spec_from_file_location("img_gen", fp); ig = importlib.util.module_from_spec(spec); spec.loader.exec_module(ig); sys.modules["img_gen"] = ig
        prompts = body.get("prompts") or []; idx = body.get("idx") or list(range(len(prompts)))
        out = os.path.join(os.getcwd(), "mvs", body.get("mv") or jid); os.makedirs(out, exist_ok=True)
        seed = int(body.get("seed") or 1); res = {}
        J["result"] = {"urls": res}
        with Slot(J):
            MODELS.clear(); SEP.clear(); import gc; gc.collect()
            for n, (k, pr) in enumerate(zip(idx, prompts)):
                J.update(msg="วาดฉากที่ %d/%d" % (n + 1, len(prompts)), pct=int(100 * n / max(1, len(prompts))))
                data = ig.generate(pr, seed + k * 101, body.get("steps", 1), 512)
                fn = "s%02d_%d.png" % (k, int(time.time() * 1000) % 100000)
                open(os.path.join(out, fn), "wb").write(data)
                res[str(k)] = "/mvs/%s/%s" % (os.path.basename(out), fn)
        J.update(status="done", pct=100, result={"urls": res})
    except Exception as e:
        traceback.print_exc(); J.update(status="error", err=str(e)[:300])


# ---------- เทรนด์เพลง: ดึงชาร์ตล่าสุดจากอินเทอร์เน็ตของคอมนี้ (เก็บไว้ 6 ชม.) ----------
_TR = {"t": 0, "d": None}
def _get(url, timeout=15):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (SlopeNorthSide trends)"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
def _itunes(cc, genre=None, n=100):
    # ชาร์ตเพลงขายดี iTunes (มีหมวดเพลง) · rss.applemarketingtools ตอบ 504 แล้ว จึงใช้ฟีดนี้แทน
    u = "https://itunes.apple.com/%s/rss/topsongs/limit=%d%s/json" % (cc, n, "/genre=%s" % genre if genre else "")
    d = json.loads(_get(u)); f = d.get("feed") or {}; out = []
    for i, e in enumerate(f.get("entry") or []):
        g = ((e.get("category") or {}).get("attributes") or {}).get("label", "")
        out.append({"p": i + 1, "t": (e.get("im:name") or {}).get("label", ""), "a": (e.get("im:artist") or {}).get("label", ""), "g": [g] if g else []})
    return out, (f.get("updated") or {}).get("label", "")[:16].replace("T", " ")
_THAI_RAP = ("GAVIN:D", "P9D", "F.HERO", "YOUNGOHM", "MILLI", "ILLSLICK", "PORZAX", "MAIYARAP", "DICERED", "SPRITE", "GUYGEEGEE", "TWOPEE", "1MILL", "JOEY BOY", "THAITANIUM", "YOUNGGU", "GUNNER", "LAZYLOXY", "UNDERDOG", "BEDUPBIW", "KILLMONKER")
def _thai(x):
    import re
    return bool(re.search(r"[ก-๙]", x["t"] + x["a"])) or any(k in x["a"].upper() for k in _THAI_RAP)
def _kworb(path):
    import re, html as H
    s = _get("https://kworb.net/spotify/country/%s" % path)
    out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S):
        cells = [H.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) < 3 or not cells[0].isdigit(): continue
        at = next((c for c in cells if " - " in c), None)
        if not at: continue
        a, t = at.split(" - ", 1)
        m = re.search(r"\s*\(w/ ([^)]*)\)\s*$", t)
        if m: t = t[:m.start()]; a = a.strip() + " w/ " + m.group(1)
        out.append({"p": int(cells[0]), "t": t.strip(), "a": a.strip(), "g": []})
        if len(out) >= 200: break
    return out
def _hip(lst):
    return [x for x in lst if any(("hip" in g.lower() or "rap" in g.lower()) for g in x["g"])]
def trends(force=False):
    if _TR["d"] and not force and time.time() - _TR["t"] < 6 * 3600: return _TR["d"]
    fp = os.path.join(os.getcwd(), "cache", "trends.json")
    if not force and not _TR["d"] and os.path.exists(fp) and time.time() - os.path.getmtime(fp) < 6 * 3600:
        try:
            _TR["d"] = json.load(open(fp, encoding="utf-8")); _TR["t"] = os.path.getmtime(fp); return _TR["d"]
        except Exception: pass
    res = {"ok": True, "at": time.strftime("%Y-%m-%d %H:%M"), "err": [], "lists": {}}
    def rank(lst): return [dict(x, p=i + 1) for i, x in enumerate(lst[:10])]
    try:
        t = _kworb("th_daily.html")
        if t: res["lists"]["th"] = {"src": "Spotify ไทย รายวัน (kworb.net)", "upd": res["at"], "items": t[:10]}
    except Exception as e: res["err"].append("spotify th: " + str(e)[:80])
    try:
        g = _kworb("global_daily.html")
        if g: res["lists"]["global"] = {"src": "Spotify Global รายวัน (kworb.net)", "upd": res["at"], "items": g[:10]}
    except Exception as e: res["err"].append("spotify global: " + str(e)[:80])
    try:
        h, up = _itunes("th", 18)
        th = [x for x in h if _thai(x)]
        if len(th) >= 5: res["lists"]["th_hip"] = {"src": "iTunes ไทย หมวด Hip-Hop/Rap (คัดศิลปินไทย)", "upd": up, "items": rank(th)}
        if "th" not in res["lists"]:
            a, up2 = _itunes("th"); res["lists"]["th"] = {"src": "iTunes ไทย เพลงขายดี (สำรอง)", "upd": up2, "items": a[:10]}
    except Exception as e: res["err"].append("itunes th: " + str(e)[:80])
    try:
        h, up = _itunes("us", 18)
        if h: res["lists"]["global_hip"] = {"src": "iTunes US หมวด Hip-Hop/Rap (ยอดซื้อ)", "upd": up, "items": rank(h)}
    except Exception as e: res["err"].append("itunes us: " + str(e)[:80])
    res["ok"] = bool(res["lists"])
    if res["ok"]:
        _TR["d"] = res; _TR["t"] = time.time()
        try:
            os.makedirs(os.path.dirname(fp), exist_ok=True); json.dump(res, open(fp, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception: pass
    return res

def run_job(jid, body):
    J = JOBS[jid]
    J.update(msg="รอคิวสักครู่ (มีคนอื่นกำลังซิงค์)", pct=1)
    with Slot(J):
        J.update(msg="เริ่มงาน")
        _run(jid, body)


def _run(jid, body):
    J = JOBS[jid]
    try:
        from faster_whisper import WhisperModel
        import importlib, align as _al
        importlib.reload(_al)                           # แก้ align.py แล้วใช้ได้ทันทีไม่ต้องปิดโปรแกรม
        align = _al.align
    except ImportError as e:
        J.update(status="error", err="ยังไม่ได้ติดตั้ง ให้พิมพ์ pip install faster-whisper แล้วเปิด start.py ใหม่ (%s)" % e)
        return
    try:
        lines, name = body["lines"], DEFAULT_MODEL
        td = tempfile.mkdtemp()
        path = os.path.join(td, "in.audio")
        raw = base64.b64decode(body["audio"])
        open(path, "wb").write(raw)
        import hashlib
        cdir = os.path.join(os.getcwd(), "cache")
        os.makedirs(cdir, exist_ok=True)
        hsh = hashlib.sha1(raw).hexdigest()[:16]
        use_vad = body.get("vad", True)
        cfile = os.path.join(cdir, hsh + "_" + DEFAULT_MODEL + ("" if use_vad else "_full") + ".json")
        olds = sorted(pathlib.Path(cdir).glob(hsh + "_*.json"))
        if olds and not body.get("fresh"):                 # เคยฟังเพลงนี้แล้ว: รวมผลทุกครั้งที่เคยฟัง ซิงค์ใหม่ได้ทันที
            sets = [[tuple(w) for w in json.load(open(f, encoding="utf-8"))["words"]] for f in olds if not str(f).endswith(".npy")]
            J.update(msg="ใช้ผลการฟังเพลงนี้ที่เก็บไว้", pct=95)
            S, E, ratio, conf = combine(lines, sets, align)
            res = {"S": [round(x, 2) for x in S], "E": [round(x, 2) for x in E], "ratio": ratio, "conf": [round(c, 2) for c in conf], "cached": True}
            vf = os.path.join(cdir, hsh + "_vocals16k.npy")
            if os.path.exists(vf):
                try:
                    import numpy as np
                    vx = np.load(vf)
                    on, vs, ve = vocal_onsets(vx)
                    res.update(von=[o for o, _ in on], vs=vs, ve=ve, syl=syllables(vx, t0=vs, t1=ve))
                    k = int(body.get("nsing") or 1)
                    if k >= 2: res["vseg"] = voice_segments(vx, min(k, 4), t0=vs, t1=ve)
                    fo = run_fa(lines, vx, vs, ve, cdir, hsh, J)
                    if fo: res["fa"] = fo
                except Exception:
                    traceback.print_exc()
            J.update(status="done", pct=100, result=res)
            return
        pcm = None
        import importlib.util
        vfile = os.path.join(cdir, hsh + "_vocals16k.npy")
        if os.path.exists(vfile):                          # เคยแยกเสียงร้องเพลงนี้แล้ว ใช้ของเดิม
            import numpy as np
            pcm = np.load(vfile); J["sep"] = True
            J.update(msg="ใช้เสียงร้องที่แยกไว้แล้ว", pct=9)
        elif importlib.util.find_spec("demucs"):    # ถ้าติดตั้ง demucs ไว้ จะแยกเสียงร้องให้เองอัตโนมัติ (แม่นกว่ามาก)
            try:
                pcm = vocals_16k(path, J)
                J["sep"] = True
                try:
                    import numpy as np
                    np.save(vfile, pcm)
                except Exception:
                    traceback.print_exc()
            except Exception as e:
                traceback.print_exc()
                J.update(msg="แยกเสียงร้องไม่สำเร็จ ใช้เสียงเต็มแทน (%s)" % str(e)[:80])
        if J.get("sep") and not body.get("whisper") and importlib.util.find_spec("transformers") and importlib.util.find_spec("pythainlp"):
            # ทางลัด: จับเวลาแบบรู้เนื้อจากเสียงร้องที่แยกแล้วเลย (แม่นกว่าและเร็วกว่าให้ AI ถอดคำ ~10 นาที)
            try:
                on, vs, ve = vocal_onsets(pcm)
                fo = run_fa(lines, pcm, vs, ve, cdir, hsh, J)
                ok = [q for q in (fo or []) if q.get("S") is not None]
                spread = (max(q["S"] for q in ok) - min(q["S"] for q in ok)) if ok else 0
                if fo and len(ok) >= .8 * len(lines) and sum(q["conf"] for q in ok) / len(ok) > -4.5 and spread >= .4 * max(1.0, ve - vs) and spread >= min(10.0, .3 * len(pcm) / 16000):
                    S = [q["S"] if q.get("S") is not None else 0 for q in fo]
                    for i in range(1, len(S)): S[i] = max(S[i], S[i - 1] + .2)
                    res = {"S": S, "E": [q["E"] if q.get("E") is not None else S[i] + 2 for i, q in enumerate(fo)],
                           "conf": [round(max(.3, min(.98, (q["conf"] + 6) / 5)), 2) for q in fo], "ratio": 1, "fa": fo,
                           "von": [o for o, _ in on], "vs": vs, "ve": ve, "syl": syllables(pcm, t0=vs, t1=ve), "fast": True}
                    k = int(body.get("nsing") or 1)
                    if k >= 2: res["vseg"] = voice_segments(pcm, min(k, 4), t0=vs, t1=ve)
                    # ตรวจซ้ำด้วย AI ตัวที่ 2 (Whisper ฟังเสียงร้อง): บรรทัดที่ 2 ตัวเห็นตรงกัน = มั่นใจจริง · ไม่ตรง = ให้ผู้ใช้เช็ก
                    try:
                        res.update(second_opinion(lines, pcm, res, name, cdir, hsh, J))
                    except Exception:
                        traceback.print_exc()
                    J.update(status="done", pct=100, result=res)
                    return
                J.update(msg="จับเวลาแบบรู้เนื้อได้ไม่ดีพอ ให้ AI ฟังเพิ่ม", pct=10)
            except Exception:
                traceback.print_exc()
        J.update(msg="โหลดโมเดล %s (ครั้งแรกต้องดาวน์โหลด)" % name, pct=10)
        if name not in MODELS:
            MODELS[name] = WhisperModel(name, device="auto", compute_type="int8", cpu_threads=os.cpu_count() or 4)
        if pcm is None:
            J.update(msg="เตรียมเสียง", pct=12)
            pcm = load_audio(path)
        segs, info = MODELS[name].transcribe(pcm, language="th", word_timestamps=True, beam_size=BEAM,
                                             condition_on_previous_text=False, temperature=0.0, no_repeat_ngram_size=4, max_new_tokens=160,
                                             vad_filter=bool(J.get("sep")) and use_vad, vad_parameters={"min_silence_duration_ms": 600},
                                             hallucination_silence_threshold=2.0, initial_prompt=" ".join(lines)[:600])
        words = []
        import time
        t0 = time.time()
        for sg in segs:
            words += [(w.word, w.start, w.end) for w in sg.words]
            done = min(1, sg.end / max(info.duration, 1))
            J.update(msg="AI ฟังเสียงร้อง (ถึงวินาทีที่ %d จาก %d · ผ่านไป %d วิ)" % (sg.end, info.duration, time.time() - t0), pct=12 + 83 * done)
        try:
            json.dump({"words": words, "sep": bool(J.get("sep")), "model": name}, open(cfile, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception:
            traceback.print_exc()
        sets = [words] + [[tuple(w) for w in json.load(open(f, encoding="utf-8"))["words"]] for f in olds if str(f) != cfile]
        S, E, ratio, conf = combine(lines, sets, align)
        res = {"S": [round(x, 2) for x in S], "E": [round(x, 2) for x in E], "ratio": ratio, "conf": [round(c, 2) for c in conf]}
        if J.get("sep"):
            try:
                on, vs, ve = vocal_onsets(pcm)
                res.update(von=[o for o, _ in on], vs=vs, ve=ve, syl=syllables(pcm, t0=vs, t1=ve))
                k = int(body.get("nsing") or 1)
                if k >= 2: res["vseg"] = voice_segments(pcm, min(k, 4), t0=vs, t1=ve)
                fo = run_fa(lines, pcm, vs, ve, cdir, hsh, J)
                if fo: res["fa"] = fo
            except Exception:
                traceback.print_exc()
        J.update(status="done", pct=100, result=res)
    except Exception as e:
        traceback.print_exc()
        J.update(status="error", err=str(e)[:300] or e.__class__.__name__)


def second_opinion(lines, pcm, res, name, cdir, hsh, J):
    """ฟังเสียงร้องด้วย Whisper แล้วเทียบเวลาต้นบรรทัดกับผลจับเวลาทีละคำ (FA)"""
    from faster_whisper import WhisperModel
    wf = os.path.join(cdir, "%s-vox-%s.json" % (hsh, name))   # ไม่ขึ้นต้น hsh_ (กันไปปนกับไฟล์ผลฟังเดิม)
    if os.path.exists(wf):
        words = [tuple(w) for w in json.load(open(wf, encoding="utf-8"))]
    else:
        J.update(msg="ตรวจซ้ำด้วย AI ตัวที่ 2 (ฟังเสียงร้องอีกรอบ ครั้งแรกราว 1-3 นาที)", pct=70)
        if name not in MODELS:
            MODELS[name] = WhisperModel(name, device="auto", compute_type="int8", cpu_threads=os.cpu_count() or 4)
        import time as _t
        words, box = [], {}
        def work():
            try:
                segs, info = MODELS[name].transcribe(pcm, language="th", word_timestamps=True, beam_size=1, condition_on_previous_text=False,
                                                     temperature=0.0, no_repeat_ngram_size=4, max_new_tokens=120, hallucination_silence_threshold=2.0,
                                                     vad_filter=True, vad_parameters={"min_silence_duration_ms": 400})
                for sg in segs:
                    if box.get("stop"): break
                    words.extend((w.word, w.start, w.end) for w in sg.words)
                    J.update(msg="ตรวจซ้ำด้วย AI ตัวที่ 2 (ถึงวินาทีที่ %d จาก %d)" % (sg.end, info.duration), pct=70 + 28 * min(1, sg.end / max(info.duration, 1)))
                box["ok"] = True
            except Exception as e:
                box["err"] = str(e)
        th = threading.Thread(target=work, daemon=True); th.start()
        lim = max(150, len(pcm) / 16000 * 2.5)          # ไม่เกิน ~2.5 เท่าความยาวเพลง: ช้ากว่านี้ข้ามการตรวจซ้ำ ใช้ผลหลักเลย
        th.join(lim)
        if not box.get("ok"):
            box["stop"] = True
            print("ตรวจซ้ำช้าเกิน/ไม่สำเร็จ ข้ามไป", box.get("err", ""), flush=True)
            return {}
        try: json.dump(words, open(wf, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception: pass
    Sw, Ew, ratio, cw = combine(lines, [words], align)
    S, C = res["S"], list(res["conf"])
    agree = 0; clash = []
    for i in range(len(S)):
        if i >= len(Sw) or Sw[i] is None: continue
        d = abs(S[i] - Sw[i])
        if cw[i] >= .55 and d <= .45:
            C[i] = max(C[i], .97); agree += 1
        elif cw[i] >= .7 and d > .9:
            C[i] = min(C[i], .4); clash.append(i)
    return {"conf": [round(c, 2) for c in C], "second": {"agree": agree, "clash": clash, "n": len(S), "wS": [round(x, 2) if x is not None else None for x in Sw]}}


# ---------- ค้นบีตจาก YouTube (yt-dlp) แล้วคัดฟรี/เสียเงิน ----------
import re as _re
_BEAT_CACHE = {}
_BEAT_LOCK = threading.Lock()
_FFP = _re.compile(r"free\s*(for|4|to\s*use\s*for)\s*profit|\bffp\b|free\s*for\s*commercial|royalty[\s-]*free|ใช้ฟรี.{0,12}หารายได้", _re.I)
_NP = _re.compile(r"non[\s-]*profit|not\s*for\s*profit|free\s*for\s*non|free\s*download|\[free\]|\(free\)|^free\b|\bfree\b.{0,20}\btype beat", _re.I)
_BUYHOST = _re.compile(r"https?://(?:www\.)?(?:beatstars\.com|bsta\.rs|airbit\.com|traktrain\.com|soundee\.com|player\.beatstars\.com|infinity\.airbit\.com|[a-z0-9-]+\.beatstars\.com)[^\s)\]]*", _re.I)
_PRICE = _re.compile(r"(?:\$\s?(\d{1,4}(?:\.\d{1,2})?))|(?:(\d{1,4}(?:\.\d{1,2})?)\s?(?:usd|\$))", _re.I)
_BPM = _re.compile(r"(\d{2,3})\s?bpm", _re.I)
_KEY = _re.compile(r"\b([A-G](?:#|b|♯|♭)?\s?(?:m|min|minor|maj|major)?)\s*(?:key)?\b(?=[^a-z]|$)")
_KEY2 = _re.compile(r"key[:\s]+([A-G](?:#|b)?\s?(?:m|min|minor|maj|major)?)", _re.I)


def _beat_info(v):
    title = v.get("title") or ""
    desc = v.get("description") or ""
    txt = title + "\n" + desc
    head = title + "\n" + desc[:600]
    free = None
    if _FFP.search(head): free = "profit"
    elif _NP.search(title) or _re.search(r"non[\s-]*profit|not\s*for\s*profit|free\s*for\s*non", desc[:800], _re.I): free = "np"
    buy = _BUYHOST.findall(desc)
    buy = [b.rstrip(".,") for b in buy]
    prices = []
    for a, b in _PRICE.findall(desc[:3000]):
        try:
            p = float(a or b)
            if 5 <= p <= 5000: prices.append(p)
        except Exception: pass
    prices = sorted(set(prices))[:8]
    bpm = None
    m = _BPM.search(txt)
    if m and 50 <= int(m.group(1)) <= 220: bpm = int(m.group(1))
    key = None
    m = _KEY2.search(txt)
    if m: key = m.group(1).strip()
    credit = bool(_re.search(r"credit|prod\.?\s*by|\(prod|must\s+include", desc[:1500], _re.I))
    paid = bool(buy or prices or _re.search(r"purchase|buy\s|lease|exclusive|untagged|license", desc[:2000], _re.I))
    vid = v.get("id") or ""
    return {"id": vid, "title": title[:140], "channel": (v.get("channel") or v.get("uploader") or "")[:60],
            "url": v.get("webpage_url") or ("https://www.youtube.com/watch?v=" + vid), "thumb": "https://i.ytimg.com/vi/%s/mqdefault.jpg" % vid if vid else "",
            "dur": v.get("duration"), "views": v.get("view_count"), "date": v.get("upload_date"),
            "free": free, "paid": paid, "buy": buy[0] if buy else "", "prices": prices, "bpm": bpm, "key": key, "credit": credit}


def beat_search(q, n=12, force=False):
    q = (q or "").strip()[:120]
    if not q: return {"ok": False, "err": "ใส่คำค้นก่อน"}
    ck = q.lower() + "|" + str(n)
    with _BEAT_LOCK:
        c = _BEAT_CACHE.get(ck)
        if c and not force and time.time() - c[0] < 6 * 3600: return c[1]
    try:
        import yt_dlp
    except Exception:
        return {"ok": False, "need": "yt-dlp", "err": "ยังไม่ได้ติดตั้งตัวค้น YouTube ปิดหน้าต่างดำแล้วดับเบิลคลิก start.bat ใหม่ (จะติดตั้ง yt-dlp ให้เอง)"}
    base = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True, "socket_timeout": 15}
    try:
        with yt_dlp.YoutubeDL(dict(base, extract_flat="in_playlist")) as y:
            r = y.extract_info("ytsearch%d:%s" % (min(n + 6, 30), q), download=False) or {}
        flat = [e for e in (r.get("entries") or []) if e and e.get("id")]
        flat = [e for e in flat if not e.get("duration") or 60 <= e["duration"] <= 600][:n]
    except Exception as e:
        return {"ok": False, "err": "ค้น YouTube ไม่สำเร็จ: " + str(e)[:160]}
    out = [None] * len(flat)
    def one(i, e):
        try:
            with yt_dlp.YoutubeDL(base) as y:
                v = y.extract_info("https://www.youtube.com/watch?v=" + e["id"], download=False, process=False) or {}
        except Exception:
            v = dict(e)
        out[i] = _beat_info(v)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda a: one(*a), enumerate(flat)))
    res = {"ok": True, "q": q, "t": int(time.time()), "items": [x for x in out if x]}
    with _BEAT_LOCK:
        _BEAT_CACHE[ck] = (time.time(), res)
        if len(_BEAT_CACHE) > 60:
            for k in sorted(_BEAT_CACHE, key=lambda k: _BEAT_CACHE[k][0])[:20]: _BEAT_CACHE.pop(k, None)
    return res


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        super().end_headers()

    def _json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _local(self):
        ip = (self.client_address or ("",))[0]
        return ip in ("127.0.0.1", "::1", "localhost") or ip.startswith("::ffff:127.") or ip.startswith("127.")
    def _auth(self):
        if not self._local():
            k = self.headers.get("X-Key", "")
            if k == PIN or (KEY and k == KEY): return True
            self._json({"status": "error", "err": "ใส่ PIN 6 หลักจากหน้าแอปบนคอมก่อน"}, 401)
            return False
        if KEY and self.headers.get("X-Key", "") != KEY:
            self._json({"status": "error", "err": "รหัสผ่านไม่ถูกต้อง"}, 401)
            return False
        return True

    def do_GET(self):
        if self.path.startswith("/api/lan"):
            if not self._local(): return self.send_error(403)
            ip = lan_ip(); return self._json({"ip": ip, "port": self.server.server_address[1], "pin": PIN, "url": ("http://%s:%d/" % (ip, self.server.server_address[1])) if ip else "", "open": HOST == "0.0.0.0"})
        if not self._local():
            pth = self.path.split("?")[0]
            if pth.endswith("/") and pth != "/": return self.send_error(403)
            if (pth.startswith("/api/mixhist") or pth.startswith("/api/beats") or pth.startswith("/api/oembed") or pth.startswith("/api/job")) and not self._auth(): return
        if self.path.startswith("/api/ping"): return self._json({"ok": True, "auth": bool(KEY) or not self._local(), "lan": not self._local(), "model": DEFAULT_MODEL, "v": 24, "beats": True, "trends": True, "mv": True, "report": True, "oembed": True, "queue": len(_Q), "mix": True, "img": __import__("importlib.util").util.find_spec("diffusers") is not None, "sep": __import__("importlib.util").util.find_spec("demucs") is not None})
        if self.path.startswith("/api/trends"):
            try: return self._json(trends("force=1" in self.path))
            except Exception as e: return self._json({"ok": False, "err": [str(e)[:160]]}, 502)
        if self.path.startswith("/api/mixhist"):
            try: return self._json(json.load(open(os.path.join(os.getcwd(), "mixes", "history.json"), encoding="utf-8")))
            except Exception: return self._json([])
        if self.path.startswith("/api/concepts"):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("mixer_mod", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mixer.py")); mx = importlib.util.module_from_spec(spec); spec.loader.exec_module(mx)
                return self._json({k: {"n": v["n"], "tags": v["tags"]} for k, v in mx.CONCEPTS.items()})
            except Exception as e: return self._json({"err": str(e)})
        if self.path.startswith("/api/oembed"):
            # อ่านชื่อเพลง/ศิลปินจากลิงก์ YouTube หรือ Spotify (ไม่ดึงไฟล์เสียง)
            try:
                import urllib.parse, urllib.request
                u = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("url", [""])[0].strip()
                host = urllib.parse.urlparse(u).hostname or ""
                if host.endswith(("youtube.com", "youtu.be")): api = "https://www.youtube.com/oembed?format=json&url="
                elif host.endswith("spotify.com"): api = "https://open.spotify.com/oembed?url="
                else: return self._json({"ok": False, "err": "รองรับเฉพาะลิงก์ YouTube หรือ Spotify"}, 400)
                req = urllib.request.Request(api + urllib.parse.quote(u, safe=""), headers={"User-Agent": "SlopeNorthSide/1.0"})
                d = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8"))
                src = "spotify" if "spotify" in host else "youtube"
                return self._json({"ok": True, "src": src, "title": d.get("title", ""), "author": d.get("author_name", ""), "thumb": d.get("thumbnail_url", "")})
            except Exception as e:
                return self._json({"ok": False, "err": "อ่านลิงก์ไม่ได้: " + str(e)[:120]}, 502)
        if self.path.startswith("/api/beats"):
            import urllib.parse
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try: n = max(4, min(20, int(qs.get("n", ["12"])[0])))
            except Exception: n = 12
            try: return self._json(beat_search(qs.get("q", [""])[0], n, qs.get("force", ["0"])[0] == "1"))
            except Exception as e: return self._json({"ok": False, "err": str(e)[:200]}, 500)
        if self.path.startswith("/api/job"):
            if not self._auth(): return
            return self._json(JOBS.get(self.path.split("id=")[-1], {"status": "error", "err": "ไม่พบงาน"}))
        if self.path.split("?")[0].endswith((".py", ".bat", ".command", ".txt")): return self.send_error(404)
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/report"):
            # บันทึกข้อผิดพลาด/เรื่องที่แจ้งจากแอป ไว้ให้ Claude ตรวจ (reports/reports.jsonl)
            n = min(int(self.headers.get("Content-Length", 0) or 0), 64 * 1024)
            try:
                body = json.loads(self.rfile.read(n) or b"{}")
                d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports"); os.makedirs(d, exist_ok=True)
                fp = os.path.join(d, "reports.jsonl")
                if os.path.exists(fp) and os.path.getsize(fp) > 5 * 1048576: os.replace(fp, fp + ".old")
                with open(fp, "a", encoding="utf-8") as f: f.write(json.dumps(body, ensure_ascii=False)[:8000] + "\n")
            except Exception as e:
                return self._json({"ok": False, "err": str(e)}, 400)
            return self._json({"ok": True})
        if self.path.startswith("/api/upload"):
            # อัปโหลดไฟล์เสียงแบบดิบ (ไม่ต้องแปลง base64) สำหรับมิกซ์
            if not self._auth(): return
            n = int(self.headers.get("Content-Length", 0))
            if n > 400 * 1048576: return self._json({"status": "error", "err": "ไฟล์ใหญ่เกิน 400MB"}, 413)
            ext = os.path.splitext(self.path.split("name=")[-1] if "name=" in self.path else "a.wav")[1][:6] or ".wav"
            fid = uuid.uuid4().hex[:10]; fpth = os.path.join(tempfile.gettempdir(), "sns_" + fid + ext)
            with open(fpth, "wb") as f:
                left = n
                while left > 0:
                    chunk = self.rfile.read(min(1 << 20, left))
                    if not chunk: break
                    f.write(chunk); left -= len(chunk)
            UPL[fid] = fpth
            return self._json({"id": fid})
        if self.path.startswith("/api/scenes"):
            if not self._auth(): return
            if queue_full(): return self._json({"status": "error", "err": "คิวเต็ม ลองใหม่อีกสักครู่"}, 503)
            n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n) or b"{}")
            jid = uuid.uuid4().hex[:8]; JOBS[jid] = {"status": "run", "pct": 1, "msg": "รอคิว"}
            threading.Thread(target=scenes_job, args=(jid, body), daemon=True).start()
            return self._json({"id": jid})
        if self.path.startswith("/api/mix"):
            if not self._auth(): return
            n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n) or b"{}")
            if queue_full(): return self._json({"status": "error", "err": "คิวเต็ม (มีคนใช้เยอะ) ลองใหม่อีกสักครู่"}, 503)
            jid = uuid.uuid4().hex[:8]; JOBS[jid] = {"status": "run", "pct": 1, "msg": "รอคิว"}
            threading.Thread(target=mix_job, args=(jid, body), daemon=True).start()
            return self._json({"id": jid})
        if self.path.startswith("/api/image"):
            if queue_full(): return self._json({"status": "error", "err": "คิวเต็ม ลองใหม่อีกสักครู่"}, 503)
            # วาดภาพปกด้วย AI บนเครื่อง (img_gen.py) ส่งกลับเป็น PNG
            if not self._auth(): return
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            try:
                import importlib.util
                fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img_gen.py")
                spec = importlib.util.spec_from_file_location("img_gen", fp); ig = sys.modules.get("img_gen")
                if ig is None:
                    ig = importlib.util.module_from_spec(spec); spec.loader.exec_module(ig); sys.modules["img_gen"] = ig
                with Slot():
                    MODELS.clear(); SEP.clear(); import gc; gc.collect()   # คืน RAM ให้ตัววาดภาพ (AI ถอดเสียงจะโหลดใหม่เองเมื่อซิงค์)
                    data = ig.generate(body.get("prompt", ""), body.get("seed", 0), body.get("steps", 2), body.get("size", 512))
                self.send_response(200); self.send_header("Content-Type", "image/png"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            except Exception as e:
                traceback.print_exc()
                self._json({"status": "error", "err": str(e)[:300]}, 500)
            return
        if self.path.startswith("/api/align"):
            if not self._auth(): return
            n = int(self.headers.get("Content-Length", 0))
            if n > MAX_BODY: return self._json({"status": "error", "err": "ไฟล์ใหญ่เกินไป"}, 413)
            body = json.loads(self.rfile.read(n))
            if queue_full(): return self._json({"status": "error", "err": "คิวเต็ม (มีคนใช้เยอะ) ลองใหม่อีกสักครู่"}, 503)
            if len(JOBS) > 50:
                for k in list(JOBS)[:25]: JOBS.pop(k, None)
            jid = uuid.uuid4().hex[:8]
            JOBS[jid] = {"status": "run", "pct": 1, "msg": "เริ่มงาน"}
            threading.Thread(target=run_job, args=(jid, body), daemon=True).start()
            return self._json({"id": jid})
        self.send_error(404)


if __name__ == "__main__":
    http.server.ThreadingHTTPServer.allow_reuse_address = os.name != "nt"   # Windows: ห้ามใช้พอร์ตซ้ำ
    if os.environ.get("PRELOAD", "1") == "1" and os.environ.get("PORT"):          # บนเซิร์ฟเวอร์: โหลดโมเดลรอไว้เลย
        def _pre():
            try:
                from faster_whisper import WhisperModel
                MODELS[DEFAULT_MODEL] = WhisperModel(DEFAULT_MODEL, device="auto", compute_type="int8")
                print("โมเดลพร้อมแล้ว", DEFAULT_MODEL)
            except Exception as e:
                print("โหลดโมเดลล่วงหน้าไม่สำเร็จ", e)
        threading.Thread(target=_pre, daemon=True).start()
    if os.name == "nt" and "--keep-others" not in sys.argv:   # ปิดโปรแกรมนี้ตัวเก่าที่ยังค้าง (กินแรม) ก่อนเปิดตัวใหม่
        try:
            ps = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' -and $_.ProcessId -ne %d "
                  "-and $_.CommandLine -like '*start.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" % os.getpid())
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=30)
            import time
            time.sleep(1.5)
        except Exception as e:
            print("ปิดตัวเก่าไม่สำเร็จ", e)
    srv = None
    for PORT in range(PORT, PORT + 10):              # ถ้าพอร์ตถูกใช้อยู่ (เปิดซ้ำ) ลองพอร์ตถัดไป
        try:
            srv = http.server.ThreadingHTTPServer((HOST, PORT), H)
            break
        except OSError:
            continue
    if srv is None:
        sys.exit("เปิดเซิร์ฟเวอร์ไม่ได้ พอร์ตไม่ว่าง")
    with srv as s:
        if "--no-browser" not in sys.argv and not os.environ.get("PORT"):
            threading.Timer(.8, lambda: webbrowser.open("http://localhost:%d/" % PORT)).start()
        print("เปิดแอปที่ http://localhost:%d  (ปิดหน้าต่างนี้เพื่อหยุด)" % PORT, flush=True)
        if HOST == "0.0.0.0" and lan_ip():
            print("ใช้ในมือถือ (ต่อ Wi-Fi เดียวกับคอม): http://%s:%d   PIN: %s" % (lan_ip(), PORT, PIN), flush=True)
            print("ถ้า Windows ถามเรื่อง Firewall ให้กด Allow (Private network)", flush=True)
        s.serve_forever()
