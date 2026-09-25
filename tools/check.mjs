#!/usr/bin/env node
/* check.mjs — 站点结构与数据注册表校验(零依赖)
 * 用法:node tools/check.mjs   (任何 ❌ 都会以退出码 1 结束)
 * 校验项:
 *   1. chapters/ch01..ch30.html 齐全,七段式骨架完整,pager 正确
 *   2. stub 章(data-status="stub")与 index 卡片 is-stub 一致
 *   3. 正式章必须引 experiments.js 且至少 1 个 exp-slot
 *   4. experiments/chNN.js 注册表(vm 沙箱执行):ESEXPERIMENTS / ESFLOWS schema 合法,
 *      id 前缀归属本章;章节页引用的 data-exp / data-flow 必须已注册
 *   5. index.html 链接的文件真实存在
 */
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];
const warn = [];
let stubCount = 0;
let doneCount = 0;

function err(file, msg) { errors.push(`❌ ${file}: ${msg}`); }
function ok(msg) { process.stdout.write('✓ ' + msg + '\n'); }

const CHAPTERS = Array.from({ length: 30 }, (_, i) => {
  const n = String(i + 1).padStart(2, '0');
  return { n, file: `chapters/ch${n}.html` };
});

/* ===== 1+2+3:章节骨架 ===== */
const isStubByCh = {};
for (const ch of CHAPTERS) {
  const p = path.join(ROOT, ch.file);
  if (!existsSync(p)) { err(ch.file, '文件不存在'); continue; }
  const html = readFileSync(p, 'utf8');
  for (const must of ['class="chapter"', `data-ch="ch${ch.n}"`, 'class="goal"', 'class="lesson"', 'class="recap"', 'class="ch-footer"']) {
    if (!html.includes(must)) err(ch.file, `缺少 ${must}`);
  }
  const stub = html.includes('data-status="stub"');
  isStubByCh[ch.n] = stub;
  if (stub) stubCount++; else doneCount++;

  // pager:上一课/下一课链接(首末课允许 disabled)
  const prevN = String(Math.max(1, Number(ch.n) - 1)).padStart(2, '0');
  const nextN = String(Math.min(30, Number(ch.n) + 1)).padStart(2, '0');
  if (ch.n !== '01' && !html.includes(`ch${prevN}.html`)) err(ch.file, `pager 缺上一课 ch${prevN}.html`);
  if (ch.n !== '30' && !html.includes(`ch${nextN}.html`)) err(ch.file, `pager 缺下一课 ch${nextN}.html`);

  if (!stub) {
    if (!html.includes('experiments.js')) err(ch.file, '正式章必须引入 assets/js/experiments.js');
    if (!html.includes('exp-slot')) err(ch.file, '正式章至少要有 1 个 data-exp 插槽');
  }
}
ok(`章节骨架:30 页齐全(stub ${stubCount} / 正式 ${doneCount})`);

/* ===== index 卡片一致性 ===== */
const indexPath = path.join(ROOT, 'index.html');
if (!existsSync(indexPath)) {
  err('index.html', '文件不存在');
} else {
  const idx = readFileSync(indexPath, 'utf8');
  for (const ch of CHAPTERS) {
    if (!idx.includes(`chapters/ch${ch.n}.html`)) err('index.html', `缺 ch${ch.n} 卡片链接`);
    const m = idx.match(new RegExp(`<a class="card([^"]*)" data-ch="ch${ch.n}"`));
    if (!m) { err('index.html', `ch${ch.n} 卡片结构不对`); continue; }
    const hasStub = m[1].includes('is-stub');
    if (hasStub !== isStubByCh[ch.n]) err('index.html', `ch${ch.n} 卡片 is-stub 与章节状态不一致`);
  }
  for (const f of ['console.html', 'cheatsheet.html']) {
    if (!existsSync(path.join(ROOT, f))) err('index.html', `链接的 ${f} 不存在`);
  }
  ok('index 卡片与链接一致');
}

