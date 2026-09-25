/* es-client.js — 全站统一的 Elasticsearch 连接层(零依赖)
 * 依赖:现代浏览器 fetch + AbortController(file:// 打开同样可用,ES 需开 CORS)
 *
 * API:
 *   ESClient.endpoint()              → 'http://localhost:9200'(localStorage 持久化)
 *   ESClient.setEndpoint(url)        → 设置并刷新徽章
 *   ESClient.auth() / setAuth(cred)  → 可选 'user:pass'(只活在当前页内存,不写 localStorage)
 *   ESClient.raw(method, path, body) → Promise<{ok,status,ms,data,text,contentType}>
 *                                      opts = { timeoutMs, endpoint, auth } 可覆盖单次请求的目标与凭据
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
  /* 学习机口令只在内存里按别名解析,深链不携带明文 */
  var LAB_AUTH = {
    anon: '',
    elastic: 'elastic:elastic-password',
    wrong: 'elastic:wrong-password',
    alice: 'tut-l29-alice:alice-password'
  };
  var sessionAuth = '';
  try { localStorage.removeItem(LS_AUTH); } catch (e) { /* 旧版曾持久化凭据,启动即清 */ }

  function endpoint() {
    try {
      var v = localStorage.getItem(LS_ENDPOINT);
      return v || DEFAULT_ENDPOINT;
    } catch (e) { return DEFAULT_ENDPOINT; }
  }
  function setEndpoint(url) {
    var u = String(url || '').trim().replace(/\/+$/, '');
    if (!/^https?:\/\//.test(u)) u = 'http://' + u;
    try { localStorage.setItem(LS_ENDPOINT, u); } catch (e) { /* 忽略 */ }
    refreshBadges();
    return u;
  }
  function auth() { return sessionAuth; }
  function setAuth(cred) {
    sessionAuth = String(cred || '').trim();
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
  function friendlyError(err) {
    var msg = String((err && err.message) || err || '');
    if (/abort/i.test(msg)) {
      return '请求超时:ES 可能还在启动(首次拉镜像+启动要 1-2 分钟),稍等再试。';
    }
    if (/Failed to fetch|NetworkError|Load failed/i.test(msg)) {
      return '连不上 ' + endpoint() + '\n\n排查顺序:\n' +
        '  1. 终端运行  bash docker/start.sh  启动 ES 9.4.0\n' +
        '  2. 浏览器直接打开 ' + endpoint() + ' 确认有响应\n' +
        '  3. 若 ES 已在跑但仍连不上,说明该实例未开 CORS(本站依赖 docker-compose.yml 里的 http.cors.* 配置)';
    }
    return msg || '未知错误';
  }

  async function raw(method, path, body, opts) {
    opts = opts || {};
    if (!path) path = '/';
    if (path.charAt(0) !== '/') path = '/' + path;
    var url = (opts.endpoint || endpoint()) + path;
    var cred = 'auth' in opts ? opts.auth : auth();   // 实验可用 auth:null 强制匿名
    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, opts.timeoutMs || 15000);
    var init = { method: method, signal: ctrl.signal, headers: {} };
    if (cred) init.headers['Authorization'] = 'Basic ' + btoa(cred);
    if (opts.headers) {
      for (var h in opts.headers) init.headers[h] = opts.headers[h];   // 实验自定义头(如 ApiKey)可覆盖上面的 Authorization
    }
    if (body != null && method !== 'GET' && method !== 'HEAD') {
      if (typeof body === 'string') {
        var parsed = true;
        try { JSON.parse(body); } catch (e) { parsed = false; }
        if (parsed) {
          // 整体是 JSON
          init.body = body;
          init.headers['Content-Type'] = 'application/json';
        } else {
          // 不是整体 JSON 就按 NDJSON(_bulk)口径发送。故意写坏的 body(坏 source 行、
          // 缺末尾换行)也走这里,让 ES 自己报解析错误——那是实验要观察的教学点,
          // 所以这里不做任何修复(不补换行)。
          init.body = body;
          init.headers['Content-Type'] = 'application/x-ndjson';
        }
      } else {
        init.body = JSON.stringify(body);
        init.headers['Content-Type'] = 'application/json';
      }
    }
    var t0 = Date.now();
    try {
      var res = await fetch(url, init);
      var ms = Date.now() - t0;
      var ct = res.headers.get('content-type') || '';
      var text = await res.text();
      var out = { ok: res.ok, status: res.status, ms: ms, contentType: ct, data: null, text: null };
      if (/json/i.test(ct)) {
        try { out.data = JSON.parse(text); } catch (e) { out.text = text; }
      } else {
        out.text = text;
      }
      return out;
    } catch (err) {
      throw new Error(friendlyError(err));
    } finally {
      clearTimeout(timer);
    }
  }

  async function ping() {
    try {
      var r = await raw('GET', '/', null, { timeoutMs: 5000 });
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
    paintBadges('checking', '连接中…', '点击重新检测');
    var r = await ping();
    if (r.ok) paintBadges('ok', r.version + ' · ' + r.cluster, endpoint() + ' — 点击重新检测');
    else paintBadges('down', '未连接 · 点击重试', '先运行 bash docker/start.sh');
  }
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.conn-badge').forEach(function (b) {
      b.addEventListener('click', refreshBadges);
    });
    if (document.querySelector('.conn-badge')) refreshBadges();
  });

  /* ===== JSON 语法高亮 ===== */
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function prettyJSON(value) {
    if (value == null) return '';
    var json = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
    return json.replace(
      /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false)\b|\bnull\b|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/g,
      function (m, str, colon, bool, num) {
        if (str) {
          return colon
            ? '<span class="tk-key">' + esc(str) + '</span>' + colon
            : '<span class="tk-str">' + esc(str) + '</span>';
        }
        if (bool) return '<span class="tk-bool">' + bool + '</span>';
        if (m === 'null') return '<span class="tk-null">null</span>';
        if (num) return '<span class="tk-num">' + num + '</span>';
        return esc(m);
      }
    );
  }

  function consoleLink(method, path, body, opts) {
    opts = opts || {};
    var q = [];
    if (opts.endpoint) q.push('ep=' + encodeURIComponent(opts.endpoint));
    if (opts.authMode) q.push('am=' + encodeURIComponent(opts.authMode));
    if (opts.allowInvalid) q.push('raw=1');
    var hash = '#run=' + encodeURIComponent(method) + '|' +
      encodeURIComponent(path) + '|' + encodeURIComponent(body || '');
    return 'console.html' + (q.length ? '?' + q.join('&') : '') + hash;
  }

  window.ESClient = {
    endpoint: endpoint,
    setEndpoint: setEndpoint,
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
