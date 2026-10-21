(function () {
  'use strict';
  var root = document.documentElement, theme = document.getElementById('theme');
  function setTheme(value) { root.dataset.theme = value; theme.textContent = value === 'dark' ? '切换浅色' : '切换深色'; }
  setTheme(localStorage.getItem('travel-search:theme') || 'light');
  theme.addEventListener('click', function () {
    setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark');
    localStorage.setItem('travel-search:theme', root.dataset.theme);
  });
  var form = document.getElementById('search-form'), status = document.getElementById('status');
  var cards = document.getElementById('cards'), submit = document.getElementById('submit'), note = document.getElementById('order-note');
  function text(tag, value, cls) { var el = document.createElement(tag); el.textContent = value; if (cls) el.className = cls; return el; }
  var labels = {relevance:'相关性降序，再按ID升序',price:'票价分升序，再按ID升序',distance:'距离km升序，再按ID升序'};
  form.addEventListener('submit', async function (event) {
    event.preventDefault(); if (submit.disabled) return;
    var data = new FormData(form);
    var input = {q:data.get('q'),cityCode:data.get('cityCode'),maxPriceFen:Math.round(Number(data.get('budget')) * 100),sortMode:data.get('sortMode'),latitude:Number(data.get('latitude')),longitude:Number(data.get('longitude')),trackScores:data.get('trackScores') === 'true'};
    cards.replaceChildren(); note.textContent = '等待结果'; status.className = ''; status.textContent = '正在搜索…';
    document.getElementById('input-json').textContent = JSON.stringify(input, null, 2);
    document.getElementById('dsl-json').textContent = '等待结果'; document.getElementById('result-json').textContent = '等待结果'; submit.disabled = true;
    var controller = new AbortController(), timer = setTimeout(function () { controller.abort(); }, 10000);
    try {
      var response = await fetch('/api/attractions/sort-search', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input),signal:controller.signal});
      var result = await response.json(); document.getElementById('result-json').textContent = JSON.stringify(result, null, 2);
      if (!response.ok) throw new Error(result.message || '搜索失败，请重试。');
      document.getElementById('dsl-json').textContent = JSON.stringify(result.esRequest, null, 2);
      note.textContent = labels[result.conditions.sortMode]; status.textContent = '找到 ' + result.total + ' 个景点，当前展示 ' + result.items.length + ' 个。';
      result.items.forEach(function (item) {
        var card = text('article', '', 'card'); card.dataset.id = item.id;
        card.append(text('div', item.cityCode + ' · 开放', 'tag'),text('div', item.id, 'id'),text('h3', item.name));
        var price = text('p', '¥' + (item.ticketPriceFen / 100).toFixed(2), 'price'); price.append(text('span', ' / CNY 搜索快照'));card.append(price);
        card.append(text('p', '评分：' + (item.score === null ? '未返回' : String(item.score)), 'metric score'));
        var distance = !item.hasLocation ? '待定位' : (item.distanceKm === null ? '本模式未计算' : item.distanceKm.toFixed(3) + ' km');
        card.append(text('p', '距离：' + distance, 'metric distance'),text('p', 'sort = ' + JSON.stringify(item.sortValues), 'sort-values')); cards.append(card);
      });
    } catch (error) {
      cards.replaceChildren(); note.textContent = '本次未成功'; status.className = 'error'; status.textContent = error.name === 'AbortError' ? '等待搜索超时，请检查本机服务后重试。' : error.message;
      document.getElementById('dsl-json').textContent = '本次搜索未成功，已清除旧卡片。';
    } finally { clearTimeout(timer); submit.disabled = false; }
  });
})();
