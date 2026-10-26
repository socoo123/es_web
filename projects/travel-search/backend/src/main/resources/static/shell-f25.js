(function () {
  'use strict';
  var form = document.getElementById('search-form'), status = document.getElementById('status');
  var fields = Array.from(form.elements), themeButton = document.getElementById('theme');
  var scenarios = {'two-nights':['2026-11-03',1,120000], 'two-rooms':['2026-11-03',2,240000], 'three-nights':['2026-11-04',1,200000], 'one-night':['2026-11-02',1,120000]};
  var reasons = {ACCEPTED:'固定快照合格', MISSING_NIGHT:'缺少住宿晚记录', SOLD_OUT:'某晚售罄', STOCK_SHORTAGE:'某晚房间数不足', MIN_STAY:'不满足入住日最短入住', MISSING_PRICE:'某晚缺价', BUDGET_EXCEEDED:'入住总价超预算'};
  function theme(value) {
    document.documentElement.dataset.theme = value;
    themeButton.textContent = value === 'dark' ? '切换浅色' : '切换深色';
    try { localStorage.setItem('travel-f25:theme', value); } catch (_) {}
  }
  var saved; try { saved = localStorage.getItem('travel-f25:theme'); } catch (_) {}
  theme(saved === 'dark' ? 'dark' : 'light');
  themeButton.addEventListener('click', function () { theme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'); });
  function el(tag, value, cls) { var n = document.createElement(tag); n.textContent = value; if (cls) n.className = cls; return n; }
  function show(id, value) { document.getElementById(id).textContent = JSON.stringify(value, null, 2); }
  function money(n) { return n === null ? '缺价' : 'CNY ' + (n / 100).toFixed(2); }
  function clear() {
    document.getElementById('cards').replaceChildren();
    ['input-json', 'dsl-json', 'result-json'].forEach(function (id) { document.getElementById(id).textContent = '尚无本轮结果'; });
    document.getElementById('total').textContent = '等待观察';
  }
  document.getElementById('scenario').addEventListener('change', function () {
    var s = scenarios[this.value];
    form.elements.checkIn.value = '2026-11-01'; form.elements.checkOut.value = s[0];
    form.elements.rooms.value = s[1]; form.elements.adultsPerRoom.value = 2; form.elements.budgetMinor.value = s[2];
    clear(); status.className = ''; status.textContent = '条件已改变，请重新核对。';
  });
  form.addEventListener('input', function () { clear(); status.className = ''; status.textContent = '条件已改变，请重新核对。'; });
  form.addEventListener('submit', async function (event) {
    event.preventDefault(); clear(); status.className = ''; status.textContent = '正在读取ES候选并核对固定逐晚表…';
    var input = {checkIn:form.elements.checkIn.value, checkOut:form.elements.checkOut.value, rooms:Number(form.elements.rooms.value), adultsPerRoom:Number(form.elements.adultsPerRoom.value), budgetMinor:Number(form.elements.budgetMinor.value)};
    fields.forEach(function (field) { field.disabled = true; });
    try {
      var response = await fetch('/api/stay/inspect', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(input)});
      var result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      document.getElementById('total').textContent = result.candidateTotal + ' 条ES候选 / ' + result.acceptedTotal + ' 条快照合格报价';
      result.decisions.forEach(function (d) {
        var card = el('article', '', 'card'); card.dataset.id = d.offerId; card.dataset.accepted = String(d.reason === 'ACCEPTED');
        card.append(el('p', d.offerId + ' · ' + d.hotelId + ' · ' + d.roomId, 'tag'), el('h3', d.hotelName));
        card.append(el('p', reasons[d.reason] + ' · ' + d.reason + (d.failedDate ? ' · ' + d.failedDate : ''), 'decision'));
        if (d.totalMinor !== null) card.append(el('p', '全部房间/住宿晚总价 ' + money(d.totalMinor) + (d.reason === 'BUDGET_EXCEEDED' ? '（超预算）' : '（快照）'), 'price'));
        else card.append(el('p', '未形成合格总价；不展示部分晚合计。', 'identity'));
        card.append(el('p', d.planId + ' · ' + d.currency + ' · ' + input.rooms + '间 · 每间' + input.adultsPerRoom + '成人 · ' + result.snapshotId, 'identity'));
        var table = el('table', '', 'nightly'), header = el('tr', '');
        ['住宿晚','快照剩余间数','每晚每间价','该日入住最短晚数'].forEach(function (t) { header.append(el('th', t)); });
        var head = el('thead',''); head.append(header); table.append(head); var body = el('tbody','');
        d.nights.forEach(function (n) { var row=el('tr',''); [n.date,n.availableRooms === null ? '缺晚' : String(n.availableRooms),money(n.priceMinor),n.minStayArrival === null ? '—' : String(n.minStayArrival)].forEach(function(t){row.append(el('td',t));}); body.append(row); });
        table.append(body); card.append(table,el('p','窄屏可横向滚动逐晚表；只用入住日最短入住规则。'+result.boundary,'boundary'));
        document.getElementById('cards').append(card);
      });
      show('input-json', result.conditions); show('dsl-json', result.esRequest); show('result-json', result);
      status.textContent = '核对完成。候选不等于合格报价；离店日不占一晚。';
    } catch (error) { clear(); status.className = 'error'; status.textContent = '核对失败：' + error.message; }
    finally { fields.forEach(function (field) { field.disabled = false; }); }
  });
})();
