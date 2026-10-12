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
      { label: 'search 线程池', method: 'GET', path: '/_cat/thread_pool/search?v&h=name,size,queue,rejected,completed' }
    ] },
    { group: '建索引 & 写文档', hint: '依次建索引、写文档。study 已存在时可直接写入。', items: [
      { label: '建 study 索引', method: 'PUT', path: '/study', body: '{\n  "settings": { "number_of_shards": 1, "number_of_replicas": 0 }\n}' },
      { label: '写一条文档', method: 'PUT', path: '/study/_doc/1?refresh=true', body: '{\n  "title": "Elasticsearch 源码精读",\n  "lesson": 14,\n  "tags": ["lucene", "segment", "translog"]\n}' },
      { label: '再看 mapping', method: 'GET', path: '/study/_mapping' }
    ] },
    { group: '分析与搜索', hint: '分词可独立执行；搜索需要先写入上方的 study 文档。', items: [
      { label: '标准分词器', method: 'POST', path: '/_analyze', body: '{\n  "analyzer": "standard",\n  "text": "Tracking a GET request through Elasticsearch internals"\n}' },
      { label: 'match 搜索', method: 'POST', path: '/study/_search', body: '{\n  "query": { "match": { "title": "源码" } }\n}' },
      { label: '带 explain 的打分', method: 'POST', path: '/study/_search', body: '{\n  "query": { "match": { "title": "Elasticsearch" } },\n  "explain": true\n}' }
    ] },
    { group: '清理', hint: '删除 study 索引及其中全部文档。', items: [
      { label: '删除 study 索引', method: 'DELETE', path: '/study' }
    ] }
  ];

  var METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'PATCH', 'OPTIONS'];
  var response = null;
  var responseView = 'formatted';
  var pending = null;
  var requestRevision = 0;
  var feedbackTimer;
  var history = [];

  function $(sel) { return document.querySelector(sel); }
  function feedback(message) {
    $('#console-feedback').textContent = message;
    clearTimeout(feedbackTimer);
    feedbackTimer = setTimeout(function () { $('#console-feedback').textContent = ''; }, 5000);
  }
  function notice(message, rawAllowed) {
    var box = $('#request-notice');
    box.textContent = message || '';
    box.hidden = !message;
    $('#send-raw').hidden = !rawAllowed;
  }
  function connection() {
    return { endpoint: EC.normalizeEndpoint($('#endpoint-input').value), auth: $('#auth-input').value };
  }

  function loadHistory() {
    try {
      var stored = JSON.parse(localStorage.getItem(HISTORY_KEY));
      if (!Array.isArray(stored)) return [];
      return stored.filter(function (h) {
        return h && METHODS.indexOf(h.m) !== -1 && typeof h.p === 'string' &&
          (h.b == null || typeof h.b === 'string');
      }).slice(0, HISTORY_MAX);
    } catch (e) { return []; }
  }
  function saveHistory() {
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(history)); }
    catch (e) { feedback('浏览器存储不可用，历史暂存于本页。'); }
  }
  function pushHistory(req, result, ep) {
    history = history.filter(function (h) {
      return !(h.m === req.m && h.p === req.p && h.b === req.b && h.ep === ep && h.f === req.f);
    });
    history.unshift({ m: req.m, p: req.p, b: req.b, ep: ep, f: req.f,
      status: result.status, t: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }) });
    history = history.slice(0, HISTORY_MAX);
    saveHistory();
    renderHistory();
  }
  function renderHistory() {
    var box = $('#hist-list');
    box.replaceChildren();
    $('#history-count').textContent = history.length;
    $('#history-clear').disabled = !history.length;
    if (!history.length) {
      var empty = document.createElement('p');
      empty.className = 'history-empty';
      empty.textContent = '还没有请求记录。完成的请求会自动保存在这里。';
      box.appendChild(empty);
    }
    history.forEach(function (h) {
      var item = document.createElement('button');
      item.type = 'button';
      item.className = 'hist-item';
      item.title = h.m + ' ' + h.p + (h.ep ? '\n' + h.ep : '') + (h.status ? '\nHTTP ' + h.status : '');
      var method = document.createElement('span');
      method.className = 'mth mth-' + h.m.toLowerCase();
      method.textContent = h.m;
      var path = document.createElement('span');
      path.className = 'hi-path';
      path.textContent = h.p;
      var time = document.createElement('span');
      time.textContent = typeof h.t === 'string' ? h.t : '';
      item.append(method, path, time);
      item.addEventListener('click', function () {
        fill(h.m, h.p, h.b || '', '历史请求', h.f);
        if (h.ep) {
          try { $('#endpoint-input').value = EC.normalizeEndpoint(h.ep); } catch (e) {}
          EC.refreshBadges();
        }
        feedback('已载入历史请求，可编辑后发送。');
      });
      box.appendChild(item);
    });
  }
  function renderPresets() {
    var box = $('#preset-box');
    PRESETS.forEach(function (group) {
      var section = document.createElement('div');
      section.className = 'preset-group';
      var heading = document.createElement('h3');
      heading.textContent = group.group;
      section.appendChild(heading);
      if (group.hint) {
        var hint = document.createElement('p');
        hint.className = 'preset-hint';
        hint.textContent = group.hint;
        section.appendChild(hint);
      }
      group.items.forEach(function (item) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'preset-item';
        button.title = item.method + ' ' + item.path;
        var method = document.createElement('span');
        method.className = 'pi-method mth mth-' + item.method.toLowerCase();
        method.textContent = item.method;
        button.append(method, document.createTextNode(item.label));
        button.addEventListener('click', function () {
          fill(item.method, item.path, item.body || '', item.label);
          button.classList.add('active');
          feedback('已载入「' + item.label + '」，可编辑后发送。');
        });
        section.appendChild(button);
      });
      box.appendChild(section);
    });
  }
  function fill(method, path, body, source, format) {
    $('#req-method').value = method;
    $('#req-path').value = path;
    $('#req-body').value = body;
    $('#body-format').value = ['json', 'ndjson'].indexOf(format) !== -1 ? format : 'auto';
    $('#request-source').textContent = source || '自由编辑';
    document.querySelectorAll('.preset-item.active').forEach(function (button) { button.classList.remove('active'); });
    notice('');
    syncBody();
  }
  function supportsBody() { return ['GET', 'HEAD'].indexOf($('#req-method').value) === -1; }
  function isStreaming(path) { return /\/(?:_bulk|_msearch)(?:\/|\?|$)/.test(path); }
  function currentRequest() {
    var path = $('#req-path').value.trim() || '/';
    if (/^[a-z][a-z\d+.-]*:\/\//i.test(path) || path.indexOf('//') === 0 || path.indexOf('#') !== -1) {
      throw new Error('请在路径栏填写 / 开头的 API 路径，服务地址填写在上方；路径不要带 #。');
    }
    if (path.charAt(0) !== '/') path = '/' + path;
    return { m: $('#req-method').value, p: path,
      /* 原文和末尾换行完整保留，GET / HEAD 明确不发送草稿。 */
      b: supportsBody() ? $('#req-body').value : '', f: $('#body-format').value };
  }
  function bodyType(req) {
    if (req.f === 'json') return 'application/json';
    if (req.f === 'ndjson' || isStreaming(req.p)) return 'application/x-ndjson';
    try { JSON.parse(req.b); return 'application/json'; } catch (e) {}
    var lines = req.b.split('\n').filter(function (line) { return line.trim(); });
    return lines.length > 1 && lines.every(function (line) {
      try { JSON.parse(line); return true; } catch (e) { return false; }
    }) ? 'application/x-ndjson' : 'application/json';
  }
  function syncBody() {
    var enabled = supportsBody();
    $('#req-body').disabled = !enabled;
    $('#format-btn').disabled = !enabled;
    $('#body-clear').disabled = !enabled;
    $('#body-format').disabled = !enabled;
    $('#req-body').placeholder = enabled ? '输入 JSON 或 NDJSON 请求体…' : '此方法不发送请求体；切换到 POST 可编辑 JSON。';
    $('#body-hint').textContent = !enabled ? 'GET / HEAD 不发送请求体；已有草稿保留，搜索 JSON 可使用 POST。' :
      (isStreaming($('#req-path').value) || $('#body-format').value === 'ndjson' ?
        'NDJSON 逐行发送，末尾换行会原样保留；格式化不会补齐缺失的换行。' : 'JSON / NDJSON 原样发送；空请求体不添加 Content-Type。');
  }
  function validateBody(req, type) {
    if (!req.b) return '';
    if (type === 'application/x-ndjson') {
      var lines = req.b.split('\n');
      for (var i = 0; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        try { JSON.parse(lines[i]); } catch (e) { return 'NDJSON 第 ' + (i + 1) + ' 行不是合法 JSON：' + e.message; }
      }
      if (!req.b.endsWith('\n')) return 'NDJSON 缺少末尾换行。可在编辑器末尾按 Enter，或原样发送以观察 ES 的错误。';
      return '';
    }
    try { JSON.parse(req.b); return ''; } catch (e) { return 'JSON 解析失败：' + e.message; }
  }
  function formatBody() {
    try {
      var req = currentRequest();
      if (!req.b) { feedback('请求体为空。'); return; }
      if (bodyType(req) === 'application/x-ndjson') {
        $('#req-body').value = req.b.split('\n').map(function (line) {
          return line.trim() ? JSON.stringify(JSON.parse(line)) : line;
        }).join('\n');
      } else $('#req-body').value = JSON.stringify(JSON.parse(req.b), null, 2);
      notice('');
      feedback('请求体已格式化。');
    } catch (err) { notice('无法格式化：' + err.message, true); }
  }
  function busy(value) {
    $('#send-btn').disabled = value;
    $('#send-btn').textContent = value ? '发送中…' : '发送请求 ↗';
    $('#cancel-btn').hidden = !value;
    $('#send-raw').disabled = value;
    $('#response-panel').setAttribute('aria-busy', String(value));
  }
  function responseStatus(label, state, meta) {
    var head = $('#resp-head');
    head.replaceChildren();
    var status = document.createElement('span');
    status.className = 'resp-status ' + (state || '');
    status.textContent = label;
    head.appendChild(status);
    if (meta) {
      var text = document.createElement('span');
      text.textContent = meta;
      head.appendChild(text);
    }
  }
  function emptyResponse(title, message) {
    var box = document.createElement('div');
    box.className = 'response-empty';
    var heading = document.createElement('strong');
    heading.textContent = title;
    var detail = document.createElement('p');
    detail.textContent = message;
    box.append(heading, detail);
    $('#resp-viewer').replaceChildren(box);
  }
  function headerText() {
    return Object.keys(response.headers || {}).map(function (name) { return name + ': ' + response.headers[name]; }).join('\n');
  }
  function responseText() {
    if (!response) return '';
    if (responseView === 'headers') return headerText();
    if (responseView === 'formatted' && response.data != null) return JSON.stringify(response.data, null, 2);
    return response.text || '';
  }
  function renderResponse() {
    if (!response) return;
    var viewer = $('#resp-viewer');
    viewer.replaceChildren();
    var error = response.data && response.data.error;
    if (!error && response.data && response.data.errors === true) {
      var failed = (response.data.items || []).filter(function (item) {
        var action = item[Object.keys(item)[0]];
        return action && action.error;
      });
      error = '部分操作失败' + (failed.length ? '（' + failed.length + ' 项）' : '') + '。HTTP 200 表示批量请求有响应，请检查 items 中每项的 status 和 error。';
    }
    if (error && responseView !== 'headers') {
      var summary = document.createElement('p');
      summary.className = 'response-error';
      summary.textContent = typeof error === 'string' ? error :
        (error.type ? error.type + ' · ' : '') + (error.reason || '查看下方完整错误响应。');
      viewer.appendChild(summary);
    }
    var text = responseText();
    if (!text) {
      emptyResponse(responseView === 'headers' ? '没有可读取的响应头' : '请求已完成 · 响应体为空',
        responseView === 'headers' ? '这里只显示浏览器允许读取的响应头；跨域响应受 CORS expose-headers 限制。' :
        'HEAD 只返回状态和响应头。其他 API 也可能正常返回空响应。');
      return;
    }
    var term = document.createElement('div');
    term.className = 'term';
    var pre = document.createElement('pre');
    if (responseView === 'formatted' && response.data != null) pre.innerHTML = EC.prettyJSON(text);
    else pre.textContent = text;
    term.appendChild(pre);
    viewer.appendChild(term);
  }
  async function send(force) {
    if (pending) return;
    var req, opts, type;
    try {
      req = currentRequest();
      opts = connection();
      type = bodyType(req);
    } catch (err) { notice(err.message); return; }
    var invalid = validateBody(req, type);
    if (invalid && !force) { notice(invalid + ' 可点击「仍然发送原文」进行破坏实验。', true); return; }
    notice('');
    var revision = ++requestRevision;
    var controller = new AbortController();
    pending = controller;
    opts.signal = controller.signal;
    opts.timeoutMs = Number($('#request-timeout').value);
    opts.contentType = type;
    $('#req-path').value = req.p;
    response = null;
    $('#copy-response').disabled = true;
    busy(true);
    responseStatus('请求中', '', req.m + ' ' + req.p);
    emptyResponse('正在等待 ES 响应', '可点击「停止请求」或按 Esc 取消等待。');
    try {
      var result = await EC.raw(req.m, req.p, req.b === '' ? null : req.b, opts);
      if (revision !== requestRevision) return;
      response = result;
      pushHistory(req, result, opts.endpoint);
      var bytes = new TextEncoder().encode(result.text || '').length;
      var partial = result.data && result.data.errors === true;
      responseStatus('HTTP ' + result.status + (partial ? ' · 部分失败' : ''), result.ok && !partial ? 'ok' : 'err',
        result.ms + ' ms · ' + (bytes < 1024 ? bytes + ' B' : (bytes / 1024).toFixed(1) + ' KB') + ' · ' + (result.contentType || '无 Content-Type').split(';')[0]);
      $('#copy-response').disabled = false;
      renderResponse();
    } catch (err) {
      if (revision !== requestRevision) return;
      responseStatus(err.code === 'aborted' ? '已停止' : (err.code === 'timeout' ? '请求超时' : '请求失败'), 'err');
      emptyResponse(err.code === 'aborted' ? '请求已停止' : '未收到 HTTP 响应', err.message);
    } finally {
      if (revision === requestRevision) { pending = null; busy(false); }
    }
  }
  function cancel() {
    if (!pending) return;
    pending.abort();
    pending = null;
    requestRevision++;
    busy(false);
    responseStatus('已停止', '');
    emptyResponse('请求已停止', '已取消浏览器等待；ES 可能已经接收并执行了请求。');
  }
  function chooseTab(button, attr) {
    var buttons = Array.from(button.parentElement.querySelectorAll('[role="tab"]'));
    buttons.forEach(function (tab) {
      tab.setAttribute('aria-selected', String(tab === button));
      tab.tabIndex = tab === button ? 0 : -1;
    });
    if (attr === 'data-side') {
      $('#preset-panel').hidden = button.getAttribute(attr) !== 'preset';
      $('#history-panel').hidden = button.getAttribute(attr) !== 'history';
    } else {
      responseView = button.getAttribute(attr);
      $('#resp-viewer').setAttribute('aria-labelledby', button.id);
      renderResponse();
    }
  }
  function wireTabs(selector, attr) {
    document.querySelectorAll(selector).forEach(function (button) {
      button.addEventListener('click', function () { chooseTab(button, attr); });
      button.addEventListener('keydown', function (event) {
        if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].indexOf(event.key) === -1) return;
        event.preventDefault();
        var buttons = Array.from(button.parentElement.querySelectorAll('[role="tab"]'));
        var index = buttons.indexOf(button);
        index = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 :
          (index + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
        chooseTab(buttons[index], attr);
        buttons[index].focus();
      });
    });
  }
  function deepLink() {
    if (!/^#run=/.test(location.hash)) return;
    try {
      /* 每段独立解码，body 内的 | 不参与分隔。兼容旧链接的原始分隔符。 */
      var parts = location.hash.slice(5).split('|');
      if (parts.length < 2 || parts.length > 3) throw new Error('链接的请求段数量不正确。');
      var method = decodeURIComponent(parts[0]).toUpperCase();
      if (METHODS.indexOf(method) === -1) throw new Error('链接中的 HTTP 方法不受支持。');
      var path = decodeURIComponent(parts[1]) || '/';
      var body = decodeURIComponent(parts[2] || '');
      var qs = new URLSearchParams(location.search || '');
      var ep = qs.get('ep');
      var mode = qs.get('am');
      if (ep) $('#endpoint-input').value = EC.normalizeEndpoint(ep);
      if (mode) {
        var cred = EC.credForMode(mode);
        if (cred == null) throw new Error('链接中的认证别名不受支持。');
        $('#auth-input').value = cred;
        EC.setAuth(cred);
      }
      cancel();
      fill(method, path, body, '来自课程的请求');
      EC.refreshBadges();
      send(qs.get('raw') === '1');
    } catch (err) { notice('无法读取课程链接：' + err.message); }
  }

  document.addEventListener('DOMContentLoaded', function () {
    history = loadHistory();
    renderPresets();
    renderHistory();
    $('#endpoint-input').value = EC.endpoint();
    EC.setConnectionProvider(connection);
    $('#connection-form').addEventListener('submit', function (event) { event.preventDefault(); });
    $('#endpoint-input').addEventListener('change', function () {
      try { $('#endpoint-input').value = EC.setEndpoint($('#endpoint-input').value); notice(''); }
      catch (err) { notice(err.message); }
    });
    $('#auth-input').addEventListener('change', function () { EC.setAuth($('#auth-input').value); EC.refreshBadges(); });
    $('#auth-clear').addEventListener('click', function () { $('#auth-input').value = ''; EC.setAuth(''); EC.refreshBadges(); feedback('认证凭据已清除。'); });
    $('#test-connection').addEventListener('click', async function () {
      var button = $('#test-connection');
      button.disabled = true;
      button.textContent = '检测中…';
      try { var result = await EC.refreshBadges(); feedback(result.ok ? '连接成功 · ES ' + result.version : result.error); }
      finally { button.disabled = false; button.textContent = '检测连接'; }
    });
    $('#history-clear').addEventListener('click', function () { history = []; saveHistory(); renderHistory(); feedback('历史记录已清空。'); });
    $('#request-form').addEventListener('submit', function (event) { event.preventDefault(); send(false); });
    $('#cancel-btn').addEventListener('click', cancel);
    $('#send-raw').addEventListener('click', function () { send(true); });
    $('#format-btn').addEventListener('click', formatBody);
    $('#body-clear').addEventListener('click', function () { $('#req-body').value = ''; notice(''); });
    ['#req-method', '#body-format'].forEach(function (selector) { $(selector).addEventListener('change', function () { notice(''); syncBody(); }); });
    $('#req-path').addEventListener('input', syncBody);
    ['#req-path', '#req-body'].forEach(function (selector) {
      $(selector).addEventListener('input', function () { notice(''); $('#request-source').textContent = '自由编辑'; });
    });
    $('#req-body').addEventListener('keydown', function (event) {
      if (event.key !== 'Tab' || event.shiftKey || event.ctrlKey || event.metaKey || event.altKey) return;
      event.preventDefault();
      this.setRangeText('  ', this.selectionStart, this.selectionEnd, 'end');
      this.dispatchEvent(new Event('input', { bubbles: true }));
    });
    document.addEventListener('keydown', function (event) {
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); send(false); }
      if (event.key === 'Escape') cancel();
    });
    wireTabs('[data-side]', 'data-side');
    wireTabs('[data-view]', 'data-view');
    $('#copy-response').addEventListener('click', async function () {
      var text = responseText();
      try {
        await navigator.clipboard.writeText(text);
        feedback('已复制当前响应视图。');
      } catch (err) {
        var range = document.createRange();
        range.selectNodeContents($('#resp-viewer'));
        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        feedback('浏览器未允许自动复制，已选中响应，请按 ⌘ / Ctrl+C。');
      }
    });
    syncBody();
    deepLink();
    window.addEventListener('hashchange', deepLink);
  });
})();
