# ดึงรายการบีต "type beat" จริงจาก YouTube (ฟรี ไม่ใช้ key ผ่าน yt-dlp) เก็บเป็น data/beats.json ให้แอปโชว์บีตจริง
# รันใน GitHub Actions ทุกวัน · ใช้: python3 ci/beats_cache.py data/beats.json
import json, subprocess, sys, time, re
ART = ["The Weeknd","Drake","Kendrick Lamar","Travis Scott","Juice WRLD","Central Cee","Mac Miller","Frank Ocean","Lil Peep","XXXTENTACION","SZA",
       "Tyler, The Creator","Don Toliver","Brent Faiyaz","PARTYNEXTDOOR","Joji","Lil Uzi Vert","J. Cole","Kanye West","Billie Eilish","Lana Del Rey",
       "Bryson Tiller","Headie One","Kordhell","Eminem","Pop Smoke","Future","Gunna","Lil Baby","21 Savage","Playboi Carti","Post Malone","Daniel Caesar",
       "6LACK","Giveon","Rod Wave","Polo G","NBA YoungBoy","Dave","Digga D","SPRITE","MILLI","YOUNGOHM","F.HERO","Three Man Down"]
GEN = {"rnb":"dark rnb type beat","drill":"uk drill type beat","trap":"melodic trap type beat","lofi":"lofi hip hop type beat","rap":"boom bap type beat",
       "thai":"thai rnb type beat","emo":"emo rap guitar type beat","phonk":"phonk type beat","pop":"pop rnb type beat"}
def search(q, n=14):
    try:
        r = subprocess.run(["yt-dlp", "ytsearch%d:%s" % (n, q), "--flat-playlist", "-J", "--no-warnings"], capture_output=True, text=True, timeout=90)
        j = json.loads(r.stdout or "{}")
    except Exception as e:
        print("fail", q, e); return []
    out = []
    for e in j.get("entries") or []:
        t = e.get("title") or ""; d = e.get("duration") or 0
        if not e.get("id") or not re.search(r"beat|instrumental|prod", t, re.I): continue
        if d and (d < 60 or d > 600): continue
        out.append({"id": e["id"], "t": t[:120], "ch": (e.get("channel") or e.get("uploader") or "")[:60], "d": int(d or 0), "v": int(e.get("view_count") or 0),
                    "free": bool(re.search(r"free\s*(for\s*profit|download|beat)|\bfree\b", t, re.I))})
    return out
res = {"updated": time.strftime("%Y-%m-%d"), "artists": {}, "genres": {}}
for a in ART:
    res["artists"][a.lower()] = search(a + " type beat"); print(a, len(res["artists"][a.lower()]))
for k, q in GEN.items():
    res["genres"][k] = search(q, 18); print(k, len(res["genres"][k]))
ok = sum(len(v) for v in res["artists"].values()) + sum(len(v) for v in res["genres"].values())
if ok < 30:
    print("too few results (%d) — YouTube may be blocking; keep old file" % ok); sys.exit(1)
json.dump(res, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":")); print("total", ok)
