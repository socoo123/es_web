/* experiments/ch15.js — 第 15 课:旗舰动画 #3(路由公式演算)+ 实验 */
(function () {
  'use strict';

  /* ===== 旗舰动画 #3:新建普通非分区索引的 floorMod 演算 ===== */
  var H_BROWN = 998382972;    // murmur3("brown") — UTF-16LE，离线计算并经本章两轮 API 核对
  var SHARD = 0;              // Math.floorMod(H_BROWN, 3)

  var PNAMES = ['① 取 _routing', '② murmur3 哈希', '③ floorMod(h,3)', '④ 查路由表'];
  var PSUBS = ['"brown"', '998382972', 'shard = 0', 'shard 0 的拷贝们'];

  function chip(x, y, w, h, cls, op) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="7" class="' + cls + '"' +
      (op != null ? ' opacity="' + op + '"' : '') + '/>';
  }
  function txt(x, y, cls, t, op) {
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + '"' +
      (op != null ? ' opacity="' + op + '"' : '') + '>' + t + '</text>';
  }

  /* 顶部流水线:lit = 已点亮的格子数(0..4),最新点亮的一格 fp-pop */
  function pipeline(lit, popNewest) {
    var s = '', xs = [15, 205, 395, 585], w = 160;
    for (var i = 0; i < 4; i++) {
      if (i < 3) {
        var aLit = i < lit - 1;
        s += '<line x1="' + (xs[i] + w + 4) + '" y1="48" x2="' + (xs[i + 1] - 6) + '" y2="48" class="fig-arrow"' +
          (aLit ? '' : ' opacity="0.3"') + ' marker-end="url(#ah15rt)"/>';
      }
      var isHot = i === lit - 1;
      s += '<g opacity="' + (i < lit ? 1 : 0.38) + '">';
      s += chip(xs[i], 16, w, 64, isHot ? 'fig-box-hot' + (isHot && popNewest ? ' fp-pop' : '') : 'fig-box');
      s += txt(xs[i] + w / 2, 40, 'fig-name', PNAMES[i]);
      s += txt(xs[i] + w / 2, 60, 'fig-key', PSUBS[i]);
      s += '</g>';
    }
    return s;
  }

  /* 中部演算区:纯文本行 */
  function midText(lines) {
    var ys = [124, 150, 176, 200], s = '';
    for (var i = 0; i < lines.length; i++) {
      s += txt(380, ys[i], lines[i][0], lines[i][1]);
    }
    return s;
  }

  /* 中部演算区:cluster state 路由表小图。mode: healthy | ars | single */
  function table(mode) {
    var compact = mode !== 'healthy';
    var ys = compact ? [126, 160, 194] : [130, 168, 206];
    var rh = compact ? 28 : 34;
    var s = txt(340, 116, 'fig-sub', 'cluster state:IndexRoutingTable["tut-l15-route"]');
    if (mode === 'healthy') {
      s += txt(676, 116, 'fig-sub', 'P=主分片 R=副本');
    }
    for (var r = 0; r < 3; r++) {
      var y = ys[r], cy = y + rh / 2 + 4;
      var hot = r === SHARD;
      s += '<g opacity="' + (hot ? 1 : 0.55) + '">';
      s += chip(45, y, 86, rh, hot ? 'fig-box-hot' + (mode === 'healthy' ? ' fp-pop' : '') : 'fig-box');
      s += txt(88, cy, 'fig-key', 'shard ' + r);
      s += chip(145, y, 170, rh, 'fig-box');
      s += txt(230, cy, 'fig-sub', 'P · node-1');
      if (mode === 'single') {
        s += chip(325, y, 170, rh, 'fig-box', 0.45);
        s += txt(410, cy, 'fig-sub', 'R · UNASSIGNED');
      } else {
        s += chip(325, y, 170, rh, 'fig-box');
        s += txt(410, cy, 'fig-sub', 'R · node-2');
      }
      s += '</g>';
      if (mode === 'ars' && hot) {
        s += txt(600, cy, 'fig-sub', '← 先看请求类型');
      }
    }
    if (mode === 'ars') {
      s += txt(380, 244, 'fig-sub', '搜索可按 ARS 排名;普通 GET 未传排名统计;写入先主后副');
    } else if (mode === 'single') {
      s += txt(380, 244, 'fig-sub', '单节点示例:副本 UNASSIGNED;主分片数设置更新拒绝,原路由不变');
    }
    return s;
  }

  function stepSvg(k) {
    var lit = k === 0 ? 0 : Math.min(k, 4);
    var s = '<svg viewBox="0 0 760 262" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs><marker id="ah15rt" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
      '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
    s += pipeline(lit, k <= 4);
    if (k === 0) {
      s += midText([
        ['fig-name', 'PUT /tut-l15-route/_doc/brown-1?routing=brown'],
        ['fig-key fp-pulse', 'shard = floorMod( murmur3(_routing), 3 )'],
        ['fig-sub', '适用:9.4.0 新建、普通非分区、无 routing_path / resharding'],
        ['fig-sub', '实际逻辑片可以迁移节点;本例不改变索引布局']
      ]);
    } else if (k === 1) {
      s += midText([
        ['fig-key', 'effectiveRouting = routing != null ? routing : id'],
        ['fig-sub', '带了 routing=brown → 用 "brown";不带 → 用 _id'],
        ['fig-sub', 'GET 缺省 routing 用 _id;搜索缺省 routing 查全部片'],
        ['fig-sub', '不同比较键可以同片;身份过滤仍要写查询条件']
      ]);
    } else if (k === 2) {
      s += midText([
        ['fig-key', 'h = murmur3("brown") = 998382972'],
        ['fig-sub', '32 位有符号整数,可能是负——所以下一步不是 %'],
        ['fig-sub', '字符串先按 UTF-16LE 编码,不是 UTF-8 的通用示例'],
        ['fig-sub', '片号还取决于索引创建版本与路由策略']
      ]);
    } else if (k === 3) {
      s += midText([
        ['fig-key', 'shard = Math.floorMod(998382972, 3) = 1'],
        ['fig-sub', '负哈希对照:"tenant-7" 的 h = -1321139497'],
        ['fig-key', 'h % 3 = -1;floorMod(h,3) = 2'],
        ['fig-sub', 'brown-1 的哈希也落 shard 0:忘带钥匙仍可能命中']
      ]);
    } else if (k === 4) {
      s += table('healthy');
    } else if (k === 5) {
      s += table('ars');
    } else {
      s += table('single');
    }
    s += '</svg>';
    return s;
  }

  var NOTES = [
    "限定 9.4.0 新建普通非分区索引、3 主分片，无 routing_path 与 resharding。示例 routing=brown：先定逻辑片，再查节点拷贝。这里只演路由，不演存储写入。",
    "写入 / GET 有 routing 就用它，缺省才用 _id。搜索不带 routing 则选全部片，不按某个 _id 兜底；带 routing 的普通搜索才缩小分片范围。",
    "ES 把 Java 字符串按 UTF-16LE 编码，再用种子 0 的 Murmur3 x86_32。brown 的哈希是 998382972，不能直接套 UTF-8 示例。数字由离线计算、官方向量及本章两轮 API 对照核验。",
    "floorMod(998382972,3)=0。负数 tenant-7 的哈希是 -1321139497，Java %3 得 -1，floorMod 得 2。brown-1 也落 shard0，因此忘带 routing 的 GET 在本例仍命中；跨片反例另用 route-0。",
    "cluster state 路由表把逻辑片换成节点上的拷贝组。这里是两节点概念示例；实验单节点没有已分配副本。节点迁移改变位置，不等于文档的逻辑路由键改变。",
    "普通 GET 未传 ARS 排名输入，保留随机化候选顺序；普通搜索在默认 ARS 开关与排名输入下排序，缺统计不承诺选到最快一份。写入先主后副。不同拷贝读取视图也不能当瞬时完全一致。",
    "单节点、1副本且主分片正常分配时，本索引 yellow；副本改0并等待可 green。Final 更新主片数会拒绝，原路由和文档保持可读。不同布局可按条件 split/shrink 或 reindex；不在这里演这些操作。"
];

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch15-routing-formula'] = {
    version: 1,
    id: 'ch15-routing-formula',
    title: '路由公式演算:从一把钥匙到一片分片',
    speed: 2000,
    steps: NOTES.map(function (note, i) { return { svg: stepSvg(i), note: note }; })
  };

  /* ===== 四组实验；原稳定 ID 保留 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch15-version"] = {
  "version": 1,
  "id": "ch15-version",
  "title": "A0 · 先核对运行版本",
  "method": "GET",
  "path": "/",
  "body": null,
  "predict": "当前服务是否为 ES 9.4.0 / Lucene 10.4.0？",
  "expect": "查看 version.number 和 lucene_version。节点版本不是索引创建版本；本课随后显式新建两索引，无匹配模板。端点默认 localhost:9200、匿名、单数据节点；换端点先确认配置与权限。"
};
  window.ESEXPERIMENTS["ch15-00-setup"] = {
  "version": 1,
  "id": "ch15-00-setup",
  "title": "A1 · 新建 3 主 1 副索引",
  "method": "PUT",
  "path": "/tut-l15-route",
  "body": {
    "settings": {
      "index.mode": "standard",
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "auto_expand_replicas": false,
      "routing_partition_size": 1,
      "refresh_interval": "-1",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "translog.durability": "request",
      "write.wait_for_active_shards": "1"
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "mode": "stored"
      },
      "properties": {
        "body": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "6 份拷贝都能放到同一节点吗？",
  "expect": "首次 acknowledged:true；shards_acknowledged 还受等待超时影响。重复创建 400 resource_already_exists_exception。配置显式 3主1副、standard、非分区、stored source、strict keyword、无管道、自动副本关闭。下一卡等本索引 yellow。"
};
  window.ESEXPERIMENTS["ch15-a-yellow"] = {
  "version": 1,
  "id": "ch15-a-yellow",
  "title": "A2 · 等待三个主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l15-route?wait_for_status=yellow&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "yellow 是否代表主分片不可用？",
  "expect": "单数据节点、默认分配且无写入/拓扑干扰：timed_out:false、status:yellow、active_primary_shards:3、unassigned_shards:3。等待 yellow 意味着至少 yellow；多节点可 green。本卡只观察本课索引，失败先停止后续卡。"
};
  window.ESEXPERIMENTS["ch15-01-shards"] = {
  "version": 1,
  "id": "ch15-01-shards",
  "title": "A3 · CAT 的 state 来自哪套枚举",
  "method": "GET",
  "path": "/_cat/shards/tut-l15-route?v&h=index,shard,prirep,state,docs,store,node",
  "body": null,
  "predict": "会出现 CREATED / RECOVERING 吗？",
  "expect": "本例稳定时 3 个 p STARTED、3 个 r UNASSIGNED；state 是 ShardRoutingState，四态含 RELOCATING，不是 JVM 的 IndexShardState。未分配行无节点与 docs/store；此时没有对应已分配的本地副本对象。"
};
  window.ESEXPERIMENTS["ch15-02-put-routing"] = {
  "version": 1,
  "id": "ch15-02-put-routing",
  "title": "A4 · brown-1 用 brown 路由写入",
  "method": "PUT",
  "path": "/tut-l15-route/_doc/brown-1?routing=brown&refresh=true",
  "body": {
    "body": "brown example"
  },
  "predict": "用 ES 的 UTF-16LE 哈希，brown 会去哪片？",
  "expect": "首次 201 created，重复 200 updated。离线 hash(brown)=998382972，floorMod(...,3)=0；需与 A7 返回核对。默认 active=1 不等未分配副本；本例 _shards.total=2、successful=1、failed=0，未分配副本无本次复制失败。refresh=true 服务后续搜索/docs 观测。"
};
  window.ESEXPERIMENTS["ch15-03-cat-docs"] = {
  "version": 1,
  "id": "ch15-03-cat-docs",
  "title": "A5 · 先记录一篇文档的分片统计",
  "method": "GET",
  "path": "/_cat/shards/tut-l15-route?v&h=shard,prirep,state,docs",
  "body": null,
  "predict": "在第二篇写入前，哪片 docs=1？",
  "expect": "从干净索引按序运行，本例主片0 docs=1、其余0，副本未分配无计数。固定 ID 重复写仍1篇，后续新增第二篇会变2；docs 是 Lucene 文档观测，不能泛化为任意嵌套/删除场景的业务条数。"
};
  window.ESEXPERIMENTS["ch15-04-ss-all"] = {
  "version": 1,
  "id": "ch15-04-ss-all",
  "title": "A6 · 搜索不带 routing 的片范围",
  "method": "GET",
  "path": "/tut-l15-route/_search_shards",
  "body": null,
  "predict": "默认选几组？每组是否包含未分配副本？",
  "expect": "shards 为3个逻辑片组，本例每组只有可选的 primary；UNASSIGNED 副本不进入该候选返回。API 描述候选而不执行查询，不能证明 ARS 排名或网络往返。"
};
  window.ESEXPERIMENTS["ch15-05-ss-routing"] = {
  "version": 1,
  "id": "ch15-05-ss-routing",
  "title": "A7 · 对照 brown 的实际目标片",
  "method": "GET",
  "path": "/tut-l15-route/_search_shards?routing=brown",
  "body": null,
  "predict": "是否与 A4 的离线算式一致？",
  "expect": "预期1组，shard=0。仅适用于本课新建普通非分区索引、无 routing_path / resharding；按实际返回核对。不是旧文案的 shard1。"
};
  window.ESEXPERIMENTS["ch15-a-id-shard"] = {
  "version": 1,
  "id": "ch15-a-id-shard",
  "title": "A8 · 对照 brown-1 的目标片",
  "method": "GET",
  "path": "/tut-l15-route/_search_shards?routing=brown-1",
  "body": null,
  "predict": "不同字符串是否必落不同片？",
  "expect": "离线 hash(brown-1)=-2007555306，floorMod(...,3)=0；与 brown 同片。此请求把 brown-1 当搜索 routing 来看片号，不是在按 _id 查询文档；下一 GET 用它作为缺省 routing 钥匙。"
};
  window.ESEXPERIMENTS["ch15-06-get-miss"] = {
  "version": 1,
  "id": "ch15-06-get-miss",
  "title": "A9 · 同片反例：缺省 routing 仍命中",
  "method": "GET",
  "path": "/tut-l15-route/_doc/brown-1",
  "body": null,
  "predict": "旧实验预期404；真实哈希规则下呢？",
  "expect": "按本课数据，预期200 found:true，_routing 回显 brown。GET 缺省用 _id=brown-1，两键都落片0，片内按 ID 可找到这篇。不同 routing 不是隔离命名空间，不能把缺省必404当通用规律。"
};
  window.ESEXPERIMENTS["ch15-07-get-hit"] = {
  "version": 1,
  "id": "ch15-07-get-hit",
  "title": "A10 · 携带原始 routing 读回",
  "method": "GET",
  "path": "/tut-l15-route/_doc/brown-1?routing=brown",
  "body": null,
  "predict": "响应是否保留原始 routing？",
  "expect": "200 found:true、_routing:brown、_source.body:brown example。GET 选择片0；普通 GET 未传 ARS 排名输入。单节点只有primary可用，不能据此验证多节点复制或选副本。"
};
  window.ESEXPERIMENTS["ch15-a-put-cross"] = {
  "version": 1,
  "id": "ch15-a-put-cross",
  "title": "A11 · 写入确定跨片的 _id",
  "method": "PUT",
  "path": "/tut-l15-route/_doc/route-0?routing=brown&refresh=true",
  "body": {
    "body": "cross shard example"
  },
  "predict": "route-0 的缺省片号也等于0吗？",
  "expect": "首次201 created，重复200 updated；带 brown 仍写片0。离线 hash(route-0)=512605379，floorMod(...,3)=2；刷新后本课两篇均可搜，按序下一卡验证缺省GET。"
};
  window.ESEXPERIMENTS["ch15-a-cross-shard"] = {
  "version": 1,
  "id": "ch15-a-cross-shard",
  "title": "A12 · 对照 route-0 的目标片",
  "method": "GET",
  "path": "/tut-l15-route/_search_shards?routing=route-0",
  "body": null,
  "predict": "它与 brown 是否确实跨片？",
  "expect": "预期1组 shard=2，和 A7 的0不同。先读实际目标号，再解释下一 GET 的404；避免凭“字符串不同”猜分片。"
};
  window.ESEXPERIMENTS["ch15-a-cross-miss"] = {
  "version": 1,
  "id": "ch15-a-cross-miss",
  "title": "A13 · 跨片反例：缺省 GET 查无",
  "method": "GET",
  "path": "/tut-l15-route/_doc/route-0",
  "body": null,
  "predict": "这次缺省GET能否命中？",
  "expect": "预期404 found:false，无业务错误 type：GET 按 route-0 算片2，文档实际在片0。不是文档丢失；下一卡携带 brown 恢复。"
};
  window.ESEXPERIMENTS["ch15-a-cross-hit"] = {
  "version": 1,
  "id": "ch15-a-cross-hit",
  "title": "A14 · 带 brown 恢复读回",
  "method": "GET",
  "path": "/tut-l15-route/_doc/route-0?routing=brown",
  "body": null,
  "predict": "恢复哪一个请求参数？",
  "expect": "200 found:true、_routing:brown、_source.body:cross shard example。routing 影响片号；required 会检查是否缺省，不会替你验证键正确。"
};
  window.ESEXPERIMENTS["ch15-a-search-all"] = {
  "version": 1,
  "id": "ch15-a-search-all",
  "title": "A15 · 无 routing 搜索仍可见两篇",
  "method": "GET",
  "path": "/tut-l15-route/_search?size=10",
  "body": null,
  "predict": "忘带 routing 的普通搜索会漏文档吗？",
  "expect": "预期 hits.total.value=2，_shards.total=3，返回 brown-1 与 route-0。前面显式 refresh 排除周期竞态；无 routing 查全部片，所以仍可见。结果不隔离租户，权限与查询过滤另行处理。"
};
  window.ESEXPERIMENTS["ch15-a-search-wrong"] = {
  "version": 1,
  "id": "ch15-a-search-wrong",
  "title": "A16 · routing=route-0 缩到无文档的片",
  "method": "GET",
  "path": "/tut-l15-route/_search?routing=route-0&size=10",
  "body": null,
  "predict": "搜索会回404，还是成功但无命中？",
  "expect": "200、hits.total.value=0、_shards.total=1；目标片2没有本课文档。带 routing 只缩小搜索范围，不是 term过滤；错误键若同片则仍可命中。此时回上一无routing卡仍两篇。"
};
  window.ESEXPERIMENTS["ch15-08-replicas-0"] = {
  "version": 1,
  "id": "ch15-08-replicas-0",
  "title": "B1 · 副本数动态改为0",
  "method": "PUT",
  "path": "/tut-l15-route/_settings",
  "body": {
    "number_of_replicas": 0
  },
  "predict": "主分片号与既有文档会变化吗？",
  "expect": "acknowledged:true；副本期望数改0，主片布局不变。分配/健康收敛异步，下一卡等待本索引green。其他索引可能仍使全局yellow。"
};
  window.ESEXPERIMENTS["ch15-09-health-green"] = {
  "version": 1,
  "id": "ch15-09-health-green",
  "title": "B2 · 等待本索引 green",
  "method": "GET",
  "path": "/_cluster/health/tut-l15-route?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "未分配副本还剩多少？",
  "expect": "timed_out:false、status:green、active_primary_shards:3、unassigned_shards:0。本例只要求三份primary；green不是磁盘耐久或备份证明。"
};
  window.ESEXPERIMENTS["ch15-10-segments"] = {
  "version": 1,
  "id": "ch15-10-segments",
  "title": "B3 · 按分片观察 Lucene 段",
  "method": "GET",
  "path": "/_cat/segments/tut-l15-route?v&h=index,shard,prirep,segment,generation,size",
  "body": null,
  "predict": "段列表是否按逻辑片和拷贝标识？",
  "expect": "已写入并刷新的片0有可搜索段；片1/2没有业务文档。记录实际段名/数量，自动落段与merge可改变列表，不承诺固定_0或一段。各拷贝独立管理Lucene文件，副本段布局也不必逐字节相同。"
};
  window.ESEXPERIMENTS["ch15-11-final-wall"] = {
  "version": 1,
  "id": "ch15-11-final-wall",
  "title": "B4 · 更新主片数被 Final 拒绝",
  "method": "PUT",
  "path": "/tut-l15-route/_settings",
  "body": {
    "index.number_of_shards": 5
  },
  "predict": "请求失败会让存量路由改变吗？",
  "expect": "预期400 illegal_argument_exception，reason含 non dynamic setting(s) [[index.number_of_shards]]，并说明创建后不能修改。更新被拒，原值3、原路由保持不变；不同布局可按条件split/shrink或reindex到目标索引，不能说只可reindex。",
  "allowInvalidBody": true
};
  window.ESEXPERIMENTS["ch15-b-settings"] = {
  "version": 1,
  "id": "ch15-b-settings",
  "title": "B5 · 检查拒绝后的索引设置",
  "method": "GET",
  "path": "/tut-l15-route/_settings?flat_settings=true",
  "body": null,
  "predict": "number_of_shards 是否真的变成5？",
  "expect": "index.number_of_shards仍3、number_of_replicas为0；检查创建版本、mode、routing_partition_size、refresh_interval=-1与auto_expand=false。本例不配置routing_path；节点版本不替代创建版本判断。"
};
  window.ESEXPERIMENTS["ch15-b-after-final"] = {
  "version": 1,
  "id": "ch15-b-after-final",
  "title": "B6 · Final 拒绝后原 GET 仍命中",
  "method": "GET",
  "path": "/tut-l15-route/_doc/route-0?routing=brown",
  "body": null,
  "predict": "旧文档是否“就地蒸发”？",
  "expect": "200 found:true，原文档与路由不变。假设直接换取模布局可能需要搬迁部分数据，不意味着所有键都会改片，更不意味着被拒请求实际做了搬迁。"
};
  window.ESEXPERIMENTS["ch15-b-replicas-one"] = {
  "version": 1,
  "id": "ch15-b-replicas-one",
  "title": "B7 · 副本期望数恢复1",
  "method": "PUT",
  "path": "/tut-l15-route/_settings",
  "body": {
    "number_of_replicas": 1
  },
  "predict": "同一份副本可和primary放同一节点吗？",
  "expect": "acknowledged:true；单节点无法满足同片主副放不同节点的要求。下一卡限定本索引检查；本课不增节点、不验证真实复制。"
};
  window.ESEXPERIMENTS["ch15-b-yellow-again"] = {
  "version": 1,
  "id": "ch15-b-yellow-again",
  "title": "B8 · 等待副本变为未分配",
  "method": "GET",
  "path": "/_cluster/health/tut-l15-route?wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "主片仍正常时状态是哪一种？",
  "expect": "本例稳定时yellow、3主片active、3副本unassigned。需核对状态与计数，单靠wait_for_status=yellow不会排除green；若设置尚未收敛重复本卡。不删primary文档，A10/A14仍可读。"
};
  window.ESEXPERIMENTS["ch15-12-req-create"] = {
  "version": 1,
  "id": "ch15-12-req-create",
  "title": "C1 · 显式创建 routing.required 索引",
  "method": "PUT",
  "path": "/tut-l15-req",
  "body": {
    "settings": {
      "index.mode": "standard",
      "number_of_shards": 3,
      "number_of_replicas": 0,
      "auto_expand_replicas": false,
      "routing_partition_size": 1,
      "refresh_interval": "-1",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "translog.durability": "request",
      "write.wait_for_active_shards": "1"
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "mode": "stored"
      },
      "_routing": {
        "required": true
      },
      "properties": {
        "title": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "required 是否能验证键的内容？",
  "expect": "首次acknowledged:true；重复创建400资源已存在。显式3主0副、standard非分区、strict keyword、stored source、无管道，required只校验缺失。先等下一卡green。"
};
  window.ESEXPERIMENTS["ch15-c-health"] = {
  "version": 1,
  "id": "ch15-c-health",
  "title": "C2 · 等待 required 索引就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l15-req?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "route索引yellow会影响这个green等待吗？",
  "expect": "本索引timed_out:false、green、3主片active、0未分配；请求限定tut-l15-req，不是全局健康。"
};
  window.ESEXPERIMENTS["ch15-13-req-missing"] = {
  "version": 1,
  "id": "ch15-13-req-missing",
  "title": "C3 · 缺省 routing 的写入被拒",
  "method": "PUT",
  "path": "/tut-l15-req/_doc/1",
  "body": {
    "title": "no routing here"
  },
  "predict": "会生成一个按_id路由的文档吗？",
  "expect": "预期400 routing_missing_exception，reason含routing is required for [tut-l15-req]/[1]；缺失检查先于选目标片，不写这篇。下一卡用显式routing成功恢复；required不保证错误键被拒。",
  "allowInvalidBody": true
};
  window.ESEXPERIMENTS["ch15-c-put"] = {
  "version": 1,
  "id": "ch15-c-put",
  "title": "C4 · 带 brown 写入required索引",
  "method": "PUT",
  "path": "/tut-l15-req/_doc/1?routing=brown&refresh=true",
  "body": {
    "title": "routing required"
  },
  "predict": "加参数后是否恢复成功？",
  "expect": "首次201 created，重复200 updated；路由片0、stored source保留title、_routing保存brown。显式refresh用于C7搜索。"
};
  window.ESEXPERIMENTS["ch15-c-get-missing"] = {
  "version": 1,
  "id": "ch15-c-get-missing",
  "title": "C5 · 缺省 routing 的 GET 也被拒",
  "method": "GET",
  "path": "/tut-l15-req/_doc/1",
  "body": null,
  "predict": "required只约束写入吗？",
  "expect": "预期400 routing_missing_exception，不是404 found:false。IndexRouting.getShard调用checkRoutingRequired；补routing=brown恢复。",
  "allowInvalidBody": true
};
  window.ESEXPERIMENTS["ch15-c-get-hit"] = {
  "version": 1,
  "id": "ch15-c-get-hit",
  "title": "C6 · 带正确键GET",
  "method": "GET",
  "path": "/tut-l15-req/_doc/1?routing=brown",
  "body": null,
  "predict": "读取的routing元数据为何值？",
  "expect": "200 found:true、_routing:brown、title:routing required。required检查键存在，仍须业务保存并使用正确键。"
};
  window.ESEXPERIMENTS["ch15-c-search-all"] = {
  "version": 1,
  "id": "ch15-c-search-all",
  "title": "C7 · required不禁止无routing搜索",
  "method": "GET",
  "path": "/tut-l15-req/_search?size=10",
  "body": null,
  "predict": "是否返回400 routing_missing_exception？",
  "expect": "本例200、hits.total.value=1、_shards.total=3；普通搜索不带routing选择全部片，不调用文档GET那条缺失检查。required不是数据访问权限或租户过滤。"
};
  window.ESEXPERIMENTS["ch15-d-close"] = {
  "version": 1,
  "id": "ch15-d-close",
  "title": "D1 · 关闭 required 索引",
  "method": "POST",
  "path": "/tut-l15-req/_close",
  "body": null,
  "predict": "close是否等同删除？",
  "expect": "预期acknowledged:true，并读取实际shards_acknowledged/indices字段；关闭保留索引元数据与磁盘数据。等响应完成再D2；tut-l15-route不受本卡影响。"
};
  window.ESEXPERIMENTS["ch15-d-closed-get"] = {
  "version": 1,
  "id": "ch15-d-closed-get",
  "title": "D2 · 已关闭索引的GET在解析层被拒",
  "method": "GET",
  "path": "/tut-l15-req/_doc/1?routing=brown",
  "body": null,
  "predict": "此处400能否证明本地readAllowed执行了？",
  "expect": "实测400 index_closed_exception，reason=closed。请求选项禁止closed，索引解析先于索引级block检查；这个GET未到本地readAllowed。关闭block本身映射403，不能代替本例返回。带routing排除缺失参数错误。",
  "allowInvalidBody": true
};
  window.ESEXPERIMENTS["ch15-d-open"] = {
  "version": 1,
  "id": "ch15-d-open",
  "title": "D3 · 重新打开索引",
  "method": "POST",
  "path": "/tut-l15-req/_open",
  "body": null,
  "predict": "会生成一份新业务文档吗？",
  "expect": "预期acknowledged:true；shards_acknowledged受分片启动等待影响。重新打开触发分片恢复，下一卡等green；不是把原CLOSED对象直接重置CREATED。"
};
  window.ESEXPERIMENTS["ch15-d-open-health"] = {
  "version": 1,
  "id": "ch15-d-open-health",
  "title": "D4 · 等待重新打开的主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l15-req?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "能用CAT状态看到每个JVM中间态吗？",
  "expect": "timed_out:false、green、3主片active。此为集群健康观测，不代表捕获了CREATED→RECOVERING→POST_RECOVERY；状态门与Engine打开时机由固定源码核对。"
};
  window.ESEXPERIMENTS["ch15-d-open-get"] = {
  "version": 1,
  "id": "ch15-d-open-get",
  "title": "D5 · 重开后读回原数据",
  "method": "GET",
  "path": "/tut-l15-req/_doc/1?routing=brown",
  "body": null,
  "predict": "关闭前的title还在吗？",
  "expect": "200 found:true、_routing:brown、title:routing required。close/open保留数据，重做若中途停在closed，先open与健康等待；干净实验则最后点名DELETE两索引后从A0重做。"
};
  window.ESEXPERIMENTS["ch15-d-recovery"] = {
  "version": 1,
  "id": "ch15-d-recovery",
  "title": "D6 · 查看恢复类型而非JVM状态",
  "method": "GET",
  "path": "/tut-l15-req/_recovery?active_only=false&detailed=true",
  "body": null,
  "predict": "这个返回的type/stage等于IndexShardState吗？",
  "expect": "记录每片type与stage；本地重开通常EXISTING_STORE / DONE，空初建通常EMPTY_STORE。实际来源看返回，不能用此API验证多节点peer复制，也不是CAT四态或IndexShardState五态。"
};
  window.ESEXPERIMENTS["ch15-14-cleanup-route"] = {
  "version": 1,
  "id": "ch15-14-cleanup-route",
  "title": "清理1 · 点名删除 tut-l15-route",
  "method": "DELETE",
  "path": "/tut-l15-route?ignore_unavailable=true",
  "body": null,
  "predict": "会删除其他章节资源吗？",
  "expect": "只点名删本课route索引及其数据/设置；通常acknowledged:true。ignore_unavailable允许重复清理；不使用通配删除。再清理req，然后A0起按序完整重做。"
};
  window.ESEXPERIMENTS["ch15-15-cleanup-req"] = {
  "version": 1,
  "id": "ch15-15-cleanup-req",
  "title": "清理2 · 点名删除 tut-l15-req",
  "method": "DELETE",
  "path": "/tut-l15-req?ignore_unavailable=true",
  "body": null,
  "predict": "索引仍关闭时可否删除其数据？",
  "expect": "点名删本课req索引及文档、mapping/设置，通常acknowledged:true；重复清理允许缺省资源。确认愿意丢弃本课数据后执行，两张清理完成再A0→D6重做，避免旧数据/旧视图混入。"
};
})();
