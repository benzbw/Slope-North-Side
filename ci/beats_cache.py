# ดึงรายการบีต "type beat" จริงจาก YouTube (ฟรี ไม่ใช้ key ผ่าน yt-dlp) เก็บเป็น data/beats.json ให้แอปโชว์บีตจริง
# รันใน GitHub Actions ทุกวัน · ใช้: python3 ci/beats_cache.py data/beats.json
import json, subprocess, sys, time, re
ART = ["The Weeknd","Drake","Kendrick Lamar","Travis Scott","Juice WRLD","Central Cee","Mac Miller","Frank Ocean","Lil Peep","XXXTENTACION","SZA",
       "Tyler, The Creator","Don Toliver","Brent Faiyaz","PARTYNEXTDOOR","Joji","Lil Uzi Vert","J. Cole","Kanye West","Billie Eilish","Lana Del Rey",
       "Bryson Tiller","Headie One","Kordhell","Eminem","Pop Smoke","Future","Gunna","Lil Baby","21 Savage","Playboi Carti","Post Malone","Daniel Caesar",
       "6LACK","Giveon","Rod Wave","Polo G","NBA YoungBoy","Dave","Digga D","SPRITE","MILLI","YOUNGOHM","F.HERO","Three Man Down","Metro Boomin","Ken Carson","Yeat","Destroy Lonely","Lil Tecca","Lil Wayne","Nas","Tyla","Burna Boy","Tems","Summer Walker","Chris Brown","Partynextdoor","Lil Durk","Kodak Black","Doja Cat","Jack Harlow","Baby Keem","Daniel Caesar","Joji"]
GEN = {"rnb":"dark rnb type beat","drill":"uk drill type beat","trap":"melodic trap type beat","lofi":"lofi hip hop type beat","rap":"boom bap type beat",
       "thai":"thai rnb type beat","emo":"emo rap guitar type beat","phonk":"phonk type beat","pop":"pop rnb type beat"}
# บีตกระแส: ตามเทรนด์ที่แร็ปเปอร์ใช้ รีมิกซ์ และเอาเพลงเก่ามาทำใหม่ (อัปเดตทุกวัน)
Y = time.strftime("%Y")
TRENDS = {
 "hot":   ["มาแรงตอนนี้", "บีตที่คนทำเยอะช่วงนี้", ["trending type beat " + Y, "hard type beat " + Y, "type beat " + Y + " new"]],
 "viral": ["ไวรัล TikTok", "บีตสั้นติดหู เหมาะทำคลิป", ["tiktok viral rap beat " + Y, "viral tiktok type beat", "catchy rap beat " + Y]],
 "remix": ["รีมิกซ์", "เพลงดังทำเป็นบีตแร็พ (drill/club remix)", ["drill remix beat " + Y, "rap remix instrumental " + Y, "trap remix type beat"]],
 "flip":  ["เพลงเก่ามาทำใหม่", "sample flip: soul, R&B ยุค 90, เพลงเก่า", ["sample flip type beat " + Y, "soul sample type beat " + Y, "90s r&b sample type beat", "old school sample boom bap beat"]],
 "jersey":["Jersey club / Jersey drill", "เบาซ์ เร็ว เต้นได้", ["jersey club type beat " + Y, "jersey drill type beat"]],
 "rage":  ["Rage", "ซินธ์แตก หนัก เร็ว 150+ BPM", ["rage type beat " + Y, "ken carson rage type beat"]],
 "afro":  ["Afro × trap / Afro drill", "จังหวะแอฟริกันบนกลอง trap/drill", ["afro drill type beat " + Y, "afrobeat trap type beat " + Y]],
 "rnbdrill":["R&B × drill / Vocal chop", "เสียงร้องตัดเป็นเมโลดี้บนกลอง drill", ["r&b drill type beat " + Y, "vocal chop type beat " + Y]],
 "phonk": ["Phonk ใหม่", "Brazilian / house / drift phonk", ["brazilian phonk " + Y, "funk phonk " + Y, "drift phonk " + Y, "house phonk " + Y]],
 "thai":  ["แดนซ์ / รีมิกซ์ไทย", "บีตแร็พไทยและบีตแดนซ์สายไทย", ["บีทแร็พไทย " + Y, "thai type beat " + Y, "บีทแดนซ์ " + Y, "thai rap beat free"]],
}
def search(q, n=14, pat=r"beat|instrumental|prod"):
    try:
        r = subprocess.run(["yt-dlp", "ytsearch%d:%s" % (n, q), "--flat-playlist", "-J", "--no-warnings"], capture_output=True, text=True, timeout=90)
        j = json.loads(r.stdout or "{}")
    except Exception as e:
        print("fail", q, e); return []
    out = []
    for e in j.get("entries") or []:
        t = e.get("title") or ""; d = e.get("duration") or 0
        if not e.get("id") or not re.search(pat, t, re.I): continue
        if d and (d < 60 or d > 600): continue
        out.append({"id": e["id"], "t": t[:120], "ch": (e.get("channel") or e.get("uploader") or "")[:60], "d": int(d or 0), "v": int(e.get("view_count") or 0),
                    "free": bool(re.search(r"free\s*(for\s*profit|download|beat)|\bfree\b", t, re.I))})
    return out
res = {"updated": time.strftime("%Y-%m-%d"), "artists": {}, "genres": {}}
for a in ART:
    if a.lower() in res["artists"]: continue
    res["artists"][a.lower()] = search(a + " type beat"); print(a, len(res["artists"][a.lower()]))
for k, q in GEN.items():
    res["genres"][k] = search(q, 18); print(k, len(res["genres"][k]))
res["trends"] = {}
for k, (name, desc, qs) in TRENDS.items():
    seen, L = set(), []
    for q in qs:
        for x in search(q, 10, r"phonk|funk|beat|prod" if k == "phonk" else r"บีท|บีต|beat|remix|รีมิกซ์|แดนซ์|dance|prod|instrumental" if k == "thai" else r"beat|instrumental|prod"):
            if x["id"] not in seen: seen.add(x["id"]); L.append(x)
    L.sort(key=lambda x: -x["v"]); res["trends"][k] = {"n": name, "d": desc, "list": L[:30]}; print("trend", k, len(L))
ok = sum(len(v) for v in res["artists"].values()) + sum(len(v) for v in res["genres"].values())
if ok < 30:
    print("too few results (%d) — YouTube may be blocking; keep old file" % ok); sys.exit(1)
import os; os.makedirs(os.path.dirname(sys.argv[1]) or ".", exist_ok=True)
json.dump(res, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":")); print("total", ok)
