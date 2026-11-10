// usage: node src/shot.js <html> <out.png> <selector> [dpr]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [html, out, sel = 'body', dpr = '1'] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1800, height: 1000 }, deviceScaleFactor: +dpr });
  p.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await p.goto('file://' + path.resolve(html));
  await p.evaluate(() => document.fonts.ready);
  await p.locator(sel).screenshot({ path: out });
  await b.close();
})();
