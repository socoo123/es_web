// tools/figwidth.mjs — SVG 文本估宽检查(与 PLAN.md 排印纪律配套)
// 用法:node tools/figwidth.mjs chapters/ch01.html ... experiments/ch01.js ...
// 估宽:fig-name/fig-key(等宽)0.6em/字符、中文 1em;fig-sub 英数 0.55em、中文 1em
// 规则:文本估宽必须 ≤ 所在盒子宽 − 12,否则列出可疑项(需人工判断是否真的溢出)
import fs from 'node:fs';

function attrs(s) {
  const o = {};
  for (const m of s.matchAll(/([\w-]+)="([^"]*)"/g)) o[m[1]] = m[2];
  return o;
}

let bad = 0;
for (const f of process.argv.slice(2)) {
  const src = fs.readFileSync(f, 'utf8');
  const svgs = src.match(/<svg[\s\S]*?<\/svg>/g) || [];
  for (const svg of svgs) {
    const rects = [...svg.matchAll(/<rect\s+([^>]*?)\/?>/g)]
      .map(m => attrs(m[1]))
      .filter(a => a.width)
      .map(a => ({ x: +a.x, y: +a.y, w: +a.width, h: +a.height }));
    for (const t of svg.matchAll(/<text\s+([^>]*)>([^<]*)<\/text>/g)) {
      const a = attrs(t[1]);
      const s = t[2];
      if (!a.class || !/fig-(name|key|sub)/.test(a.class) || !a.x) continue;
      const px = /fig-name/.test(a.class) ? 13 : 12;
      const mono = /fig-(name|key)/.test(a.class);
      let w = 0;
      for (const ch of s) {
        const cjk = ch.codePointAt(0) > 0x2e7f; // CJK 与全角标点
        w += cjk ? px : px * (mono ? 0.6 : 0.55);
      }
      const anchor = a['text-anchor'] || 'start';
      const cx = anchor === 'middle' ? +a.x : anchor === 'end' ? +a.x - w / 2 : +a.x + w / 2;
      const ty = +a.y;
      // 找基线落入、水平有交集的盒子
      const box = rects.find(r =>
        cx + w / 2 > r.x + 2 && cx - w / 2 < r.x + r.w - 2 && ty > r.y + 2 && ty < r.y + r.h + 3);
      if (box && w > box.w - 12) {
        bad++;
        console.log(`${f}: “${s.slice(0, 34)}” 估宽 ${w.toFixed(0)} > 盒宽可用 ${box.w - 12}(y=${ty})`);
      }
    }
  }
}
console.log(bad ? `✗ ${bad} 处可疑溢出(需人工复核)` : '✓ 全部文本估宽在盒内');
process.exit(bad ? 1 : 0);
