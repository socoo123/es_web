(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const theme = $('theme');
  const fields = ['q','hotel-sort','room-sort','scope','breakfast','flexible'];
  function applyTheme(v) { document.documentElement.dataset.theme=v;theme.textContent=v==='dark'?'切换浅色':'切换深色'; }
  try { applyTheme(localStorage.getItem('travel-f27-theme') || 'light'); } catch (_) { applyTheme('light'); }
  theme.onclick=()=>{const v=document.documentElement.dataset.theme==='dark'?'light':'dark';applyTheme(v);try{localStorage.setItem('travel-f27-theme',v);}catch(_){}};
  function node(tag,text,cls) { const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e; }
  const money=v=>'¥'+(v/100).toFixed(2);
  function clear() {
    $('cards').replaceChildren();$('decisions').replaceChildren();$('boundary').textContent='';$('total').textContent='等待观察';
    for(const id of ['input-json','dsl-json','result-json'])$(id).textContent='尚无本轮结果';
  }
  for(const id of fields)$(id).onchange=()=>{clear();$('status').textContent='条件已改变，请重新观察。';$('status').className='';};
  $('search-form').onsubmit=async event=>{
    event.preventDefault();clear();$('submit').disabled=true;for(const id of fields)$(id).disabled=true;
    $('status').textContent='Java正在检索酒店并逐晚核对报价…';$('status').className='';
    const input={q:$('q').value,hotelSort:$('hotel-sort').value,roomSort:$('room-sort').value,
      requireBreakfast:$('breakfast').checked,requireFlexible:$('flexible').checked,scope:$('scope').value};
    try {
      const response=await fetch('/api/hotel-ranking/inspect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input)});
      const result=await response.json();
      if(!response.ok)throw new Error(response.status+' · '+result.code+' · '+result.message);
      $('input-json').textContent=JSON.stringify(input,null,2);$('dsl-json').textContent=JSON.stringify(result.esRequest,null,2);$('result-json').textContent=JSON.stringify(result,null,2);
      $('total').textContent='候选'+result.candidateHotelTotal+'家 · 已核对'+result.inspectedHotelCount+'家/'+result.inspectedOfferCount+'报价 · 展示'+result.hotels.length+'家';
      $('boundary').textContent=result.boundary+' 合格报价'+result.acceptedOfferCount+'条；参考时刻'+result.referenceTime+'。';
      for(const h of result.hotels) {
        const card=node('article','','hotel');card.dataset.hotelId=h.hotelId;
        card.append(node('h3',h.hotelId+' · '+h.hotelName),
          node('p','酒店排序值：'+JSON.stringify(h.hotelSortValues)),
          node('p','品质信号：'+(h.qualitySignal==null?'缺失':h.qualitySignal)+' · 相关性分数：'+h.score),
          node('p','所选房型 '+h.selectedOfferId+' · 两晚 '+money(h.selectedTotalMinor),'price'),
          node('p','该酒店合格房型最低总价 '+money(h.minimumTotalMinor)+'；所选房型按当前偏好决定。'));
        if(input.hotelSort==='distance')card.append(node('p','距固定中心点：'+
          (h.hotelSortValues[0]==='Infinity'?'缺坐标（排末尾）':Number(h.hotelSortValues[0]).toFixed(1)+' 米')));
        const list=node('ol','');
        for(const room of h.rooms) {
          const li=node('li',room.offerId+' / '+room.roomId+' · '+(room.meal==='breakfast'?'含早':'不含早')+' · '+
            (room.cancellation==='flexible'?'可退':'不可退')+' · 两晚 '+money(room.totalMinor));
          li.dataset.offerId=room.offerId;list.append(li);
        }
        card.append(list);$('cards').append(card);
      }
      const reasons={ACCEPTED:'固定快照合格',MISSING_PRICE:'某晚缺价',STALE_INVENTORY:'库存超过固定5分钟阈值',
        FUTURE_INVENTORY:'库存时刻晚于固定参考时刻',MISSING_NIGHT:'缺住宿晚',SOLD_OUT:'某晚售罄',MIN_STAY:'最短入住不符'};
      for(const d of result.decisions)$('decisions').append(node('p',d.hotelId+' / '+d.offerId+' · '+(reasons[d.reason]||d.reason)+(d.totalMinor==null?'':' · 两晚 '+money(d.totalMinor))));
      $('status').textContent=result.completeCandidateSet?'完整候选已核对；房型重排保持酒店次序。':'仅前2家候选，核对失败后不补位；请切回完整范围比较。';
    } catch(error) { clear();$('status').textContent=error.message||'连接失败，请检查本机Java与ES。';$('status').className='error'; }
    finally { $('submit').disabled=false;for(const id of fields)$(id).disabled=false; }
  };
})();
