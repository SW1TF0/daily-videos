// node src/render.js <timeline.json> <out_silent.mp4> [--still t out.png]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

(async () => {
  const [tlPath, out, flag, stillT, stillOut] = process.argv.slice(2);
  const data = JSON.parse(fs.readFileSync(tlPath, 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
  await page.goto('file://' + path.resolve(__dirname, 'video.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async (d) => { await window.setup(d); }, data);
  // warm fonts/emoji
  await page.evaluate(async () => { await window.renderFrame(0); });

  if (flag === '--still') {
    for (const [i, t] of String(stillT).split(',').entries()) {
      await page.evaluate(async (tt) => { await window.renderFrame(tt); }, +t);
      await page.screenshot({ path: stillOut.replace('%d', i), type: 'png' });
    }
    await browser.close();
    return;
  }

  const fps = data.fps;
  const n = Math.ceil(data.duration * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    await page.evaluate(async (tt) => { await window.renderFrame(tt); }, i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.error(`frame ${i}/${n} ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  await browser.close();
  console.error(`rendered ${n} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
})();
