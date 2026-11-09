# สร้างคำถาม (prompt) สั้นๆ ส่งให้ GPT แบบฟรี (gpt-oss บนเครื่อง GitHub) — จำกัดขนาดให้ทำงานจบในเวลา
# ใช้: python3 ci/gpt_packet.py review|task  > .gpt/prompt.txt
import os, re, subprocess, sys

LIMIT = int(os.environ.get('PACKET_CHARS', '8000'))
RULES = """คุณคือ GPT ทำหน้าที่ Co-Developer ของโปรเจกต์ Slope North Side (แอปทำเพลง/วิดีโอเนื้อเพลง เป็น HTML+JavaScript ไฟล์เดียว ประกอบจาก src/)
Claude เป็น Lead Developer ผู้ตัดสินใจขั้นสุดท้าย งานของคุณส่งเป็นความเห็นหรือ patch ให้ Claude ตรวจ
กติกา: ห้ามเปลี่ยนโครงสร้างหลัก ห้ามลบฟีเจอร์เดิม ห้ามใส่ key/รหัสผ่าน ต้องใช้ได้ทั้งมือถือ 390px และคอม ถ้าไม่แน่ใจให้บอกตรงๆ
ตอบภาษาไทย ศัพท์เทคนิคใช้อังกฤษได้"""

def clean(t, n):
    t = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', t or '')
    return t[:n]

def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout

def review():
    base, head = os.environ['BASE'], os.environ['HEAD']
    files = [f for f in sh('git', 'diff', '--name-only', base + '...' + head).split('\n') if f]
    # ไฟล์ที่ประกอบออกมาแล้ว (index.html, write.html ที่ root) ไม่ต้องส่ง ดูจากต้นฉบับใน src/ แทน
    skip = re.compile(r'^(index\.html|write\.html|sw\.js|manifest\.json|.*\.png|.*\.jpg|src/data/.*)$')
    want = [f for f in files if not skip.match(f)]
    # PR body บรรทัด "focus: a, b" → ส่งเฉพาะไฟล์เหล่านั้น (diff ใหญ่เกินรุ่นฟรี)
    fm = re.search(r'^\s*focus\s*:\s*(.+)$', os.environ.get('BODY') or '', re.M | re.I)
    if fm:
        fl = [x.strip().strip('`') for x in re.split(r'[,\s]+', fm.group(1)) if x.strip()]
        fl = [f for f in fl if os.path.isfile(f)]
        if fl:  # ส่งไฟล์เต็ม (โค้ดอาจอยู่บน main แล้ว diff จึงว่าง)
            body = ''
            for f in fl:
                body += '=== FILE: %s ===\n%s\n' % (f, open(f, encoding='utf-8', errors='replace').read())
            cut = len(body) > LIMIT
            return '\n'.join([RULES, '', 'งาน: รีวิวโค้ดในไฟล์ต่อไปนี้ หา bug ที่ทำให้ใช้งานพัง ข้อมูลหาย มือถือใช้ไม่ได้ หรือความปลอดภัย',
                'ตอบไม่เกิน 6 ข้อ เฉพาะปัญหาที่เห็นจริงในโค้ดด้านล่าง ห้ามเดาโค้ดที่ไม่เห็น แต่ละข้อ: [ร้ายแรง/กลาง/เล็ก] ไฟล์ — ยกโค้ดจริง 1 บรรทัดเป็นหลักฐาน — ปัญหา — วิธีแก้สั้นๆ',
                'ไม่ต้องเสนอเรื่องสไตล์โค้ด · ปิดท้ายด้วยบรรทัด "สรุป: ..."', '', 'บริบท: ' + clean(os.environ.get('BODY'), 900), '',
                'FILES' + (' (ตัดเหลือ %d ตัวอักษรแรก)' % LIMIT if cut else '') + ':', body[:LIMIT]])
    diff = sh('git', 'diff', '-U2', base + '...' + head, '--', *want) if want else ''
    cut = len(diff) > LIMIT
    out = [RULES, '',
           'งาน: รีวิว Pull Request นี้ หา bug, ผลกระทบกับฟีเจอร์เดิม, ปัญหามือถือ, ความปลอดภัย, จุดที่ช้า',
           'ตอบไม่เกิน 6 ข้อ เฉพาะปัญหาที่เห็นจริงใน DIFF ด้านล่าง ห้ามเดาโค้ดที่ไม่เห็น แต่ละข้อ: [ร้ายแรง/กลาง/เล็ก] ไฟล์ — ยกโค้ดจริงจาก DIFF 1 บรรทัดเป็นหลักฐาน — ปัญหา — วิธีแก้สั้นๆ',
           'ไม่ต้องเสนอเรื่องสไตล์โค้ด (เช่น with open) หรือเครื่องมือที่ GitHub มีให้อยู่แล้ว (gh, node, python)',
           'ถ้าไม่เจอปัญหา บอกว่า "ไม่พบปัญหา" แล้วบอก 1-2 อย่างที่ควรทดสอบเพิ่ม · ปิดท้ายด้วยบรรทัด "สรุป: ควร merge / ควรแก้ก่อน"',
           '', 'ชื่อ PR: ' + clean(os.environ.get('TITLE'), 200),
           'คำอธิบาย: ' + clean(os.environ.get('BODY'), 1200),
           'ไฟล์ที่เปลี่ยน: ' + ', '.join(files[:40]), '',
           'DIFF' + (' (ตัดเหลือ %d ตัวอักษรแรก เพราะรุ่นฟรีรับได้จำกัด)' % LIMIT if cut else '') + ':',
           diff[:LIMIT] or '(ไม่มีไฟล์ต้นฉบับเปลี่ยน)']
    return '\n'.join(out)

