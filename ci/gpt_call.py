# เรียก GPT ผ่าน GitHub Models (ฟรี) ด้วย GITHUB_TOKEN ของ workflow — ไม่ใช้ OpenAI API key
# ใช้: python3 ci/gpt_call.py <prompt.txt> <out.md> [model] [max_tokens]
import json, os, sys, time, urllib.request, urllib.error
p, out = sys.argv[1], sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 else 'openai/gpt-4.1-mini'
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 2000
tok = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
body = json.dumps({'model': model, 'max_tokens': mx, 'temperature': 0.2,
                   'messages': [{'role': 'user', 'content': open(p, encoding='utf-8').read()}]}).encode()
req = urllib.request.Request('https://models.github.ai/inference/chat/completions', data=body, method='POST',
                             headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json', 'Accept': 'application/json'})
for attempt in range(2):
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read().decode('utf-8', 'replace')
        try:
            j = json.loads(raw)
        except Exception:
            print('ตอบกลับไม่ใช่ JSON (HTTP 200):', raw[:500]); sys.exit(2)
        if 'choices' not in j:
            print('ไม่มี choices:', raw[:800]); sys.exit(2)
        txt = j['choices'][0]['message']['content'] or ''
        u = j.get('usage') or {}
        open(out, 'w', encoding='utf-8').write(txt)
        line = '%s,%s,%s,%s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), model, u.get('prompt_tokens', ''), u.get('completion_tokens', ''))
        print('usage:', line)
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            open(os.environ['GITHUB_STEP_SUMMARY'], 'a').write('GPT usage: model %s · input %s · output %s tokens (ฟรี)\n' % (model, u.get('prompt_tokens'), u.get('completion_tokens')))
        sys.exit(0)
    except urllib.error.HTTPError as e:
        msg = e.read().decode('utf-8', 'replace')[:800]
        print('HTTP', e.code, msg)
        if e.code == 429 and attempt == 0:
            time.sleep(20); continue
        sys.exit(1)
