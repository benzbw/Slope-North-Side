// ทดสอบหน้าแต่งเพลง (write.html): ทุกแท็บ ทุกปุ่ม · AI ทำบีต · สุ่มสแลง · จำหน้าเดิม · ไม่มี error
// ใช้: node tests/write_smoke.cjs <web dir> [shots dir]
const { chromium } = require('playwright'), http = require('http'), fs = require('fs'), path = require('path');
const ROOT = process.argv[2] || 'out/web', SHOTS = process.argv[3] || 'out/shots';fs.mkdirSync(SHOTS, { recursive: true });
const srv = http.createServer((q, r) => { let f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end() }
  r.writeHead(200, { 'Content-Type': f.endsWith('.html') ? 'text/html; charset=utf-8' : f.endsWith('.json') ? 'application/json' : 'application/octet-stream' }); fs.createReadStream(f).pipe(r) });
let fails = 0; const check = (n, ok, d) => { console.log((ok ? 'PASS ' : 'FAIL ') + n + (d ? ' — ' + d : '')); if (!ok) fails++ };
(async () => { await new Promise(r => srv.listen(0, '127.0.0.1', r)); const U = 'http://127.0.0.1:' + srv.address().port + '/write.html'; const b = await chromium.launch();
 for (const [lab, vp] of [['mobile', { width: 390, height: 844 }], ['desktop', { width: 1280, height: 800 }]]) {
  const ctx = await b.newContext({ viewport: vp }); await ctx.route(/youtube|ytimg|puter|githubusercontent|github\.io/, r => r.abort()); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(String(e))); p.on('dialog', d => d.dismiss().catch(() => {}));
  await p.goto(U); await p.waitForTimeout(1500);
  check(lab + ': เปิดหน้าแต่งเพลง', await p.isVisible('text=① หาแรงบันดาลใจ'));
  for (const tab of ['① หาแรงบันดาลใจ', '② หาบีต', '③ สมุดเนื้อเพลง']) { await p.click('text=' + tab); await p.waitForTimeout(500);
   if (tab.startsWith('③')) { const nb = await p.$('#sw-nn'); if (nb) { await nb.click(); await p.waitForTimeout(500) } await p.fill('#sw-tx', '[Hook]\nทดสอบ').catch(() => {}) }
   const ids = await p.$$eval('#sw-body button', a => a.filter(x => x.offsetParent).map((x, i) => { x.dataset.au = 'w' + i; return { id: 'w' + i, t: x.textContent.trim() } }));
   for (const x of ids.slice(0, 60)) { if (/^‹|ทุกเพลง|ลบ|อัด|ทำบีต|สุ่มใหม่/.test(x.t)) continue; await p.evaluate(id => { const e = document.querySelector('[data-au="' + id + '"]'); if (e) e.click() }, x.id).catch(() => {}); await p.waitForTimeout(120);
    await p.keyboard.press('Escape').catch(() => {}); for (const c of await p.$$('.sx-x:visible')) await c.click().catch(() => {}) }
   const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); check(lab + ': ' + tab + ' ไม่ล้นจอ', over <= 2, over + 'px') }
  await p.click('text=② หาบีต'); await p.waitForTimeout(500);
  if (await p.isVisible('#bl')) { await p.selectOption('#bl-l', '110'); await p.click('#bl-go'); await p.waitForFunction(() => document.querySelector('#bl-out audio'), null, { timeout: 120000 }).catch(() => {});
   check(lab + ': AI ทำบีต', !!(await p.$('#bl-out audio')), (await p.textContent('#bl-out b').catch(() => '')).slice(0, 60)) }
  await p.screenshot({ path: path.join(SHOTS, 'write-' + lab + '.png') });
  check(lab + ': ไม่มี error ในหน้า', errs.length == 0, errs.slice(0, 3).join(' | ')); await ctx.close() }
 await b.close(); srv.close(); console.log(fails ? 'FAILED ' + fails : 'ALL PASS'); process.exit(fails ? 1 : 0) })();
