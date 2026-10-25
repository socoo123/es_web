(function () {
  'use strict';
  var form = document.getElementById('search-form');
  var status = document.getElementById('status');
  var fields = Array.from(form.elements);
  var button = document.getElementById('theme');
  function theme(value) {
    document.documentElement.dataset.theme = value;
    button.textContent = value === 'dark' ? '切换浅色' : '切换深色';
    try { localStorage.setItem('travel-f17:theme', value); } catch (_) {}
  }
  var saved; try { saved = localStorage.getItem('travel-f17:theme'); } catch (_) {}
  theme(saved === 'dark' ? 'dark' : 'light');
  button.addEventListener('click', function () { theme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'); });
  function show(id, value) { document.getElementById(id).textContent = JSON.stringify(value, null, 2); }
  function clear() {
    document.getElementById('cards').replaceChildren();
    ['input-json', 'dsl-json', 'es-json', 'result-json'].forEach(function (id) { document.getElementById(id).textContent = '尚无本轮结果'; });
    document.getElementById('total').textContent = '等待提交';
    document.getElementById('count-note').textContent = 'completion不返回全部候选总数。';
  }
  function element(tag, value, cls) {
    var node = document.createElement(tag); node.textContent = value; if (cls) node.className = cls; return node;
  }
  function changed() { clear(); status.className = ''; status.textContent = '条件已改变，请重新提交观察。'; }
  form.addEventListener('input', changed); form.addEventListener('change', changed);
  form.addEventListener('submit', async function (event) {
    event.preventDefault(); clear(); status.className = ''; status.textContent = '正在调用本机Java与ES…';
    var input = {q: form.elements.q.value, cityCode: form.elements.cityCode.value, mode: form.elements.mode.value};
    fields.forEach(function (field) { field.disabled = true; });
    try {
      var response = await fetch('/api/attractions/suggestions', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input)});
      var result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      document.getElementById('total').textContent = result.returnedCount + ' 份候选';
      document.getElementById('count-note').textContent = result.total === null
        ? 'completion原始返回' + result.rawCandidateCount + '条，按业务ID保留' + result.returnedCount + '份；上限' + result.candidateLimit + '，全部候选总数未知。'
        : '普通搜索总计' + result.total + '份 · ' + result.relation + '；本次展示' + result.returnedCount + '份，上限' + result.candidateLimit + '。';
      result.items.forEach(function (item) {
        var card = element('article', '', 'card'); card.dataset.id = item.id;
        card.append(element('p', item.cityCode + ' · ' + item.currency + ' / ' + item.status, 'tag'), element('h3', item.name),
          element('p', item.pinyinFull + ' / ' + item.pinyinInitials, 'pinyin'), element('p', item.suggestionText === null ? '普通搜索候选' : '匹配提示：' + item.suggestionText, 'suggestion'),
          element('p', item.id, 'id'), element('p', (item.ticketPriceFen / 100).toFixed(2) + ' 元', 'price'));
        document.getElementById('cards').append(card);
      });
      show('input-json', result.conditions); show('dsl-json', result.esRequest); show('es-json', result.esResponse); show('result-json', result);
      status.textContent = result.returnedCount ? '请求完成。逐份判断：哪个候选符合当前意图？' : '请求完成，0份候选。输入线索不足或没有匹配，这不是连接错误。';
    } catch (error) { clear(); status.className = 'error'; status.textContent = '观察失败：' + error.message;
    } finally { fields.forEach(function (field) { field.disabled = false; }); }
  });
})();
