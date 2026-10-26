(function () {
  'use strict';
  var form = document.getElementById('search-form'), status = document.getElementById('status');
  var fields = Array.from(form.elements), themeButton = document.getElementById('theme');
  function theme(value) {
    document.documentElement.dataset.theme = value;
    themeButton.textContent = value === 'dark' ? '切换浅色' : '切换深色';
    try { localStorage.setItem('travel-f23:theme', value); } catch (_) {}
  }
  var saved; try { saved = localStorage.getItem('travel-f23:theme'); } catch (_) {}
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
      var response = await fetch('/api/model/inspect', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input)});
      var result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      document.getElementById('total').textContent = result.total + (result.model === 'offers' ? ' 条报价' : ' 家酒店') + ' · ' + result.model;
      result.items.forEach(function (item) {
        var s = item.source, card = el('article', '', 'card'); card.dataset.id = item.id;
        card.append(el('p', item.id + ' · ' + s.hotel_id + ' · ' + s.city_code, 'tag'), el('h3', s.hotel_name));
        if (result.model === 'offers') {
          card.append(el('p', s.room_id + ' · ' + s.room_name + ' · ' + s.bed_type + ' · 可住' + s.capacity + '人', 'identity'),
            el('p', s.currency + ' ' + (s.price_minor / 100).toFixed(2) + ' / 单晚', 'price'),
            el('p', s.offer_id + ' · ' + s.rate_plan_id + ' · ' + s.meal + ' · ' + s.cancellation, 'identity'),
            el('p', s.service_date + ' · 酒店' + s.hotel_status + ' / 报价' + s.offer_status, 'identity'),
            el('p', 'snapshot_at=' + s.snapshot_at + '；可售状态来自固定快照，下单前仍需核验。', 'boundary'));
        } else {
          card.append(el('p', '酒店状态=' + s.hotel_status + '；本次命中ID是酒店ID。', 'identity'));
          if (s.rooms) {
            var list = el('ul', '');
            s.rooms.forEach(function (room) { list.append(el('li', room.room_id + ' · ' + room.room_name + ' · ' + room.rates.length + '个价目快照')); });
            card.append(list, el('p', '列出的是完整_source中的全部房型，r101查找没有自动裁剪数组；rates为object，仅作明细，不用于多字段联合筛选。', 'boundary'));
          } else card.append(el('p', '主文档不含房型、计划或价格，无法凭它回答房型报价条件。', 'boundary'));
        }
        document.getElementById('cards').append(card);
      });
      show('input-json', result.conditions); show('dsl-json', result.esRequest); show('result-json', result);
      status.textContent = '完成。核对根文档ID、所属房型和报价边界；报价条数不能直接叫酒店数。';
    } catch (error) { clear(); status.className = 'error'; status.textContent = '观察失败：' + error.message; }
    finally { fields.forEach(function (field) { field.disabled = false; }); }
  });
})();
