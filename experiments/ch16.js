/* experiments/ch16.js — 第 16 课:Query Then Fetch 实验 + 两阶段搜索旗舰动画(注册表) */
(function () {
  'use strict';

  /* ===== 旗舰动画:一次 _search 的 Query / Fetch 两阶段 ===== */
  function defs(id) {
    return '<defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
  }
  function rect(x, y, w, h, cls, anim) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="9" class="' + cls + (anim ? ' ' + anim : '') + '"/>';
  }
  function txt(x, y, s, cls, warn, anim) {
    var st = warn ? ' style="fill: rgb(var(--warn))"' : '';
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + (anim ? ' ' + anim : '') + '"' + st + '>' + s + '</text>';
  }
  function line(x1, y1, x2, y2, id) {
    return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" class="fig-arrow" marker-end="url(#' + id + ')"/>';
  }

  /* 步骤 1:请求到达协调节点 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s1');
    s += rect(15, 25, 730, 64, 'fig-box');
    s += txt(380, 50, 'POST /tut-l16-qtf/_search', 'fig-key');
    s += txt(380, 72, '{"size":10,"query":{"match":{"title":"elasticsearch"}}}', 'fig-sub');
    s += line(380, 89, 380, 118, 'ah16s1');
    s += rect(230, 122, 300, 58, 'fig-box-hot', 'fp-pop');
    s += txt(380, 146, '协调节点', 'fig-name');
    s += txt(380, 168, '默认 SearchType = QUERY_THEN_FETCH', 'fig-sub');
    s += txt(380, 212, 'REST 只造 SearchRequest,不跑 Lucene', 'fig-sub');
    s += txt(380, 234, '真正跑 Lucene 的是各 shard 上的 SearchService', 'fig-sub');
    s += txt(380, 268, 'TransportSearchAction:indices:data/read/search', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 2:受控扇出 Query,不等待全部响应 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s2');
    s += rect(230, 15, 300, 52, 'fig-box');
    s += txt(380, 38, 'doRun:一个 for 循环', 'fig-name');
    s += txt(380, 58, '不 await 全部响应，可排队调度', 'fig-sub');
    s += line(280, 67, 137, 105, 'ah16s2');
    s += line(380, 67, 380, 105, 'ah16s2');
    s += line(480, 67, 633, 105, 'ah16s2');
    for (var i = 0; i < 3; i++) {
      var x = 15 + i * 250, cx = x + 112;
      s += rect(x, 109, 225, 78, 'fig-box');
      s += txt(cx, 131, 'shard ' + i, 'fig-name');
      s += txt(cx, 151, 'phase/query', 'fig-key');
      s += txt(cx, 171, '回 (docId,score)', 'fig-sub');
    }
    s += rect(15, 198, 730, 80, 'fig-box');
    s += txt(380, 220, 'outstandingShards = 3', 'fig-key');
    s += txt(380, 242, '消费结果完成，倒数到 0 后调度 Fetch', 'fig-sub');
    s += txt(380, 264, '分片 Query / Fetch 都可使用 search 池', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 3:普通本地候选上限 from+size,示意数据 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s3');
    var rows = [
      ['doc=7  s=9.41', 'doc=1  s=9.39', 'doc=6  s=9.44'],
      ['doc=19 s=9.38', 'doc=8  s=9.35', 'doc=15 s=9.36'],
      ['doc=2  s=9.31', 'doc=22 s=9.30', 'doc=11 s=9.29']
    ];
    for (var i = 0; i < 3; i++) {
      var x = 15 + i * 250, cx = x + 112;
      s += rect(x, 15, 225, 170, 'fig-box');
      s += txt(cx, 38, 'shard ' + i + ' · EXTERNAL', 'fig-name');
      s += txt(cx, 60, '本地 Top-10 · 示意数据', 'fig-sub');
      s += txt(cx, 84, rows[0][i], 'fig-key');
      s += txt(cx, 104, rows[1][i], 'fig-key');
      s += txt(cx, 124, rows[2][i], 'fig-key');
      s += txt(cx, 148, '…', 'fig-sub');
      s += txt(cx, 168, '假设足量匹配，至多 10 条', 'fig-sub');
    }
    s += rect(15, 198, 730, 74, 'fig-box-hot', 'fp-pop');
    s += txt(380, 222, '普通每片候选上限 from+size', 'fig-name');
    s += txt(380, 244, 'doc 是 shard 内的 Lucene 文档号,不是 _id', 'fig-sub');
    s += txt(380, 264, '只看已 refresh 的快照,未 refresh 写入对该读者不可见', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 4:倒数到 0,全局归并 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s4');
    s += rect(15, 15, 730, 56, 'fig-box');
    s += txt(380, 38, 'outstandingShards:3 → 2 → 1 → 0', 'fig-key');
    s += txt(380, 58, '消费完成后调度归并，不固定回调线程', 'fig-sub');
    s += line(127, 124, 310, 150, 'ah16s4');
    s += line(380, 124, 380, 150, 'ah16s4');
    s += line(633, 124, 450, 150, 'ah16s4');
    for (var i = 0; i < 3; i++) {
      var x = 15 + i * 250, cx = x + 112;
      s += rect(x, 80, 225, 44, 'fig-box');
      s += txt(cx, 98, 'shard ' + i + ' · 10 条', 'fig-sub');
      s += txt(cx, 116, '(docId,score)', 'fig-sub');
    }
    s += rect(205, 154, 350, 64, 'fig-box-hot', 'fp-pop');
    s += txt(380, 178, '全局归并:30 选 10', 'fig-name');
    s += txt(380, 200, 'sortDocs · mergeTopDocs', 'fig-key');
    s += rect(15, 232, 730, 50, 'fig-box');
    s += txt(380, 255, 'Query 候选至多 30 条：此例假设每片足量', 'fig-sub');
    s += txt(380, 275, '此刻一篇 _source 都还没搬过', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 5:fillDocIdsToLoad 按 shardIndex 分组 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s5');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 38, 'fillDocIdsToLoad:按 shardIndex 分组', 'fig-name');
    s += txt(380, 58, '全局 Top-10 的每个 doc 回到自己的 shard', 'fig-sub');
    var groups = [
      { n: 'shard 0', ids: 'doc 7, 19, 2', c: '3 篇待取' },
      { n: 'shard 1', ids: 'doc 1, 8, 22, 3, 4', c: '5 篇待取', hot: true },
      { n: 'shard 2', ids: 'doc 6, 15', c: '2 篇待取' }
    ];
    for (var i = 0; i < 3; i++) {
      var g = groups[i], x = 15 + i * 250, cx = x + 112;
      s += rect(x, 80, 225, 96, g.hot ? 'fig-box-hot' : 'fig-box', g.hot ? 'fp-pop' : null);
      s += txt(cx, 104, g.n, 'fig-name');
      s += txt(cx, 128, g.ids, 'fig-key');
      s += txt(cx, 152, g.c, 'fig-sub');
    }
    s += rect(15, 192, 730, 80, 'fig-box');
    s += txt(380, 214, '某 shard 一条都没进全局 Top-10 → 槽位 null', 'fig-sub');
    s += txt(380, 236, '不发 Fetch，释放本例普通 reader', 'fig-sub');
    s += txt(380, 256, 'Fetch 扇出宽度 ≤ 持有命中文档的 shard 数', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 6:Fetch 只向持有者发 docId 列表 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s6');
    s += rect(15, 60, 250, 90, 'fig-box-hot');
    s += txt(140, 92, 'FetchSearchPhase', 'fig-name');
    s += txt(140, 114, 'sendExecuteFetch', 'fig-key');
    s += txt(140, 136, '按分组发 docId 列表', 'fig-sub');
    s += line(265, 105, 300, 45, 'ah16s6');
    s += line(265, 105, 300, 115, 'ah16s6');
    s += line(265, 105, 300, 185, 'ah16s6');
    var targets = [
      { y: 20, n: 'shard 0 · 取 3 篇 _source', k: '[phase/fetch/id] doc=7,19,2' },
      { y: 90, n: 'shard 1 · 取 5 篇 _source', k: '[phase/fetch/id] doc=1,8,22,3,4' },
      { y: 160, n: 'shard 2 · 取 2 篇 _source', k: '[phase/fetch/id] doc=6,15' }
    ];
    for (var i = 0; i < 3; i++) {
      var t = targets[i];
      s += rect(300, t.y, 445, 50, 'fig-box');
      s += txt(522, t.y + 22, t.n, 'fig-name');
      s += txt(522, t.y + 40, t.k, 'fig-sub');
    }
    s += rect(15, 230, 730, 54, 'fig-box-hot', 'fp-pop');
    s += txt(380, 252, '默认只取最终页，至多 10 条命中', 'fig-name');
    s += txt(380, 274, '一阶段方案会把 20 篇进不了响应的正文也搬回来', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 7:组装响应,对照 GET */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s7');
    s += rect(15, 15, 730, 54, 'fig-box-hot', 'fp-pop');
    s += txt(380, 38, 'merge 组装最终 hits', 'fig-name');
    s += txt(380, 60, '本例默认含 _source，按全局顺序输出', 'fig-sub');
    s += rect(15, 90, 355, 112, 'fig-box');
    s += txt(192, 112, 'GET(第 10 课)', 'fig-name');
    s += txt(192, 136, '按 _id 只打 1 个 shard', 'fig-sub');
    s += txt(192, 158, 'Realtime:未 refresh 也读得到', 'fig-sub');
    s += txt(192, 180, '返回这一篇 _source', 'fig-sub');
    s += rect(390, 90, 355, 112, 'fig-box');
    s += txt(567, 112, 'SEARCH(本课)', 'fig-name');
    s += txt(567, 136, '默认打全部 shard 组', 'fig-sub');
    s += txt(567, 158, '只看已 refresh 的 EXTERNAL 快照', 'fig-sub');
    s += txt(567, 180, '先比分,再取正文', 'fig-sub');
    s += rect(15, 218, 730, 58, 'fig-box');
    s += txt(380, 240, '_shards.total = 3 · hits.hits = 10', 'fig-key');
    s += txt(380, 262, '两列之间没有箭头:GET 失败不会改走 SEARCH', 'fig-sub');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch16-qtf'] = {
    version: 1,
    id: 'ch16-qtf',
    title: '一次搜索的两阶段:Query Then Fetch',
    speed: 2400,
    steps: [
      { svg: step1(), note: "限定普通三分片、from=0、size=10、无 rank / rescore / suggest，假设每片足量命中。分片角色可同在一台节点；箭头不等于网络包。REST 构造 SearchRequest 后委托搜索动作。" },
      { svg: step2(), note: "每个分片组选择一份拷贝，受每节点并发限制，可先排队。没有 await 全部响应；异步接口也可能同步回调，不保证立刻释放线程。结果消费完成后才倒数。" },
      { svg: step3(), note: "Query 使用已打开的 EXTERNAL 读者。普通每片至多 from+size 条，实际还受匹配数影响；图中是假设足量的虚构排名，不是本课 30 篇数据。doc 是该读者中的 Lucene 全局文档号。" },
      { svg: step4(), note: "消费完成后 outstandingShards 归零，再进入下一阶段；FetchSearchPhase.run 通过 context.execute 调度归并，不固定在最后网络回调线程。图中从假设的 30 候选取全局 10 条。" },
      { svg: step5(), note: "按 shardIndex 将最终窗口的 doc 分组。图中 3/5/2 是示意分配；空分组不发 Fetch，释放本例普通临时读者。PIT / scroll 的保留规则另论。" },
      { svg: step6(), note: "Fetch 携带读者上下文与 Lucene doc 列表，回到选定读者加载命中，并非再次执行查询或逐篇 REST GET。默认返回 _source；关闭 _source 不能据此推断没有 Fetch。" },
      { svg: step7(), note: "协调端按全局顺序合成 hits，本例至多 10 条。普通 GET 按 _id / routing 定片，默认 realtime；普通 SEARCH 默认遍历分片组，读已 refresh 视图。单分片可合并 Query / Fetch，但不是新 SearchType。" }
    ]
  };

  /* ===== 实验：按 A → B → C → D → 清理顺序注册 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch16-14-node"] = {
    "version": 1,
    "id": "ch16-14-node",
    "title": "A1 · 核对节点版本",
    "method": "GET",
    "path": "/?filter_path=version",
    "body": null,
    "predict": "节点版本与 Lucene 版本是多少？",
    "expect": "version.number=9.4.0、lucene_version=10.4.0；本课另要求匿名单节点 localhost:9200，节点版本不代表索引创建版本。"
  };
  window.ESEXPERIMENTS["ch16-00-setup"] = {
    "version": 1,
    "id": "ch16-00-setup",
    "title": "实验 0 · 建 tut-l16-qtf:3 主分片,冻结自动 refresh",
    "method": "PUT",
    "path": "/tut-l16-qtf",
    "body": {
      "settings": {
        "index": {
          "mode": "standard",
          "number_of_shards": 3,
          "number_of_replicas": 0,
          "auto_expand_replicas": "false",
          "refresh_interval": "-1",
          "max_result_window": 10000,
          "default_pipeline": "_none",
          "final_pipeline": "_none"
        }
      },
      "mappings": {
        "dynamic": "strict",
        "_source": {
          "enabled": true
        },
        "properties": {
          "title": {
            "type": "text",
            "analyzer": "standard"
          },
          "n": {
            "type": "integer"
          }
        }
      }
    },
    "predict": "3 个主分片对一次搜索意味着什么?refresh_interval=-1 又冻结了什么?",
    "expect": "首次 acknowledged=true；重复创建为 400 resource_already_exists_exception。本例显式 3 主片、0 副本、standard、strict mapping、周期 refresh=-1 与窗口 10000。禁用周期刷新不阻止手动或其他原因刷新；按后续健康卡等待。"
  };
  window.ESEXPERIMENTS["ch16-15-health"] = {
    "version": 1,
    "id": "ch16-15-health",
    "title": "A3 · 等待本课三主片就绪",
    "method": "GET",
    "path": "/_cluster/health/tut-l16-qtf?wait_for_status=green&wait_for_active_shards=3&timeout=10s",
    "body": null,
    "predict": "只有本课索引会等待什么？",
    "expect": "timed_out=false、status=green、active_primary_shards=3、active_shards=3；0 副本的 green 不表示有冗余。若超时先恢复节点/分片分配，不继续。"
  };
  window.ESEXPERIMENTS["ch16-16-settings"] = {
    "version": 1,
    "id": "ch16-16-settings",
    "title": "A4 · 读回窗口和刷新设置",
    "method": "GET",
    "path": "/tut-l16-qtf/_settings?flat_settings=true",
    "body": null,
    "predict": "窗口和刷新设置属于索引还是本次请求？",
    "expect": "index.number_of_shards=3、number_of_replicas=0、refresh_interval=-1、max_result_window=10000；API 以字符串显示设置，size 与 from 不会改这些配置。"
  };
  window.ESEXPERIMENTS["ch16-01-bulk"] = {
    "version": 1,
    "id": "ch16-01-bulk",
    "title": "实验 1 · 30 篇文档一次性写入(?refresh=true)",
    "method": "POST",
    "path": "/tut-l16-qtf/_bulk?refresh=true",
    "body": "{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"1\"}}\n{\"title\":\"document number 1 about elasticsearch\",\"n\":1}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"2\"}}\n{\"title\":\"document number 2 about elasticsearch\",\"n\":2}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"3\"}}\n{\"title\":\"document number 3 about elasticsearch\",\"n\":3}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"4\"}}\n{\"title\":\"document number 4 about elasticsearch\",\"n\":4}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"5\"}}\n{\"title\":\"document number 5 about elasticsearch\",\"n\":5}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"6\"}}\n{\"title\":\"document number 6 about elasticsearch\",\"n\":6}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"7\"}}\n{\"title\":\"document number 7 about elasticsearch\",\"n\":7}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"8\"}}\n{\"title\":\"document number 8 about elasticsearch\",\"n\":8}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"9\"}}\n{\"title\":\"document number 9 about elasticsearch\",\"n\":9}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"10\"}}\n{\"title\":\"document number 10 about elasticsearch\",\"n\":10}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"11\"}}\n{\"title\":\"document number 11 about elasticsearch\",\"n\":11}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"12\"}}\n{\"title\":\"document number 12 about elasticsearch\",\"n\":12}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"13\"}}\n{\"title\":\"document number 13 about elasticsearch\",\"n\":13}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"14\"}}\n{\"title\":\"document number 14 about elasticsearch\",\"n\":14}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"15\"}}\n{\"title\":\"document number 15 about elasticsearch\",\"n\":15}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"16\"}}\n{\"title\":\"document number 16 about elasticsearch\",\"n\":16}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"17\"}}\n{\"title\":\"document number 17 about elasticsearch\",\"n\":17}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"18\"}}\n{\"title\":\"document number 18 about elasticsearch\",\"n\":18}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"19\"}}\n{\"title\":\"document number 19 about elasticsearch\",\"n\":19}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"20\"}}\n{\"title\":\"document number 20 about elasticsearch\",\"n\":20}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"21\"}}\n{\"title\":\"document number 21 about elasticsearch\",\"n\":21}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"22\"}}\n{\"title\":\"document number 22 about elasticsearch\",\"n\":22}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"23\"}}\n{\"title\":\"document number 23 about elasticsearch\",\"n\":23}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"24\"}}\n{\"title\":\"document number 24 about elasticsearch\",\"n\":24}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"25\"}}\n{\"title\":\"document number 25 about elasticsearch\",\"n\":25}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"26\"}}\n{\"title\":\"document number 26 about elasticsearch\",\"n\":26}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"27\"}}\n{\"title\":\"document number 27 about elasticsearch\",\"n\":27}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"28\"}}\n{\"title\":\"document number 28 about elasticsearch\",\"n\":28}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"29\"}}\n{\"title\":\"document number 29 about elasticsearch\",\"n\":29}\n{\"index\":{\"_index\":\"tut-l16-qtf\",\"_id\":\"30\"}}\n{\"title\":\"document number 30 about elasticsearch\",\"n\":30}\n",
    "predict": "refresh=true 之后 SEARCH 立刻能看见几篇?每篇落哪个 shard 由什么决定?",
    "expect": "首次 errors=false，30 项均 created / 201；同次重写固定 ID 则 updated / 200，不增加文档数。refresh=true 刷新受影响分片，使成功写入可搜；不用固定字节或均匀路由假设。"
  };
  window.ESEXPERIMENTS["ch16-02-shards"] = {
    "version": 1,
    "id": "ch16-02-shards",
    "title": "实验 2 · _cat/shards:3 个 primary 的文档分布",
    "method": "GET",
    "path": "/_cat/shards/tut-l16-qtf?format=json&h=shard,prirep,state,docs",
    "predict": "30 篇在 3 个 shard 上是整齐的 10/10/10 吗?",
    "expect": "3 条 STARTED / p，文档数合计 30；本次固定数据实测为 12/9/9。哈希不保证均匀。size=10 时各片本地候选上限 10/9/9，合计 28；最终响应仍是全局 10 条。"
  };
  window.ESEXPERIMENTS["ch16-03-search"] = {
    "version": 1,
    "id": "ch16-03-search",
    "title": "实验 3 · from=0&size=10:hits 是 10,不是 30",
    "method": "POST",
    "path": "/tut-l16-qtf/_search?filter_path=_shards,hits.total,hits.hits._id,hits.hits._score",
    "body": {
      "from": 0,
      "size": 10,
      "query": {
        "match": {
          "title": "elasticsearch"
        }
      },
      "track_total_hits": true
    },
    "predict": "hits.hits 几条?_shards.total 是 1 还是 3?每个 shard 内部回了几条(响应里看不到,用公式算)?",
    "expect": "hits.hits 长度 10、hits.total={value:30,relation:eq}、_shards.total=successful=3、failed=0。候选上限是每片 min(10,本地匹配数)，本课上限合计 28；客户端响应不展示候选数组。"
  };
  window.ESEXPERIMENTS["ch16-04-profile"] = {
    "version": 1,
    "id": "ch16-04-profile",
    "title": "实验 4 · profile:true:searches 与 fetch 两段",
    "method": "POST",
    "path": "/tut-l16-qtf/_search?filter_path=_shards,hits.hits._id,profile.shards.id,profile.shards.searches,profile.shards.fetch",
    "body": {
      "profile": true,
      "size": 10,
      "query": {
        "match": {
          "title": "elasticsearch"
        }
      }
    },
    "predict": "3 个 shard 都有 searches(query 段)吗?都有 fetch 段吗?每个 fetch 是加载 10 篇吗?",
    "expect": "3 个参与分片都有 searches 查询/collector 树；仅执行 Fetch 的分片有 fetch。本例各 fetch.breakdown.load_stored_fields_count 合计为 10；next_reader_count 是切换段读者次数，时间也不是文档数。profile 不能测网络传输、协调归并或证明网络包数。"
  };
  window.ESEXPERIMENTS["ch16-05-profile-size1"] = {
    "version": 1,
    "id": "ch16-05-profile-size1",
    "title": "实验 5 · size=1:谁的 fetch 消失了",
    "method": "POST",
    "path": "/tut-l16-qtf/_search?filter_path=_shards,hits.hits._id,profile.shards.id,profile.shards.searches,profile.shards.fetch",
    "body": {
      "profile": true,
      "size": 1,
      "query": {
        "match": {
          "title": "elasticsearch"
        }
      }
    },
    "predict": "全局第 1 名只住在一个 shard 上——另外两个 shard 的 profile 里还会出现 fetch 吗?",
    "expect": "本例 3 个 searches，1 个 fetch，hits 长度 1；另外两片候选出局，不发 Fetch。不要固定最高分所属片或评分小数。若查询超时/失败/加入 suggest 等条件，不能沿用这个数量。"
  };
  window.ESEXPERIMENTS["ch16-17-source-off"] = {
    "version": 1,
    "id": "ch16-17-source-off",
    "title": "B4 · 不返回 _source，仍观察 Fetch",
    "method": "POST",
    "path": "/tut-l16-qtf/_search?filter_path=hits.hits,profile.shards.id,profile.shards.searches,profile.shards.fetch",
    "body": {
      "profile": true,
      "size": 1,
      "_source": false,
      "sort": [
        {
          "n": "asc"
        }
      ]
    },
    "predict": "_source:false 是否等于取消 Fetch？",
    "expect": "返回一条命中且无 _source；仍有 1 个 fetch 和 3 个 searches。Fetch 还有 _id、字段等工作，关闭正文不改变 mapping 的 _source.enabled。"
  };
  window.ESEXPERIMENTS["ch16-18-size-zero"] = {
    "version": 1,
    "id": "ch16-18-size-zero",
    "title": "B5 · size=0：聚合继续，hits 为空",
    "method": "POST",
    "path": "/tut-l16-qtf/_search",
    "body": {
      "profile": true,
      "size": 0,
      "track_total_hits": true,
      "aggs": {
        "n_stats": {
          "stats": {
            "field": "n"
          }
        }
      }
    },
    "predict": "不收 hits 还能算全体文档的聚合吗？",
    "expect": "hits.hits=[]、total.value=30，n_stats.count=30、sum=465、min=1、max=30；本例无 suggest，无 fetch profile。size=0 不等于整条查询无工作。"
  };
  window.ESEXPERIMENTS["ch16-06-deep-fail"] = {
    "version": 1,
    "id": "ch16-06-deep-fail",
    "title": "实验 6 · from=10000&size=10:踩 max_result_window",
    "method": "POST",
    "path": "/tut-l16-qtf/_search",
    "body": {
      "from": 10000,
      "size": 10,
      "query": {
        "match_all": {}
      }
    },
    "predict": "按公式每个 shard 要回几条?这次请求能走到 Fetch 阶段吗?",
    "expect": "HTTP 400；顶层 error.type=search_phase_execution_exception、reason=all shards failed；root_cause / failed_shards.reason 含 illegal_argument_exception 与窗口 10010 > 10000。错误可能按原因分组，failed_shards 数组长度不等于实际失败片数。未进入 Fetch。"
  };
  window.ESEXPERIMENTS["ch16-07-window-edge"] = {
    "version": 1,
    "id": "ch16-07-window-edge",
    "title": "实验 7 · from=9990&size=10:恰好过闸",
    "method": "POST",
    "path": "/tut-l16-qtf/_search?filter_path=hits.total,hits.hits",
    "body": {
      "from": 9990,
      "size": 10,
      "query": {
        "match_all": {}
      }
    },
    "predict": "窗口 9990+10=10000,能过闸吗?只有 30 篇文档,hits 会是几条?",
    "expect": "HTTP 200，窗口等于 10000 可过；total.value=30、hits.hits=[]。本地 collector 容量受 reader.numDocs 限制，不会凭空返回每片 10000 条。空最终页无需 Fetch。"
  };
  window.ESEXPERIMENTS["ch16-08-last-page"] = {
    "version": 1,
    "id": "ch16-08-last-page",
    "title": "实验 8 · from=20&size=10:30 篇里的最后一页",
    "method": "POST",
    "path": "/tut-l16-qtf/_search?filter_path=hits.hits._id,hits.hits._source.n",
    "body": {
      "from": 20,
      "size": 10,
      "query": {
        "match_all": {}
      },
      "sort": [
        {
          "n": "asc"
        }
      ]
    },
    "predict": "会返回哪 10 个 _id?这一页每个 shard 的 Query 窗口是多少条?",
    "expect": "按唯一整数 n 升序返回 _id 21..30；普通窗口为 30，各片实际不足 30。只有选中的 10 条进入 Fetch；sort 候选携带排序值，不能只称 doc/score 元组。"
  };
  window.ESEXPERIMENTS["ch16-19-after-first"] = {
    "version": 1,
    "id": "ch16-19-after-first",
    "title": "B9 · search_after 前页，读取末项 sort",
    "method": "POST",
    "path": "/tut-l16-qtf/_search",
    "body": {
      "size": 5,
      "sort": [
        {
          "n": "asc"
        }
      ],
      "track_total_hits": true
    },
    "predict": "第一批末项的 sort 值是多少？",
    "expect": "_id 1..5，各条 sort 为 [n]，最后为 [5]。本组只读冻结的 30 篇、n 唯一；跨请求有并发变化时要稳定视图需 PIT。"
  };
  window.ESEXPERIMENTS["ch16-20-after-next"] = {
    "version": 1,
    "id": "ch16-20-after-next",
    "title": "B10 · 使用末项 [5] 取下一批",
    "method": "POST",
    "path": "/tut-l16-qtf/_search",
    "body": {
      "from": 0,
      "size": 5,
      "sort": [
        {
          "n": "asc"
        }
      ],
      "search_after": [
        5
      ],
      "track_total_hits": true
    },
    "predict": "不把 from 改成 5，会返回哪批？",
    "expect": "_id 6..10，末项 sort=[10]；普通候选窗口为 size=5，查询仍可能处理很多匹配，不承诺常数成本。继续翻页把整个末项 sort 数组原样传入。"
  };
  window.ESEXPERIMENTS["ch16-22-reset-nrt"] = {
    "version": 1,
    "id": "ch16-22-reset-nrt",
    "title": "C1 · 删除旧 nrt 并刷新",
    "method": "DELETE",
    "path": "/tut-l16-qtf/_doc/nrt?refresh=true",
    "body": null,
    "predict": "重复本组怎样消除旧的可搜版本？",
    "expect": "第一次无旧 nrt 为 404 / result=not_found；重复本组则 deleted / 200。refresh=true 让删除进入搜索视图。只有指定 nrt 被重置，不删基础 30 篇。"
  };
  window.ESEXPERIMENTS["ch16-23-absent"] = {
    "version": 1,
    "id": "ch16-23-absent",
    "title": "C2 · 确认重置后的基线",
    "method": "GET",
    "path": "/tut-l16-qtf/_count?q=_id:nrt&filter_path=count",
    "body": null,
    "predict": "写入前 count 应该是多少？",
    "expect": "count=0；若不是 0，先重做删除刷新，确认没有其他写入或刷新任务。随后按 C3–C7 顺序执行。"
  };
  window.ESEXPERIMENTS["ch16-09-nrt-write"] = {
    "version": 1,
    "id": "ch16-09-nrt-write",
    "title": "实验 9 · 写一篇不 refresh 的文档",
    "method": "PUT",
    "path": "/tut-l16-qtf/_doc/nrt",
    "body": {
      "title": "written but not refreshed",
      "n": 31
    },
    "predict": "本课索引冻结了自动 refresh:写入返回 201 之后,SEARCH 能看到它吗?GET 呢?",
    "expect": "前置重置删除后，首次 created / 201；同次重写是 updated / 200。未要求 refresh；无其他刷新动作时，GET 可见而外部搜索视图仍不含 nrt。重做 C 组需先删除并 refresh，再写入。"
  };
  window.ESEXPERIMENTS["ch16-10-nrt-get"] = {
    "version": 1,
    "id": "ch16-10-nrt-get",
    "title": "实验 10 · 同一篇,GET 立刻读得到",
    "method": "GET",
    "path": "/tut-l16-qtf/_doc/nrt?filter_path=found,_id,_version",
    "predict": "SEARCH(马上做实验 11)搜不到的这篇,GET 能读到手吗?",
    "expect": "found=true、_id=nrt。默认 realtime 的 GET 可读未 external refresh 的写入；具体可走 translog 或内部 searcher，不能从本响应判定存储路径。"
  };
  window.ESEXPERIMENTS["ch16-11-nrt-count"] = {
    "version": 1,
    "id": "ch16-11-nrt-count",
    "title": "实验 11 · 同一篇,SEARCH 数不到",
    "method": "GET",
    "path": "/tut-l16-qtf/_count?q=_id:nrt&filter_path=count",
    "predict": "count 是 0 还是 1?",
    "expect": "在本组删除并刷新→未刷新写入→GET 后，且无并发刷新/恢复等条件下 count=0。刷新卡之后重复本卡会是 1；重新观察不可见阶段必须从本组重置卡开始。"
  };
  window.ESEXPERIMENTS["ch16-12-refresh"] = {
    "version": 1,
    "id": "ch16-12-refresh",
    "title": "实验 12 · 手动 _refresh,回去重数",
    "method": "POST",
    "path": "/tut-l16-qtf/_refresh?filter_path=_shards",
    "predict": "refresh 之后重跑实验 11,count 会变多少?",
    "expect": "本例 _shards.total=successful=3、failed=0。接着运行“刷新后计数”应为 1。这只是本课索引的 refresh，不修改周期刷新设置。"
  };
  window.ESEXPERIMENTS["ch16-21-count-visible"] = {
    "version": 1,
    "id": "ch16-21-count-visible",
    "title": "C7 · 刷新后同条件计数",
    "method": "GET",
    "path": "/tut-l16-qtf/_count?q=_id:nrt&filter_path=count",
    "body": null,
    "predict": "与刷新前的 0 对照什么？",
    "expect": "count=1；现在读者包含 nrt。再次运行 C 组必须从删除刷新和基线卡开始。"
  };
  window.ESEXPERIMENTS["ch16-24-single-setup"] = {
    "version": 1,
    "id": "ch16-24-single-setup",
    "title": "D1 · 创建单分片对照索引",
    "method": "PUT",
    "path": "/tut-l16-single",
    "body": {
      "settings": {
        "index": {
          "mode": "standard",
          "number_of_shards": 1,
          "number_of_replicas": 0,
          "auto_expand_replicas": "false",
          "refresh_interval": "-1",
          "max_result_window": 10000,
          "default_pipeline": "_none",
          "final_pipeline": "_none"
        }
      },
      "mappings": {
        "dynamic": "strict",
        "_source": {
          "enabled": true
        },
        "properties": {
          "title": {
            "type": "text",
            "analyzer": "standard"
          },
          "n": {
            "type": "integer"
          }
        }
      }
    },
    "predict": "一台节点和一个分片是同一条件吗？",
    "expect": "首次 acknowledged=true；1 主片、0 副本、strict mapping，与主实验单节点的 3 分片对照。重复创建 400，先点名清理。"
  };
  window.ESEXPERIMENTS["ch16-25-single-write"] = {
    "version": 1,
    "id": "ch16-25-single-write",
    "title": "D2 · 写两篇并等待刷新",
    "method": "POST",
    "path": "/tut-l16-single/_bulk?refresh=true",
    "body": "{\"index\":{\"_id\":\"1\"}}\n{\"title\":\"single first\",\"n\":1}\n{\"index\":{\"_id\":\"2\"}}\n{\"title\":\"single second\",\"n\":2}\n",
    "predict": "两篇都已 refresh，from=1 会留下哪篇？",
    "expect": "首次 2 项 created / 201、errors=false；同次重复为 updated / 200。索引创建响应和 refresh 成功后再做搜索。"
  };
  window.ESEXPERIMENTS["ch16-26-single-profile"] = {
    "version": 1,
    "id": "ch16-26-single-profile",
    "title": "D3 · 单分片 query-and-fetch 对照",
    "method": "POST",
    "path": "/tut-l16-single/_search",
    "body": {
      "profile": true,
      "from": 1,
      "size": 1,
      "sort": [
        {
          "n": "asc"
        }
      ]
    },
    "predict": "只参与一个分片时还能看见 query 与 fetch 吗？",
    "expect": "_shards.total=successful=1；返回 _id=2、_source.n=2，一个 searches 和一个 fetch。源码确认无 rank / kNN 的普通 QTF 合并执行；profile 本身不证明网络往返数量。"
  };
  window.ESEXPERIMENTS["ch16-13-cleanup"] = {
    "version": 1,
    "id": "ch16-13-cleanup",
    "title": "清理 · 删除 tut-l16-qtf",
    "method": "DELETE",
    "path": "/tut-l16-qtf?ignore_unavailable=true",
    "predict": "冻结的 refresh_interval 需要恢复吗?",
    "expect": "点名删除 tut-l16-qtf 的数据和设置；ignore_unavailable=true 允许重复清理。另一张清理卡删除 tut-l16-single。清理后从 A、B、C、D 顺序重做，不需要恢复集群设置。"
  };
  window.ESEXPERIMENTS["ch16-27-single-cleanup"] = {
    "version": 1,
    "id": "ch16-27-single-cleanup",
    "title": "清理 2 · 删除单分片索引",
    "method": "DELETE",
    "path": "/tut-l16-single?ignore_unavailable=true",
    "body": null,
    "predict": "如何只删除本章对照资源？",
    "expect": "acknowledged=true；仅删除 tut-l16-single 及其设置；允许重复清理。"
  };
  window.ESEXPERIMENTS["ch16-28-removed"] = {
    "version": 1,
    "id": "ch16-28-removed",
    "title": "清理确认 · 主实验索引不存在",
    "method": "HEAD",
    "path": "/tut-l16-qtf",
    "body": null,
    "predict": "清理后为什么没有 JSON body？",
    "expect": "HTTP 404，HEAD 无响应正文。主实验索引已不存在；验收同时检查 tut-l16-single 为 404。重新执行须先创建。"
  };
})();
