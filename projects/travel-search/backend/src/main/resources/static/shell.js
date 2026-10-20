(function () {
  'use strict';
  var root = document.documentElement;
  var theme = document.getElementById('theme');
  function setTheme(value) {
    root.dataset.theme = value;
    theme.textContent = value === 'dark' ? '切换浅色' : '切换深色';
  }
  setTheme(localStorage.getItem('travel-search:theme') || 'light');
  theme.addEventListener('click', function () {
    setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark');
    localStorage.setItem('travel-search:theme', root.dataset.theme);
  });
  var form = document.getElementById('search-form');
  var status = document.getElementById('status');
  var cards = document.getElementById('cards');
  var submit = document.getElementById('submit');
  function text(tag, value, className) {
    var element = document.createElement(tag);
    element.textContent = value;
    if (className) element.className = className;
    return element;
  }
  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    if (submit.disabled) return;
    var data = new FormData(form);
    var input = {q: data.get('q'), cityCode: data.get('cityCode'),
      maxPriceFen: Math.round(Number(data.get('budget')) * 100),
      latitude: 30.25, longitude: 120.15, radiusKm: Number(data.get('radiusKm'))};
    cards.replaceChildren();
    status.className = '';
    status.textContent = '正在寻找符合条件的景点…';
    document.getElementById('input-json').textContent = JSON.stringify(input, null, 2);
    document.getElementById('dsl-json').textContent = '等待结果';
    document.getElementById('result-json').textContent = '等待结果';
    submit.disabled = true;
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, 10000);
    try {
      var response = await fetch('/api/attractions/search', {method: 'POST',
        headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input), signal: controller.signal});
      var result = await response.json();
      document.getElementById('result-json').textContent = JSON.stringify(result, null, 2);
      if (!response.ok) throw new Error(result.message || '搜索失败，请稍后重试。');
      document.getElementById('dsl-json').textContent = JSON.stringify(result.esRequest, null, 2);
      status.textContent = '找到 ' + result.total + ' 个景点，当前展示 ' + result.items.length + ' 个。';
      if (!result.items.length) status.textContent += ' 可以调整关键词、预算或距离后再试。';
      result.items.forEach(function (item) {
        var card = text('article', '', 'card');
        card.dataset.id = item.id;
        card.append(text('div', item.cityCode + ' · 开放', 'tag'), text('h3', item.name), text('div', item.id, 'id'));
        var price = text('p', '¥' + (item.ticketPriceFen / 100).toFixed(2), 'price');
        price.append(text('span', ' / CNY 搜索快照'));
        card.append(price); cards.append(card);
      });
    } catch (error) {
      cards.replaceChildren();
      status.className = 'error';
      status.textContent = error.name === 'AbortError' ? '等待搜索超时，请核对本机服务后重试。' : error.message;
      document.getElementById('dsl-json').textContent = '本次搜索未成功，不展示旧命中。';
    } finally {
      clearTimeout(timer); submit.disabled = false;
    }
  });
})();
