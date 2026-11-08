# สร้างคำถาม (prompt) สั้นๆ ส่งให้ GPT แบบฟรี (gpt-oss บนเครื่อง GitHub) — จำกัดขนาดให้ทำงานจบในเวลา
# ใช้: python3 ci/gpt_packet.py review|task  > .gpt/prompt.txt
import os, re, subprocess, sys

LIMIT = int(os.environ.get('PACKET_CHARS', '12000'))
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
    diff = sh('git', 'diff', '-U2', base + '...' + head, '--', *want) if want else ''
    cut = len(diff) > LIMIT
    out = [RULES, '',
           'งาน: รีวิว Pull Request นี้ หา bug, ผลกระทบกับฟีเจอร์เดิม, ปัญหามือถือ, ความปลอดภัย, จุดที่ช้า',
           'ตอบเป็นรายการ แต่ละข้อ: [ร้ายแรง/กลาง/เล็ก] ไฟล์:บรรทัด — ปัญหา — วิธีแก้ (ถ้ามีโค้ดให้สั้นที่สุด)',
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
    if total > LIMIT:
        sys.stderr.write('ไฟล์รวม %d ตัวอักษร เกินที่รุ่นฟรีรับได้ (%d) แบ่งงานให้เล็กลง หรือระบุไฟล์ที่เล็กกว่า\n' % (total, LIMIT)); sys.exit(4)
    out = [RULES, '',
           'งาน (จาก Issue): ' + clean(os.environ.get('TITLE'), 200), clean(body, 2000), '',
           'ตอบเป็น unified diff เท่านั้น ใน code block ```diff ... ``` ใช้ path แบบ a/<path> b/<path> แก้เฉพาะไฟล์ที่ให้มา เปลี่ยนให้น้อยที่สุด',
           'หลัง code block เขียนเหตุผลสั้นๆ ไม่เกิน 5 บรรทัด และสิ่งที่ Claude ควรทดสอบ', ''] + parts
    return '\n'.join(out)

if __name__ == '__main__':
    print(review() if sys.argv[1:] == ['review'] else task())
