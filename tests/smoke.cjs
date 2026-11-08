// ทดสอบแบบเร็ว (smoke) ของเว็บแอปที่ประกอบแล้ว: มือถือ + คอม
// ใช้: node tests/smoke.cjs <โฟลเดอร์ web> [โฟลเดอร์เก็บภาพหน้าจอ]
// ผ่าน = ไม่มี error ในหน้าเว็บ และทุกหน้าหลักเปิดได้
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(process.argv[2] || 'out/web');
const SHOTS = path.resolve(process.argv[3] || 'out/shots');
fs.mkdirSync(SHOTS, { recursive: true });
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png' };
const srv = http.createServer((q, r) => {
  let f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  if (f.endsWith('/')) f += 'index.html';
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r);
});
const results = [];
function check(name, ok, detail) { results.push({ name, ok: !!ok, detail: detail || '' }); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' — ' + detail : '')); }
async function run(browser, label, viewport) {
  const p = await browser.newPage({ viewport });
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  const base = 'http://127.0.0.1:' + srv.address().port + '/';
  await p.goto(base); await p.waitForTimeout(1500);
  if (await p.isVisible('#sx-id')) {
    await p.fill('#sx-id', 'ci-tester'); await p.fill('#sx-pw', 'ci-pass-123');
    if (await p.isVisible('#sx-pw2')) await p.fill('#sx-pw2', 'ci-pass-123');
    await p.click('#sx-lgo'); await p.waitForTimeout(1500);
  }
  check(label + ': หน้าแรกมีเครื่องมือ 4 อัน', (await p.$$('#sx .sx-tool')).length === 4);
  await p.screenshot({ path: path.join(SHOTS, label + '-home.png') });
  await p.evaluate(() => window.SNSExplore && SNSExplore.open()); await p.waitForTimeout(300);
  await p.fill('#ex-q', 'The Weeknd'); await p.click('#ex-go'); await p.waitForTimeout(500);
  check(label + ': ค้นหาแนวเพลงตอบ', /Dark|R&B/.test(await p.textContent('#ex-out')));
  await p.click('#ex-close');
  await p.evaluate(() => window.SNSTrend && SNSTrend.open()); await p.waitForTimeout(400);
  check(label + ': เทรนด์มีอย่างน้อย 10 อันดับ', (await p.$$('#tr-chart .tr-li')).length >= 10);
  await p.click('#tr-close');
  await p.click('#sx-new'); await p.waitForTimeout(400); await p.fill('#sx-nn', 'CI Song'); await p.click('#sx-ngo'); await p.waitForTimeout(2500);
  const tabs = await p.evaluate(() => [...document.querySelectorAll('#pg1 .sx-sub button')].map(b => b.textContent));
  check(label + ': เข้าโปรเจกต์ได้ (แท็บขั้น 1)', tabs.length >= 3, tabs.join(' / '));
  await p.screenshot({ path: path.join(SHOTS, label + '-step1.png') });
  for (const s of ['2', '3']) { await p.evaluate(s => { const b = document.querySelector('#dock nav button[data-s="' + s + '"]'); b && b.click() }, s); await p.waitForTimeout(500); }
  await p.screenshot({ path: path.join(SHOTS, label + '-step3.png') });
  check(label + ': ไม่มี error ในหน้าเว็บ', errs.length === 0, errs.slice(0, 3).join(' | '));
  await p.close();
}
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const b = await chromium.launch();
  try { await run(b, 'mobile', { width: 390, height: 844 }); await run(b, 'desktop', { width: 1280, height: 800 }); }
  catch (e) { check('การทดสอบรันจบ', false, e.message); }
  await b.close(); srv.close();
  fs.writeFileSync(path.join(SHOTS, 'results.json'), JSON.stringify(results, null, 1));
  const bad = results.filter(r => !r.ok).length;
  console.log(bad ? bad + ' FAIL' : 'ALL PASS (' + results.length + ')');
  process.exit(bad ? 1 : 0);
})();
