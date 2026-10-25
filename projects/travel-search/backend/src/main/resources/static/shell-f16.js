(function () {
  'use strict';
  var form = document.getElementById('search-form');
  var status = document.getElementById('status');
  var fields = Array.from(form.elements);
  var themeButton = document.getElementById('theme');
  function theme(value) {
    document.documentElement.dataset.theme = value;
    themeButton.textContent = value === 'dark' ? '切换浅色' : '切换深色';
    try { localStorage.setItem('travel-f16:theme', value); } catch (_) {}
  }
  var saved; try { saved = localStorage.getItem('travel-f16:theme'); } catch (_) {}
  theme(saved === 'dark' ? 'dark' : 'light');
  themeButton.addEventListener('click', function () {
    theme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
  });
  function show(id, value) { document.getElementById(id).textContent = JSON.stringify(value, null, 2); }
  function clear() {
    document.getElementById('cards').replaceChildren();
    ['query-tokens', 'base-tokens'].forEach(function (id) { document.getElementById(id).textContent = '尚无 token'; });
    ['input-json', 'base-request-json', 'query-request-json', 'base-analysis-json', 'query-analysis-json', 'dsl-json', 'result-json'].forEach(function (id) {
      document.getElementById(id).textContent = '尚无本轮结果';
    });
    document.getElementById('total').textContent = '等待搜索';
    document.getElementById('analysis-note').textContent = '两侧都分析本次输入，不读取历史词项。';
  }
  function element(tag, value, cls) {
    var node = document.createElement(tag); node.textContent = value; if (cls) node.className = cls; return node;
  }
  function tokens(id, values) {
    var box = document.getElementById(id); box.replaceChildren();
    if (!values.length) { box.textContent = '分析成功，0 个 token'; return; }
    values.forEach(function (value) {
      var token = element('div', '', 'token');
      token.append(element('strong', value.token), element('small', 'position ' + value.position + ' · length ' + value.positionLength),
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
      maxPriceFen: Number(budget[0]) * 100 + Number(((budget[1] || '') + '00').slice(0, 2)), mode: form.elements.mode.value};
    fields.forEach(function (field) { field.disabled = true; });
    try {
      var response = await fetch('/api/attractions/synonym-search', {method: 'POST',
        headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input)});
      var result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      tokens('query-tokens', result.queryTokens); tokens('base-tokens', result.baseTokens);
      document.getElementById('analysis-note').textContent = '当前查询链：' + result.analyzer + ' · 两侧都分析本次输入，不读取历史词项';
      document.getElementById('total').textContent = result.total + ' 份 · ' + result.relation;
      result.items.forEach(function (item) {
        var card = element('article', '', 'card'); card.dataset.id = item.id;
        card.append(element('p', item.cityCode + ' · ' + item.currency + ' / ' + item.status, 'tag'), element('h3', item.name),
          element('p', item.nameEn, 'english'), element('p', '别名：' + (item.aliases.join('、') || '无'), 'aliases'),
          element('p', item.id, 'id'), element('p', (item.ticketPriceFen / 100).toFixed(2) + ' 元', 'price'));
        document.getElementById('cards').append(card);
      });
      show('input-json', result.conditions); show('query-request-json', result.queryAnalysisRequest);
      show('base-request-json', result.baseAnalysisRequest); show('base-analysis-json', result.baseAnalysis); show('query-analysis-json', result.queryAnalysis); show('dsl-json', result.esRequest); show('result-json', result);
      status.textContent = result.total ? '请求完成。逐份核对：扩展出的查询路径，是否符合游客意图？' : '请求完成，0 份命中。核对 token 与硬条件；这不是连接错误。';
    } catch (error) {
      clear(); status.className = 'error'; status.textContent = '观察失败：' + error.message;
    } finally { fields.forEach(function (field) { field.disabled = false; }); }
  });
})();
