"""Slope North Side · ซิงค์เนื้อบนคลาวด์ฟรี (GitHub Actions)
อ่านงานที่เข้ารหัสจาก jobs/*.bin (กิ่ง sync-jobs) → แยกเสียงร้อง (demucs) → จับเวลาทีละคำแบบรู้เนื้อ (fa.py)
→ เขียนผลที่เข้ารหัสด้วยกุญแจของงานนั้นไว้ที่ results/<id>.bin แล้วลบไฟล์งาน
รูปแบบไฟล์งาน: b"SNS1" | len(2) | RSA-OAEP(SHA-256) ห่อกุญแจ AES-256 | IV(12) | AES-GCM( len(4) | JSON | เสียง )
รูปแบบผล:      b"SNR1" | IV(12) | AES-GCM( JSON )"""
import os, sys, json, glob, struct, traceback, tempfile, time

CODE = os.path.abspath(os.environ.get("SNS_CODE", "code"))
JOBS = os.path.abspath(os.environ.get("SNS_JOBS", "jobs"))
sys.path.insert(0, os.path.join(CODE, "src", "app"))


def keys():
    from cryptography.hazmat.primitives import serialization
    pem = os.environ["SNS_SYNC_KEY"].encode()
    return serialization.load_pem_private_key(pem, password=None)


