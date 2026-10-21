(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const base = '/api/attractions/changes';
  let read = null, page = null, conditions = null, busy = false;
  const json = value => JSON.stringify(value, null, 2);
  function message(id, text, error = false) { $(id).textContent = text; $(id).classList.toggle('error', error); }
  function controls() {
    for (const id of ['read', 'refresh', 'submit']) $(id).disabled = busy;
    $('save').disabled = busy || !read;
    $('next').disabled = busy || !page?.hasNext;
    $('close').disabled = busy || !page;
  }
  async function api(path, method = 'POST', data) {
    const response = await fetch(base + path, {method, headers:{'Content-Type':'application/json'},
      body:data === undefined ? undefined : JSON.stringify(data)});
    const result = await response.json();
    if (!response.ok) throw new Error(`${response.status} ${result.code}: ${result.message}`);
    return result;
  }
  function clearSearch() {
    page = null; $('cards').replaceChildren(); $('page-note').textContent = '等待重新搜索';
    for (const id of ['input-json','dsl-json','result-json']) $(id).textContent = '尚无当前结果';
    controls();
  }
  async function release() {
    const old = page; clearSearch();
    if (old) await api('/pages/close', 'POST', {cursor:old.cursor});
  }
  async function run(task, statusId) {
    if (busy) return;
    busy = true; controls();
    try { await task(); }
    catch (error) {
      if (statusId === 'status') clearSearch();
      if (statusId === 'write-status') { read = null; $('document-json').textContent = '当前版本无效，请重读后核对草稿。'; }
      message(statusId, error.message, true);
    } finally { busy = false; controls(); }
  }
  $('read').addEventListener('click', () => run(async () => {
    const value = $('document-id').value;
    if (!/^[a-z0-9-]{1,60}$/.test(value)) throw new Error('业务ID格式不正确。');
    read = await api('/' + encodeURIComponent(value), 'GET');
    $('price').value = read.document.ticket_price_fen; $('state').value = read.document.status;
    $('document-json').textContent = json(read);
    message('write-status', `GET：${read.id}，${read.document.ticket_price_fen}分，${read.document.status}。已读取当前版本。`);
  }, 'write-status'));
  $('document-id').addEventListener('input', () => { read = null; controls(); message('write-status', 'ID已变，请重新读取。'); });
  $('save').addEventListener('click', () => run(async () => {
    const price = Number($('price').value);
    if ($('price').value === '' || !Number.isInteger(price) || price < 0 || price > 100000000) throw new Error('请输入有效整数分。');
    const input = {seqNo:read.seqNo, primaryTerm:read.primaryTerm, ticketPriceFen:price, status:$('state').value};
    const result = await api('/' + encodeURIComponent(read.id), 'PATCH', input);
    // Only a new GET enables another edit; never silently acquire a new token after a conflict.
    read = null; $('document-json').textContent = json(result);
    message('write-status', `${result.result}：ES已接受；这不是搜索可见的确认。可先GET和搜索对照，再显式refresh。再次修改请重读。`);
  }, 'write-status'));
  $('refresh').addEventListener('click', () => run(async () => {
    await api('/refresh'); message('write-status', 'refresh完成。请重新搜索读取新视图；已有PIT仍保持原资料。');
  }, 'write-status'));
  function render(result) {
    page = result; $('cards').replaceChildren();
    for (const item of result.items) {
      const card = document.createElement('article'); card.className = 'card'; card.dataset.id = item.id;
      const name = document.createElement('h3'); name.textContent = item.name;
      const id = document.createElement('p'); id.className = 'id'; id.textContent = item.id;
      const price = document.createElement('p'); price.className = 'price'; price.textContent = (item.ticketPriceFen / 100).toFixed(2) + ' 元';
      const raw = document.createElement('p'); raw.className = 'tag'; raw.textContent = `${item.ticketPriceFen}分 · sort ${JSON.stringify(item.sortValues)}`;
      card.append(name, id, price, raw); $('cards').append(card);
    }
    $('page-note').textContent = `第${result.pageNumber}页 · 总计${result.total}份 · ${result.hasNext ? '可继续' : '末页'}`;
    message('status', result.total ? '当前PIT视图；价格与GET可能不同。' : '当前条件没有命中。');
    $('input-json').textContent = json(result.conditions); $('dsl-json').textContent = json(result.esRequest); $('result-json').textContent = json(result);
  }
  $('search-form').addEventListener('submit', event => {
    event.preventDefault(); run(async () => {
      await release();
      const data = new FormData(event.target), fen = Math.round(Number(data.get('budget')) * 100);
      conditions = {search:{q:data.get('q'), cityCode:data.get('cityCode'), maxPriceFen:fen, sortMode:data.get('sortMode'),
        latitude:30.25, longitude:120.15, trackScores:false}, pageSize:2};
      render(await api('/pages/start', 'POST', conditions));
    }, 'status');
  });
  $('search-form').addEventListener('change', () => run(async () => {
    await release(); message('status', '条件已变，旧轮已关闭，请重新搜索。');
  }, 'status'));
  $('next').addEventListener('click', () => run(async () => render(await api('/pages/next', 'POST', {cursor:page.cursor, afterPage:page.pageNumber, conditions})), 'status'));
  $('close').addEventListener('click', () => run(async () => { await release(); message('status', '已关闭这一轮。'); }, 'status'));
  function theme(value) {
    document.documentElement.dataset.theme = value; localStorage.setItem('travel-f12:theme', value);
    $('theme').textContent = value === 'dark' ? '切换浅色' : '切换深色';
  }
  theme(localStorage.getItem('travel-f12:theme') || 'light');
  $('theme').addEventListener('click', () => theme(document.documentElement.dataset.theme === 'light' ? 'dark' : 'light'));
  controls();
})();
