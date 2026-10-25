(function () {
  'use strict';
  var form = document.getElementById('search-form');
  var status = document.getElementById('status');
  var fields = Array.from(form.elements);
  var themeButton = document.getElementById('theme');
  function theme(value) {
    document.documentElement.dataset.theme = value;
    themeButton.textContent = value === 'dark' ? '切换浅色' : '切换深色';
    try { localStorage.setItem('travel-f19:theme', value); } catch (_) {}
  }
  var saved; try { saved = localStorage.getItem('travel-f19:theme'); } catch (_) {}
  theme(saved === 'dark' ? 'dark' : 'light');
  themeButton.addEventListener('click', function () {
    theme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
  });
  function show(id, value) { document.getElementById(id).textContent = JSON.stringify(value, null, 2); }
  function element(tag, value, cls) {
    var node = document.createElement(tag); node.textContent = value; if (cls) node.className = cls; return node;
  }
  function clear() {
    document.getElementById('cards').replaceChildren();
    document.getElementById('explain-summary').replaceChildren();
    ['input-json', 'dsl-json', 'explain-request-json', 'explain-json', 'result-json'].forEach(function (id) {
      document.getElementById(id).textContent = '尚无本轮结果';
    });
    document.getElementById('total').textContent = '等待搜索';
    document.getElementById('explain-note').textContent = '等待提交；也可以选择被条件排除的资料。';
  }
  function summary(container, explanation) {
    var nodes = (explanation.details || []).filter(function (n) { return n.value > 0; });
    if (!nodes.length) { container.append(element('p', '根没有非零贡献；结合 matched 与完整解释树判断。', 'note')); return; }
    nodes.forEach(function (n) {
      var metric = element('div', '', 'metrics');
      metric.append(element('strong', n.description), element('span', 'value = ' + n.value));
      container.append(metric);
    });
  }
  form.addEventListener('input', function () {
    clear(); status.className = ''; status.textContent = '条件已改变，请重新提交观察。';
  });
  form.addEventListener('submit', async function (event) {
    event.preventDefault(); clear(); status.className = ''; status.textContent = '正在调用本机 Java 与 ES…';
    var budget = form.elements.budget.value.split('.');
    var input = {q: form.elements.q.value, cityCode: form.elements.cityCode.value,
      maxPriceFen: Number(budget[0]) * 100 + Number(((budget[1] || '') + '00').slice(0, 2)),
      mode: form.elements.mode.value, nameWeight: Number(form.elements.nameWeight.value), explainId: form.elements.explainId.value};
    fields.forEach(function (field) { field.disabled = true; });
    try {
      var response = await fetch('/api/attractions/weight-search', {method: 'POST',
        headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input)});
      var result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      document.getElementById('total').textContent = result.total + ' 份 · ' + result.relation;
      result.items.forEach(function (item, i) {
        var card = element('article', '', 'card'); card.dataset.id = item.id;
        card.append(element('p', (i + 1) + ' · ' + item.cityCode + ' · CNY / open', 'tag'),
          element('h3', item.name), element('p', item.id, 'id'),
          element('p', item.description, 'description'), element('p', '_score = ' + item.score, 'score'),
          element('p', (item.ticketPriceFen / 100).toFixed(2) + ' 元', 'price'));
        summary(card, item.explanation);
        var details = element('details', '');
        details.append(element('summary', '完整命中解释树'), element('pre', JSON.stringify(item.explanation, null, 2)));
        card.append(details); document.getElementById('cards').append(card);
      });
      var explained = result.explainResponse;
      document.getElementById('explain-note').textContent = explained._id + ' · matched=' + explained.matched + ' · value=' + explained.explanation.value +
        (explained.matched ? '' : ' · 完整条件未匹配；下方若有文本子句贡献，也不是候选得分。');
      summary(document.getElementById('explain-summary'), explained.explanation);
      show('explain-json', explained); show('input-json', result.conditions); show('dsl-json', result.esRequest);
      show('explain-request-json', {path: result.explainPath, body: result.explainRequest}); show('result-json', result);
      status.textContent = result.total ? '请求完成。先核对候选，再比较加和、取大与奖励的真实贡献。' : '请求完成，0 份命中。查看单份解释；这不是连接错误。';
    } catch (error) {
      clear(); status.className = 'error'; status.textContent = '观察失败：' + error.message;
    } finally { fields.forEach(function (field) { field.disabled = false; }); }
  });
})();
