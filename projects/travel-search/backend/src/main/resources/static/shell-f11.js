(function () {
  'use strict';
  var root=document.documentElement, theme=document.getElementById('theme');
  function setTheme(t){root.dataset.theme=t;theme.textContent=t==='dark'?'切换浅色':'切换深色';}
  setTheme(localStorage.getItem('travel-search:theme')||'light');
  theme.onclick=function(){setTheme(root.dataset.theme==='dark'?'light':'dark');localStorage.setItem('travel-search:theme',root.dataset.theme);};
  var form=document.getElementById('search-form'), fields=document.getElementById('fields');
  var start=document.getElementById('submit'), next=document.getElementById('next'), close=document.getElementById('close');
  var status=document.getElementById('status'), cards=document.getElementById('cards'), history=document.getElementById('history'), note=document.getElementById('order-note');
  var current=null, busy=false, canNext=false;
  function controls(){fields.disabled=busy;start.disabled=busy;next.disabled=busy||!canNext;close.disabled=busy||!current;}
  function clear(){cards.replaceChildren();history.replaceChildren();note.textContent='等待新搜索';canNext=false;}
  function text(tag,value,cls){var el=document.createElement(tag);el.textContent=value;if(cls)el.className=cls;return el;}
  function input(){var d=new FormData(form);return {search:{q:d.get('q'),cityCode:d.get('cityCode'),maxPriceFen:Math.round(Number(d.get('budget'))*100),sortMode:d.get('sortMode'),latitude:Number(d.get('latitude')),longitude:Number(d.get('longitude')),trackScores:d.get('trackScores')==='true'},pageSize:Number(d.get('pageSize'))};}
  async function request(action,body){
    var response=await fetch('/api/attractions/pages/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    var result=await response.json();
    if(!response.ok)throw new Error(response.status+' · '+result.code+' · '+result.message);
    return result;
  }
  async function closeCurrent(){if(current){await request('close',{cursor:current.cursor});current=null;canNext=false;}}
  function display(result){
    current=result;canNext=result.hasNext;cards.replaceChildren();
    result.items.forEach(function(item){
      var card=text('article','', 'card');card.dataset.id=item.id;
      var mode=result.conditions.search.sortMode, first=item.sortValues[0];
      var metric=mode==='distance'?(first==='Infinity'?'待定位':first+' km'):mode==='price'?first+' 分':'相关性 '+first;
      card.append(text('p',item.id,'card-city'),text('h3',item.name),text('p',(item.ticketPriceFen/100).toFixed(2)+' 元 · '+item.ticketPriceFen+'分','card-price'),text('p','排序首值：'+metric,'metric'),text('p','score: '+(item.score===null?'未返回':item.score)),text('p','sort: '+JSON.stringify(item.sortValues),'sort-values'));cards.append(card);
    });
    history.append(text('li','第'+result.pageNumber+'页：'+result.items.map(function(i){return i.id;}).join(' → ')));
    note.textContent='第'+result.pageNumber+'页 · 本轮共'+result.total+'条';
    status.textContent=result.total===0?'本轮没有命中，请关闭或换条件重新搜索。':result.hasNext?'本页'+result.items.length+'条，可继续下一页。':'已到末页，请关闭这一轮。';
    document.getElementById('input-json').textContent=JSON.stringify(result.conditions,null,2);
    document.getElementById('dsl-json').textContent=JSON.stringify(result.esRequest,null,2);
    document.getElementById('result-json').textContent=JSON.stringify(result,null,2);
  }
  async function run(action){
    if(busy)return;busy=true;controls();status.className='';
    try{await action();}
    catch(error){clear();status.className='error';status.textContent=error.message+'；请关闭旧分页后从第一页开始。';document.getElementById('result-json').textContent=error.message;}
    finally{busy=false;controls();}
  }
  form.onsubmit=function(event){event.preventDefault();var conditions=input();run(async function(){await closeCurrent();clear();status.textContent='正在打开搜索视图…';display(await request('start',conditions));});};
  next.onclick=function(){if(!current||!canNext)return;var turn={cursor:current.cursor,afterPage:current.pageNumber,conditions:current.conditions};run(async function(){cards.replaceChildren();status.textContent='读取下一页…';display(await request('next',turn));});};
  close.onclick=function(){run(async function(){await closeCurrent();clear();status.textContent='这一轮已关闭，可以重新搜索。';document.getElementById('dsl-json').textContent='分页已关闭';document.getElementById('result-json').textContent='分页已关闭';});};
  form.addEventListener('input',function(){if(!current||busy)return;canNext=false;clear();run(async function(){await closeCurrent();status.textContent='条件已改变，旧分页已关闭；请从第一页开始。';document.getElementById('dsl-json').textContent='条件已改变，等待新搜索';document.getElementById('result-json').textContent='旧分页已关闭';});});
  window.addEventListener('pagehide',function(){if(current)fetch('/api/attractions/pages/close',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cursor:current.cursor}),keepalive:true}).catch(function(){});});
  controls();
}());