/* ===== 4:注册表 ===== */
const expDir = path.join(ROOT, 'experiments');
const registry = { exps: {}, flows: {} };
if (existsSync(expDir)) {
  for (const f of readdirSync(expDir).filter((x) => x.endsWith('.js'))) {
    const code = readFileSync(path.join(expDir, f), 'utf8');
    const sandbox = { window: {} };
    try {
      vm.createContext(sandbox);
      vm.runInContext(code, sandbox, { filename: f });
    } catch (e) {
      err(`experiments/${f}`, `执行失败:${e.message}`);
      continue;
    }
    const win = sandbox.window;
    const exps = win.ESEXPERIMENTS || {};
    const flows = win.ESFLOWS || {};
    const fileCh = (f.match(/^ch(\d{2})\.js$/) || [])[1];
    if (!fileCh) { err(`experiments/${f}`, '文件名必须是 chNN.js'); continue; }

    for (const [id, x] of Object.entries(exps)) {
      if (!id.startsWith(`ch${fileCh}-`)) err(`experiments/${f}`, `实验 ${id} 前缀不属于本章`);
      if (x.version !== 1) err(`experiments/${f}`, `${id}: version 必须为 1`);
      if (x.id !== id) err(`experiments/${f}`, `${id}: id 字段与键不一致`);
      if (!x.title || x.title.length > 60) err(`experiments/${f}`, `${id}: title 缺失或超 60 字`);
      if (!['GET', 'POST', 'PUT', 'DELETE', 'HEAD'].includes(x.method)) err(`experiments/${f}`, `${id}: method 非法`);
      if (typeof x.path !== 'string' || !x.path.startsWith('/')) err(`experiments/${f}`, `${id}: path 必须以 / 开头`);
      if (typeof x.body === 'string' && x.body.trim() && x.allowInvalidBody !== true) {
        const okJson = (() => { try { JSON.parse(x.body); return true; } catch { return false; } })();
        const okNd = !okJson && x.body.endsWith('\n') &&
          x.body.split('\n').filter(l => l.trim()).every(l => { try { JSON.parse(l); return true; } catch { return false; } });
        if (!okJson && !okNd) err(`experiments/${f}`, `${id}: body 字符串既不是合法 JSON,也不是带末尾换行的 NDJSON`);
      }
      registry.exps[id] = x;
    }
    for (const [id, fl] of Object.entries(flows)) {
      if (!id.startsWith(`ch${fileCh}-`)) err(`experiments/${f}`, `动画 ${id} 前缀不属于本章`);
      if (fl.version !== 1) err(`experiments/${f}`, `${id}: version 必须为 1`);
      if (!fl.title || fl.title.length > 60) err(`experiments/${f}`, `${id}: title 缺失或超 60 字`);
      if (!(fl.speed >= 600 && fl.speed <= 6000)) err(`experiments/${f}`, `${id}: speed 需在 600-6000`);
      if (!Array.isArray(fl.steps) || fl.steps.length < 2 || fl.steps.length > 40) {
        err(`experiments/${f}`, `${id}: steps 需 2-40 步`);
      } else {
        fl.steps.forEach((st, i) => {
          if (typeof st.svg !== 'string' || !st.svg.trimStart().startsWith('<svg')) {
            err(`experiments/${f}`, `${id} 第 ${i + 1} 步:svg 必须是 <svg> 开头的完整片段`);
          } else {
            const opens = (st.svg.match(/<svg/g) || []).length;
            const closes = (st.svg.match(/<\/svg>/g) || []).length;
            if (opens !== closes) err(`experiments/${f}`, `${id} 第 ${i + 1} 步:svg 标签未闭合`);
          }
          if (!st.note || st.note.length > 200) err(`experiments/${f}`, `${id} 第 ${i + 1} 步:note 缺失或超 200 字`);
        });
      }
      registry.flows[id] = fl;
    }
  }
}
ok(`注册表:实验 ${Object.keys(registry.exps).length} 个,动画 ${Object.keys(registry.flows).length} 个`);

