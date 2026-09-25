/* console.js — 控制台页:请求构建 / 预设 / 历史 / 深链(#run=METHOD|PATH|BODY) */
(function () {
  'use strict';
  var EC = window.ESClient;
  var HISTORY_KEY = 'es-web:history';
  var HISTORY_MAX = 60;

  /* P0 内置预设;后续章节实验也可经深链跳进来 */
  var PRESETS = [
    { group: '集群体检', items: [
      { label: '节点信息', method: 'GET', path: '/' },
      { label: '集群健康', method: 'GET', path: '/_cluster/health' },
      { label: '索引列表', method: 'GET', path: '/_cat/indices?v' },
      { label: '节点列表', method: 'GET', path: '/_cat/nodes?v&h=name,heap.percent,cpu,load_1m' },
      { label: 'search 线程池', method: 'GET', path: '/_cat/thread_pool?v&h=name,size,queue,rejected,completed' }
    ] },
    { group: '建索引 & 写文档', items: [
      { label: '建 study 索引', method: 'PUT', path: '/study', body: '{\n  "settings": { "number_of_shards": 1, "number_of_replicas": 0 }\n}' },
      { label: '写一条文档', method: 'PUT', path: '/study/_doc/1?refresh=true', body: '{\n  "title": "Elasticsearch 源码精读",\n  "lesson": 14,\n  "tags": ["lucene", "segment", "translog"]\n}' },
      { label: '再看 mapping', method: 'GET', path: '/study/_mapping' }
    ] },
    { group: '分析与搜索', items: [
      { label: '标准分词器', method: 'POST', path: '/study/_analyze', body: '{\n  "analyzer": "standard",\n  "text": "Tracking a GET request through Elasticsearch internals"\n}' },
      { label: 'match 搜索', method: 'POST', path: '/study/_search', body: '{\n  "query": { "match": { "title": "源码" } }\n}' },
      { label: '带 explain 的打分', method: 'POST', path: '/study/_search', body: '{\n  "query": { "match": { "title": "lucene" } },\n  "explain": true\n}' }
    ] },
    { group: '清理', items: [
      { label: '删除 study 索引', method: 'DELETE', path: '/study' }
    ] }
  ];

  function esc(s) { return EC.esc(String(s)); }
  function $(sel) { return document.querySelector(sel); }

  function loadHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; } catch (e) { return []; }
  }
  function saveHistory(list) {
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(list.slice(0, HISTORY_MAX))); } catch (e) { /* 忽略 */ }
  }
  function pushHistory(entry) {
    var list = loadHistory().filter(function (h) {
      return !(h.m === entry.m && h.p === entry.p && h.b === entry.b);
    });
    list.unshift(entry);
    saveHistory(list);
    renderHistory();
  }

  function renderHistory() {
    var box = $('#hist-list');
    if (!box) return;
    var list = loadHistory();
    box.innerHTML = '';
    if (!list.length) {
      var empty = document.createElement('div');
      empty.className = 'exp-status';
      empty.textContent = '暂无历史(每条请求自动留痕)';
      box.appendChild(empty);
      return;
    }
    list.slice(0, 20).forEach(function (h) {
      var it = document.createElement('div');
      it.className = 'hist-item';
      var m = document.createElement('span');
      m.className = 'mth mth-' + h.m.toLowerCase();
      m.textContent = h.m;
      var p = document.createElement('span');
      p.className = 'hi-path';
      p.textContent = h.p;
      var t = document.createElement('span');
      t.style.marginLeft = 'auto';
      t.style.fontSize = '11.5px';
      t.textContent = h.t || '';
      it.appendChild(m); it.appendChild(p); it.appendChild(t);
      it.addEventListener('click', function () {
        fill(h.m, h.p, h.b || '');
        send();
      });
      box.appendChild(it);
    });
  }

  function renderPresets() {
    var box = $('#preset-box');
    if (!box) return;
    PRESETS.forEach(function (g) {
      var grp = document.createElement('div');
      grp.className = 'preset-group';
      var h = document.createElement('h3');
      h.textContent = g.group;
      grp.appendChild(h);
      g.items.forEach(function (it) {
        var b = document.createElement('button');
        b.className = 'preset-item';
        var m = document.createElement('span');
        m.className = 'pi-method mth mth-' + it.method.toLowerCase();
        m.textContent = it.method;
        b.appendChild(m);
        b.appendChild(document.createTextNode(it.label));
        b.addEventListener('click', function () {
          fill(it.method, it.path, it.body || '');
          send();
        });
        grp.appendChild(b);
      });
      box.appendChild(grp);
    });
  }

  function fill(method, path, body) {
    var $m = $('#req-method'), $p = $('#req-path'), $b = $('#req-body');
    if (!$m) return;
    $m.value = method;
    $p.value = path;
    $b.value = body || '';
    syncBodyVis();
  }

  function syncBodyVis() {
    var m = $('#req-method').value;
    var wrap = $('#req-body-wrap');
    wrap.style.display = (m === 'GET' || m === 'HEAD') ? 'none' : '';
  }

  function currentRequest() {
    return {
      m: $('#req-method').value,
      p: $('#req-path').value.trim() || '/',
      /* 不 trim body:Bulk NDJSON 的末尾换行是协议的一部分,删掉会变成请求级 400 */
      b: $('#req-body').value || ''
    };
  }

  function bodyLooksStructured(raw) {
    try { JSON.parse(raw); return true; } catch (e) {}
    var lines = raw.split('\n').filter(function (l) { return l.trim() !== ''; });
    if (!lines.length) return false;
    for (var i = 0; i < lines.length; i++) {
      try { JSON.parse(lines[i]); } catch (e) { return false; }
    }
    return true;
  }

  function showSendAnyway(reason) {
    var head = $('#resp-head');
    var out = $('#resp-viewer');
    head.innerHTML = '<span class="resp-status err">JSON 可能无效</span>';
    out.innerHTML = '';
    var note = document.createElement('div');
    note.className = 'term';
    var pre = document.createElement('pre');
    pre.textContent = reason + '\n\n这只是浏览器侧提示。点「仍然发送原文」会把文本框里的内容原样交给 ES,由它决定状态码。';
    note.appendChild(pre);
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn';
    btn.textContent = '仍然发送原文';
    btn.addEventListener('click', function () { send(true); });
    out.appendChild(note);
    out.appendChild(btn);
  }

  async function send(force) {
    var req = currentRequest();
    var out = $('#resp-viewer');
    var head = $('#resp-head');
    head.innerHTML = '<span class="exp-status">运行中…</span>';
    out.innerHTML = '';
    if (!force && req.b && req.m !== 'GET' && req.m !== 'HEAD' && !bodyLooksStructured(req.b)) {
      showSendAnyway('请求体既不是合法 JSON,也不是逐行 JSON 的 NDJSON。破坏实验(坏 source 行)需要原样送出才能看到条级失败。');
      return;
    }
    var epEl = $('#endpoint-input');
    var auEl = $('#auth-input');
    var opts = {};
    if (epEl && epEl.value.trim()) opts.endpoint = epEl.value.trim().replace(/\/+$/, '');
    opts.auth = auEl ? auEl.value.trim() : '';
    try {
      var r = await EC.raw(req.m, req.p, req.b === '' ? null : req.b, opts);
      var time = new Date();
      var pad = function (n) { return n < 10 ? '0' + n : '' + n; };
      pushHistory({ m: req.m, p: req.p, b: req.b, t: pad(time.getHours()) + ':' + pad(time.getMinutes()) });
      var st = document.createElement('span');
      st.className = 'resp-status ' + (r.ok ? 'ok' : 'err');
      st.textContent = 'HTTP ' + r.status;
      var meta = document.createElement('span');
      meta.textContent = r.ms + ' ms · ' + (r.contentType || 'text').split(';')[0];
      head.innerHTML = '';
      head.appendChild(st);
      head.appendChild(meta);
      var term = document.createElement('div');
      term.className = 'term';
      var pre = document.createElement('pre');
      pre.innerHTML = r.data != null ? EC.prettyJSON(r.data) : esc(r.text || '(空响应)');
      term.appendChild(pre);
      out.appendChild(term);
      EC.refreshBadges();
    } catch (err) {
      var st2 = document.createElement('span');
      st2.className = 'resp-status err';
      st2.textContent = '连接失败';
      head.innerHTML = '';
      head.appendChild(st2);
      var t2 = document.createElement('div');
      t2.className = 'term';
      var p2 = document.createElement('pre');
      p2.textContent = err.message;
      t2.appendChild(p2);
      out.appendChild(t2);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    renderPresets();
    renderHistory();

    var ep = $('#endpoint-input');
    if (ep) {
      ep.value = EC.endpoint();
      ep.addEventListener('change', function () { EC.setEndpoint(ep.value); });
    }
    var au = $('#auth-input');
    if (au) {
      au.value = '';
      au.addEventListener('change', function () { EC.setAuth(au.value); });
    }
    var clearAuth = $('#auth-clear');
    if (clearAuth && au) {
      clearAuth.addEventListener('click', function () {
        au.value = '';
        EC.setAuth('');
      });
    }
    $('#req-method').addEventListener('change', syncBodyVis);
    $('#send-btn').addEventListener('click', function () { send(false); });
    ['#req-path', '#req-body'].forEach(function (sel) {
      $(sel).addEventListener('keydown', function (e) {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); send(); }
      });
    });
    syncBodyVis();

    /* 深链:console.html?ep=&am=anon|elastic|wrong|alice&raw=1#run=METHOD|PATH|BODY
       am 是实验别名,口令不进 URL;raw=1 表示破坏实验,跳过浏览器侧 JSON 门直接发给 ES。
       端点与凭据只填进本页输入框,不写 localStorage。 */
    var qs = new URLSearchParams(location.search || '');
    var deepEp = qs.get('ep');
    var deepAm = qs.get('am');
    var deepRaw = qs.get('raw') === '1';
    if (deepEp && ep) ep.value = deepEp;
    if (deepAm && au) {
      var cred = EC.credForMode(deepAm);
      if (cred != null) {
        au.value = cred;
        EC.setAuth(cred);
      }
    }
    var m = /^#run=(.+)$/.exec(location.hash || '');
    if (m) {
      try {
        var parts = decodeURIComponent(m[1]).split('|');
        fill(parts[0] || 'GET', parts[1] || '/', parts[2] || '');
        send(deepRaw);
      } catch (e) { /* 忽略坏链 */ }
    }
  });
})();