def task():
    body = os.environ.get('BODY') or ''
    paths = []
    for line in body.split('\n'):
        m = re.match(r'\s*(?:files?|ไฟล์)\s*:\s*(.+)$', line, re.I)
        if m:
            paths += [p.strip().strip('`') for p in re.split(r'[,\s]+', m.group(1)) if p.strip()]
    paths = [p for p in paths if re.match(r'^[\w./-]+$', p) and '..' not in p and os.path.isfile(p)]
    if not paths:
        sys.stderr.write('ไม่พบบรรทัด files: ที่ชี้ไฟล์ที่มีอยู่จริง\n'); sys.exit(3)
    parts, total = [], 0
    for p in paths:
        t = open(p, encoding='utf-8', errors='replace').read()
        total += len(t)
        parts.append('=== FILE: %s ===\n%s' % (p, t))
    open('.gpt/files.txt', 'w').write('\n'.join(paths))
    if total > LIMIT:
        sys.stderr.write('ไฟล์รวม %d ตัวอักษร เกินที่รุ่นฟรีรับได้ (%d) แบ่งงานให้เล็กลง หรือระบุไฟล์ที่เล็กกว่า\n' % (total, LIMIT)); sys.exit(4)
    out = [RULES, '',
           'งาน (จาก Issue): ' + clean(os.environ.get('TITLE'), 200), clean(body, 2000), '',
           'ตอบด้วย "ไฟล์ที่แก้แล้วทั้งไฟล์" ไฟล์ละ 1 code block บรรทัดแรกในบล็อกต้องเป็นคอมเมนต์บอก path เช่น // FILE: tests/write_smoke.cjs',
           'ใส่โค้ดเดิมที่ไม่ได้แก้ครบทุกบรรทัด ห้ามย่อ ห้ามเขียน ... แทนโค้ด แก้เฉพาะที่งานขอ',
           'หลัง code block เขียนเหตุผลสั้นๆ ไม่เกิน 5 บรรทัด', ''] + parts
    return '\n'.join(out)

if __name__ == '__main__':
    print(review() if sys.argv[1:] == ['review'] else task())
