# Slope North Side — คู่มือสำหรับเซสชันใหม่ (สำหรับ Claude)

## ที่อยู่ของแอป
- ลิงก์หลัก (claude.ai artifact, มีบัญชี/ซิงค์/ผู้ช่วย/วาด MV ด้วย Claude): https://claude.ai/artifact/8AxN6jBbSnhs5148EB2CeK
  - capabilities: downloads, user, sample, assets {upload: interact}, db (rules: logs/tickets อ่านได้เฉพาะ admin, เขียนเฉพาะของตัวเอง)
  - อัปเดตจากเซสชันอื่น: Artifact read ด้วย url แล้ว publish ทับด้วย url (ไม่ส่ง capabilities เพื่อคงค่าเดิม)
- เว็บสาธารณะ (PWA ติดตั้งได้, ไม่ฝังเพลง): GitHub Pages ของ repo นี้ (root ของ main)
- แอปบนคอมผู้ใช้ (Windows): `Downloads\slope-north-side-pc\` รัน `start.bat` → http://localhost:8790 (เซิร์ฟเวอร์ `start.py` v22: faster-whisper, forced alignment MMS, demucs, mixer, SD-Turbo, LAN + PIN)

## ซอร์ส (โฟลเดอร์ src/)
- `new.html` — แอปหลัก (มี `__AUDIO__` เป็นที่ใส่ไฟล์เพลง base64 ของ Dangerous — ไฟล์เพลงไม่อยู่ใน repo เพราะ repo เป็น Public; ดึงได้จาก artifact หรือไฟล์ `slope-north-side-synced.html` บนคอมผู้ใช้ ตัวแปร `window.SNS_AUDIO`)
- `shell_boot.js`, `shell.css`, `shell.js` — ระบบบัญชี/โปรเจกต์/หน้าแรก/ผู้ช่วย (prefix `.sx-`, `window.SNS`, `window.SNSX`)
- `app/build.py` — สร้าง pc/, space/, synced/ และ artifact/ (`FUSED=src/data/fused_fa5.json SWV=bw-vNN python3 build.py OUT`) โดยอ่าน `/tmp/w/new.html`, `/tmp/w/audio.b64`, `/tmp/w/shell*.{js,css}` — ปรับ path ตามที่วางไฟล์
- `app/build_web.py` — สร้างเว็บสาธารณะจาก synced (ตัดเพลง, ใส่ manifest/sw)
- `app/start.py`, `app/mixer.py`, `app/img_gen.py`, `fa/fa.py` — เซิร์ฟเวอร์และ AI บนคอม
- `data/fused_fa5.json` — เวลาซิงค์ของ Dangerous (S,E,C,Q,Y,U)

## ส่วน SNS Pro ใน new.html (เซสชัน "SNS · MV & ภาพ", 5 พ.ย. 18:20)
- อยู่ระหว่าง `/*PRO-BEGIN*/` … `/*PRO-END*/` (ก่อน `setTimeout(function(){ensureSyl()},1200)`) — ตั้งค่าเก็บใน localStorage `bwpro`, จังหวะเพลงใน `bwbeat`
- ส่งออก 720p/1080p/1080p60 (`QUAL`, `expSize`), ลายน้ำแบรนด์ `drawWM` (วาดทั้งพรีวิว fxc และวิดีโอ)
- จังหวะเพลง `beatGrid()` (autocorrelation + ไล่ความเร็วละเอียด; Dangerous ≈ 76.6 BPM — อย่าใช้ comb อย่างเดียว เพราะโดนจังหวะแฝง 115 หลอก)
- MV: `drawMV` ใหม่ ใช้แผนช็อต `mvPlan()` (ตัดตามหัวห้อง, กรอบภาพ FRM, กล้อง MOV, ทรานซิชัน black/fade/flash/whip/cut) + เกรดสี `gradeCanvas` (cine/noir/bleach/vhs/thermal/night) + HUD
- ปก: `drawCover` = `drawCoverPro` (chrome/lofi/y3k/thermal/night/type/glass) แล้วค่อย `drawCover0` (แบบเดิม), ตัวอย่างปกเล็ก `cvThumbs`
- ชุดโปรโมท `PK`/`drawPk`/`pkAll` (zip), Spotify Canvas `pkCanvas`, แพ็กส่งช่างตัดต่อ `mvPack` (SRT/LRC/shotlist.csv/markers EDL/beats.csv/ภาพฉาก/ปก)
- ทดสอบได้ผ่าน `window.__snsPro`

## เทรนด์ & โอกาสแมส (เซสชัน "SNS · เทรนด์", 5–6 พ.ย.)
- โมดูลอยู่ที่ `src/trend.html` (style + `#trd` + script) — build.py แทรกต่อจาก shell.js (`TREND=` ชี้ไฟล์ได้, ค่าเริ่ม `/tmp/w/trend.html`)
- `window.SNSSong()` ใน new.html (ก่อน `go(1);`) ส่งเนื้อ/เวลา/ความยาว/แนว/feat ให้โมดูล · หน้าแรกมีการ์ด + STEPS ข้อแรกใน shell.js
- เปิดด้วย `SNSTrend.open(tab)` (tab: chart/me/next) · ศิลปินเก็บใน localStorage `sns:artists` (+ db `data/users/<uid>/trend` ในลิงก์ claude.ai)
- ข้อมูลชาร์ต/ประเด็นข่าวฝังใน `SNAP`, `GENRES`, `TOPICS` (ณ 5 พ.ย. 2569) ต้องอัปเดตเป็นระยะ · ชาร์ตสด: start.py v23 `/api/trends` (Apple Music RSS th/us + kworb Spotify, cache 6 ชม. ใน cache/trends.json)
- **ยังไม่ได้ลง artifact** (เซสชันที่ทำปิดเครือข่าย แก้ artifact ไม่ได้) → เซสชันถัดไป: build แล้ว publish `artifact/slope-north-side.html` ทับลิงก์หลัก

## ข้อมูลผู้ใช้
- ผู้ใช้: ศิลปินไทย Bedupbiw (แบรนด์ Slope North Side, ID แบรนด์ Slopenorthside44) — พูดไทย, เป็นงานอดิเรก, อยากได้งานระดับโลก
- เพลงตัวอย่าง: "Dangerous" Bedupbiw ft. Killmonker (ธีมแดงมืดแบบ The Weeknd)
- รายงานความคืบหน้าอยู่ในเอกสารโปรเจกต์ `claude/รายงานความคืบหน้า-แอป-Slope-North-Side.md`
- งานตรวจอัตโนมัติทุก 6 ชม. (scheduled task "SNS · ตรวจและซ่อมแอปอัตโนมัติ") อ่าน logs/tickets ใน db ของ artifact

## กติกาที่ผู้ใช้ตั้งไว้
- ถ้าบอก "รันเอง" = ทำงานต่อเองจนเสร็จ ไม่ต้องรอให้กดอนุญาต
- อัปเดตทั้ง 3 ที่ทุกครั้ง: artifact, repo นี้ (web), ไฟล์บนคอม (ผ่าน device bridge)
