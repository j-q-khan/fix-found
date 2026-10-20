// Deterministic frame capture: headless Chrome (isolated profile) via CDP over Node's native WebSocket -> ffmpeg.
// usage: node toolchain/capture.mjs <video_dir> <out.mp4> [holdSeconds=1.0] [stills=comma list of seconds]
// Frame size and the length limit come from <video_dir>/meta.json (format, max_seconds). Run one capture at a time (fixed port).
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const dir = path.resolve(process.argv[2]);
const out = process.argv[3];
const hold = parseFloat(process.argv[4] || '1.0');
const stills = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
const META = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'));
const [W, H] = { '16:9': [1920, 1080], '9:16': [1080, 1920] }[META.format];
const TL = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'), 'utf8'));
fs.writeFileSync(path.join(dir, 'timeline.js'), 'window.TL=' + JSON.stringify(TL) + ';');
const fps = TL.fps, total = TL.total + hold, N = Math.round(total * fps);
if (!stills && total > META.max_seconds) { console.error(`refusing: ${total.toFixed(2)}s > ${META.max_seconds}s`); process.exit(2); }

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const prof = path.join(here, 'chrome-profile');
const port = 9335;
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`,
  `--window-size=${W},${H}`, '--hide-scrollbars', '--force-device-scale-factor=1', '--allow-file-access-from-files',
  pathToFileURL(path.join(dir, 'anim.html')).href], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));

let ws, id = 0; const pending = new Map();
function send(method, params = {}) { const i = ++id; ws.send(JSON.stringify({ id: i, method, params }));
  return new Promise((res, rej) => pending.set(i, { res, rej })); }

async function main() {
  let target;
  for (let k = 0; k < 50 && !target; k++) { await sleep(200);
    try { const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); target = list.find(t => t.type === 'page'); } catch {} }
  if (!target) throw new Error('chrome did not start');
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result); } });
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  let ready = false;
  for (let k = 0; k < 100 && !ready; k++) {
    const r = await send('Runtime.evaluate', { expression: `typeof window.render==='function' && [...document.images].every(i=>i.complete&&i.naturalWidth>0)`, returnByValue: true });
    ready = r.result.value === true; if (!ready) await sleep(100); }
  if (!ready) throw new Error('page/images not ready (check image paths)');

  async function frameAt(t) {
    const r = await send('Runtime.evaluate', { expression: `(()=>{try{render(${t.toFixed(4)});return ''}catch(e){return String(e.stack||e)}})()`, returnByValue: true });
    if (r.result.value) throw new Error(r.result.value);
    const shot = await send('Page.captureScreenshot', { format: 'jpeg', quality: 92 });
    return Buffer.from(shot.data, 'base64');
  }

  if (stills) {
    for (const s of stills) fs.writeFileSync(path.join(dir, `still_${s}.jpg`), await frameAt(s));
  } else {
    const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-i', path.join(dir, 'narration.wav'), '-af', 'apad', '-t', total.toFixed(3),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
      '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < N; f++) {
      const buf = await frameAt(f / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 300 === 0) process.stdout.write(`frame ${f}/${N}\n`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  ws.close(); chrome.kill();
  console.log('done', stills ? 'stills' : out, total.toFixed(1) + 's');
}
main().catch(e => { console.error(e.message); try { chrome.kill(); } catch {} process.exit(1); });
