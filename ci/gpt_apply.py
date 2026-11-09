# เอาไฟล์ที่ GPT ส่งกลับ (ทั้งไฟล์) มาเขียนทับ แล้วตรวจไวยากรณ์ · ใช้: python3 ci/gpt_apply.py .gpt/response.md .gpt/files.txt
import re, subprocess, sys, ast, os
resp = open(sys.argv[1], encoding='utf-8').read()
allowed = [x.strip() for x in open(sys.argv[2]).read().split('\n') if x.strip()] if os.path.isfile(sys.argv[2]) else []
blocks = re.findall(r'```[\w.+-]*\n(.*?)```', resp, re.S)
if not blocks: print('GPT ไม่ได้ส่งโค้ดมา'); sys.exit(1)
done = 0
for b in blocks:
    first = b.split('\n', 1)[0]
    m = re.search(r'FILE:\s*([\w./-]+)', first)
    path = m.group(1) if m else (allowed[0] if len(allowed) == 1 and len(blocks) == 1 else None)
    if not path or path not in allowed: print('ข้ามบล็อก (ไม่ระบุไฟล์ที่อนุญาต):', first[:80]); continue
    body = b.split('\n', 1)[1] if m else b
    old = open(path, encoding='utf-8').read()
    if len(body) < len(old) * 0.7: print('ไม่ใช้: ไฟล์ที่ส่งมาสั้นกว่าเดิมมาก (น่าจะย่อโค้ด)', path, len(body), '/', len(old)); continue
    if re.search(r'^\s*(//|#)?\s*\.\.\.\s*$', body, re.M): print('ไม่ใช้: มี ... แทนโค้ด', path); continue
    open(path, 'w', encoding='utf-8').write(body if body.endswith('\n') else body + '\n')
    if path.endswith(('.js', '.cjs')):
        r = subprocess.run(['node', '--check', path], capture_output=True, text=True)
        if r.returncode: print('ไวยากรณ์ผิด:', path, r.stderr[:400]); open(path, 'w', encoding='utf-8').write(old); continue
    if path.endswith('.py'):
        try: ast.parse(body)
        except SyntaxError as e: print('ไวยากรณ์ผิด:', path, e); open(path, 'w', encoding='utf-8').write(old); continue
    print('ใช้แล้ว:', path); done += 1
sys.exit(0 if done else 1)
