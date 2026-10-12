/* es-client.js — 全站统一的 Elasticsearch 连接层(零依赖)
 * 依赖:现代浏览器 fetch + AbortController(file:// 打开同样可用,ES 需开 CORS)
 *
 * API:
 *   ESClient.endpoint()              → 'http://localhost:9200'(localStorage 持久化)
 *   ESClient.setEndpoint(url)        → 设置并刷新徽章
 *   ESClient.auth() / setAuth(cred)  → 可选 'user:pass'(只活在当前页内存,不写 localStorage)
 *   ESClient.raw(method, path, body) → Promise<{ok,status,ms,data,text,contentType}>
 *                                      opts = { timeoutMs, endpoint, auth, signal, contentType, headers }
 *   ESClient.ping()                  → Promise<{ok,version,cluster,error}>
 *   ESClient.prettyJSON(value)       → 带语法高亮的 HTML 字符串
 *   ESClient.consoleLink(m,p,b,opts) → 控制台深链;opts.endpoint / authMode / allowInvalid
 *                                      凭据用实验别名(anon|elastic|wrong|alice),不进 URL
 *   ESClient.refreshBadges()         → 重测连接并更新所有 .conn-badge
 */
(function () {
  'use strict';
  var LS_ENDPOINT = 'es-web:endpoint';
  var LS_AUTH = 'es-web:auth';
  var DEFAULT_ENDPOINT = 'http://localhost:9200';
  /* 从脚本位置定位站点根,兼容 chapters/、Pages 子路径和 file://。 */
  var CONSOLE_URL = new URL('../../console.html', document.currentScript.src).href;
  /* 学习机口令只在内存里按别名解析,深链不携带明文 */
  var LAB_AUTH = {
    anon: '',
    elastic: 'elastic:elastic-password',
    wrong: 'elastic:wrong-password',
    alice: 'tut-l29-alice:alice-password'
  };
  var sessionAuth = '';
  var connectionProvider = null;
  var badgeRevision = 0;
  try { localStorage.removeItem(LS_AUTH); } catch (e) { /* 旧版曾持久化凭据,启动即清 */ }

  function endpoint() {
    try {
      var v = localStorage.getItem(LS_ENDPOINT);
      return v || DEFAULT_ENDPOINT;
    } catch (e) { return DEFAULT_ENDPOINT; }
  }
  function normalizeEndpoint(url) {
    var value = String(url || '').trim();
    if (!value) throw new Error('请输入 ES 服务地址，例如 http://localhost:9200。');
    if (!/^[a-z][a-z\d+.-]*:\/\//i.test(value)) value = 'http://' + value;
    var parsed;
    try { parsed = new URL(value); } catch (e) { throw new Error('服务地址无效，请检查主机名和端口。'); }
    if (!/^https?:$/.test(parsed.protocol) || !parsed.hostname || parsed.username || parsed.password || parsed.search || parsed.hash) {
      throw new Error('服务地址须为 HTTP / HTTPS 地址；凭据请填在 Basic 认证栏，地址中不要带查询参数或 #。');
    }
    return parsed.href.replace(/\/+$/, '');
  }
  function setEndpoint(url) {
    var u = normalizeEndpoint(url);
    try { localStorage.setItem(LS_ENDPOINT, u); } catch (e) { /* 忽略 */ }
    refreshBadges();
    return u;
  }
  function auth() { return sessionAuth; }
  function setAuth(cred) {
    sessionAuth = String(cred || '');
    try { localStorage.removeItem(LS_AUTH); } catch (e) { /* 忽略 */ }
    return sessionAuth;
  }
  function authModeFor(cred) {
    if (cred == null || cred === '') return 'anon';
    var keys = Object.keys(LAB_AUTH);
    for (var i = 0; i < keys.length; i++) {
      if (LAB_AUTH[keys[i]] === cred) return keys[i];
    }
    return '';
  }
  function credForMode(mode) {
    return Object.prototype.hasOwnProperty.call(LAB_AUTH, mode) ? LAB_AUTH[mode] : null;
  }

  /* 把 fetch 异常翻译成人能看懂的指引 */
  function friendlyError(err, target, timedOut) {
    target = target || endpoint();
    var msg = String((err && err.message) || err || '');
    if (timedOut) return '请求超时：' + target + ' 未在设定时间内完成响应。可增大超时时间或检查 ES 状态。';
    if ((err && err.name === 'AbortError') || /abort/i.test(msg)) {
      return '请求已停止。';
    }
    if (/Failed to fetch|NetworkError|Load failed/i.test(msg)) {
      return '连不上 ' + target + '\n\n排查顺序:\n' +
        '  1. 终端运行  bash docker/start.sh  启动 ES 9.4.0\n' +
        '  2. 浏览器直接打开 ' + target + '，检查地址、端口和服务状态\n' +
        '  3. 服务可用时，检查 CORS、HTTPS 混合内容或本地网络访问权限；具体原因可在浏览器开发者工具中查看';
    }
    return msg || '未知错误';
  }

  async function raw(method, path, body, opts) {
    opts = opts || {};
    method = String(method || 'GET').toUpperCase();
    if (!path) path = '/';
    if (path.charAt(0) !== '/') path = '/' + path;
    var target = normalizeEndpoint(opts.endpoint || endpoint());
    var url = target + path;
    var cred = 'auth' in opts ? opts.auth : auth();   // 实验可用 auth:null 强制匿名
    var init = { method: method, headers: {} };
    if (cred) {
      var bytes = new TextEncoder().encode(cred);
      var binary = '';
      bytes.forEach(function (byte) { binary += String.fromCharCode(byte); });
      init.headers['Authorization'] = 'Basic ' + btoa(binary);
    }
    if (opts.headers) {
      for (var h in opts.headers) init.headers[h] = opts.headers[h];   // 实验自定义头(如 ApiKey)可覆盖上面的 Authorization
    }
    if (body != null && method !== 'GET' && method !== 'HEAD') {
      if (typeof body === 'string') {
        var parsed = true;
        try { JSON.parse(body); } catch (e) { parsed = false; }
        init.body = body;
        var streaming = /\/(?:_bulk|_msearch)(?:\/|\?|$)/.test(path);
        var lines = body.split('\n').filter(function (line) { return line.trim(); });
        var ndjson = !parsed && lines.length > 1 && lines.every(function (line) {
          try { JSON.parse(line); return true; } catch (e) { return false; }
        });
        init.headers['Content-Type'] = streaming || ndjson ? 'application/x-ndjson' : 'application/json';
      } else {
        init.body = JSON.stringify(body);
        init.headers['Content-Type'] = 'application/json';
      }
    }
    if (init.body != null) {
      var headerType = Object.keys(opts.headers || {}).find(function (key) { return key.toLowerCase() === 'content-type'; });
      if (headerType) init.headers['Content-Type'] = opts.headers[headerType];
      if (headerType && headerType !== 'Content-Type') delete init.headers[headerType];
      if (opts.contentType) init.headers['Content-Type'] = opts.contentType;
    }
    var ctrl = new AbortController();
    var timedOut = false;
    var abort = function () { ctrl.abort(); };
    if (opts.signal) {
      if (opts.signal.aborted) abort();
      else opts.signal.addEventListener('abort', abort, { once: true });
    }
    init.signal = ctrl.signal;
    var timer = setTimeout(function () { timedOut = true; ctrl.abort(); }, opts.timeoutMs || 15000);
    var t0 = Date.now();
    try {
      var res = await fetch(url, init);
      var ct = res.headers.get('content-type') || '';
      var text = await res.text();
      var headers = {};
      res.headers.forEach(function (value, name) { headers[name] = value; });
      var out = { ok: res.ok, status: res.status, ms: Date.now() - t0, contentType: ct, data: null, text: text, headers: headers };
      if (/json/i.test(ct)) {
        try { out.data = JSON.parse(text); } catch (e) { out.text = text; }
      } else {
        out.text = text;
      }
      return out;
    } catch (err) {
      var failure = new Error(friendlyError(err, target, timedOut));
      failure.code = timedOut ? 'timeout' : (ctrl.signal.aborted ? 'aborted' : 'network');
      throw failure;
    } finally {
      clearTimeout(timer);
      if (opts.signal) opts.signal.removeEventListener('abort', abort);
    }
  }

  async function ping(opts) {
    try {
      var r = await raw('GET', '/', null, Object.assign({ timeoutMs: 5000 }, opts || {}));
      if (r.ok && r.data && r.data.version) {
        return { ok: true, version: r.data.version.number, cluster: r.data.cluster_name };
      }
      return { ok: false, error: 'HTTP ' + r.status };
    } catch (err) {
      return { ok: false, error: err.message };
    }
  }

  /* ===== 连接徽章 ===== */
  function paintBadges(state, label, title) {
    document.querySelectorAll('.conn-badge').forEach(function (b) {
      b.dataset.state = state;
      var lab = b.querySelector('.conn-label');
      if (lab) lab.textContent = label;
      if (title) b.title = title;
    });
  }
  async function refreshBadges() {
    var revision = ++badgeRevision;
    paintBadges('checking', '连接中…', '点击重新检测');
    var opts, target, r;
    try {
      opts = connectionProvider ? connectionProvider() : {};
      target = normalizeEndpoint(opts.endpoint || endpoint());
      r = await ping(opts);
    } catch (err) { r = { ok: false, error: err.message }; }
    if (revision !== badgeRevision) return r;
    if (r.ok) paintBadges('ok', r.version + ' · ' + r.cluster, target + ' — 点击重新检测');
    else paintBadges('down', (r.error && /^HTTP /.test(r.error) ? r.error + ' · 点击重试' : '未连接 · 点击重试'), r.error || '检查 ES 服务地址');
    return r;
  }
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.conn-badge').forEach(function (b) {
      b.addEventListener('click', function () { refreshBadges(); });
    });
    if (document.querySelector('.conn-badge')) Promise.resolve().then(refreshBadges);
  });

  /* ===== JSON 语法高亮 ===== */
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function prettyJSON(value) {
    if (value == null) return '';
    var json = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
    var pattern = /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false)\b|\bnull\b|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/g;
    var html = '', end = 0, match;
    while ((match = pattern.exec(json))) {
      html += esc(json.slice(end, match.index));
      var kind = match[1] ? (match[2] ? 'key' : 'str') : match[3] ? 'bool' : match[4] ? 'num' : 'null';
      html += '<span class="tk-' + kind + '">' + esc(match[1] || match[0]) + '</span>' + (match[2] || '');
      end = pattern.lastIndex;
    }
    return html + esc(json.slice(end));
  }

  function consoleLink(method, path, body, opts) {
    opts = opts || {};
    var q = [];
    if (opts.endpoint) q.push('ep=' + encodeURIComponent(opts.endpoint));
    if (opts.authMode) q.push('am=' + encodeURIComponent(opts.authMode));
    if (opts.allowInvalid) q.push('raw=1');
    var hash = '#run=' + encodeURIComponent(method) + '|' +
      encodeURIComponent(path) + '|' + encodeURIComponent(body || '');
    return CONSOLE_URL + (q.length ? '?' + q.join('&') : '') + hash;
  }

  window.ESClient = {
    endpoint: endpoint,
    setEndpoint: setEndpoint,
    normalizeEndpoint: normalizeEndpoint,
    setConnectionProvider: function (provider) { connectionProvider = provider; },
    auth: auth,
    setAuth: setAuth,
    authModeFor: authModeFor,
    credForMode: credForMode,
    raw: raw,
    ping: ping,
    prettyJSON: prettyJSON,
    esc: esc,
    consoleLink: consoleLink,
    refreshBadges: refreshBadges,
    friendlyError: friendlyError
  };
})();
