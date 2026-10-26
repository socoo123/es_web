(function () {
  'use strict';
  var form = document.getElementById('search-form');
  var status = document.getElementById('status');
  var fields = Array.from(form.elements);
  var themeButton = document.getElementById('theme');
  function theme(value) {
    document.documentElement.dataset.theme = value;
    themeButton.textContent = value === 'dark' ? '切换浅色' : '切换深色';
    try { localStorage.setItem('travel-f22:theme', value); } catch (_) {}
  }
  var saved; try { saved = localStorage.getItem('travel-f22:theme'); } catch (_) {}
  theme(saved === 'dark' ? 'dark' : 'light');
  themeButton.addEventListener('click', function () { theme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'); });
  function element(tag, text, cls) {
    var node = document.createElement(tag); node.textContent = text; if (cls) node.className = cls; return node;
  }
  function show(id, value) { document.getElementById(id).textContent = JSON.stringify(value, null, 2); }
  function clear() {
    document.getElementById('cards').replaceChildren(); document.getElementById('macro').replaceChildren();
    ['input-json', 'dsl-json', 'result-json'].forEach(function (id) { document.getElementById(id).textContent = '尚无本轮结果'; });
    document.getElementById('total').textContent = '等待评估';
  }
  form.addEventListener('input', function () { clear(); status.className = ''; status.textContent = '条件已改变，请重新提交评估。'; });
  form.addEventListener('submit', async function (event) {
    event.preventDefault(); clear(); status.className = ''; status.textContent = '正在调用本机Java与ES…';
    var input = {split: form.elements.split.value, strategy: form.elements.strategy.value};
    fields.forEach(function (field) { field.disabled = true; });
    try {
      var response = await fetch('/api/quality/evaluate', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input)});
      var result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      document.getElementById('total').textContent = result.queries.length + ' 查询 · ' + result.fixtureVersion;
      document.getElementById('macro').append(element('p', 'Recall@10 = ' + result.macro.recall.toFixed(6)), element('p', 'nDCG@10 = ' + result.macro.ndcg.toFixed(6)));
      result.queries.forEach(function (query) {
        var card = element('article', '', 'card'); card.dataset.id = query.id;
        card.append(element('p', query.id + ' · 匹配总数 ' + query.total + ' · 返回 ' + query.ids.length, 'tag'), element('h3', query.text), element('p', query.intent, 'intent'),
          element('p', 'Recall@10=' + query.recall.toFixed(6) + ' · nDCG@10=' + query.ndcg.toFixed(6), 'quality'),
          element('p', '相关 ' + query.relevant_retrieved + '/' + query.relevant_docs + ' · DCG=' + query.dcg.toFixed(6) + ' · IDCG=' + query.ideal_dcg.toFixed(6), 'quality'));
        var list = element('ol', '', 'ranking');
        query.ids.forEach(function (id, i) {
          var hit = query.esResponse.hits.hits[i]; var item = element('li', hit._source.name); item.dataset.grade = query.grades[i];
          item.append(element('span', id + ' · 人工等级=' + query.grades[i] + ' · ES_score=' + hit._score)); list.append(item);
        });
        card.append(list); document.getElementById('cards').append(card);
      });
      show('input-json', result.conditions); show('dsl-json', result.queries.map(function (q) { return {id: q.id, request: q.esRequest}; })); show('result-json', result);
      status.textContent = '计算完成。比较同集同口径的逐查询得失；平均提高仍可能保留坏案例。';
    } catch (error) { clear(); status.className = 'error'; status.textContent = '评估失败：' + error.message; }
    finally { fields.forEach(function (field) { field.disabled = false; }); }
  });
})();
