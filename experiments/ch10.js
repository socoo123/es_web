/* 第十章：9 步机制动画；一个条件化读取例子，不是 API 响应记录。 */
(function () {
  'use strict';
  var notes = [
    '条件：9.4.0 新建普通索引、1 主 0 副、stored _source、refresh_interval=-1，无其他外部刷新。显式 ID 写入版本 1；Lucene 写侧和 translog 已接收操作，但 EXTERNAL 尚未发布。不能推出所有 segment 都没有它。',
    'RestGetAction 把路径和查询参数装入 GetRequest，realtime 默认 true，再经 client.get 交给动作框架。REST 负责输入与 HTTP 输出，存储读取继续向下。',
    '固定路由表、普通非分区索引：有效键 routing ?? id；按创建版本选 hashToShardId 分支。选一个 shard，再迭代它的可搜索副本，发送 get[s]；这不是请求广播。',
    '引擎按 uid 锁住 VersionMap 的查询；unsafe 时可能先刷新内部视图。命中删除条目直接不存在。未删除且 location 可读时进入 translog；没有可用操作则回退 INTERNAL。',
    '默认 realtime 取得版本 1。初始 location 跟踪关闭，未跟踪时可打开跟踪并必要时刷新 INTERNAL；可用 location 则读 translog reader。响应不能证明命中了哪条路径，也不表示 EXTERNAL 已发布。',
    '同一数据、无外部刷新：SEARCH 的 EXTERNAL 视图仍为空，hits=0；realtime=false 的 GET 也在该视图查 uid，因此可返回 404。普通 reader 路径同样使用 Lucene。',
    '显式外部 refresh 完成，EXTERNAL 发布版本 1。SEARCH 命中；非实时 GET 也返回版本 1。内部刷新与外部发布的区别是本章关键，不是 refresh_interval 的延迟承诺。',
    '再写同一 ID 得版本 2，暂不外部刷新。实时 GET 可读 views=11 的版本 2，非实时 GET 仍成功返回 views=10 的版本 1。近实时的落后不仅表现为 404，也会表现为旧数据。',
    '再显式外部 refresh，发布最新视图后两种 GET 都可读版本 2。这是本例的完整状态；没有证明固定时限、吞吐优劣或跨节点强一致。对应实验 A12–A14 后可自行 _refresh 验证。'
  ];
  var outcomes = ['版本 1 已写入；EXTERNAL 未发布','REST → GetRequest → client.get','routing / id 定 shard；get[s] 定交接','删除 / 可读 location / INTERNAL 回退','实时 found=true；具体路径由状态决定','SEARCH：0 hits；非实时 GET：404','外部 refresh：发布版本 1','实时读版本 2；非实时仍读版本 1','再次发布：两种 GET 都能读版本 2'];
  function box(x,y,w,h,name,sub,hot) {
    return '<g><rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="9" class="'+(hot?'fig-box-hot fp-pop':'fig-box')+'"/><text x="'+(x+w/2)+'" y="'+(y+25)+'" text-anchor="middle" class="fig-key">'+name+'</text><text x="'+(x+w/2)+'" y="'+(y+47)+'" text-anchor="middle" class="fig-sub">'+sub+'</text></g>';
  }
  function stepSvg(i) {
    var marker='ah10-realtime-'+i;
    var s='<svg viewBox="0 0 760 354" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="读取可见性第 '+(i+1)+' 步"><defs><marker id="'+marker+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="fig-arrowhead"/></marker></defs>';
    var names=['GET _doc/1','RestGetAction','TransportGetAction','InternalEngine'];
    var subs=['输入与回调','请求组装','路由与交接','选择读取视图'];
    for(var j=0;j<4;j++) {
      var x=8+j*190;
      s+=box(x,12,172,66,names[j],subs[j],i===j && i>0);
      if(j<3) s+='<line x1="'+(x+176)+'" y1="45" x2="'+(x+186)+'" y2="45" class="fig-arrow" marker-end="url(#'+marker+')"/>';
    }
    s+='<text x="380" y="103" text-anchor="middle" class="fig-sub">实时分支：下方箭头表示条件选择，不是依次读取三个存储</text>';
    s+=box(15,119,220,80,'VersionMap','uid → 版本 / 删除 / 位置',i===3);
    s+=box(270,119,220,80,'translog reader','未删且 location 可读',i===4);
    s+=box(525,119,220,80,'INTERNAL searcher','其余：必要时内部刷新',i===4);
    s+='<line x1="239" y1="158" x2="264" y2="158" class="fig-arrow" marker-end="url(#'+marker+')"/>';
    s+='<path d="M125 203L125 225L635 225L635 203" class="fig-arrow" marker-end="url(#'+marker+')"/>';
    s+='<text x="380" y="220" text-anchor="middle" class="fig-sub">未命中或无可读操作 → 回退；删除条目直接不存在</text>';
    var external=i<6?'无 Doc1':(i<8?'版本 1 · views=10':'版本 2 · views=11');
    s+=box(15,249,730,66,'EXTERNAL · SEARCH / 非实时 GET',external,i===5 || i===6 || i===8);
    s+='<text x="380" y="343" text-anchor="middle" class="fig-key">'+outcomes[i]+'</text></svg>';
    return s;
  }
  window.ESFLOWS=window.ESFLOWS||{};
  window.ESFLOWS['ch10-realtime-get']={version:1,id:'ch10-realtime-get',title:'Realtime GET：读取分支与新旧版本',speed:2200,steps:notes.map(function(note,i){return {svg:stepSvg(i),note:note};})};
  window.ESEXPERIMENTS=window.ESEXPERIMENTS||{};
  window.ESEXPERIMENTS["ch10-00-version"] = {
  "version": 1,
  "id": "ch10-00-version",
  "title": "前提 · 核对 ES 与 Lucene 版本",
  "method": "GET",
  "path": "/",
  "body": null,
  "predict": "本轮预期依据哪个版本？",
  "expect": "核对 version.number=9.4.0、version.lucene_version=10.4.0；不同版本须重新核对。本轮环境未运行真实 API，下面是固定源码预期。"
};
  window.ESEXPERIMENTS["ch10-00-setup"] = {
  "version": 1,
  "id": "ch10-00-setup",
  "title": "A1 · 创建关闭自动 refresh 的索引",
  "method": "PUT",
  "path": "/tut-l10-nrt",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "mode": "standard",
      "mapping.source.mode": "stored"
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "keyword"
        },
        "views": {
          "type": "integer"
        }
      }
    }
  },
  "predict": "关闭自动 refresh 后，哪份读取视图不会定期发布？",
  "expect": "200；检查 acknowledged 与 shards_acknowledged。-1 关闭周期刷新，不禁显式 / 内部刷新。本实验无其他刷新来源；单节点 1 主 0 副，接着等本索引 green。已存在返回 400 resource_already_exists_exception，先做清理。"
};
  window.ESEXPERIMENTS["ch10-00-health"] = {
  "version": 1,
  "id": "ch10-00-health",
  "title": "A2 · 等待本课索引可用",
  "method": "GET",
  "path": "/_cluster/health/tut-l10-nrt?wait_for_status=green&timeout=5s&filter_path=status,timed_out,active_primary_shards,unassigned_shards",
  "body": null,
  "predict": "只看全局集群 green 能否代替本索引等待？",
  "expect": "status=green、timed_out=false、active_primary_shards=1、unassigned_shards=0 再继续。超时不是成功；检查分配后重试。其他索引不参与本请求。"
};
  window.ESEXPERIMENTS["ch10-01-put"] = {
  "version": 1,
  "id": "ch10-01-put",
  "title": "A3 · 写入第一版，不要求 refresh",
  "method": "PUT",
  "path": "/tut-l10-nrt/_doc/1",
  "body": {
    "title": "nrt-get",
    "views": 10
  },
  "predict": "新建空索引第一次写入 _id=1，result 与版本是什么？",
  "expect": "首次 201、created、_version=1；保存响应。写入进入 Lucene 写侧及 translog，VersionMap 的 location 不保证存在。单独重写是 200 updated、版本递增；完整对照须清理重建。"
};
  window.ESEXPERIMENTS["ch10-02-get"] = {
  "version": 1,
  "id": "ch10-02-get",
  "title": "A4 · 默认 realtime GET",
  "method": "GET",
  "path": "/tut-l10-nrt/_doc/1?filter_path=found,_id,_version,_source",
  "body": null,
  "predict": "尚未外部 refresh，GET 能返回第一版吗？",
  "expect": "200、found=true，版本等于 A3，_source.views=10。可能读 translog，也可能必要时刷新内部视图后从 INTERNAL 读取；此响应不能证明具体分支或索引已可搜索。"
};
  window.ESEXPERIMENTS["ch10-03-search-miss"] = {
  "version": 1,
  "id": "ch10-03-search-miss",
  "title": "A5 · SEARCH 对照未发布的视图",
  "method": "POST",
  "path": "/tut-l10-nrt/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "nrt-get"
      }
    }
  },
  "predict": "title 是显式 keyword；这次 term 查询能看到它吗？",
  "expect": "按全新索引、A1–A4 顺序且无其他外部刷新来源，hits.total.value=0。SEARCH 读取 EXTERNAL 快照；若已命中，检查是否复用了索引或有 _refresh / 刷新写入 / 后台操作，再清理重做。"
};
  window.ESEXPERIMENTS["ch10-04-nonrealtime"] = {
  "version": 1,
  "id": "ch10-04-nonrealtime",
  "title": "A6 · 非实时 GET 读取 EXTERNAL",
  "method": "GET",
  "path": "/tut-l10-nrt/_doc/1?realtime=false&filter_path=found,_id",
  "body": null,
  "predict": "与默认 GET 相比，只改 realtime 会得到哪个状态？",
  "expect": "实验前提下 404、found=false；不是缺 handler。普通分片会先 ensureShardSearchActive；一般默认设置下搜索唤醒也可能触发刷新，本实验新索引显式 -1、无待发布来源。"
};
  window.ESEXPERIMENTS["ch10-05-refresh-flag"] = {
  "version": 1,
  "id": "ch10-05-refresh-flag",
  "title": "A7 · 默认 GET 只加 refresh=true",
  "method": "GET",
  "path": "/tut-l10-nrt/_doc/1?refresh=true&filter_path=found,_id",
  "body": null,
  "predict": "普通可提升分片会因为这个参数显式 externalRefresh 吗？",
  "expect": "200、found=true；普通分片的 asyncGet 只在 refresh && !realtime 时显式 externalRefresh。默认 realtime 下该标志不走这条分支，但 realtime 读取本身仍可能内部刷新。"
};
  window.ESEXPERIMENTS["ch10-06-search-still-miss"] = {
  "version": 1,
  "id": "ch10-06-search-still-miss",
  "title": "A8 · 检查 SEARCH 仍未发布",
  "method": "POST",
  "path": "/tut-l10-nrt/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "nrt-get"
      }
    }
  },
  "predict": "A7 成功是否足以推出现在能搜索？",
  "expect": "按本组前提仍为 0；这对照的是 EXTERNAL 可见性，不是 translog 命中证明。若不符，停止比较并检查外部刷新 / 旧数据后重做。"
};
  window.ESEXPERIMENTS["ch10-07-refresh-nonrealtime"] = {
  "version": 1,
  "id": "ch10-07-refresh-nonrealtime",
  "title": "A9 · 非实时 GET 显式刷新所选分片",
  "method": "GET",
  "path": "/tut-l10-nrt/_doc/1?refresh=true&realtime=false&filter_path=found,_id,_version,_source",
  "body": null,
  "predict": "两个参数同时给，普通分片执行什么额外步骤？",
  "expect": "200、found=true、views=10。asyncGet 等所选分片 externalRefresh 完成后读 EXTERNAL；本索引只有一个分片，下一卡 SEARCH 才能用此结果。不能推广为多分片全索引 _refresh。"
};
  window.ESEXPERIMENTS["ch10-08-search-hit"] = {
  "version": 1,
  "id": "ch10-08-search-hit",
  "title": "A10 · SEARCH 对照发布后的视图",
  "method": "POST",
  "path": "/tut-l10-nrt/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "nrt-get"
      }
    }
  },
  "predict": "数据未变，只发布了搜索视图，命中数呢？",
  "expect": "hits.total.value=1。显式 keyword / term 避免分词干扰；A5 / A8 与本卡只比较本组同一份数据。"
};
  window.ESEXPERIMENTS["ch10-09-source-filter"] = {
  "version": 1,
  "id": "ch10-09-source-filter",
  "title": "A11 · 仅过滤本次响应的 _source",
  "method": "GET",
  "path": "/tut-l10-nrt/_doc/1?_source_includes=title&filter_path=found,_source",
  "body": null,
  "predict": "views 会从 mapping 或原始文档删除吗？",
  "expect": "200、found=true，_source 只含 title。SourceFilter 作用于本次输出；下方完整 GET 仍可返回 views，不修改文档或索引配置。"
};
  window.ESEXPERIMENTS["ch10-09-update"] = {
  "version": 1,
  "id": "ch10-09-update",
  "title": "A12 · 更新同一 ID，暂不发布搜索视图",
  "method": "PUT",
  "path": "/tut-l10-nrt/_doc/1",
  "body": {
    "title": "nrt-get",
    "views": 11
  },
  "predict": "已有版本 1 已可搜索，再写入会怎样？",
  "expect": "按顺序首次执行此卡：200、updated、_version=2。保存实际版本；再次点它继续递增。没有 refresh 参数，EXTERNAL 仍保留 A9 发布的 views=10。"
};
  window.ESEXPERIMENTS["ch10-09-get-latest"] = {
  "version": 1,
  "id": "ch10-09-get-latest",
  "title": "A13 · 实时 GET 对照最新写入",
  "method": "GET",
  "path": "/tut-l10-nrt/_doc/1?filter_path=found,_version,_source",
  "body": null,
  "predict": "实时 GET 会返回 views=10 还是 11？",
  "expect": "200、found=true、views=11；_version 与刚才 A12 的写入响应一致。不能只背版本 2，也不能据此断言必从 translog 读。"
};
  window.ESEXPERIMENTS["ch10-09-get-old"] = {
  "version": 1,
  "id": "ch10-09-get-old",
  "title": "A14 · 非实时 GET 可成功返回旧值",
  "method": "GET",
  "path": "/tut-l10-nrt/_doc/1?realtime=false&filter_path=found,_version,_source",
  "body": null,
  "predict": "非实时读是必定 404，还是也可能读到旧版本？",
  "expect": "200、found=true、views=10、_version=1（A9 视图）。缺文档与旧值是两种结果。须保持无外部刷新来源；若已返回新值，重建索引并按 A1–A14 重做。"
};
  window.ESEXPERIMENTS["ch10-09-invalid-preference"] = {
  "version": 1,
  "id": "ch10-09-invalid-preference",
  "title": "A15 · 检查已不支持的 _primary preference",
  "method": "GET",
  "path": "/tut-l10-nrt/_doc/1?preference=_primary",
  "body": null,
  "predict": "9.4.0 的 Preference.parse 有 _primary 吗？",
  "expect": "预期 400 illegal_argument_exception，reason 含 no Preference for [_primary]。该预期错误不改数据；去掉 preference 即可恢复。_replica 也不在本版本枚举中。"
};
  window.ESEXPERIMENTS["ch10-10-routing-setup"] = {
  "version": 1,
  "id": "ch10-10-routing-setup",
  "title": "B1 · 创建普通 5 分片 routing 索引",
  "method": "PUT",
  "path": "/tut-l10-routed",
  "body": {
    "settings": {
      "number_of_shards": 5,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "mode": "standard",
      "mapping.source.mode": "stored"
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "keyword"
        },
        "owner": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "两把不同的有效键一定落到不同分片吗？",
  "expect": "200；确认两个 acknowledged 字段，再做 B2。该索引在 9.4.0 新建、普通非分区、无 routing_path / resharding；取模可能碰撞，因此先用 B4 / B5 核对落点。已存在须先清理。"
};
  window.ESEXPERIMENTS["ch10-10-routing-health"] = {
  "version": 1,
  "id": "ch10-10-routing-health",
  "title": "B2 · 等待 5 个主分片 green",
  "method": "GET",
  "path": "/_cluster/health/tut-l10-routed?wait_for_status=green&timeout=5s&filter_path=status,timed_out,active_primary_shards,unassigned_shards",
  "body": null,
  "predict": "哪些条件满足后才可以比较 routing？",
  "expect": "status=green、timed_out=false、active_primary_shards=5、unassigned_shards=0。只等本课索引；异常时先恢复分片分配。"
};
  window.ESEXPERIMENTS["ch10-11-routing-put"] = {
  "version": 1,
  "id": "ch10-11-routing-put",
  "title": "B3 · 用 user123 写入并刷新写入分片",
  "method": "PUT",
  "path": "/tut-l10-routed/_doc/3?routing=user123&refresh=true",
  "body": {
    "title": "routed-doc",
    "owner": "user123"
  },
  "predict": "有效键是 3 还是 user123？",
  "expect": "有效键为 user123；首次 201 created，重复 200 updated。写入的 refresh=true 发布本次受影响分片，让 B8 的搜索不依赖自动刷新；这与默认 GET 的 refresh 标志不同。"
};
  window.ESEXPERIMENTS["ch10-12-shards-key-id"] = {
  "version": 1,
  "id": "ch10-12-shards-key-id",
  "title": "B4 · 模拟未带 routing 的 GET 落点",
  "method": "GET",
  "path": "/tut-l10-routed/_search_shards?routing=3&filter_path=shards.shard",
  "body": null,
  "predict": "为什么用 routing=3 而不是不带 routing？",
  "expect": "普通非分区索引下，routing=3 模拟 GET 退回 _id=3 的有效键；记下 shard 号。_search_shards 不带 routing 会列出全部分片，不是 GET 实际去处。此卡只列路由候选，不读文档。"
};
  window.ESEXPERIMENTS["ch10-13-shards-key-routing"] = {
  "version": 1,
  "id": "ch10-13-shards-key-routing",
  "title": "B5 · 查写入 routing 的落点",
  "method": "GET",
  "path": "/tut-l10-routed/_search_shards?routing=user123&filter_path=shards.shard",
  "body": null,
  "predict": "它与 B4 的 shard 是否不同？",
  "expect": "比较 B4 / B5 的真实返回，按本组新建索引与固定键应不同。源码哈希计算不是 API 实测；若同片，漏 routing 的 GET 可成功，须查索引创建版本 / 配置，不能把 404 当必然。"
};
  window.ESEXPERIMENTS["ch10-14-get-no-routing"] = {
  "version": 1,
  "id": "ch10-14-get-no-routing",
  "title": "B6 · 未带 routing 的 GET",
  "method": "GET",
  "path": "/tut-l10-routed/_doc/3?filter_path=found,_id",
  "body": null,
  "predict": "B4 / B5 不同片且 B3 成功时，返回什么？",
  "expect": "在上述条件下 404、found=false；GET 只读退回 _id 所选分片，不广播。不存在是正常响应，不会试另一副本来寻找文档；同片碰撞时可能成功。"
};
  window.ESEXPERIMENTS["ch10-15-get-with-routing"] = {
  "version": 1,
  "id": "ch10-15-get-with-routing",
  "title": "B7 · 带写入时相同 routing 的 GET",
  "method": "GET",
  "path": "/tut-l10-routed/_doc/3?routing=user123&filter_path=found,_id,_routing",
  "body": null,
  "predict": "routing 正确时能否读回 _routing？",
  "expect": "200、found=true、_id=3、_routing=user123。routing 除用于选分片，还作为元数据保存并返回；它不只是临时 hash 输入。"
};
  window.ESEXPERIMENTS["ch10-16-search-fanout"] = {
  "version": 1,
  "id": "ch10-16-search-fanout",
  "title": "B8 · 不限 routing 的 SEARCH",
  "method": "GET",
  "path": "/tut-l10-routed/_search?q=_id:3&filter_path=hits.total,hits.hits._id,hits.hits._routing",
  "body": null,
  "predict": "GET 未带 routing 扑空，SEARCH 不带 routing 呢？",
  "expect": "本组只有这一篇数据且 B3 已刷新：1 hit，回显 _id=3 / _routing=user123。普通未限定搜索路由的请求考虑全部 5 个分片；不能用搜索命中推断 GET 去了哪个 shard。"
};
  window.ESEXPERIMENTS["ch10-17-cleanup"] = {
  "version": 1,
  "id": "ch10-17-cleanup",
  "title": "清理 1 · 显式删除 tut-l10-nrt",
  "method": "DELETE",
  "path": "/tut-l10-nrt",
  "body": null,
  "predict": "重做可见性对照前需要恢复什么？",
  "expect": "200 acknowledged=true 后，从版本核对、A1 / A2 重新开始；删除本课第一组索引及其数据。已不存在为 404 index_not_found_exception，可直接创建。只重写旧 ID 无法清除旧 EXTERNAL 视图。"
};
  window.ESEXPERIMENTS["ch10-18-cleanup"] = {
  "version": 1,
  "id": "ch10-18-cleanup",
  "title": "清理 2 · 显式删除 tut-l10-routed",
  "method": "DELETE",
  "path": "/tut-l10-routed",
  "body": null,
  "predict": "删除影响哪些资源，怎样重做？",
  "expect": "200 acknowledged=true，删除本课第二组索引及 routing 元数据；不影响其他索引。已不存在返回 404，可从 B1 / B2 开始。重新创建、等待、写入、核对两把键再读。"
};
})();
