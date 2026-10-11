/* 第 11 课：固定版本源码预期；真实 API 验证见本章验收记录。 */
(function () {
  'use strict';
  var fields = [
    ['title', 'Elasticsearch Guide', 'text + keyword', 1],
    ['price', '29.99', 'float', 2],
    ['in_stock', 'true', 'boolean', 2],
    ['publish_date', '2024-01-15', 'date', 3],
    ['tags', 'search / database', 'text + keyword', 4],
    ['author', '普通对象', 'object', 4],
    ['author.name', 'John Doe', 'text + keyword', 4],
    ['author.age', '35', 'long', 4]
  ];
  var notes = [
    '普通 standard 索引、stored source、dynamic:true、无模板。主分片用当前 mapping 解析输入：已有 mapper 按声明走；未知值才进入动态推断。此播放器是源码机制例子，非 API 采样。',
    'title 是未知字符串。numeric_detection=false，且不匹配动态日期；无模板覆盖、父对象不含维度，兜底 text + keyword，子字段 ignore_above=256。主值不会在 source 内复制成子字段。',
    'price 的 JSON 浮点走普通 concrete 策略得到 float；in_stock 得到 boolean。已有数字字段的 coercion 与未知字符串的 numeric_detection 分开判断。',
    'publish_date 的非纯数字字符串匹配动态日期格式，得到 date。JSON null 通常不创建未知 mapper；空数组也不能凭空决定元素类型。本例不在 strict 模式。',
    'tags 使用元素类型，得到 text+keyword；author 按 object 展开两个叶子。不是 nested，数组对象的配对关系不保留。符合版本 / 尺寸等条件的 float 数组还可自动成为 dense_vector。',
    'DocumentParser.createDynamicUpdate 生成候选并放入 ParsedDocument；IndexShard 发现 update 非空，返回 MAPPING_UPDATE_REQUIRED，此时尚未提交本次 Engine 写入。',
    '主分片预检，向主节点请求 mapping 更新；主节点合并并写索引元数据，主分片等待版本变化后重解析。没有新增更新才继续 Engine；失败或等待超时另行返回，mapping 更新不是文档事务回滚。',
    '随后写 price:"29.99"：已有 float mapper 且 coerce=true，可以解析成功；price 类型不变，stored source 仍保留原字符串。不是 JSON token 一变就必须 400。',
    '写 price:"not-a-number"：coerce 也无法解析，ignore_malformed 未开启，本篇被拒。已有 mapping 和已写文档保持；PUT _mapping 改 float 的类型则是另一种 merge 冲突。'
  ];
  function text(x,y,cls,value) { return '<text x="'+x+'" y="'+y+'" text-anchor="middle" class="'+cls+'">'+value+'</text>'; }
  function box(x,y,w,h,hot) {return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="9" class="'+(hot?'fig-box-hot fp-pop':'fig-box')+'"/>';}
  function snapshot(step) {
    var marker='ch11-dynamic-arrow-'+step;
    var s='<svg viewBox="0 0 760 442" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="动态映射机制步骤 '+(step+1)+'">';
    s+='<defs><marker id="'+marker+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
    var stages=[['解析当前 mapping','已有 / 未知 mapper'],['本地更新候选','尚未提交 Engine'],['发布后重解析','无更新才继续写入']];
    for(var j=0;j<3;j++) {
      var x=10+j*250;s+=box(x,10,240,60,(step<5?j===0:step===5?j===1:j===2));
      s+=text(x+120,34,'fig-name',stages[j][0])+text(x+120,55,'fig-sub',stages[j][1]);
      if(j<2)s+='<line x1="'+(x+240)+'" y1="40" x2="'+(x+248)+'" y2="40" class="fig-arrow" marker-end="url(#'+marker+')"/>';
    }
    for(var i=0;i<fields.length;i++) {
      var f=fields[i],x=10+(i%2)*380,y=84+Math.floor(i/2)*67;
      s+=box(x,y,360,59,step===f[3]||(step>=7&&f[0]==='price'));
      s+=text(x+180,y+20,'fig-key',f[0]+' · '+(step>=7&&f[0]==='price'?(step===7?'字符串 29.99':'not-a-number'):f[1]));
      s+=text(x+180,y+43,'fig-name',step>=f[3]?f[2]:'待推断');
    }
    var state=step<5?'当前持久 mapping 仍未收到本次候选':step===5?'候选已生成；不是集群状态更新':step===6?'主节点更新 → 等待应用 → 重试写入':step===7?'数值 coercion 成功；mapping 保持 float':'数值解析失败；当前文档未写入';
    s+=box(10,363,740,66,step>=5)+text(380,389,'fig-name',state);
    s+=text(380,413,'fig-sub',step===7?'stored _source 保留字符串；API 预期 201 / created':step===8?'API 预期 400；此前映射与文档仍在':'有限快照示意；refresh 与搜索可见性另判');
    return s+'</svg>';
  }
  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch11-dynamic-mapping'] = {version:1,id:'ch11-dynamic-mapping',title:'动态映射：候选、发布、重解析与数值 coercion',speed:2200,steps:notes.map(function(note,i){return {svg:snapshot(i),note:note};})};

  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch11-00-version'] = {
  "version": 1,
  "id": "ch11-00-version",
  "title": "A0 · 核对实际节点版本",
  "method": "GET",
  "path": "/",
  "body": null,
  "predict": "返回的版本是否与本课 ES 9.4.0 / Lucene 10.4.0 相符？",
  "expect": "读取 version.number / lucene_version；其他版本先停止并核对差异。此卡只读；不把 build_hash 当成索引创建版本。"
};
  window.ESEXPERIMENTS['ch11-00-setup'] = {
  "version": 1,
  "id": "ch11-00-setup",
  "title": "A1 · 显式建立动态推断索引",
  "method": "PUT",
  "path": "/tut-l11-inferred",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "index.mapping.total_fields.limit": 1000,
      "index.mapping.total_fields.ignore_dynamic_beyond_limit": false,
      "index.mapping.coerce": true,
      "index.mapping.ignore_malformed": false
    },
    "mappings": {
      "dynamic": true,
      "date_detection": true,
      "numeric_detection": false,
      "dynamic_templates": [],
      "properties": {}
    }
  },
  "predict": "先确认资源不存在；这一份 mapping 放开了哪些未知字段？",
  "expect": "首次 200 acknowledged=true；shards_acknowledged 需结合健康等待。重复创建为 400 resource_already_exists_exception；先点名清理，再从创建重做。"
};
  window.ESEXPERIMENTS['ch11-00-health'] = {
  "version": 1,
  "id": "ch11-00-health",
  "title": "A2 · 等待本课主分片",
  "method": "GET",
  "path": "/_cluster/health/tut-l11-inferred?wait_for_status=green&timeout=5s",
  "body": null,
  "predict": "副本为 0，分片已分配了吗？",
  "expect": "timed_out=false、status=green、active_primary_shards=1；否则先修复分片分配再继续。不要求其他索引或全集群 green。"
};
  window.ESEXPERIMENTS['ch11-01-infer-put'] = {
  "version": 1,
  "id": "ch11-01-infer-put",
  "title": "A3 · 写入未知字段并显式刷新",
  "method": "PUT",
  "path": "/tut-l11-inferred/_doc/1?refresh=true",
  "body": {
    "title": "Elasticsearch Guide",
    "price": 29.99,
    "in_stock": true,
    "publish_date": "2024-01-15",
    "tags": [
      "search",
      "database"
    ],
    "author": {
      "name": "John Doe",
      "age": 35
    }
  },
  "predict": "title、price、日期串、tags 和对象分别产生哪类 mapper？",
  "expect": "首次 201 result=created；重复同 ID 为 200 updated、版本增加。refresh=true 让随后 B 组搜索可见；不能从响应推断动态更新次数。"
};
  window.ESEXPERIMENTS['ch11-02-infer-mapping'] = {
  "version": 1,
  "id": "ch11-02-infer-mapping",
  "title": "A4 · 读回类型，比较原值与字段结构",
  "method": "GET",
  "path": "/tut-l11-inferred/_mapping",
  "body": null,
  "predict": "数组是否独占一种类型？keyword 子字段是否出现在 _source？",
  "expect": "title / tags / author.name 为 text+fields.keyword(ignore_above=256)；price=float、in_stock=boolean、publish_date=date、author.age=long；author 下有 properties。未显式的 object.type 可能省略。"
};
  window.ESEXPERIMENTS['ch11-03-detection-put'] = {
  "version": 1,
  "id": "ch11-03-detection-put",
  "title": "A5 · 字符串与 JSON 数字分开推断",
  "method": "PUT",
  "path": "/tut-l11-inferred/_doc/2",
  "body": {
    "sku": "42",
    "qty": 42
  },
  "predict": "numeric_detection=false 是否也禁止 JSON 数字被识别？",
  "expect": "首次 201 created，重复 200 updated；sku 字符串与 qty 数字走不同 token。不需要搜索，这一步不加 refresh。"
};
  window.ESEXPERIMENTS['ch11-04-detection-mapping'] = {
  "version": 1,
  "id": "ch11-04-detection-mapping",
  "title": "A6 · 读回 sku / qty",
  "method": "GET",
  "path": "/tut-l11-inferred/_mapping?filter_path=**.sku,**.qty",
  "body": null,
  "predict": "带引号的 42 和不带引号的 42 是同一类型吗？",
  "expect": "sku=text+keyword，qty=long。此实验显式复现 numeric_detection 默认 false；它仅控制未知字符串的数值推断。"
};
  window.ESEXPERIMENTS['ch11-04-coerce-put'] = {
  "version": 1,
  "id": "ch11-04-coerce-put",
  "title": "A7 · 已有 float 接受数值字符串",
  "method": "PUT",
  "path": "/tut-l11-inferred/_doc/3",
  "body": {
    "price": "29.99"
  },
  "predict": "price 已是 float，数值字符串是否必然冲突？",
  "expect": "首次 201 created，重复 200 updated；本索引 coerce=true，数值 mapper 可解析该字符串，price 仍是 float。未知字符串推断与已有数值字段 coercion 是两件事。"
};
  window.ESEXPERIMENTS['ch11-04-coerce-get'] = {
  "version": 1,
  "id": "ch11-04-coerce-get",
  "title": "A8 · 原始字符串仍在 stored _source",
  "method": "GET",
  "path": "/tut-l11-inferred/_doc/3",
  "body": null,
  "predict": "索引侧解析成数值后，_source 的引号会消失吗？",
  "expect": "200 found=true，_source.price 仍为字符串 \"29.99\"。本例 stored source 保留原输入；不是说 float 字段存成了 keyword，也不能据 GET 判断搜索结构。"
};
  window.ESEXPERIMENTS['ch11-04-invalid-number'] = {
  "version": 1,
  "id": "ch11-04-invalid-number",
  "title": "A9 · 无法解析的数值才失败",
  "method": "PUT",
  "path": "/tut-l11-inferred/_doc/4",
  "body": {
    "price": "not-a-number"
  },
  "predict": "coerce=true 能否接受任意字符串？",
  "expect": "400，reason 链含 failed to parse field [price] of type [float]。ignore_malformed 未启用，本篇被拒；原 price mapping 不改。此请求可重复，修正值后重发或直接清理。"
};
  window.ESEXPERIMENTS['ch11-05-analyze-text'] = {
  "version": 1,
  "id": "ch11-05-analyze-text",
  "title": "B1 · 查看 title 的分析结果",
  "method": "POST",
  "path": "/tut-l11-inferred/_analyze",
  "body": {
    "field": "title",
    "text": "Elasticsearch Guide"
  },
  "predict": "同一输入会产生几个 token？",
  "expect": "标准分析器产生 elasticsearch、guide。_analyze 只处理本次输入，不查询已有文档，也不写入索引；本例无自定义分析器 / search_analyzer。"
};
  window.ESEXPERIMENTS['ch11-06-analyze-keyword'] = {
  "version": 1,
  "id": "ch11-06-analyze-keyword",
  "title": "B2 · 查看 keyword 的单个词项",
  "method": "POST",
  "path": "/tut-l11-inferred/_analyze",
  "body": {
    "field": "title.keyword",
    "text": "Elasticsearch Guide"
  },
  "predict": "没有 normalizer 时大小写和空格怎样保留？",
  "expect": "一个 token：Elasticsearch Guide；本例 keyword 无 normalizer。显式 normalizer 会改变规范化行为，不能泛化为所有 keyword 原样保存。"
};
  window.ESEXPERIMENTS['ch11-07-term-miss'] = {
  "version": 1,
  "id": "ch11-07-term-miss",
  "title": "B3 · term 的大小写未对上",
  "method": "POST",
  "path": "/tut-l11-inferred/_search",
  "body": {
    "query": {
      "term": {
        "title": "Elasticsearch"
      }
    },
    "track_total_hits": true
  },
  "predict": "title 词典里保存的是大写还是小写？",
  "expect": "hits.total.value=0；不是因为 term 不能查 text，而是本次词项 Elasticsearch 与 elasticsearch 不同。"
};
  window.ESEXPERIMENTS['ch11-08-match-hit'] = {
  "version": 1,
  "id": "ch11-08-match-hit",
  "title": "B4 · match 分析后命中",
  "method": "POST",
  "path": "/tut-l11-inferred/_search",
  "body": {
    "query": {
      "match": {
        "title": "Elasticsearch"
      }
    },
    "track_total_hits": true
  },
  "predict": "查询侧 standard 产生哪个词项？",
  "expect": "hits.total.value=1，命中 _id=1。这里字段默认 search_analyzer 与写入分析相符；请求指定 analyzer 或字段另配 search_analyzer 时需另判。"
};
  window.ESEXPERIMENTS['ch11-09-term-keyword'] = {
  "version": 1,
  "id": "ch11-09-term-keyword",
  "title": "B5 · 整串 term 命中 keyword",
  "method": "POST",
  "path": "/tut-l11-inferred/_search",
  "body": {
    "query": {
      "term": {
        "title.keyword": "Elasticsearch Guide"
      }
    },
    "track_total_hits": true
  },
  "predict": "只给 Elasticsearch 能命中这份完整词项吗？",
  "expect": "完整串命中 _id=1，hits.total.value=1；本例无 normalizer、未超过 ignore_above。term 匹配倒排词项，聚合 / 排序才主要使用 doc_values。"
};
  window.ESEXPERIMENTS['ch11-09-term-text-hit'] = {
  "version": 1,
  "id": "ch11-09-term-text-hit",
  "title": "B6 · 小写 term 也能查询 text",
  "method": "POST",
  "path": "/tut-l11-inferred/_search",
  "body": {
    "query": {
      "term": {
        "title": "elasticsearch"
      }
    },
    "track_total_hits": true
  },
  "predict": "term 不能查 text 的说法是否成立？",
  "expect": "hits.total.value=1，_id=1；准确词项可以命中。term 不跑全文切词链，调用字段类型提供的词项转换；不能推出查询原串必命中。"
};
  window.ESEXPERIMENTS['ch11-09-match-keyword'] = {
  "version": 1,
  "id": "ch11-09-match-keyword",
  "title": "B7 · match 也能查询 keyword",
  "method": "POST",
  "path": "/tut-l11-inferred/_search",
  "body": {
    "query": {
      "match": {
        "title.keyword": "Elasticsearch Guide"
      }
    },
    "track_total_hits": true
  },
  "predict": "match 是否只能用于 text？",
  "expect": "hits.total.value=1，_id=1。本例 keyword analyzer 可走单词项快捷路径；match 不会自动把 keyword 拆成全文词项。"
};
  window.ESEXPERIMENTS['ch11-10-strict-create'] = {
  "version": 1,
  "id": "ch11-10-strict-create",
  "title": "C1 · 建立 strict 索引",
  "method": "PUT",
  "path": "/tut-l11-strict",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "index.mapping.total_fields.limit": 1000,
      "index.mapping.total_fields.ignore_dynamic_beyond_limit": false,
      "index.mapping.coerce": true,
      "index.mapping.ignore_malformed": false
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "text"
        }
      }
    }
  },
  "predict": "先确认资源不存在；这一份 mapping 放开了哪些未知字段？",
  "expect": "首次 200 acknowledged=true；shards_acknowledged 需结合健康等待。重复创建为 400 resource_already_exists_exception；先点名清理，再从创建重做。"
};
  window.ESEXPERIMENTS['ch11-12-false-create'] = {
  "version": 1,
  "id": "ch11-12-false-create",
  "title": "C2 · 建立 false 索引",
  "method": "PUT",
  "path": "/tut-l11-false",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "index.mapping.total_fields.limit": 1000,
      "index.mapping.total_fields.ignore_dynamic_beyond_limit": false,
      "index.mapping.coerce": true,
      "index.mapping.ignore_malformed": false
    },
    "mappings": {
      "dynamic": false,
      "properties": {
        "title": {
          "type": "text"
        }
      }
    }
  },
  "predict": "先确认资源不存在；这一份 mapping 放开了哪些未知字段？",
  "expect": "首次 200 acknowledged=true；shards_acknowledged 需结合健康等待。重复创建为 400 resource_already_exists_exception；先点名清理，再从创建重做。"
};
  window.ESEXPERIMENTS['ch11-12-runtime-create'] = {
  "version": 1,
  "id": "ch11-12-runtime-create",
  "title": "C3 · 建立 runtime 索引",
  "method": "PUT",
  "path": "/tut-l11-runtime",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "index.mapping.total_fields.limit": 1000,
      "index.mapping.total_fields.ignore_dynamic_beyond_limit": false,
      "index.mapping.coerce": true,
      "index.mapping.ignore_malformed": false
    },
    "mappings": {
      "dynamic": "runtime",
      "date_detection": true,
      "numeric_detection": false,
      "dynamic_templates": [],
      "properties": {}
    }
  },
  "predict": "先确认资源不存在；这一份 mapping 放开了哪些未知字段？",
  "expect": "首次 200 acknowledged=true；shards_acknowledged 需结合健康等待。重复创建为 400 resource_already_exists_exception；先点名清理，再从创建重做。"
};
  window.ESEXPERIMENTS['ch11-12-health'] = {
  "version": 1,
  "id": "ch11-12-health",
  "title": "C4 · 等待三份对照资源",
  "method": "GET",
  "path": "/_cluster/health/tut-l11-strict,tut-l11-false,tut-l11-runtime?wait_for_status=green&timeout=5s",
  "body": null,
  "predict": "本组索引是否全部建好并分配？",
  "expect": "timed_out=false、green、active_primary_shards=3；否则先处理创建 / 分配问题。此健康范围只含本组三个索引。"
};
  window.ESEXPERIMENTS['ch11-11-strict-reject'] = {
  "version": 1,
  "id": "ch11-11-strict-reject",
  "title": "C5 · strict 拒绝未知字段",
  "method": "PUT",
  "path": "/tut-l11-strict/_doc/1",
  "body": {
    "title": "ok",
    "unknown_field": "boom"
  },
  "predict": "是否只忽略 unknown_field，保留 title？",
  "expect": "400；reason 链含 mapping set to strict, dynamic introduction of [unknown_field] within [_doc] is not allowed，常包于 document_parsing_exception。完整文档被拒，下一卡验证未创建。"
};
  window.ESEXPERIMENTS['ch11-11-strict-missing'] = {
  "version": 1,
  "id": "ch11-11-strict-missing",
  "title": "C6 · 验证失败文档不存在",
  "method": "GET",
  "path": "/tut-l11-strict/_doc/1",
  "body": null,
  "predict": "strict 失败后有没有半篇文档？",
  "expect": "按本课干净前提，404 found=false，无成功写入。若曾单独写入同 ID，失败更新不会删除旧文档；请清理恢复前提。"
};
  window.ESEXPERIMENTS['ch11-13-false-swallow'] = {
  "version": 1,
  "id": "ch11-13-false-swallow",
  "title": "C7 · false 保存原值，不建立未知 mapper",
  "method": "PUT",
  "path": "/tut-l11-false/_doc/1?refresh=true",
  "body": {
    "title": "visible",
    "note": "retained"
  },
  "predict": "note 会被从原文档删掉吗？",
  "expect": "首次 201 created；重复 200 updated。title 按已知 mapping 索引，note 随 stored _source 保留；显式 refresh 供 C10 的 exists 对照。"
};
  window.ESEXPERIMENTS['ch11-14-false-mapping'] = {
  "version": 1,
  "id": "ch11-14-false-mapping",
  "title": "C8 · mapping 只声明 title",
  "method": "GET",
  "path": "/tut-l11-false/_mapping",
  "body": null,
  "predict": "properties 中会出现 note 吗？",
  "expect": "properties 只有 title，dynamic=false。未知字段未成为持久 mapper；不能把内部 ignored source 保存与 API _ignored 返回一概等同。"
};
  window.ESEXPERIMENTS['ch11-14-false-get'] = {
  "version": 1,
  "id": "ch11-14-false-get",
  "title": "C9 · GET 能取回 note",
  "method": "GET",
  "path": "/tut-l11-false/_doc/1",
  "body": null,
  "predict": "没有 note mapper，GET 是否仍有原值？",
  "expect": "200 found=true，_source.note=retained。无索引结构不等于原值丢失；本例 stored source、未用 source excludes 或禁用 source。"
};
  window.ESEXPERIMENTS['ch11-14-false-exists'] = {
  "version": 1,
  "id": "ch11-14-false-exists",
  "title": "C10 · 刷新后 exists 仍找不到 note",
  "method": "POST",
  "path": "/tut-l11-false/_search",
  "body": {
    "query": {
      "exists": {
        "field": "note"
      }
    },
    "track_total_hits": true
  },
  "predict": "C7 已 refresh，是可见性问题还是没有字段结构？",
  "expect": "hits.total.value=0，因为未映射 note；不是未刷新。可用请求级 runtime_mappings 查询该 source 值，此处未提供。"
};
  window.ESEXPERIMENTS['ch11-14-runtime-put'] = {
  "version": 1,
  "id": "ch11-14-runtime-put",
  "title": "C11 · runtime 推断字符串与小数",
  "method": "PUT",
  "path": "/tut-l11-runtime/_doc/1?refresh=true",
  "body": {
    "label": "Guide",
    "price": 29.99
  },
  "predict": "runtime 的字符串是否也是 text+keyword，小数是否也是 float？",
  "expect": "首次 201 created，重复 200 updated；本例产生 runtime.label=keyword、runtime.price=double。不建立它们的倒排；本篇 source 入库并刷新，供 C13 查询。"
};
  window.ESEXPERIMENTS['ch11-14-runtime-mapping'] = {
  "version": 1,
  "id": "ch11-14-runtime-mapping",
  "title": "C12 · 对照 runtime 区域",
  "method": "GET",
  "path": "/tut-l11-runtime/_mapping",
  "body": null,
  "predict": "字段会出现在 properties 还是 runtime？",
  "expect": "runtime 下 label.type=keyword、price.type=double；properties 没有这两个具体字段。runtime 字段仍会占 mapping 元数据、计入 total_fields.limit。"
};
  window.ESEXPERIMENTS['ch11-14-runtime-query'] = {
  "version": 1,
  "id": "ch11-14-runtime-query",
  "title": "C13 · 查询时读取 source 计算 runtime 值",
  "method": "POST",
  "path": "/tut-l11-runtime/_search",
  "body": {
    "query": {
      "term": {
        "label": "Guide"
      }
    },
    "track_total_hits": true,
    "fields": [
      "label",
      "price"
    ]
  },
  "predict": "没有倒排时，显式 runtime 字段能命中吗？",
  "expect": "hits.total.value=1，_id=1，fields 回显 label / price；依赖允许此类查询（默认 search.allow_expensive_queries=true）。若被禁先核对配置，不改集群设置。"
};
  window.ESEXPERIMENTS['ch11-15-merge-conflict'] = {
  "version": 1,
  "id": "ch11-15-merge-conflict",
  "title": "D1 · 已有 text 不能改成 keyword",
  "method": "PUT",
  "path": "/tut-l11-inferred/_mapping",
  "body": {
    "properties": {
      "title": {
        "type": "keyword"
      }
    }
  },
  "predict": "merge 比较文档数量，还是已有 mapper 的类型？",
  "expect": "400；reason 链含 mapper [title] cannot be changed from type [text] to [keyword]。已有映射不变；即使零文档也受类型检查，和数值字符串 coercion 无关。"
};
  window.ESEXPERIMENTS['ch11-16-merge-add'] = {
  "version": 1,
  "id": "ch11-16-merge-add",
  "title": "D2 · 新增字段，保留原有 mapping",
  "method": "PUT",
  "path": "/tut-l11-inferred/_mapping",
  "body": {
    "properties": {
      "status": {
        "type": "keyword"
      }
    }
  },
  "predict": "这个请求会替换并删掉其他字段吗？",
  "expect": "200 acknowledged=true，新 status=keyword；重复同一更新可为无实际变更，仍成功。可更新哪些参数由各 mapper 决定；新增 mapping 不会给历史文档回填 status 或新 multi-field。"
};
  window.ESEXPERIMENTS['ch11-16-merge-read'] = {
  "version": 1,
  "id": "ch11-16-merge-read",
  "title": "D3 · 读回成功与失败更新的结果",
  "method": "GET",
  "path": "/tut-l11-inferred/_mapping?filter_path=**.title,**.status,**.price",
  "body": null,
  "predict": "失败的 D1 和成功的 D2 留下了什么？",
  "expect": "title 仍 text+keyword，price 仍 float，新 status=keyword。查询 mapping 只能证明结构，不能证明 status 已有文档值。"
};
  window.ESEXPERIMENTS['ch11-17-field-caps'] = {
  "version": 1,
  "id": "ch11-17-field-caps",
  "title": "E1 · 字段能力是配置结果",
  "method": "GET",
  "path": "/tut-l11-inferred/_field_caps?fields=title,title.keyword,price,sku,qty,status",
  "body": null,
  "predict": "text 是否不可查询？没有 status 值是否会缺失能力？",
  "expect": "本例 title(text) searchable=true、aggregatable=false；title.keyword / price / qty / status 可搜可聚合。能力由 mapping / 配置决定；无值仍可返回 status 能力，不是命中统计。"
};
  window.ESEXPERIMENTS['ch11-18-cleanup'] = {
  "version": 1,
  "id": "ch11-18-cleanup",
  "title": "清理 · 点名删除本课四个索引",
  "method": "DELETE",
  "path": "/tut-l11-inferred,tut-l11-strict,tut-l11-false,tut-l11-runtime?ignore_unavailable=true",
  "body": null,
  "predict": "会删除哪些资源，部分索引不存在时怎样重做？",
  "expect": "200 acknowledged=true；四个点名索引及文档 / mapping 一起删除。ignore_unavailable=true 容许部分不存在；再次按 A0→A→B→C→D→E 完整执行，不删除其他 tut-l11-* 资源。"
};
})();
