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
