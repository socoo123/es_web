/* experiments.js — 章内「动手实验」运行器(零依赖)
 *
 * 数据注册:
 *   window.ESEXPERIMENTS['ch08-01-thread-pool'] = {
 *     version: 1, id: 'ch08-01-thread-pool', title: '看看 write 池的真实队列',
 *     method: 'GET', path: '/_cat/thread_pool?v&h=name,size,queue,rejected',
 *     body: null,                       // POST/PUT 可给对象或字符串
 *     predict: '先猜:8 核机器上 search 池多大?队列多长?',   // 预测→操作→对照
 *     expect: 'size=((8*3)/2)+1=13,queue=size*1000=13000'   // 操作后对照
 *   };
 * 页面插槽:<div class="exp-slot" data-exp="ch08-01-thread-pool"></div>
 */
(function () {
  'use strict';
  var EC = window.ESClient;
  function esc(s) { return EC ? EC.esc(String(s)) : String(s); }

  function build(slot) {
    var id = slot.getAttribute('data-exp');
    var spec = (window.ESEXPERIMENTS || {})[id];
    if (!spec) {
      slot.innerHTML = '<div class="exp"><div class="fp-error">未找到实验 ' + esc(id) +
        '(检查 experiments/chNN.js 注册)</div></div>';
      return;
    }
    var box = document.createElement('div');
    box.className = 'exp';

    var head = document.createElement('div');
    head.className = 'exp-head';
    var title = document.createElement('div');
    title.className = 'exp-title';
    title.textContent = spec.title || id;
    var mth = document.createElement('span');
    mth.className = 'mth mth-' + String(spec.method || 'get').toLowerCase();
    mth.textContent = spec.method || 'GET';
    var pathEl = document.createElement('code');
    pathEl.textContent = spec.path;
    head.appendChild(title);
    head.appendChild(mth);
    head.appendChild(pathEl);
    if (spec.endpoint) {
      // 指定目标端点的实验(如第 29 课的 9201 安全节点):标注出来,避免与全局端点混淆
      var epEl = document.createElement('span');
      epEl.className = 'exp-endpoint';
      epEl.textContent = '@ ' + spec.endpoint.replace(/^https?:\/\//, '');
      epEl.title = '本实验固定发往该端点(ch29 安全节点):先 bash docker/start-secure.sh';
      head.appendChild(epEl);
    }

    var body = document.createElement('div');
    body.className = 'exp-body';

    if (spec.predict) {
      var pre = document.createElement('div');
      pre.className = 'exp-predict';
      pre.textContent = spec.predict;
      body.appendChild(pre);
    }

    if (spec.body != null) {
      var req = document.createElement('div');
      req.className = 'exp-req term';
      var reqPre = document.createElement('pre');
      reqPre.innerHTML = EC ? EC.prettyJSON(spec.body) : esc(JSON.stringify(spec.body, null, 2));
      req.appendChild(reqPre);
      body.appendChild(req);
    }

    var actions = document.createElement('div');
    actions.className = 'exp-actions';
    var runBtn = document.createElement('button');
    runBtn.className = 'btn primary';
    runBtn.textContent = '▶ 在本地 ES 上运行';
    var status = document.createElement('span');
    status.className = 'exp-status';
    status.textContent = '';
    actions.appendChild(runBtn);
    actions.appendChild(status);

    var result = document.createElement('div');
    result.className = 'exp-result';
    result.style.display = 'none';

    var consoleA = document.createElement('a');
    consoleA.className = 'btn code';
    consoleA.textContent = '在控制台中打开';
    var linkOpts = {};
    if (spec.endpoint) linkOpts.endpoint = spec.endpoint;
    if ('auth' in spec && EC) linkOpts.authMode = EC.authModeFor(spec.auth);
    if (spec.allowInvalidBody) linkOpts.allowInvalid = true;
    consoleA.href = EC ? EC.consoleLink(spec.method, spec.path,
      spec.body == null ? '' : (typeof spec.body === 'string' ? spec.body : JSON.stringify(spec.body, null, 2)),
      linkOpts) : '#';
    if ('auth' in spec && !linkOpts.authMode) {
      consoleA.title = '这条实验的凭据没有内置别名,打开控制台后请自行填写,链接里不会带密码';
    }
    actions.appendChild(consoleA);

    body.appendChild(actions);
    body.appendChild(result);

    if (spec.expect) {
      var exp = document.createElement('div');
      exp.className = 'exp-expect';
      exp.textContent = spec.expect;
      body.appendChild(exp);
    }

    runBtn.addEventListener('click', async function () {
      runBtn.disabled = true;
      status.textContent = '运行中…';
      result.style.display = 'none';
      try {
        var opts = { endpoint: spec.endpoint };   // 未指定则用全局端点
        if ('auth' in spec) opts.auth = spec.auth; // 实验自带凭据(ch29);未指定则回落全局凭据
        if (spec.headers) opts.headers = spec.headers;  // 实验自定义头(第 29 课 ApiKey)
        var r = await EC.raw(spec.method, spec.path, spec.body, opts);
        var head2 = document.createElement('div');
        head2.className = 'resp-head';
        var st = document.createElement('span');
        st.className = 'resp-status ' + (r.ok ? 'ok' : 'err');
        st.textContent = 'HTTP ' + r.status;
        var meta = document.createElement('span');
        meta.textContent = r.ms + ' ms · ' + (r.contentType || 'text');
        head2.appendChild(st);
        head2.appendChild(meta);
        var term = document.createElement('div');
        term.className = 'term';
        var pre2 = document.createElement('pre');
        pre2.innerHTML = r.data != null ? EC.prettyJSON(r.data) : esc(r.text || '(空响应)');
        term.appendChild(pre2);
        result.innerHTML = '';
        result.appendChild(head2);
        result.appendChild(term);
        result.style.display = '';
        status.textContent = r.ok ? '' : 'ES 返回错误(看响应里的 reason)';
      } catch (err) {
        var t2 = document.createElement('div');
        t2.className = 'term';
        var p2 = document.createElement('pre');
        p2.textContent = err.message;
        t2.appendChild(p2);
        result.innerHTML = '';
        result.appendChild(t2);
        result.style.display = '';
        status.textContent = '连接失败';
      } finally {
        runBtn.disabled = false;
      }
    });

    box.appendChild(head);
    box.appendChild(body);
    slot.appendChild(box);
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.exp-slot').forEach(build);
  });
})();
