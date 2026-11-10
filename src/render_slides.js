// node src/render_slides.js <post.json> <out_dir>  -> out_dir/slide_1.jpg ... (1080x1350)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const [postPath, outDir] = process.argv.slice(2);
  const post = JSON.parse(fs.readFileSync(postPath, 'utf8'));
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
  await page.goto('file://' + path.resolve(__dirname, 'slides.html'));
  const files = [];
  for (let i = 0; i < post.slides.length; i++) {
    await page.evaluate(async ([p, n]) => { await window.renderSlide(p, n); }, [post, i]);
    const f = path.join(outDir, `slide_${i + 1}.jpg`);
    await page.locator('#s').screenshot({ path: f, type: 'jpeg', quality: 92 });
    files.push(f);
  }
  await browser.close();
  console.log(JSON.stringify(files));
})();
