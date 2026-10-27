(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const theme = $('theme');
  function applyTheme(value) { document.documentElement.dataset.theme = value; theme.textContent = value === 'dark' ? '切换浅色' : '切换深色'; }
  try { applyTheme(localStorage.getItem('travel-f26-theme') || 'light'); } catch (_) { applyTheme('light'); }
  theme.onclick = () => { const v = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; applyTheme(v); try { localStorage.setItem('travel-f26-theme', v); } catch (_) {} };
  function node(tag, value, cls) { const e = document.createElement(tag); e.textContent = value; if (cls) e.className = cls; return e; }
  function clear() { $('cards').replaceChildren(); $('decisions').replaceChildren(); $('boundary').textContent = ''; $('total').textContent = '等待观察'; for (const id of ['input-json','dsl-json','result-json']) $(id).textContent = '尚无本轮结果'; }
  $('mode').onchange = () => { clear(); $('status').textContent = '范围已改变，请重新观察。'; $('status').className = ''; };
  $('search-form').onsubmit = async event => {
    event.preventDefault(); clear(); $('submit').disabled = true; $('mode').disabled = true;
    $('status').textContent = '正在由Java查询ES并核对固定逐晚表…'; $('status').className = '';
    const input = {mode: $('mode').value};
    try {
      const response = await fetch('/api/collapse/inspect', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(input)});
      const result = await response.json();
      if (!response.ok) throw new Error(response.status + ' · ' + result.code + ' · ' + result.message);
      $('input-json').textContent = JSON.stringify(input, null, 2); $('dsl-json').textContent = JSON.stringify(result.esRequest, null, 2); $('result-json').textContent = JSON.stringify(result, null, 2);
      $('total').textContent = '已查' + result.inspectedOfferCount + '条 / ' + result.inspectedHotelCount + '家；展示' + result.displayedHotelCount + '家';
      $('boundary').textContent = result.boundary + ' ES条件命中' + result.candidateOfferTotal + '条报价；cardinality酒店估计' + result.candidateHotelEstimate + '家。合格报价' + result.acceptedOfferCount + '条。';
      const label = input.mode === 'top-offers' ? '已查报价最低两晚总价' : '该范围内酒店合格房型最低两晚总价';
      for (const h of result.hotels) {
        const card = node('article','', 'hotel'); card.dataset.hotelId = h.hotelId;
        card.append(node('h3', h.hotelId + ' · ' + h.hotelName), node('p',label), node('p','¥' + (h.minimumTotalMinor/100).toFixed(2),'price'), node('p','最低价报价：' + h.minimumOfferId), node('p','已查合格报价：' + h.acceptedOfferIds.join('、')));
        $('cards').append(card);
      }
      const reasons = {ACCEPTED:'固定快照合格', MISSING_NIGHT:'缺少住宿晚记录', SOLD_OUT:'某晚售罄', MIN_STAY:'不满足入住日最短入住', MISSING_PRICE:'某晚缺价'};
      for (const d of result.decisions) $('decisions').append(node('p', d.offerId + ' / ' + d.hotelId + ' · ' + (reasons[d.reason] || d.reason) + (d.totalMinor == null ? '' : ' · 两晚CNY ' + d.totalMinor + '分')));
      $('status').textContent = result.completeCandidateSet ? '已完整核对本固定快照的候选；h04/h05同为600元，酒店ID决定同价次序。' : '范围有限：请切换全部候选，对照范围外h04/h05的600元。';
    } catch (error) { clear(); $('status').textContent = error.message || '连接失败，请检查本机Java与ES。'; $('status').className = 'error'; }
    finally { $('submit').disabled = false; $('mode').disabled = false; }
  };
})();
