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
  var cards = document.getElementById('cards'), submit = document.getElementById('submit');
  var prices = document.getElementById('prices'), scope = document.getElementById('scope-note');
  function text(tag, value, cls) { var el = document.createElement(tag); el.textContent = value; if (cls) el.className = cls; return el; }
  function clear() {
    cards.replaceChildren(); prices.replaceChildren(); scope.textContent = '';
    document.querySelectorAll('.choice output').forEach(function (el) { el.textContent = '—'; });
  }
  function facet(name, group) {
    var complete = group.docCountErrorUpperBound === 0 && group.sumOtherDocCount === 0;
    document.querySelectorAll('[name="' + name + '"]').forEach(function (input) {
      var bucket = group.buckets.find(function (b) { return b.key === input.value; });
      document.getElementById('count-' + name + '-' + input.value).textContent = bucket ?
        String(bucket.docCount) + (bucket.docCountErrorUpperBound !== 0 ? '（上界 +' + bucket.docCountErrorUpperBound + '）' : '') : (complete ? '0' : '未返回');
    });
    return complete;
  }
  form.addEventListener('submit', async function (event) {
    event.preventDefault(); if (submit.disabled) return;
    var data = new FormData(form);
    var input = {q:data.get('q'),cityCodes:data.getAll('cityCodes'),themes:data.getAll('themes'),maxPriceFen:Math.round(Number(data.get('budget')) * 100)};
    clear(); status.className = ''; status.textContent = '正在更新景点与筛选数字…';
    document.getElementById('input-json').textContent = JSON.stringify(input, null, 2);
    document.getElementById('dsl-json').textContent = '等待结果';
    document.getElementById('result-json').textContent = '等待结果'; submit.disabled = true;
    var controller = new AbortController(), timer = setTimeout(function () { controller.abort(); }, 10000);
    try {
      var response = await fetch('/api/attractions/facet-search', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input),signal:controller.signal});
      var result = await response.json(); document.getElementById('result-json').textContent = JSON.stringify(result, null, 2);
      if (!response.ok) throw new Error(result.message || '搜索失败，请稍后重试。');
      document.getElementById('dsl-json').textContent = JSON.stringify(result.esRequest, null, 2);
      status.textContent = '找到 ' + result.total + ' 个景点，当前展示 ' + result.items.length + ' 个。';
      var cityComplete = facet('cityCodes', result.cities), themeComplete = facet('themes', result.themes);
      scope.textContent = '城市计数范围：' + result.cities.scopeTotal + ' 份；主题计数范围：' + result.themes.scopeTotal +
        ' 份，其中未填主题 ' + result.missingThemeCount + ' 份。' + (cityComplete && themeComplete ? ' 本次桶完整且误差上界为 0。' : ' 本次桶可能截断或有误差，请查看接口记录。');
      var labels = {'under-100':'不足 ¥100','100-to-200':'¥100 至不足 ¥200','200-plus':'¥200 起'};
      prices.append(text('p', '当前命中价格分布（保留全部筛选与预算）：'));
      result.prices.forEach(function (b) { var el = text('span', labels[b.key] + '：' + b.docCount); el.dataset.key = b.key; prices.append(el); });
      result.items.forEach(function (item) {
        var card = text('article', '', 'card'); card.dataset.id = item.id;
        card.append(text('div', item.cityCode + ' · 开放', 'tag'),text('div', item.id, 'id'),text('h3', item.name),text('p', item.themes.length ? item.themes.join(' / ') : '未填主题', 'themes'));
        var price = text('p', '¥' + (item.ticketPriceFen / 100).toFixed(2), 'price'); price.append(text('span', ' / CNY 搜索快照'));
        card.append(price); cards.append(card);
      });
    } catch (error) {
      clear(); status.className = 'error'; status.textContent = error.name === 'AbortError' ? '等待搜索超时，请检查本机服务后重试。' : error.message;
      document.getElementById('dsl-json').textContent = '本次搜索未成功，已清除旧卡片与计数。';
    } finally { clearTimeout(timer); submit.disabled = false; }
  });
})();
