#!/usr/bin/env node
/* 连接层回归：node tools/console-check.mjs [--live] [--report=path]
 * 零依赖。--live 只使用唯一命名的临时索引，finally 点名清理。
 */
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync, writeFileSync } from 'node:fs';
const source = readFileSync(new URL('../assets/js/es-client.js', import.meta.url), 'utf8');
const checks = [];
function client(fetcher = async () => new Response('{}', { headers: { 'Content-Type': 'application/json' } })) {
  const storage = new Map();
  const label = { textContent: '' };
  const badge = { dataset: {}, querySelector: () => label };
  const sandbox = { window: {}, document: { currentScript: { src: 'http://site.test/es_web/assets/js/es-client.js' },
    addEventListener() {}, querySelectorAll: () => [badge] }, URL, TextEncoder, AbortController,
    setTimeout, clearTimeout, btoa, fetch: fetcher,
    localStorage: { getItem: k => storage.get(k) || null, setItem: (k, v) => storage.set(k, v), removeItem: k => storage.delete(k) } };
  vm.runInNewContext(source, sandbox);
  return { ec: sandbox.window.ESClient, storage, label, badge };
}
async function check(name, run) {
  try { await run(); checks.push({ name, pass: true }); console.log('✓ ' + name); }
  catch (error) { checks.push({ name, pass: false, error: error.message }); console.error('✗ ' + name + ': ' + error.message); }
}
function json(data, status = 200) { return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json', 'X-Test': 'visible' } }); }
await check('地址归一化、代理前缀、拒绝凭据/非 HTTP 地址', async () => {
  const { ec } = client();
  assert.equal(ec.normalizeEndpoint(' localhost:9200/ '), 'http://localhost:9200');
  assert.equal(ec.normalizeEndpoint('https://example.test/proxy/'), 'https://example.test/proxy');
  for (const url of ['', 'ftp://site.test', 'http://user:pass@site.test', 'http://site.test?password=secret', 'http://site.test#hash']) assert.throws(() => ec.normalizeEndpoint(url));
});
await check('课程深链保留 Pages 前缀、独立编码 | / Unicode / 换行、认证别名', async () => {
  const { ec } = client();
  const body = '{"text":"中文 | %20"}\n';
  const url = new URL(ec.consoleLink('POST', '/_analyze?x=a|b', body, { endpoint: 'http://localhost:9201', authMode: 'wrong', allowInvalid: true }));
  assert.equal(url.pathname, '/es_web/console.html');
  const parts = url.hash.slice(5).split('|').map(decodeURIComponent);
  assert.deepEqual(parts, ['POST', '/_analyze?x=a|b', body]);
  assert.equal(url.searchParams.get('am'), 'wrong');
  assert.equal(url.searchParams.get('raw'), '1');
  assert.equal(url.searchParams.get('ep'), 'http://localhost:9201');
  assert(!url.href.includes('password'));
});
await check('JSON / NDJSON 按接口识别，Bulk 原文与末尾换行不改写', async () => {
  const calls = [];
  const { ec } = client(async (url, init) => { calls.push({ url, init }); return json({ ok: true }); });
  const nd = '{"delete":{"_index":"test","_id":"1"}}\n';
  await ec.raw('POST', '/_bulk', nd);
  assert.equal(calls.at(-1).init.body, nd);
  assert.equal(calls.at(-1).init.headers['Content-Type'], 'application/x-ndjson');
  await ec.raw('POST', '/test/_bulk', nd.slice(0, -1));
  assert.equal(calls.at(-1).init.body, nd.slice(0, -1));
  await ec.raw('POST', '/_search', '{broken');
  assert.equal(calls.at(-1).init.headers['Content-Type'], 'application/json');
  await ec.raw('POST', '/_bulk', '{"index":{}}\n{bad source}\n');
  assert.equal(calls.at(-1).init.headers['Content-Type'], 'application/x-ndjson');
  await ec.raw('POST', '/_msearch', '{}\n{}\n');
  assert.equal(calls.at(-1).init.headers['Content-Type'], 'application/x-ndjson');
});
await check('GET / HEAD 无 body，无 body 时不额外添加 Content-Type', async () => {
  const calls = [];
  const { ec } = client(async (url, init) => { calls.push(init); return new Response(null, { status: 200 }); });
  for (const method of ['GET', 'HEAD']) {
    await ec.raw(method, '/', '{"ignored":true}');
    assert.equal(calls.at(-1).body, undefined);
    assert.equal(calls.at(-1).headers['Content-Type'], undefined);
  }
});
await check('显式 Content-Type 和实验自定义 Authorization 生效', async () => {
  let sent;
  const { ec } = client(async (url, init) => { sent = init; return json({}); });
  await ec.raw('POST', '/_bulk', '{}', { headers: { 'content-type': 'application/json', Authorization: 'ApiKey fake' }, auth: 'user:pass' });
  assert.equal(sent.headers.Authorization, 'ApiKey fake');
  assert.equal(sent.headers['Content-Type'], 'application/json');
  assert.equal(sent.headers['content-type'], undefined);
  await ec.raw('POST', '/_search', '{}', { contentType: 'application/x-ndjson' });
  assert.equal(sent.headers['Content-Type'], 'application/x-ndjson');
});
await check('Unicode Basic 认证保留密码空格，凭据只在内存', async () => {
  let sent;
  const { ec, storage } = client(async (url, init) => { sent = init; return json({}); });
  const cred = '测试: pa ss ';
  ec.setAuth(cred);
  await ec.raw('GET', '/');
  assert.equal(Buffer.from(sent.headers.Authorization.slice(6), 'base64').toString('utf8'), cred);
  assert.equal(ec.auth(), cred);
  assert.equal(storage.has('es-web:auth'), false);
});
await check('保留精确响应原文、JSON 数据与可读取的响应头', async () => {
  const raw = '{ "count": 1 }\n';
  const { ec } = client(async () => new Response(raw, { headers: { 'Content-Type': 'application/json', 'X-Test': 'value' } }));
  const result = await ec.raw('GET', '/');
  assert.equal(result.text, raw);
  assert.equal(result.data.count, 1);
  assert.equal(result.headers['x-test'], 'value');
  assert.equal((await client(async () => new Response('broken', { headers: { 'Content-Type': 'application/json' } })).ec.raw('GET', '/')).text, 'broken');
});
await check('停止与超时分开报告，无未清理的定时器', async () => {
  const wait = (url, init) => new Promise((resolve, reject) => {
    if (init.signal.aborted) reject(new DOMException('aborted', 'AbortError'));
    else init.signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')), { once: true });
  });
  const { ec } = client(wait);
  const ctrl = new AbortController();
  const result = ec.raw('GET', '/', null, { signal: ctrl.signal });
  ctrl.abort();
  await assert.rejects(result, e => e.code === 'aborted');
  await assert.rejects(ec.raw('GET', '/', null, { timeoutMs: 10 }), e => e.code === 'timeout');
  await assert.rejects(ec.raw('GET', '/', null, { signal: ctrl.signal }), e => e.code === 'aborted');
});
await check('失败提示使用单次目标地址，不误报默认端点或断言 CORS 原因', async () => {
  const { ec } = client(async () => { throw new TypeError('Failed to fetch'); });
  await assert.rejects(ec.raw('GET', '/', null, { endpoint: 'http://localhost:9201' }), e => e.message.includes('9201') && !e.message.includes('9200') && e.message.includes('检查 CORS'));
});
await check('连接徽章读取页面目标，旧检测结果不能覆盖新地址', async () => {
  const resolvers = [];
  const { ec, badge, label } = client(() => new Promise(resolve => resolvers.push(resolve)));
  let ep = 'http://localhost:9200';
  ec.setConnectionProvider(() => ({ endpoint: ep, auth: '' }));
  const old = ec.refreshBadges();
  ep = 'http://localhost:9201';
  const latest = ec.refreshBadges();
  resolvers[1](json({ version: { number: '9.4.0' }, cluster_name: 'new' }));
  await latest;
  resolvers[0](json({ version: { number: '9.4.0' }, cluster_name: 'old' }));
  await old;
  assert(label.textContent.includes('new'));
  assert(badge.title.includes('9201'));
});
await check('高亮所有文本均转义，HTML 字符不会成为标签', async () => {
  const { ec } = client();
  for (const value of ['<img src=x onerror=alert(1)>', { text: '<script>alert(1)</script>', n: 0, b: false }]) {
    const html = ec.prettyJSON(value);
    assert(!/<(?:img|script)\b/.test(html));
    assert(html.includes('&lt;'));
  }
});
if (process.argv.includes('--live')) {
  const index = 'tut-console-qa-' + Date.now();
  const { ec } = client(fetch);
  const opts = { endpoint: 'http://127.0.0.1:9200', auth: '' };
  const call = (m, p, b, extra) => ec.raw(m, p, b, { ...opts, ...extra });
  try {
    await check('真实 ES：9.4.0 版本、健康 JSON、CAT 文本、HEAD 空响应', async () => {
      assert.equal((await call('GET', '/')).data.version.number, '9.4.0');
      assert((await call('GET', '/_cluster/health')).data.status);
      assert((await call('GET', '/_cat/nodes?v')).text.includes('name'));
      const head = await call('HEAD', '/' + index);
      assert.equal(head.status, 404); assert.equal(head.text, '');
    });
    await check('真实 ES：包含 | / 中文的 POST 与非法 JSON 400', async () => {
      const r = await call('POST', '/_analyze', '{"analyzer":"keyword","text":"中文 | %20"}');
      assert.equal(r.status, 200); assert.equal(r.data.tokens[0].token, '中文 | %20');
      const bad = await call('POST', '/_search', '{broken');
      assert.equal(bad.status, 400); assert(bad.data.error);
    });
    await check('真实 ES：临时索引、Bulk 换行成功 / 缺换行 400 / 坏 source 条级失败', async () => {
      const created = await call('PUT', '/' + index, { settings: { number_of_shards: 1, number_of_replicas: 0 } });
      assert.equal(created.status, 200);
      const nd = '{"index":{"_id":"1"}}\n{"text":"hello | world"}\n';
      const good = await call('POST', '/' + index + '/_bulk?refresh=true', nd);
      assert.equal(good.status, 200); assert.equal(good.data.errors, false);
      const missing = await call('POST', '/' + index + '/_bulk', nd.slice(0, -1));
      assert.equal(missing.status, 400); assert(missing.data.error.reason.includes('newline'));
      const bad = await call('POST', '/' + index + '/_bulk', '{"index":{"_id":"bad"}}\n{this is not json}\n');
      assert.equal(bad.status, 200); assert.equal(bad.data.errors, true); assert.equal(bad.data.items[0].index.status, 400);
      assert.equal((await call('GET', '/' + index + '/_doc/1')).data._source.text, 'hello | world');
    });
  } finally {
    await check('真实 ES：点名清理临时索引，HEAD 404 确认', async () => {
      const r = await call('DELETE', '/' + index);
      assert([200, 404].includes(r.status));
      assert.equal((await call('HEAD', '/' + index)).status, 404);
    });
  }
}
const report = { time: new Date().toISOString(), type: 'connection-unit-and-optional-real-es', live: process.argv.includes('--live'), checks };
const reportArg = process.argv.find(arg => arg.startsWith('--report='));
if (reportArg) writeFileSync(reportArg.slice(9), JSON.stringify(report, null, 2) + '\n');
if (checks.some(c => !c.pass)) process.exitCode = 1;
console.log(`${checks.filter(c => c.pass).length}/${checks.length} checks passed`);
