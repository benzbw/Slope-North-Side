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
- ข้อมูลชาร์ต/ประเด็นข่าวฝังใน `SNAP`, `GENRES`, `TOPICS` (ณ 6 พ.ย. 2569: Spotify ไทย/Global จาก kworb, iTunes ไทยหมวด Hip-Hop/Rap) ต้องอัปเดตเป็นระยะ · ชาร์ตสด: start.py `/api/trends` (kworb Spotify ไทย/Global + iTunes RSS `itunes.apple.com/<cc>/rss/topsongs/limit=100/genre=18/json`, cache 6 ชม. ใน cache/trends.json) — `rss.applemarketingtools.com` ตอบ 504 แล้ว อย่าใช้
- start.py ใน repo = v24 ของคอมผู้ใช้ (มีค้นบีต YouTube จากเซสชันแต่งเพลง) + เทรนด์ · **write.html และหน้าแต่งเพลงใน index.html บนคอมยังไม่อยู่ใน src/** (อยู่ในเซสชัน "SNS · แต่งเพลง & หาบีต")
- ลง artifact แล้ว (version 14, 6 พ.ย. 11:40 โดยเซสชัน "SNS Studio · แอปหลัก")

## คลิป Reel/ฮุค (เซสชัน "SNS Studio · แอปหลัก", 6 พ.ย.)
- `VSEC` เลือกท่อน (`#vsec`, `secList()`), `VEND` ตอนจบ (`#vend`: auto/echo/fade/stop/loop) — `clipRange()` คืน `{s,e,mode,te,lw,tail}`
- กราฟเสียง `EF` (highpass/lowpass/bandpass→delay feedback) ต่อระหว่าง `mo` กับ `an`/`rdest`; `efReset()` หลังบันทึก · ต้นคลิปไล่ lowpass 700→20k Hz 1.1 วิ
- echo: ที่ `te` (2-3 คำท้าย) ไฮพาส 650 Hz + ส่งเข้า delay 0.42 วิ แล้วหยุดเพลง บันทึกหางเสียงต่อ 2.8 วิ (ไม่มีไฟล์เสียงร้องแยก จึงตัดบีตด้วยฟิลเตอร์)
- **index.html บนคอมมีโหมดแต่งเพลงที่ไม่อยู่ใน src/** → แก้คอมด้วยการ patch ไฟล์บนคอมโดยตรง ห้ามส่ง pc/index.html จาก build ทับ

## สตูดิโอมิกซ์ในแอปหลัก + แนวเพลง + ฟังเทียบ (เซสชัน "SNS Studio · แอปหลัก", 6 พ.ย.)
- โมดูล `src/mixstudio.html` = SNS Mix Engine (จากเซสชันมิกซ์) + UI (`#mxp`) + glue (แนวเพลง/ฟังเทียบ) — build.py แทรกด้วย `MIXST=` (ค่าเริ่ม `/tmp/w/mixstudio.html`)
- ย้ายมิกซ์ไปขั้น 1 แท็บแรก "เสียง & แนว" (`#mxcard`, `#gnr`) เพราะ AI ต้องใช้เพลงที่มิกซ์แล้วไปซิงค์ · สตูดิโอมิกซ์แบบเดิม (start.bat) ย้ายไปอยู่ใน `<details id="mx-old">` ขั้น 3 › เสียง
- ออโต้จูนเริ่มที่ "นิดเดียว" 35% (natural, speed ≥55ms, tol 0.18 st) · คีย์หาเองจากบีต+เสียงร้อง `detectKey()` จัดอันดับ 24 คีย์ แสดง % มั่นใจ (`window.SNSKey`)
- BPM ใช้ autocorrelation `SNSGenre.bpm` (Dangerous = 76) แทน `SNSMix.bpmOf` (ได้ 106 ผิด) ทั้งดีเลย์ในมิกซ์และแนวเพลง
- แนวเพลง `SNSGenre` (10 แนว: BPM/คีย์/สเปกตรัมเทียบ CURVES/คำในเนื้อ) + ลิงก์ Spotify/YouTube/Apple Music + ศิลปินใกล้กัน + ปุ่มถาม AI (sample)
- ฟังเทียบขั้น 3 › เสียง (`#cmp`): ไฟล์เพลงเทียบ สลับฟังที่จุดเดียวกัน ปรับความดังให้เท่ากัน รายงานต่าง BPM/คีย์/LUFS/โทน

## หน้าค้นหาแนวเพลง, เทรนด์มาแรง/Gen Z, คำฮิต, วันปล่อยชน, Shorts, ปกจากรูป (เซสชัน "SNS Studio · แอปหลัก", 8 พ.ย.)
- `src/xdata.js` (`window.SNSData`: MOOD เพลงตามอารมณ์ทุกแนว, SLANG ไทย/อังกฤษ now/old, AUD % คนฟังต่อแนว, GENZ, REL วันปล่อย/อีเวนต์) — build.py แทรกด้วย `XDATA=` และใส่ใน write.html ด้วย (patches/patch_write.py)
- `src/explore.html` (`#xpl`, `window.SNSExplore`) หน้า "ค้นหาแนวเพลง" เปิดจากหน้าแรก (การ์ดเครื่องมือ `.sx-tools`) · ห้ามใช้ id `exp` (ชนกับปุ่มใน new.html) · มี radar วันปล่อยใน `#rl-radar`
- แนวเพลงถูกย้ายออกจากแท็บมิกซ์ (แท็บขั้น 1 = "เสียง (มิกซ์)")
- trend.html: ชาร์ตไทย/โลก Top 20 รายสัปดาห์ 5 พ.ย., แท็บ มาแรง (`th_new`/`global_new`) และ Gen Z, ทุกแถวกดฟัง YouTube/Spotify
- new.html: Shorts (`#vshorts`, `bestSec()`/`VBEST` เลือกท่อนจากความดัง+ฮุค+ประโยคซ้ำ), ปกจากรูปผู้ใช้ `drawCoverPhoto` (ph_cine/ph_frame/ph_poster/ph_mag ไม่วาดคนใหม่)
- แพตช์สำหรับไฟล์บนคอม: `src/patches/*.py` (รันกับ index.html / write.html บนคอมแล้วแทรก xdata+explore ก่อน </body>, แทนบล็อก trend เดิม)

## ข้อมูลผู้ใช้
- ผู้ใช้: ศิลปินไทย Bedupbiw (แบรนด์ Slope North Side, ID แบรนด์ Slopenorthside44) — พูดไทย, เป็นงานอดิเรก, อยากได้งานระดับโลก
- เพลงตัวอย่าง: "Dangerous" Bedupbiw ft. Killmonker (ธีมแดงมืดแบบ The Weeknd)
- รายงานความคืบหน้าอยู่ในเอกสารโปรเจกต์ `claude/รายงานความคืบหน้า-แอป-Slope-North-Side.md`
- งานตรวจอัตโนมัติทุก 6 ชม. (scheduled task "SNS · ตรวจและซ่อมแอปอัตโนมัติ") อ่าน logs/tickets ใน db ของ artifact

## กติกาที่ผู้ใช้ตั้งไว้
- ถ้าบอก "รันเอง" = ทำงานต่อเองจนเสร็จ ไม่ต้องรอให้กดอนุญาต
- อัปเดตทั้ง 3 ที่ทุกครั้ง: artifact, repo นี้ (web), ไฟล์บนคอม (ผ่าน device bridge)
