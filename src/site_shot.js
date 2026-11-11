// Site check for the coder: screenshots on a phone and a desktop + the problems a visitor would hit.
//
// usage: node src/site_shot.js <url | folder | file.html> [out_dir] [--pages index.html,bg/index.html] [--no-links]
//   url      a live page (https://www.smartmenukj.com/bg/)
//   folder   a site checkout: served on a local port, so it can be checked before a push
//   out_dir  default out/site_shot/<host or folder>/   (out/ is never committed)
//
// For every page and view (phone 390x844 @2x, desktop 1440x900 @1x):
//   <page>-<view>.png        what the visitor sees first
//   <page>-<view>-full.png   the whole page (cut at 8000 px)
// and report.json: console errors, failed requests and 4xx/5xx, missing title / description / h1 / lang / alt,
// horizontal scroll on the phone, broken internal links. Exit code 1 if anything is wrong.
// Requests the environment's network blocks (ERR_TUNNEL_CONNECTION_FAILED) are listed apart as `blocked_by_env_network`:
// they are not site bugs; add the host to the environment's allowed domains if the check needs it.
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.avif': 'image/avif', '.gif': 'image/gif',
  '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.mp4': 'video/mp4',
  '.webm': 'video/webm', '.txt': 'text/plain', '.xml': 'application/xml', '.pdf': 'application/pdf' };