/* ===== 章节页引用的 data-exp / data-flow 必须已注册 ===== */
for (const ch of CHAPTERS) {
  const p = path.join(ROOT, ch.file);
  if (!existsSync(p)) continue;
  const html = readFileSync(p, 'utf8');
  for (const m of html.matchAll(/data-exp="([^"]+)"/g)) {
    if (!registry.exps[m[1]]) err(ch.file, `引用的实验 ${m[1]} 未注册`);
  }
  for (const m of html.matchAll(/data-flow="([^"]+)"/g)) {
    if (!registry.flows[m[1]]) err(ch.file, `引用的动画 ${m[1]} 未注册`);
  }
}
ok('章节页 data-exp / data-flow 引用全部可解析');

/* ===== 事实锚点与控制台回归(不快照正文) ===== */
const banned = ['10.3.2', '25.0.2+10', '4.1.130.Final'];
for (const rel of ['chapters', 'experiments']) {
  for (const f of readdirSync(path.join(ROOT, rel))) {
    if (!/\.(html|js)$/.test(f)) continue;
    const text = readFileSync(path.join(ROOT, rel, f), 'utf8');
    for (const bad of banned) {
      if (text.includes(bad)) err(`${rel}/${f}`, `仍含已勘误的版本数字 ${bad}`);
    }
  }
}
const ch02html = readFileSync(path.join(ROOT, 'chapters/ch02.html'), 'utf8');
for (const needle of ['10.4.0', '26.0.1+8', '4.1.132.Final']) {
  if (!ch02html.includes(needle)) err('chapters/ch02.html', `版本表缺少 ${needle}`);
}
const ch02exp = readFileSync(path.join(ROOT, 'experiments/ch02.js'), 'utf8');
if (!ch02exp.includes('10.4.0') || !ch02exp.includes('26.0.1')) {
  err('experiments/ch02.js', '实验预期未锚定 Lucene 10.4.0 / JDK 26.0.1');
}
const consoleJs = readFileSync(path.join(ROOT, 'assets/js/console.js'), 'utf8');
if (/req-body'\)\.value[\s\S]{0,40}\.trim\(/.test(consoleJs)) {
  err('assets/js/console.js', '发送路径仍在 trim 请求体,会吃掉 Bulk 末尾换行');
}
if (!consoleJs.includes('仍然发送原文') || !consoleJs.includes("qs.get('raw')")) {
  err('assets/js/console.js', '缺少破坏实验的原样发送入口');
}
const clientJs = readFileSync(path.join(ROOT, 'assets/js/es-client.js'), 'utf8');
if (!clientJs.includes('authMode') || /localStorage\.setItem\(LS_AUTH/.test(clientJs)) {
  err('assets/js/es-client.js', '深链凭据别名缺失,或仍把 Basic 凭据写入 localStorage');
}
const expJs = readFileSync(path.join(ROOT, 'assets/js/experiments.js'), 'utf8');
if (!expJs.includes('authMode') || !expJs.includes('allowInvalid')) {
  err('assets/js/experiments.js', '控制台深链未带端点/认证别名或破坏实验标记');
}
const ch13 = readFileSync(path.join(ROOT, 'chapters/ch13.html'), 'utf8');
if (!ch13.includes('application/x-ndjson')) err('chapters/ch13.html', '未说明 NDJSON 的 Content-Type');
const cheat = readFileSync(path.join(ROOT, 'cheatsheet.html'), 'utf8');
const rootRow = cheat.split('\n').find((line) => line.includes('GET /</code>'));
if (rootRow && /版本、集群名、角色/.test(rootRow)) err('cheatsheet.html', 'GET / 仍被写成能看角色');
ok('版本锚点、Bulk 换行与深链凭据检查通过');

/* ===== 汇总 ===== */
if (warn.length) warn.forEach((w) => process.stdout.write('⚠ ' + w + '\n'));
if (errors.length) {
  errors.forEach((e) => process.stderr.write(e + '\n'));
  process.stderr.write(`\n共 ${errors.length} 处错误,修复后再继续。\n`);
  process.exit(1);
}
process.stdout.write('\n全部通过 ✅\n');
