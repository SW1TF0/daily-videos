// SmartMenuKJ mascot "Плочко": the SmartMenuKJ app icon (dark tile with three white
// tiles and a blue dot) with cute eyes, muscular arms, big gloves and blue sneakers.
// Mascot.svg(pose) returns an SVG <g> string; every pose value is optional.
(function (global) {
  const D = Math.PI / 180;
  const BLUE0 = '#6cc4ff', BLUE = '#0a84ff', BLUE2 = '#0050e0';
  const OUT = '#141416';
  const THEMES = {
    dark: {
      body0: '#4a4a4f', body1: '#232326', body2: '#0f0f11',
      limb0: '#3a3a3e', limb1: '#1c1c1f',
      tile0: '#ffffff', tile1: '#d6d6de',
      brow: '#d1d1d6', mouthLine: '#f5f5f7', rim: 'rgba(255,255,255,0.13)', limbRim: '#55555c', happyEye: '#ffffff',
    },
    light: {
      body0: '#ffffff', body1: '#f2f2f6', body2: '#d5d5dc',
      limb0: '#ffffff', limb1: '#dcdce2',
      tile0: '#3a3a3e', tile1: '#1d1d1f',
      brow: '#3a3a3e', mouthLine: '#1d1d1f', rim: 'rgba(0,0,0,0.10)', limbRim: '#b9b9c2', happyEye: '#1d1d1f',
    },
  };

  const DEFAULT = {
    x: 0, y: 0, scale: 1, theme: 'dark', id: 'm',
    rot: 0, squash: 1, hop: 0,
    eyes: { open: 1, lookX: 0, lookY: 0, happy: 0 },
    brows: { y: 0, angle: 0 },
    mouth: { open: 0, wide: 0.5, smile: 0.6 },
    blush: 0.55,
    armL: { s: 75, e: 15, hand: 'open', flex: 0, front: false, h: 0 },
    armR: { s: 75, e: 15, hand: 'open', flex: 0, front: false, h: 0 },
    legL: { a: 92, lift: 0 },
    legR: { a: 88, lift: 0 },
  };

  function merge(base, over) {
    const out = Array.isArray(base) ? base.slice() : Object.assign({}, base);
    for (const k in (over || {})) {
      const v = over[k];
      if (v && typeof v === 'object' && !Array.isArray(v) && base[k] && typeof base[k] === 'object') out[k] = merge(base[k], v);
      else if (v !== undefined) out[k] = v;
    }
    return out;
  }
  const f = (n) => (Math.round(n * 100) / 100).toString();

  function capsule(x, y, len, w, ang, fill, extra = '') {
    return `<rect x="0" y="${f(-w / 2)}" width="${f(len)}" height="${f(w)}" rx="${f(w / 2)}" transform="translate(${f(x)},${f(y)}) rotate(${f(ang)})" fill="${fill}" stroke="${OUT}" stroke-width="5" ${extra}/>`;
  }

  // Big cartoon glove drawn pointing along +x, wrist at the origin.
  function hand(type, id) {
    const W = `url(#${id}-glove)`;
    const cuff = `<rect x="-8" y="-27" width="24" height="54" rx="11" fill="#e9e9ef" stroke="${OUT}" stroke-width="5"/>`;
    const fistBody = `<rect x="10" y="-40" width="78" height="80" rx="36" fill="${W}" stroke="${OUT}" stroke-width="5"/>`;
    const knuckles = `<g stroke="${OUT}" stroke-width="4" stroke-linecap="round" fill="none">
        <path d="M70 -16 q12 2 16 0"/><path d="M71 3 q12 2 16 0"/><path d="M69 21 q10 2 14 0"/></g>`;
    const thumbWrap = `<ellipse cx="44" cy="-24" rx="24" ry="13" transform="rotate(-12 44 -24)" fill="${W}" stroke="${OUT}" stroke-width="5"/>`;
    if (type === 'fist') return cuff + fistBody + knuckles + thumbWrap;
    if (type === 'point') return cuff + capsule(62, -16, 62, 24, -4, W) + fistBody + `<g stroke="${OUT}" stroke-width="4" stroke-linecap="round" fill="none"><path d="M71 6 q12 2 16 0"/><path d="M69 22 q10 2 14 0"/></g>` + thumbWrap;
    if (type === 'thumb') return cuff + capsule(40, -24, 50, 26, -88, W) + fistBody + knuckles;
    // open palm / wave
    return cuff +
      capsule(50, -22, 56, 23, -30, W) + capsule(56, -8, 62, 23, -10, W) +
      capsule(56, 8, 58, 23, 10, W) + capsule(50, 22, 48, 22, 30, W) +
      `<rect x="10" y="-36" width="62" height="72" rx="30" fill="${W}" stroke="${OUT}" stroke-width="5"/>` +
      capsule(26, -26, 44, 24, -72, W) +
      `<path d="M30 -4 q14 6 30 0" stroke="${OUT}" stroke-width="3.5" fill="none" stroke-linecap="round" opacity="0.55"/>`;
  }

  // Right arm in mascot space; the left arm is the same drawing mirrored.
  function arm(a, id, th) {
    const S = { x: 134, y: 40 };
    const L1 = 80, L2 = 70;
    const s = a.s * D, se = (a.s + a.e) * D;
    const E = { x: S.x + Math.cos(s) * L1, y: S.y + Math.sin(s) * L1 };
    const Wr = { x: E.x + Math.cos(se) * L2, y: E.y + Math.sin(se) * L2 };
    // bicep bulges toward the side the forearm folds to
    const side = a.e >= 0 ? 1 : -1;
    const n = { x: -Math.sin(s) * side, y: Math.cos(s) * side };
    const flex = a.flex || 0;
    const M = { x: (S.x + E.x) / 2 + n.x * (5 + flex * 15), y: (S.y + E.y) / 2 + n.y * (5 + flex * 15) };
    const ry = 19 + flex * 24;
    const limb = `url(#${id}-limb)`;
    return `<g>
      <line x1="${f(S.x)}" y1="${f(S.y)}" x2="${f(E.x)}" y2="${f(E.y)}" stroke="${th.limbRim}" stroke-width="51" stroke-linecap="round"/>
      <ellipse cx="${f(M.x)}" cy="${f(M.y)}" rx="${f(L1 * 0.40 + 3.5)}" ry="${f(ry + 3.5)}" transform="rotate(${f(a.s)} ${f(M.x)} ${f(M.y)})" fill="${th.limbRim}"/>
      <line x1="${f(E.x)}" y1="${f(E.y)}" x2="${f(Wr.x)}" y2="${f(Wr.y)}" stroke="${th.limbRim}" stroke-width="45" stroke-linecap="round"/>
      <line x1="${f(S.x)}" y1="${f(S.y)}" x2="${f(E.x)}" y2="${f(E.y)}" stroke="${limb}" stroke-width="44" stroke-linecap="round"/>
      <ellipse cx="${f(M.x)}" cy="${f(M.y)}" rx="${f(L1 * 0.40)}" ry="${f(ry)}" transform="rotate(${f(a.s)} ${f(M.x)} ${f(M.y)})" fill="${limb}"/>
      <ellipse cx="${f(M.x + n.x * ry * 0.35)}" cy="${f(M.y + n.y * ry * 0.35)}" rx="${f(L1 * 0.22)}" ry="${f(ry * 0.32)}" transform="rotate(${f(a.s)} ${f(M.x + n.x * ry * 0.35)} ${f(M.y + n.y * ry * 0.35)})" fill="${th.rim}" opacity="${f(0.6 + flex * 0.8)}"/>
      <line x1="${f(E.x)}" y1="${f(E.y)}" x2="${f(Wr.x)}" y2="${f(Wr.y)}" stroke="${limb}" stroke-width="38" stroke-linecap="round"/>
      <g transform="translate(${f(Wr.x)},${f(Wr.y)}) rotate(${f(a.s + a.e + (a.h || 0))})">${hand(a.hand, id)}</g>
    </g>`;
  }

  function leg(l, id, th) {
    const H = { x: 64, y: 160 };
    const len = 64;
    const a = l.a * D;
    const F = { x: H.x + Math.cos(a) * len, y: H.y + Math.sin(a) * len - (l.lift || 0) };
    return `<g>
      <line x1="${H.x}" y1="${H.y}" x2="${f(F.x)}" y2="${f(F.y)}" stroke="${th.limbRim}" stroke-width="49" stroke-linecap="round"/>
      <line x1="${H.x}" y1="${H.y}" x2="${f(F.x)}" y2="${f(F.y)}" stroke="url(#${id}-limb)" stroke-width="42" stroke-linecap="round"/>
      <g transform="translate(${f(F.x)},${f(F.y)}) rotate(${f(l.a - 90)})">
        <path d="M-30 -2 C-30 -26 6 -30 22 -14 C34 -4 50 2 52 14 L52 22 L-30 22 Z" fill="url(#${id}-shoe)" stroke="${OUT}" stroke-width="5" stroke-linejoin="round"/>
        <rect x="-34" y="18" width="90" height="14" rx="7" fill="#ffffff" stroke="${OUT}" stroke-width="5"/>
        <path d="M-6 -2 L18 8" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>
        <path d="M-12 8 L10 14" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>
      </g>
    </g>`;
  }

  function eye(cx, cy, e, sideSign, id, th) {
    if (e.happy > 0.5) {
      return `<path d="M${cx - 36} ${cy + 12} Q${cx} ${cy - 34} ${cx + 36} ${cy + 12}" stroke="${th.happyEye}" stroke-width="13" fill="none" stroke-linecap="round"/>`;
    }
    const open = Math.max(0.06, Math.min(1, e.open));
    const lx = (e.lookX || 0) * 15, ly = (e.lookY || 0) * 15 + 7;
    const clip = `${id}-eye${sideSign > 0 ? 'R' : 'L'}`;
    return `<g transform="translate(${cx},${cy}) scale(1,${f(open)})">
      <clipPath id="${clip}"><rect x="-50" y="-56" width="100" height="112" rx="47"/></clipPath>
      <rect x="-50" y="-56" width="100" height="112" rx="47" fill="url(#${id}-eyeW)"/>
      <g clip-path="url(#${clip})">
        <circle cx="${f(lx)}" cy="${f(ly)}" r="43" fill="url(#${id}-iris)"/>
        <circle cx="${f(lx)}" cy="${f(ly + 3)}" r="22" fill="#08102a"/>
        <circle cx="${f(lx - 15)}" cy="${f(ly - 16)}" r="14" fill="#ffffff"/>
        <circle cx="${f(lx + 14)}" cy="${f(ly + 13)}" r="6.5" fill="#ffffff" opacity="0.95"/>
        <circle cx="${f(lx - 2)}" cy="${f(ly + 24)}" r="3.5" fill="#ffffff" opacity="0.8"/>
        <path d="M-50 -56 H50 V-38 Q0 -50 -50 -38 Z" fill="#000" opacity="0.07"/>
      </g>
      <g stroke="${th.brow}" stroke-width="5.5" stroke-linecap="round">
        <line x1="${36 * sideSign}" y1="-46" x2="${50 * sideSign}" y2="-60"/>
        <line x1="${44 * sideSign}" y1="-34" x2="${60 * sideSign}" y2="-43"/>
        <line x1="${48 * sideSign}" y1="-21" x2="${63 * sideSign}" y2="-25"/>
      </g>
    </g>`;
  }

  function mouth(m, id, th) {
    const cy = 2;
    const o = Math.max(0, Math.min(1, m.open));
    const w = 15 + (m.wide ?? 0.5) * 13;
    const sm = (m.smile ?? 0.6);
    if (o < 0.05) {
      return `<path d="M${f(-w)} ${cy} Q0 ${f(cy + 4 + sm * 15)} ${f(w)} ${cy}" stroke="${th.mouthLine}" stroke-width="6.5" fill="none" stroke-linecap="round"/>`;
    }
    const depth = 9 + o * 32;
    const top = cy - sm * 3;
    const d = `M${f(-w)} ${f(top)} Q0 ${f(top + sm * 8)} ${f(w)} ${f(top)} Q${f(w * 0.9)} ${f(top + depth)} 0 ${f(top + depth)} Q${f(-w * 0.9)} ${f(top + depth)} ${f(-w)} ${f(top)} Z`;
    return `<clipPath id="${id}-mouth"><path d="${d}"/></clipPath>
      <path d="${d}" fill="#4a0b1c"/>
      <g clip-path="url(#${id}-mouth)">
        <rect x="${f(-w)}" y="${f(top - 6)}" width="${f(w * 2)}" height="${f(6 + 4 + o * 5)}" fill="#ffffff"/>
        <ellipse cx="0" cy="${f(top + depth + 4)}" rx="${f(w * 0.62)}" ry="${f(8 + o * 10)}" fill="#ff5f7e"/>
      </g>
      <path d="${d}" fill="none" stroke="${OUT}" stroke-width="4" stroke-linejoin="round"/>`;
  }

  function defs(id, th) {
    return `<defs>
      <linearGradient id="${id}-body" x1="0" y1="0" x2="0.35" y2="1">
        <stop offset="0" stop-color="${th.body0}"/><stop offset="0.55" stop-color="${th.body1}"/><stop offset="1" stop-color="${th.body2}"/>
      </linearGradient>
      <linearGradient id="${id}-limb" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">
        <stop offset="0" stop-color="${th.limb0}"/><stop offset="1" stop-color="${th.limb1}"/>
      </linearGradient>
      <linearGradient id="${id}-tile" x1="0" y1="0" x2="0.3" y2="1">
        <stop offset="0" stop-color="${th.tile0}"/><stop offset="1" stop-color="${th.tile1}"/>
      </linearGradient>
      <radialGradient id="${id}-dot" cx="0.35" cy="0.3" r="0.75">
        <stop offset="0" stop-color="${BLUE0}"/><stop offset="0.55" stop-color="${BLUE}"/><stop offset="1" stop-color="${BLUE2}"/>
      </radialGradient>
      <radialGradient id="${id}-iris" cx="0.4" cy="0.3" r="0.8">
        <stop offset="0" stop-color="${BLUE0}"/><stop offset="0.6" stop-color="${BLUE}"/><stop offset="1" stop-color="#002a8a"/>
      </radialGradient>
      <linearGradient id="${id}-eyeW" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e3e3ea"/>
      </linearGradient>
      <linearGradient id="${id}-glove" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e6e6ee"/>
      </linearGradient>
      <linearGradient id="${id}-shoe" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="${BLUE0}"/><stop offset="0.5" stop-color="${BLUE}"/><stop offset="1" stop-color="${BLUE2}"/>
      </linearGradient>
      <radialGradient id="${id}-blush"><stop offset="0" stop-color="#ff7a98" stop-opacity="1"/><stop offset="1" stop-color="#ff7a98" stop-opacity="0"/></radialGradient>
      <filter id="${id}-sh" x="-20%" y="-20%" width="140%" height="160%">
        <feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="#000" flood-opacity="0.45"/>
      </filter>
    </defs>`;
  }

  function svg(poseIn) {
    const p = merge(DEFAULT, poseIn || {});
    const th = THEMES[p.theme] || THEMES.dark;
    const id = p.id;
    const sq = p.squash;
    const sx = 1 / Math.sqrt(sq);
    // abs = the logo grid (tile 56, gap 18, radius 16, dot r 28), like the app icon
    const T = 52, G = 16, gx = -(T + G / 2), gy = 48;
    const abs = `<g filter="url(#${id}-sh)">
        <rect x="${gx}" y="${gy}" width="${T}" height="${T}" rx="15" fill="url(#${id}-tile)"/>
        <rect x="${gx + T + G}" y="${gy}" width="${T}" height="${T}" rx="15" fill="url(#${id}-tile)"/>
        <rect x="${gx}" y="${gy + T + G}" width="${T}" height="${T}" rx="15" fill="url(#${id}-tile)"/>
        <circle cx="${gx + T + G + T / 2}" cy="${gy + T + G + T / 2}" r="${T / 2}" fill="url(#${id}-dot)"/>
      </g>
      <g fill="#ffffff" opacity="${p.theme === 'dark' ? 0.55 : 0.25}">
        <rect x="${gx + 8}" y="${gy + 6}" width="${T - 26}" height="7" rx="3.5"/>
        <rect x="${gx + T + G + 8}" y="${gy + 6}" width="${T - 26}" height="7" rx="3.5"/>
        <rect x="${gx + 8}" y="${gy + T + G + 6}" width="${T - 26}" height="7" rx="3.5"/>
        <ellipse cx="${gx + T + G + T / 2 - 8}" cy="${gy + T + G + 14}" rx="11" ry="6"/>
      </g>`;
    const bodyRect = `<rect x="-158" y="-178" width="316" height="356" rx="122" fill="url(#${id}-body)"/>
      <rect x="-156.5" y="-176.5" width="313" height="353" rx="120.5" fill="none" stroke="${th.rim}" stroke-width="3"/>
      <ellipse cx="-66" cy="-140" rx="58" ry="22" transform="rotate(-24 -66 -140)" fill="#ffffff" opacity="${p.theme === 'dark' ? 0.10 : 0.7}"/>`;
    const aa = (p.antenna || 0) * Math.PI / 180;
    const tip = { x: Math.sin(aa) * 62, y: -172 - Math.cos(aa) * 62 };
    const ctl = { x: Math.sin(aa * 0.4) * 30, y: -172 - Math.cos(aa * 0.4) * 32 };
    const antenna = `<path d="M0 -160 Q${f(ctl.x)} ${f(ctl.y)} ${f(tip.x)} ${f(tip.y)}" stroke="${th.limbRim}" stroke-width="15" fill="none" stroke-linecap="round"/>
      <path d="M0 -160 Q${f(ctl.x)} ${f(ctl.y)} ${f(tip.x)} ${f(tip.y)}" stroke="url(#${id}-limb)" stroke-width="10" fill="none" stroke-linecap="round"/>
      <circle cx="${f(tip.x)}" cy="${f(tip.y)}" r="19" fill="url(#${id}-dot)" stroke="${OUT}" stroke-width="3"/>
      <ellipse cx="${f(tip.x - 6)}" cy="${f(tip.y - 7)}" rx="6.5" ry="4.5" fill="#fff" opacity="0.85"/>`;
    const brows = [-1, 1].map((sgn) => `<line x1="-15" y1="0" x2="15" y2="0" transform="translate(${70 * sgn},${-140 + p.brows.y}) rotate(${p.brows.angle * sgn})" stroke="${th.brow}" stroke-width="8" stroke-linecap="round"/>`).join('');
    const blush = p.blush > 0 ? [-1, 1].map((sgn) => `<ellipse cx="${112 * sgn}" cy="-6" rx="30" ry="17" fill="url(#${id}-blush)" opacity="${f(Math.min(1, p.blush * 1.1))}"/>`).join('') : '';
    const armsBack = (p.armL.front ? '' : `<g transform="scale(-1,1)">${arm(p.armL, id, th)}</g>`) + (p.armR.front ? '' : arm(p.armR, id, th));
    const armsFront = (p.armL.front ? `<g transform="scale(-1,1)">${arm(p.armL, id, th)}</g>` : '') + (p.armR.front ? arm(p.armR, id, th) : '');
    const hopShadow = Math.max(0.35, 1 - p.hop / 220);
    return `<g transform="translate(${f(p.x)},${f(p.y)}) scale(${f(p.scale)})">
      ${defs(id, th)}
      <ellipse cx="0" cy="262" rx="${f(150 * hopShadow)}" ry="${f(18 * hopShadow)}" fill="#000" opacity="${f(0.28 * hopShadow)}"/>
      <g transform="translate(0,${f(-p.hop)}) translate(0,250) rotate(${f(p.rot)}) scale(${f(sx)},${f(sq)}) translate(0,-250)">
        <g transform="scale(-1,1)">${leg(p.legL, id, th)}</g>${leg(p.legR, id, th)}
        ${armsBack}
        ${antenna}
        ${bodyRect}
        ${abs}
        ${blush}
        ${brows}
        ${eye(-70, -70, p.eyes, -1, id, th)}${eye(70, -70, p.eyes, 1, id, th)}
        ${mouth(p.mouth, id, th)}
        ${armsFront}
      </g>
    </g>`;
  }

  const api = { svg, DEFAULT, THEMES, merge };
  if (typeof module !== 'undefined') module.exports = api;
  global.Mascot = api;
})(typeof window !== 'undefined' ? window : globalThis);