def open_job(priv, raw):
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if raw[:4] != b"SNS1": raise ValueError("bad magic")
    n = struct.unpack(">H", raw[4:6])[0]
    wk = raw[6:6 + n]; iv = raw[6 + n:18 + n]; ct = raw[18 + n:]
    key = priv.decrypt(wk, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    pt = AESGCM(key).decrypt(iv, ct, None)
    jl = struct.unpack(">I", pt[:4])[0]
    meta = json.loads(pt[4:4 + jl].decode("utf-8"))
    return key, meta, pt[4 + jl:]


def seal(key, obj):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    iv = os.urandom(12)
    return b"SNR1" + iv + AESGCM(key).encrypt(iv, json.dumps(obj, ensure_ascii=False).encode("utf-8"), None)


class J(dict):
    def update(self, *a, **k):
        super().update(*a, **k)
        if "msg" in self: print("  ·", self.get("msg"), self.get("pct", ""), flush=True)



# ---------- ตรวจซ้ำด้วยหู AI ตัวที่ 2 (Whisper) แล้วแก้คำที่ FA วางผิดที่ ----------
# FA มักยืด/บีบเนื้อเมื่อเสียงร้องเร็วหรือมีช่วงอินโทร · Whisper ฟังทีละ 12 วิ โดยบอกเนื้อช่วงนั้นให้รู้
# แล้วเทียบตัวอักษรกับเนื้อจริง → ได้เวลาทีละคำ · แทนที่เฉพาะบรรทัดที่หลักฐานชัด
TH_C = set(chr(c) for c in range(0x0E01, 0x0E2F)); TH_V = set('ะาำิีึืุูเแโใไๅ')
EQ = [set('ขคฆ'), set('ทธฑฒถฐ'), set('สศษซ'), set('พภผ'), set('ฟฝ'), set('ตฏ'), set('ดฎ'), set('ชฌฉ'), set('นณ'), set('ลฬร'), set('ยญ'), set('ฮห'), set('ใไ'), set('aeiou')]
def _sk(s): return [c for c in s.lower() if c in TH_C or c in TH_V or (c.isascii() and c.isalnum())]
def _sim(a, b):
    if a == b: return 2
    for g in EQ:
        if a in g and b in g: return 1
    return -1
def _align(A, B):
    import numpy as np
    n, m = len(A), len(B); G = -1
    S = np.zeros((n + 1, m + 1), dtype=np.int32); P = np.zeros((n + 1, m + 1), dtype=np.int8)
    for i in range(1, n + 1): S[i, 0] = S[i - 1, 0] + G; P[i, 0] = 1
    for j in range(1, m + 1): S[0, j] = 0; P[0, j] = 2
    for i in range(1, n + 1):
        a = A[i - 1]
        for j in range(1, m + 1):
            d = S[i - 1, j - 1] + _sim(a, B[j - 1]); u = S[i - 1, j] + G; l = S[i, j - 1] + G
            if d >= u and d >= l: S[i, j] = d; P[i, j] = 0
            elif u >= l: S[i, j] = u; P[i, j] = 1
            else: S[i, j] = l; P[i, j] = 2
    j = int(S[n].argmax()); i = n; mp = {}
    while i > 0 and j > 0:
        p = P[i, j]
        if p == 0:
            if _sim(A[i - 1], B[j - 1]) > 0: mp[i - 1] = j - 1
            i -= 1; j -= 1
        elif p == 1: i -= 1
        else: j -= 1
    return mp
def refine(wm, pcm, lines, fo, res, win=12.0, step=10.0):
    import statistics
    n = len(pcm) / 16000.0; ww = []; cand = {}
    S0 = [q.get("S") for q in fo]; E0 = [q.get("E") for q in fo]
    t = max(0.0, (min([s for s in S0 if s is not None] or [0]) - 1.0))
    while t < n - 1:
        a, b = t, min(n, t + win)
        idx = [j for j in range(len(fo)) if S0[j] is not None and S0[j] < b + 2.5 and (E0[j] or S0[j] + 2) > a - 2.5]
        if idx:
            lo, hi = max(0, idx[0] - 1), min(len(fo), idx[-1] + 2); idx = list(range(lo, hi))
            prompt = " ".join(lines[j] for j in idx)[:700]
            segs, info = wm.transcribe(pcm[int(a * 16000):int(b * 16000)], language="th", word_timestamps=True, beam_size=5,
                                       condition_on_previous_text=False, vad_filter=False, initial_prompt=prompt)
            B = []; BT = []
            for sg in segs:
                for w in sg.words:
                    ws, we = w.start + a, w.end + a; ww.append([w.word, round(ws, 2), round(we, 2), round(w.probability, 2)])
                    cs = _sk(w.word)
                    for k, ch in enumerate(cs): B.append(ch); BT.append(ws + (we - ws) * k / max(1, len(cs)))
            A = []; AW = []
            for j in idx:
                for wi, u in enumerate(fo[j].get("units") or []):
                    for ch in _sk(u[1]): A.append(ch); AW.append((j, wi))
            if A and B:
                first = {}
                for ia, ib in _align(A, B).items():
                    first.setdefault(AW[ia], []).append(BT[ib])
                for key, v in first.items():
                    tv = min(v)
                    if a + .5 < tv < b - .5 or (a == 0 and tv < b - .5):  # ขอบหน้าต่างเชื่อไม่ได้
                        cand.setdefault(key, []).append(tv)
        t += step
    nfix = 0
    for j, q in enumerate(fo):
        U = q.get("units") or []
        if len(U) < 2 or S0[j] is None: continue
        got = {i: statistics.median(cand[(j, i)]) for i in range(len(U)) if (j, i) in cand}
        if len(got) < max(2, .6 * len(U)): continue
        ks = sorted(got); tt = [got[k] for k in ks]
        if any(tt[i + 1] <= tt[i] for i in range(len(tt) - 1)): continue
        if any(tt[i + 1] - tt[i] > 2.5 for i in range(len(tt) - 1)): continue
        if abs(tt[0] - U[ks[0]][2]) > 6: continue
        diff = statistics.median(abs(got[k] - U[k][2]) for k in ks)
        if diff < .2: continue
        new = []
        for i in range(len(U)):
            if i in got: new.append(got[i]); continue
            pv = max([k for k in ks if k < i], default=None); nx = min([k for k in ks if k > i], default=None)
            if pv is not None and nx is not None: new.append(got[pv] + (got[nx] - got[pv]) * (i - pv) / (nx - pv))
            elif pv is not None: new.append(got[pv] + (U[i][2] - U[pv][2]))
            else: new.append(got[nx] - (U[nx][2] - U[i][2]))
        for i in range(len(U)):
            U[i][2] = round(new[i], 2); U[i][3] = round(min(new[i + 1] - .02 if i + 1 < len(U) else new[i] + .6, new[i] + .6), 2)
        q["S"] = U[0][2]; q["E"] = round(U[-1][3] + .3, 2)
        res["S"][j] = q["S"]; res["E"][j] = q["E"]; res["conf"][j] = max(res["conf"][j], .85); nfix += 1
    for i in range(1, len(res["S"])):
        if res["S"][i] <= res["S"][i - 1]: res["S"][i] = res["S"][i - 1] + .05
    for i in range(len(res["S"]) - 1):
        if res["E"][i] > res["S"][i + 1] - .03: res["E"][i] = round(res["S"][i + 1] - .03, 2)
    res["refined"] = nfix
    print("  Whisper ตรวจซ้ำ แก้", nfix, "บรรทัด", flush=True)
    return ww

def run(meta, audio):
    import numpy as np
    import start as S
    lines = meta["lines"]
    td = tempfile.mkdtemp()
    path = os.path.join(td, "in.audio")
    open(path, "wb").write(audio)
    job = J()
    t0 = time.time()
    pcm = S.vocals_16k(path, job)
    print("  แยกเสียงร้อง", round(time.time() - t0), "วิ", len(pcm) / 16000, "วิของเพลง", flush=True)
    on, vs, ve = S.vocal_onsets(pcm)
    cdir = os.path.join(td, "cache"); os.makedirs(cdir, exist_ok=True)
    fo = S.run_fa(lines, pcm, vs, ve, cdir, "job", job)
    if not fo: raise RuntimeError("จับเวลาทีละคำไม่สำเร็จ")
    ok = [q for q in fo if q.get("S") is not None]
    S_ = [q["S"] if q.get("S") is not None else 0 for q in fo]
    for i in range(1, len(S_)): S_[i] = max(S_[i], S_[i - 1] + .2)
    res = {"S": S_, "E": [q["E"] if q.get("E") is not None else S_[i] + 2 for i, q in enumerate(fo)],
           "conf": [round(max(.3, min(.98, (q["conf"] + 6) / 5)), 2) for q in fo], "ratio": 1, "fa": fo,
           "von": [o for o, _ in on], "vs": vs, "ve": ve, "syl": S.syllables(pcm, t0=vs, t1=ve), "fast": True, "cloud": True}
    k = int(meta.get("nsing") or 1)
    if k >= 2: res["vseg"] = S.voice_segments(pcm, min(k, 4), t0=vs, t1=ve)
    # ความเห็นที่ 2: Whisper ฟังเสียงร้องที่แยกแล้ว ได้คำ+เวลา ใช้ตรวจ/แก้ช่วงที่ FA ยืดผิด
    try:
        from faster_whisper import WhisperModel
        t1 = time.time()
        wm = WhisperModel(meta.get("wmodel") or "large-v3", device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
        ww = []
        win = float(meta.get("wwin") or 0)
        if meta.get("wranges"):
            # ฟังเฉพาะช่วงที่ขอ: [[เริ่ม, จบ, "prompt"], ...] ผลแต่ละช่วงติดป้าย r
            for ri, rg in enumerate(meta["wranges"]):
                a = int(rg[0] * 16000); b = int(rg[1] * 16000)
                segs, info = wm.transcribe(pcm[a:b], language="th", word_timestamps=True, beam_size=5,
                                           condition_on_previous_text=False, vad_filter=False,
                                           initial_prompt=(rg[2] if len(rg) > 2 else None))
                for sg in segs:
                    ww.extend([w.word, round(w.start + rg[0], 2), round(w.end + rg[0], 2), round(w.probability, 2), ri] for w in sg.words)
        elif win > 0:
            # ฟังทีละช่วงสั้น ๆ (ไม่ใช้ VAD) — กันอาการหยุดถอดกลางเพลงแร็ปเร็ว
            n = len(pcm) / 16000.0; t = 0.0
            while t < n - .5:
                a = int(t * 16000); b = int(min(n, t + win + 1.0) * 16000)
                segs, info = wm.transcribe(pcm[a:b], language="th", word_timestamps=True, beam_size=3,
                                           condition_on_previous_text=False, vad_filter=False,
                                           initial_prompt="Bedupbiw, Slope North Side. แร็ปไทย")
                for sg in segs:
                    ww.extend([w.word, round(w.start + t, 2), round(w.end + t, 2), round(w.probability, 2)] for w in sg.words if w.start < win + .5)
                t += win
        else:
            ww = refine(wm, pcm, lines, fo, res)
        res["whisper"] = ww
        print("  Whisper", len(ww), "คำ", round(time.time() - t1), "วิ", flush=True)
    except Exception as e:
        print("  Whisper ข้าม:", e, flush=True)
    spread = (max(q["S"] for q in ok) - min(q["S"] for q in ok)) if ok else 0
    res["spread"] = round(spread, 2)
    print("  เสร็จ", len(ok), "/", len(lines), "บรรทัด · ช่วง", round(spread, 1), "วิ · รวม", round(time.time() - t0), "วิ", flush=True)
    return res


def main():
    files = sorted(glob.glob(os.path.join(JOBS, "jobs", "*.bin")))[:4]
    if not files:
        print("ไม่มีงาน"); return
    priv = keys()
    os.makedirs(os.path.join(JOBS, "results"), exist_ok=True)
    for f in files:
        jid = os.path.basename(f)[:-4]
        print("งาน", jid, os.path.getsize(f) // 1024, "KB", flush=True)
        key = None
        try:
            key, meta, audio = open_job(priv, open(f, "rb").read())
            out = {"ok": True, "result": run(meta, audio)}
        except Exception as e:
            traceback.print_exc()
            out = {"ok": False, "err": str(e)[:300] or e.__class__.__name__}
        if key is not None:
            open(os.path.join(JOBS, "results", jid + ".bin"), "wb").write(seal(key, out))
        os.remove(f)


if __name__ == "__main__":
    main()