const VIEWS = [
  { name: 'phone', viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  { name: 'desktop', viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
];
const MAX_FULL = 8000;

function serve(root) {
  root = path.resolve(root);
  return new Promise(ok => {
    const srv = http.createServer((req, res) => {
      let f = path.join(root, decodeURIComponent(req.url.split(/[?#]/)[0]));
      if (!f.startsWith(root)) { res.writeHead(403); return res.end(); }
      if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
      if (!fs.existsSync(f) && fs.existsSync(f + '.html')) f += '.html';
      fs.readFile(f, (e, d) => {
        if (e) { res.writeHead(404, { 'content-type': 'text/plain' }); return res.end('404'); }
        res.writeHead(200, { 'content-type': TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream' });
        res.end(d);
      });
    });
    srv.listen(0, '127.0.0.1', () => ok(srv));
  });
}

function slug(u) {
  const p = new URL(u).pathname.replace(/\/index\.html?$/, '/').replace(/\.html?$/, '');
  return (p.replace(/^\/|\/$/g, '').replace(/[^\w-]+/g, '_') || 'home');
}

async function checkPage(browser, url, outDir, checkLinks) {
  const page_ = { url, views: {} };
  for (const v of VIEWS) {
    const ctx = await browser.newContext({ viewport: v.viewport, deviceScaleFactor: v.deviceScaleFactor, isMobile: !!v.isMobile,
      hasTouch: !!v.hasTouch, locale: 'bg-BG' });
    const page = await ctx.newPage();
    const errors = [], failed = [];
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 300)); });
    page.on('pageerror', e => errors.push('JS: ' + e.message.slice(0, 300)));
    page.on('requestfailed', r => failed.push(`${r.failure()?.errorText || 'failed'} ${r.url().slice(0, 200)}`));
    page.on('response', r => { if (r.status() >= 400) failed.push(`${r.status()} ${r.url().slice(0, 200)}`); });
    let status = null;
    try {
      const r = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      status = r && r.status();
    } catch (e) {
      try { const r = await page.goto(url, { waitUntil: 'load', timeout: 30000 }); status = r && r.status(); }
      catch (e2) { errors.push('LOAD: ' + e2.message.slice(0, 200)); }
    }
    await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});
    await page.waitForTimeout(600);  // entrance animations
    const name = `${slug(page.url() || url)}-${v.name}`;
    await page.screenshot({ path: path.join(outDir, `${name}.png`) }).catch(e => errors.push('SHOT: ' + e.message));
    const h = await page.evaluate(() => document.documentElement.scrollHeight).catch(() => 0);
    await page.screenshot({ path: path.join(outDir, `${name}-full.png`), fullPage: h <= MAX_FULL,
      clip: h > MAX_FULL ? { x: 0, y: 0, width: v.viewport.width, height: MAX_FULL } : undefined }).catch(() => {});
    const info = await page.evaluate(() => {
      const meta = n => (document.querySelector(`meta[name="${n}"]`) || {}).content || '';
      const links = [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.startsWith(location.origin));
      return {
        final_url: location.href, title: document.title, description: meta('description'), lang: document.documentElement.lang,
        h1: document.querySelectorAll('h1').length, viewport_meta: !!document.querySelector('meta[name="viewport"]'),
        og_image: !!document.querySelector('meta[property="og:image"]'),
        img_no_alt: [...document.images].filter(i => !i.hasAttribute('alt')).map(i => i.currentSrc || i.src).slice(0, 10),
        img_broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && (i.currentSrc || i.src)).map(i => i.currentSrc || i.src).slice(0, 10),
        overflow_x: document.documentElement.scrollWidth > window.innerWidth + 1 ? document.documentElement.scrollWidth : 0,
        internal_links: [...new Set(links.map(l => l.split('#')[0]))],
      };
    }).catch(e => ({ error: e.message }));
    page_.views[v.name] = { status, screenshot: `${name}.png`, errors: [...new Set(errors)], failed: [...new Set(failed)], ...info };
    if (v.name === 'phone') page_.internal_links = info.internal_links || [];
    delete page_.views[v.name].internal_links;
    await ctx.close();
  }
  if (checkLinks) {
    const ctx = await browser.newContext();
    const broken = [];
    for (const l of (page_.internal_links || []).slice(0, 60)) {
      try {
        const r = await ctx.request.get(l, { timeout: 15000, maxRedirects: 5 });
        if (r.status() >= 400) broken.push(`${r.status()} ${l}`);
      } catch (e) { broken.push(`ERR ${l}`); }
    }
    page_.links_broken = broken;
    await ctx.close();
  }
  delete page_.internal_links;
  return page_;
}

const BLOCKED = /ERR_TUNNEL_CONNECTION_FAILED|ERR_PROXY_CONNECTION_FAILED/;

function blockedHosts(p) {
  const hosts = new Set();
  for (const v of Object.values(p.views))
    v.failed.filter(f => BLOCKED.test(f)).forEach(f => { try { hosts.add(new URL(f.split(' ').pop()).host); } catch (e) {} });
  return [...hosts];
}

function problems(p) {
  const out = [];
  for (const [vn, v] of Object.entries(p.views)) {
    if (v.status && v.status >= 400) out.push(`${vn}: HTTP ${v.status}`);
    v.errors.filter(e => !BLOCKED.test(e)).forEach(e => out.push(`${vn}: ${e}`));
    v.failed.filter(f => !BLOCKED.test(f)).forEach(f => out.push(`${vn}: ресурс ${f}`));
    (v.img_broken || []).forEach(i => out.push(`${vn}: счупена снимка ${i}`));
    if (vn === 'phone' && v.overflow_x) out.push(`phone: хоризонтален скрол (ширина ${v.overflow_x}px при 390px)`);
  }
  const v = p.views.phone || {};
  if (!v.title) out.push('няма <title>');
  if (!v.description) out.push('няма meta description');
  if (!v.lang) out.push('няма lang на <html>');
  if (v.h1 !== 1) out.push(`h1: ${v.h1} (трябва 1)`);
  if (!v.viewport_meta) out.push('няма meta viewport');
  if (v.img_no_alt && v.img_no_alt.length) out.push(`снимки без alt: ${v.img_no_alt.length}`);
  (p.links_broken || []).forEach(l => out.push(`счупена връзка ${l}`));
  return [...new Set(out)];
}

(async () => {
  const args = process.argv.slice(2);
  const opt = n => { const i = args.indexOf(n); if (i < 0) return null; const v = args[i + 1]; args.splice(i, 2); return v; };
  const noLinks = args.includes('--no-links'); if (noLinks) args.splice(args.indexOf('--no-links'), 1);
  const pagesArg = opt('--pages');
  const [target, outArg] = args;
  if (!target) { console.error('usage: node src/site_shot.js <url | folder | file.html> [out_dir] [--pages a.html,b/] [--no-links]'); process.exit(2); }
  let base, srv = null, label;
  if (/^https?:\/\//.test(target)) { base = target; label = new URL(target).host; }
  else {
    const abs = path.resolve(target);
    const dir = fs.statSync(abs).isDirectory() ? abs : path.dirname(abs);
    srv = await serve(dir);
    base = `http://127.0.0.1:${srv.address().port}/` + (fs.statSync(abs).isDirectory() ? '' : path.basename(abs));
    label = path.basename(dir);
  }
  const outDir = path.resolve(outArg || path.join(__dirname, '..', 'out', 'site_shot', label.replace(/[^\w.-]+/g, '_')));
  fs.mkdirSync(outDir, { recursive: true });
  const urls = pagesArg ? pagesArg.split(',').map(p => new URL(p.trim(), base).href) : [base];
  const browser = await chromium.launch();
  const report = { target, out_dir: outDir, pages: [] };
  for (const u of urls) {
    const p = await checkPage(browser, u, outDir, !noLinks);
    p.problems = problems(p);
    p.blocked_by_env_network = blockedHosts(p);
    report.pages.push(p);
  }
  await browser.close();
  if (srv) srv.close();
  fs.writeFileSync(path.join(outDir, 'report.json'), JSON.stringify(report, null, 1));
  const n = report.pages.reduce((a, p) => a + p.problems.length, 0);
  console.log(JSON.stringify({ out_dir: outDir, pages: report.pages.map(p => ({ url: p.url, final_url: p.views.phone?.final_url,
    title: p.views.phone?.title, screenshots: Object.values(p.views).map(v => v.screenshot), problems: p.problems,
    ...(p.blocked_by_env_network.length ? { blocked_by_env_network: p.blocked_by_env_network } : {}) })), total_problems: n }, null, 1));
  process.exit(n ? 1 : 0);
})();
