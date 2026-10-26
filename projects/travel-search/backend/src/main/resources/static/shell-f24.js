(function () {
  'use strict';
  var form = document.getElementById('search-form'), status = document.getElementById('status');
  var fields = Array.from(form.elements), themeButton = document.getElementById('theme');
  function theme(value) {
    document.documentElement.dataset.theme = value;
    themeButton.textContent = value === 'dark' ? '切换浅色' : '切换深色';
    try { localStorage.setItem('travel-f24:theme', value); } catch (_) {}
  }
  var saved; try { saved = localStorage.getItem('travel-f24:theme'); } catch (_) {}
  theme(saved === 'dark' ? 'dark' : 'light');
  themeButton.addEventListener('click', function () { theme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'); });
  function el(tag, value, cls) { var n = document.createElement(tag); n.textContent = value; if (cls) n.className = cls; return n; }
  function show(id, value) { document.getElementById(id).textContent = JSON.stringify(value, null, 2); }
  function clear() {
    document.getElementById('cards').replaceChildren();
    ['input-json', 'dsl-json', 'result-json'].forEach(function (id) { document.getElementById(id).textContent = '尚无本轮结果'; });
    document.getElementById('total').textContent = '等待观察';
  }
  form.addEventListener('input', function () { clear(); status.className = ''; status.textContent = '案例已改变，请重新观察。'; });
  form.addEventListener('submit', async function (event) {
    event.preventDefault(); clear(); status.className = ''; status.textContent = '正在调用本机Java与ES…';
    var input = {mode: form.elements.mode.value}; fields.forEach(function (field) { field.disabled = true; });
    try {
      var response = await fetch('/api/nested/inspect', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input)});
      var result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      document.getElementById('total').textContent = result.total + ' 家酒店 · ' + result.model;
      result.items.forEach(function (item) {
        var card = el('article', '', 'card'); card.dataset.id = item.id;
        card.append(el('p', item.id + ' · ' + result.conditions.mode, 'tag'), el('h3', item.hotelName));
        if (item.sortPriceMinor !== null && item.sortPriceMinor !== undefined)
          card.append(el('p', '排序值 CNY ' + (item.sortPriceMinor / 100).toFixed(2) + ' / 单晚', 'price'));
        if (item.offers.length) {
          card.append(el('p', '合格报价共 ' + item.matchingOffers + ' 条；inner_hits展示前 ' + item.offers.length + ' 条', 'identity'));
          item.offers.forEach(function (offer) {
            var s = offer.source;
            card.append(el('p', s.offer_id + ' · ' + s.room_id + ' · ' + s.room_name, 'identity'),
              el('p', '合格报价 CNY ' + (s.price_minor / 100).toFixed(2) + ' / 单晚', 'price'),
              el('p', s.bed_type + ' · 可住' + s.capacity + '人 · ' + s.meal + ' · ' + s.cancellation + ' · ' + s.rate_plan_id, 'identity'),
              el('p', s.service_date + ' · ' + s.currency + ' · ' + s.offer_status + ' · ' + s.snapshot_at, 'identity'));
          });
        } else card.append(el('p', '故意错误对照：命中没有证明同一条目合格，不展示可售价格。', 'boundary'));
        if (result.conditions.mode === 'unfiltered-sort') card.append(el('p', '故意错误对照：排序价可来自不合格条目；h02排序100元，合格报价650元。', 'boundary'));
        card.append(el('p', '根_source含全部' + item.source.rooms.length + '条报价，未被inner_hits裁剪；' + result.boundary, 'boundary'));
        document.getElementById('cards').append(card);
      });
      show('input-json', result.conditions); show('dsl-json', result.esRequest); show('result-json', result);
      status.textContent = '完成。核对酒店次序、报价ID、inner_hits总数与实际排序值。';
    } catch (error) { clear(); status.className = 'error'; status.textContent = '观察失败：' + error.message; }
    finally { fields.forEach(function (field) { field.disabled = false; }); }
  });
})();
