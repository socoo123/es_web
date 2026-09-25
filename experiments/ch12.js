/* experiments/ch12.js — 第 12 课:摄取管道(前半场 _simulate 不落盘,后半场小索引用完即删) */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch12-01-put-fields'] = {
    version: 1, id: 'ch12-01-put-fields',
    title: '实验 1 · 定义管道 tut-l12-fields(set + rename)',
    method: 'PUT', path: '/_ingest/pipeline/tut-l12-fields',
    body: {
      description: 'set environment then rename hostname to host',
      processors: [
        { set: { field: 'environment', value: 'production' } },
        { rename: { field: 'hostname', target_field: 'host' } }
      ]
    },
    predict: '先猜:这份数据存在哪?这一步会创建哪个索引、写入哪篇文档?acknowledged 回什么?',
    expect: '对照:acknowledged: true。pipeline 是集群级注册表项(存在 IngestService 的 pipeline 表里),不建索引、不碰文档。processors 数组顺序 = 执行顺序:set 先加 environment,rename 后把 hostname 改成 host。'
  };

  window.ESEXPERIMENTS['ch12-02-simulate-fields'] = {
    version: 1, id: 'ch12-02-simulate-fields',
    title: '实验 2 · _simulate:不落盘看 JSON 怎么变',
    method: 'POST', path: '/_ingest/pipeline/tut-l12-fields/_simulate',
    body: { docs: [{ _source: { hostname: 'web-01', level: 'INFO' } }] },
    predict: '先猜:doc._source 里还有 hostname 吗?host 和 environment 出现了吗?跑完之后索引里有几篇文档?',
    expect: '对照:doc._source 是 host: web-01、environment: production、level: INFO,没有 hostname——SetProcessor.setFieldValue 加字段,RenameProcessor 先 removeField 再写新名。文档数是 0:_simulate 在 ingest 节点跑完 Pipeline.execute 就返回,不进 BulkOperation.route、不落盘;此刻去 GET 这个从未创建的索引,是 404 index_not_found(路由命中、资源不存在)。'
  };

  window.ESEXPERIMENTS['ch12-03-simulate-verbose'] = {
    version: 1, id: 'ch12-03-simulate-verbose',
    title: '实验 3 · verbose=true:看每一步的中间态',
    method: 'POST', path: '/_ingest/pipeline/tut-l12-fields/_simulate?verbose=true',
    body: { docs: [{ _source: { hostname: 'web-01', level: 'INFO' } }] },
    predict: '先猜:能不能看见「set 之后、rename 之前」的文档?那时 hostname 还在吗?',
    expect: '对照:verbose 用 TrackingResultProcessor 把每个 processor 包一层,processor_results 里每一步留一份当时的文档:第一个(set)之后 hostname 还在、environment 已出现;第二个(rename)之后 hostname 消失、host 出现。调管道就靠这个,不必真写入。'
  };

  window.ESEXPERIMENTS['ch12-04-grok-inline'] = {
    version: 1, id: 'ch12-04-grok-inline',
    title: '实验 4 · 内联管道:grok 拆日志再 remove',
    method: 'POST', path: '/_ingest/pipeline/_simulate',
    body: {
      pipeline: {
        description: 'parse one log line, inline',
        processors: [
          { grok: { field: 'message', patterns: ['%{TIMESTAMP_ISO8601:log_timestamp} %{LOGLEVEL:level} %{GREEDYDATA:log_message}'] } },
          { remove: { field: 'message' } }
        ]
      },
      docs: [
        { _source: { message: '2024-01-15T10:30:00 ERROR Out of memory exception' } },
        { _source: { message: '2024-01-15T10:31:00 INFO Application recovered' } }
      ]
    },
    predict: '先猜:一行日志会拆出哪三个字段?message 还在吗?两行都能匹配吗?',
    expect: '对照:两篇都出现 log_timestamp / level / log_message,message 被 remove 掉——GrokProcessor.captures 命中后 matches.forEach(setFieldValue),随后的 remove 处理器删原始行。路径不带 id、管道写在 body 里,是 RestSimulatePipelineAction 四条路由里的内联那条:连索引都不用建。'
  };

  window.ESEXPERIMENTS['ch12-05-onfailure-inline'] = {
    version: 1, id: 'ch12-05-onfailure-inline',
    title: '实验 5 · 内联 on_failure:date 解析失败不炸整篇',
    method: 'POST', path: '/_ingest/pipeline/_simulate',
    body: {
      pipeline: {
        processors: [
          {
            date: {
              field: 'raw_date', target_field: '@timestamp', formats: ['yyyy-MM-dd'], tag: 'parse-date',
              on_failure: [
                { set: { field: 'date_parse_error', value: 'Failed to parse date: {{_ingest.on_failure_message}}' } }
              ]
            }
          }
        ]
      },
      docs: [
        { _source: { raw_date: '2024-01-15' } },
        { _source: { raw_date: 'not-a-date' } }
      ]
    },
    predict: '先猜:not-a-date 会让整条 _simulate 报错吗?那篇文档还会出现在 docs 里吗?会多出什么字段?',
    expect: '对照:好的那篇有 @timestamp(按 UTC 解析成当天零点,以你的返回为准);坏的那篇没有 @timestamp,但多了 date_parse_error,内嵌 {{_ingest.on_failure_message}} 展开的失败原因,文档仍在结果里——CompoundProcessor 捕获异常后先 putFailureMetadata(message / processor_type / tag / pipeline)再跑 on_failure 链,链成功则文档留下,而不是整篇 400。'
  };

  window.ESEXPERIMENTS['ch12-06-create-index'] = {
    version: 1, id: 'ch12-06-create-index',
    title: '实验 6 · 建索引 tut-l12-docs(1 分片 0 副本)',
    method: 'PUT', path: '/tut-l12-docs',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: '先猜:为什么 replicas 写 0?(第 1 课)1 个主分片对这组实验意味着什么?',
    expect: '对照:单节点上副本无处安放,写 0 直接 green。1 个主分片让这组实验不被「另一号 shard」干扰——本组看的是 _source 怎么变,不是路由;路由留给 tut-l12-routed。'
  };

  window.ESEXPERIMENTS['ch12-07-write-pipelined'] = {
    version: 1, id: 'ch12-07-write-pipelined',
    title: '实验 7 · 带 ?pipeline= 写入 _id=1',
    method: 'PUT', path: '/tut-l12-docs/_doc/1?pipeline=tut-l12-fields&refresh=true',
    body: { hostname: 'web-01', level: 'INFO' },
    predict: '先猜:存进 Lucene 的 _source 是原始 JSON 还是改过的?refresh=true 是为了让什么立刻可见?',
    expect: '对照:result: created。单条 PUT 也走 bulk(TransportSingleItemBulkWriteAction):TransportAbstractBulkAction 发现 ?pipeline= 先跑 IngestService,updateIndexRequestSource 用改完的 map 覆盖 IndexRequest 的 source,然后才 route、进 Lucene。refresh=true 让下一篇 GET 立即可见(第 10 课的 realtime GET 是另一条路)。'
  };

  window.ESEXPERIMENTS['ch12-08-get-doc1'] = {
    version: 1, id: 'ch12-08-get-doc1',
    title: '实验 8 · GET _id=1:对照 _source',
    method: 'GET', path: '/tut-l12-docs/_doc/1?filter_path=_id,_source',
    body: null,
    predict: '先猜:_source 里是 host 还是 hostname?有没有 environment?pipeline 会不会只影响搜索、不改存储?',
    expect: '对照:host: web-01、environment: production、level: INFO,没有 hostname。存进 Lucene 的就是改过的 JSON——pipeline 不是查询期脚本,它改的是「即将写入的那份 JSON」,改完经 updateIndexRequestSource 覆盖回 IndexRequest。'
  };

  window.ESEXPERIMENTS['ch12-09-write-plain'] = {
    version: 1, id: 'ch12-09-write-plain',
    title: '实验 9 · 对照:不带 pipeline 写 _id=2',
    method: 'PUT', path: '/tut-l12-docs/_doc/2?refresh=true',
    body: { hostname: 'web-02', level: 'WARN' },
    predict: '先猜:同一个索引、不带 ?pipeline=,这篇会被处理吗?它的 _source 长什么样?',
    expect: '对照:不会。_id=2 的 _source 仍是 hostname: web-02、没有 environment——?pipeline= 只作用于这一次请求;想让整索引默认走管道要设 index.default_pipeline(请求 pipeline 会覆盖它,index.final_pipeline 则总在最后跑)。'
  };

  window.ESEXPERIMENTS['ch12-10-get-mapping'] = {
    version: 1, id: 'ch12-10-get-mapping',
    title: '实验 10 · 看 mapping:动态推断发生在 ingest 之后',
    method: 'GET', path: '/tut-l12-docs/_mapping',
    body: null,
    predict: '先猜:environment / host / hostname / level 会被推断成什么类型?mapping 是在第几个 processor 跑的时候看的字段?',
    expect: '对照:四个都是 text + fields.keyword——动态映射发生在 ingest 之后、写入具体索引之时(第 11 课的动态字符串推断),它看到的是 pipeline 改完的 JSON:doc1 造出了 host 列,doc2 造出了 hostname 列,两套字段并存正是「客户端各改各的」的代价。'
  };

  window.ESEXPERIMENTS['ch12-11-create-routed'] = {
    version: 1, id: 'ch12-11-create-routed',
    title: '实验 11 · 建索引 tut-l12-routed(5 分片)',
    method: 'PUT', path: '/tut-l12-routed',
    body: { settings: { number_of_shards: 5, number_of_replicas: 0 } },
    predict: '先猜:为什么要 5 个主分片?0 副本是为了什么?',
    expect: '对照:5 把「hash 取模的篮子」拉开,两把不同的键更可能落在不同 shard 号上,演示才明显;0 副本保持单节点 green。主分片数是 Final 设置(第 5 课),路由哈希的除数不能变。'
  };

  window.ESEXPERIMENTS['ch12-12-put-routing-pipeline'] = {
    version: 1, id: 'ch12-12-put-routing-pipeline',
    title: '实验 12 · 定义改 _routing 的管道',
    method: 'PUT', path: '/_ingest/pipeline/tut-l12-routing',
    body: {
      description: 'overwrite _routing before shard selection',
      processors: [
        { set: { field: '_routing', value: 'tenant-a' } }
      ]
    },
    predict: '先猜:_routing 是 _source 里的普通字段吗?set 一个元数据名,IngestDocument 会让过吗?',
    expect: '对照:会让。IngestDocMetadata.PROPERTIES 里 ROUTING 是 StringField.withWritable().withNullable();IngestCtxMap 把下划线开头的键交给 metadata,所以 setFieldValue("_routing", ...) 与改普通字段走同一套路径 API——只是值必须是 String 或 null。'
  };

  window.ESEXPERIMENTS['ch12-13-shards-by-id'] = {
    version: 1, id: 'ch12-13-shards-by-id',
    title: '实验 13 · 写入前:算 hash("1") 落哪号 shard',
    method: 'GET', path: '/tut-l12-routed/_search_shards?routing=1&filter_path=shards.shard',
    body: null,
    predict: '先猜:还没写入就能查路由吗?routing=1 模拟的是哪把键?',
    expect: '对照:能查——_search_shards 只做路由计算、不碰数据。routing=1 模拟「若无 pipeline,有效键就是 _id 字符串 "1"」:IndexRouting.Unpartitioned.indexShard 的 shardId(id, routing) = hash(routing) 对 5 取模。记下这个 shard 号(以你的返回为准)。'
  };

  window.ESEXPERIMENTS['ch12-14-shards-by-tenant'] = {
    version: 1, id: 'ch12-14-shards-by-tenant',
    title: '实验 14 · 写入前:算 hash("tenant-a") 落哪号',
    method: 'GET', path: '/tut-l12-routed/_search_shards?routing=tenant-a&filter_path=shards.shard',
    body: null,
    predict: '先猜:和上一把键的 shard 号一定不同吗?',
    expect: '对照:大多数情况不同,但 floorMod(hash, 5) 只有 5 个值,撞车不算原理失败——撞了就换个 value 再演示(和第 10 课同一纪律)。要点是:两把键各算各的,文档只会躺在写入时实际生效那把键的 shard 上。'
  };

  window.ESEXPERIMENTS['ch12-15-write-routed'] = {
    version: 1, id: 'ch12-15-write-routed',
    title: '实验 15 · 带 pipeline 写入:URL 不带 routing',
    method: 'PUT', path: '/tut-l12-routed/_doc/1?pipeline=tut-l12-routing&refresh=true',
    body: { title: 'routed-by-pipeline' },
    predict: '先猜:选 shard 用的是 hash("1") 还是 hash("tenant-a")?URL 上可没带 routing。',
    expect: '对照:用的是 tenant-a。set 先把 _routing 写成 tenant-a,updateIndexRequestMetadata 里 request.routing(metadata.getRouting()) 把它写回 IndexRequest,之后 BulkOperation.route 才调 indexRouting.indexShard——此时 routing 已非空,第 10 课规则:有 routing 就只 hash routing,不再混入 _id。'
  };

  window.ESEXPERIMENTS['ch12-16-get-miss'] = {
    version: 1, id: 'ch12-16-get-miss',
    title: '实验 16 · GET 不带 routing:打错 shard 就 404',
    method: 'GET', path: '/tut-l12-routed/_doc/1?filter_path=found,_id,_routing',
    body: null,
    predict: '先猜:不带 routing 的 GET 是 200 还是 404?为什么?',
    expect: '对照:若实验 13/14 的 shard 号不同,这里 found: false(HTTP 404):GET 的有效键退回 _id 字符串 "1",只打 hash("1") 那一个 shard,打错了不广播(第 10 课不变量)。若两号恰好相同则这次会命中——那是取模撞车,不是 pipeline 没生效,以实验 17 的 _routing 为准。'
  };

  window.ESEXPERIMENTS['ch12-17-get-hit'] = {
    version: 1, id: 'ch12-17-get-hit',
    title: '实验 17 · GET 带 tenant-a:命中并回显 _routing',
    method: 'GET', path: '/tut-l12-routed/_doc/1?routing=tenant-a&filter_path=found,_id,_routing,_source',
    body: null,
    predict: '先猜:这次能找到吗?返回里的 _routing 是什么值?',
    expect: '对照:found: true,_routing: tenant-a。写入时实际生效的键就是它,GET 用同一把键命中同一号 shard。这顺带证明 pipeline 改的 routing 被持久化成文档元数据——不只是改改响应字段。'
  };

  window.ESEXPERIMENTS['ch12-18-search-fanout'] = {
    version: 1, id: 'ch12-18-search-fanout',
    title: '实验 18 · SEARCH 扇出:不带 routing 也能找到',
    method: 'GET', path: '/tut-l12-routed/_search?q=_id:1&filter_path=hits.total,hits.hits._id,hits.hits._routing',
    body: null,
    predict: '先猜:不带 routing 的搜索能找到吗?它和 GET 的差别在哪?',
    expect: '对照:能命中——搜索扇出到全部 5 个 shard,不依赖某一把键;若返回带 _routing,值是 tenant-a。GET 是「一把键一个 shard」,SEARCH 是「全部 shard 收齐再归并」:改 routing 伤害的是 GET,不是搜索。'
  };

  window.ESEXPERIMENTS['ch12-19-clean-indices'] = {
    version: 1, id: 'ch12-19-clean-indices',
    title: '清理 1 · 删除两个实验索引',
    method: 'DELETE', path: '/tut-l12-docs,tut-l12-routed',
    body: null,
    predict: '先猜:文档和 mapping 会跟着索引一起没吗?管道注册表受影响吗?',
    expect: '对照:acknowledged: true。文档、mapping、default_pipeline 一类索引级设置随索引删除;集群级的 pipeline 注册表不受影响——它是另一层状态。'
  };

  window.ESEXPERIMENTS['ch12-20-clean-pipelines'] = {
    version: 1, id: 'ch12-20-clean-pipelines',
    title: '清理 2 · 删除两条管道',
    method: 'DELETE', path: '/_ingest/pipeline/tut-l12-fields,tut-l12-routing',
    body: null,
    predict: '先猜:逗号列表一次删多条行吗?',
    expect: '对照:acknowledged: true。pipeline 存在集群状态里,删除即全集群生效;不删它会一直躺在注册表里,等下一次同名单词。'
  };
})();
