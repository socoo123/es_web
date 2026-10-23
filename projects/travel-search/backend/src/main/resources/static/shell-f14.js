(function () {
  'use strict';
  var form = document.getElementById('search-form');
  var status = document.getElementById('status');
  var fields = Array.from(form.elements);
  var themeButton = document.getElementById('theme');
  function theme(value) {
    document.documentElement.dataset.theme = value;
    themeButton.textContent = value === 'dark' ? '切换浅色' : '切换深色';
    try { localStorage.setItem('travel-f14:theme', value); } catch (_) {}
  }
  var saved; try { saved = localStorage.getItem('travel-f14:theme'); } catch (_) {}
  theme(saved === 'dark' ? 'dark' : 'light');
  themeButton.addEventListener('click', function () {
    theme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
  });
  function show(id, value) { document.getElementById(id).textContent = JSON.stringify(value, null, 2); }
  function clear() {
    document.getElementById('cards').replaceChildren();
    ['query-tokens', 'sample-tokens'].forEach(function (id) { document.getElementById(id).textContent = '尚无 token'; });
    ['input-json', 'query-request-json', 'sample-request-json', 'dsl-json', 'result-json'].forEach(function (id) {
      document.getElementById(id).textContent = '尚无本轮结果';
    });
    document.getElementById('total').textContent = '等待搜索';
    document.getElementById('analysis-note').textContent = '等待提交；左边分析查询，右边分析页面固定样本。';
  }
  function element(tag, value, cls) {
    var node = document.createElement(tag); node.textContent = value; if (cls) node.className = cls; return node;
  }
  function tokens(id, values) {
    var box = document.getElementById(id); box.replaceChildren();
    if (!values.length) { box.textContent = '分析成功，0 个 token'; return; }
    values.forEach(function (value) {
      var token = element('div', '', 'token');
      token.append(element('strong', value.token), element('small', 'position ' + value.position),
        element('small', 'offset [' + value.startOffset + ', ' + value.endOffset + ')'));
      box.append(token);
    });
  }
  form.addEventListener('input', function () {
    clear(); status.className = ''; status.textContent = '条件已改变，请重新提交观察。';
  });
  form.addEventListener('submit', async function (event) {
    event.preventDefault(); clear(); status.className = ''; status.textContent = '正在调用本机 Java 与 ES…';
    var budget = form.elements.budget.value.split('.');
    var input = {q: form.elements.q.value, cityCode: form.elements.cityCode.value,
      maxPriceFen: Number(budget[0]) * 100 + Number(((budget[1] || '') + '00').slice(0, 2)), candidate: form.elements.candidate.value};
    fields.forEach(function (field) { field.disabled = true; });
    try {
      var response = await fetch('/api/attractions/analyzer-search', {method: 'POST',
        headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input)});
      var result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      tokens('query-tokens', result.queryTokens); tokens('sample-tokens', result.sampleTokens);
      document.getElementById('analysis-note').textContent = '字段 ' + result.field + ' · analyzer ' + result.analyzer + ' · 写入样本：' + result.sampleText;
      document.getElementById('total').textContent = result.total + ' 份 · ' + result.relation;
      result.items.forEach(function (item) {
        var card = element('article', '', 'card'); card.dataset.id = item.id;
        card.append(element('p', item.cityCode + ' · CNY / open', 'tag'), element('h3', item.name),
          element('p', item.id, 'id'), element('p', (item.ticketPriceFen / 100).toFixed(2) + ' 元', 'price'));
        document.getElementById('cards').append(card);
      });
      show('input-json', result.conditions); show('query-request-json', result.queryAnalysisRequest);
      show('sample-request-json', result.sampleAnalysisRequest); show('dsl-json', result.esRequest); show('result-json', result);
      status.textContent = result.total ? '请求完成。逐份核对：含有这些词项，是否就符合游客意图？' : '请求完成，0 份命中。核对 token 与硬条件；这不是连接错误。';
    } catch (error) {
      clear(); status.className = 'error'; status.textContent = '观察失败：' + error.message;
    } finally { fields.forEach(function (field) { field.disabled = false; }); }
  });
})();
