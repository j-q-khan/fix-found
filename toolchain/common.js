// Shared engine for Fix Found videos. scenes.html marks elements declaratively:
//   data-a="scene beat offset type [dur]"   type: show | pop | left | right | fade | grow | drop | stamp | type
//   data-count="scene beat offset dur target [comma]"
// "type" reveals an element's text one character at a time (for terminal lines).
// scenes.html may define window.extra(t) for custom motion. render(t) is deterministic (driven by capture.mjs).
const TL = window.TL, $ = id => document.getElementById(id), W = +document.body.dataset.w;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), P = (t, a, d) => clamp((t - a) / d);
const out3 = x => 1 - Math.pow(1 - x, 3), back = x => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const S = Object.fromEntries(TL.scenes.map(s => [s.id, s]));
const B = (id, i = 0) => S[id].beats[Math.min(i, S[id].beats.length - 1)].start;
const BD = (id, i = 0) => S[id].beats[Math.min(i, S[id].beats.length - 1)].dur;
const END = id => S[id].start + S[id].dur;
const NS = 'http://www.w3.org/2000/svg';

function anim(el, p, type) {
  const e = out3(p);
  switch (type) {
    case 'pop': el.style.opacity = clamp(p * 3); el.style.transform = `scale(${p <= 0 ? 0 : back(p)})`; break;
    case 'left': el.style.opacity = e; el.style.transform = `translateX(${(1 - e) * -160}px)`; break;
    case 'right': el.style.opacity = e; el.style.transform = `translateX(${(1 - e) * 160}px)`; break;
    case 'fade': el.style.opacity = e; break;
    case 'grow': el.style.opacity = p > 0 ? 1 : 0; el.style.transformOrigin = 'left center'; el.style.transform = `scaleX(${e})`; break;
    case 'drop': el.style.opacity = clamp(p * 3); el.style.transform = `translateY(${(1 - out3(p)) * -260}px) rotate(${(1 - e) * 12}deg)`; break;
    case 'stamp': el.style.opacity = clamp(p * 4); el.style.transform = `scale(${p <= 0 ? 2.4 : 2.4 - 1.4 * out3(p)}) rotate(-6deg)`; break;
    case 'type': el.style.opacity = p > 0 ? 1 : 0; el.textContent = el._full.slice(0, Math.round(el._full.length * p)); break;
    default: el.style.opacity = e; el.style.transform = `translateY(${(1 - e) * 40}px)`;
  }
}
const ANIM = [...document.querySelectorAll('[data-a]')].map(el => { const [s, b, o, ty, d] = el.dataset.a.split(' ');
  if (ty === 'type') el._full = el.textContent;
  return { el, s, b: +b, o: +o, ty: ty || 'show', d: +(d || (ty === 'type' ? 1.2 : 0.55)) }; });
const COUNT = [...document.querySelectorAll('[data-count]')].map(el => { const [s, b, o, d, n, f] = el.dataset.count.split(' ');
  return { el, s, b: +b, o: +o, d: +d, n: +n, f }; });

window.render = function (t) {
  $('dots').style.transform = `translate(${-(t * 9) % 44}px,${-(t * 5) % 44}px)`;
  $('bar').style.width = (W * clamp(t / TL.total)) + 'px';
  let chap = ''; const last = TL.scenes[TL.scenes.length - 1];
  for (const s of TL.scenes) { const el = $('s-' + s.id); if (!el) continue;
    const fi = s.start === 0 ? 1 : P(t, s.start, .4), fo = s === last ? 1 : 1 - P(t, s.start + s.dur - .4, .4), o = Math.min(fi, fo);
    el.style.opacity = o; el.style.visibility = o > 0 ? 'visible' : 'hidden'; if (o > .5 && s.label) chap = s.label; }
  $('chapter').textContent = chap;
  const cv = $('cover'); if (cv) { const o = 1 - P(t, 0.45, 0.35); cv.style.opacity = o; cv.style.visibility = o > 0 ? 'visible' : 'hidden'; }
  for (const a of ANIM) anim(a.el, P(t, B(a.s, a.b) + a.o, a.d), a.ty);
  for (const c of COUNT) { const v = Math.round(c.n * out3(P(t, B(c.s, c.b) + c.o, c.d))); c.el.textContent = c.f === 'comma' ? v.toLocaleString('en-US') : v; }
  // burned-in captions: the chunk being spoken, from timeline.json
  const cap = TL.captions.find(c => t >= c.start && t < c.end), span = $('cap').firstElementChild;
  span.textContent = cap ? cap.text : ''; $('cap').style.opacity = cap ? 1 : 0;
  if (window.extra) window.extra(t);
};
// keep chips on the same row from overlapping (emoji widths vary)
document.querySelectorAll('.scene').forEach(sc => {
  const rows = {}; [...sc.children].filter(e => e.classList.contains('chip') && e.style.left).forEach(e => (rows[e.style.top] = rows[e.style.top] || []).push(e));
  Object.values(rows).forEach(r => { r.sort((a, b) => a.offsetLeft - b.offsetLeft);
    for (let i = 1; i < r.length; i++) { const min = r[i - 1].offsetLeft + r[i - 1].offsetWidth + 22; if (r[i].offsetLeft < min) r[i].style.left = min + 'px'; } });
});
window.render(0);
