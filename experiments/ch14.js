/* ch14：固定 9.4.0 源码校对的预期；本轮真实 ES 未运行。 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch14-version"] = {
  "version": 1,
  "id": "ch14-version",
  "title": "A0 · 核对运行版本",
  "method": "GET",
  "path": "/?filter_path=version.number,version.lucene_version,cluster_name",
  "body": null,
  "predict": "端点是否为本课的 9.4.0 / Lucene 10.4.0？",
  "expect": "HTTP 200；核对 version.number=9.4.0、version.lucene_version=10.4.0。默认 http://localhost:9200、单数据节点、匿名学习端点；认证由控制台选定，版本不同先核对差异。本轮云环境未运行真实 API。"
};
  window.ESEXPERIMENTS["ch14-00-nrt-setup"] = {
  "version": 1,
  "id": "ch14-00-nrt-setup",
  "title": "A1 · 新建 tut-l14-nrt",
  "method": "PUT",
  "path": "/tut-l14-nrt",
  "body": {
    "settings": {
      "index.mode": "standard",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "translog.durability": "request",
      "translog.sync_interval": "5s",
      "translog.flush_threshold_age": "1h",
      "translog.flush_threshold_size": "10gb",
      "mapping.source.mode": "stored",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "routing_partition_size": 1,
      "write.wait_for_active_shards": "1"
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "enabled": true
      },
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
  "predict": "先清理本课索引；无匹配模板、外部写入或刷新。为什么同时明确刷新与耐久配置？",
  "expect": "HTTP 200，acknowledged=true；若已存在则 400，先清理再从本组开始。普通索引、1 主 0 副、严格 mapping、stored source、无管道；-1 关闭周期 refresh，request 等待日志同步。1h 推迟年龄 flush，不会关闭全部后台维护。"
};
  window.ESEXPERIMENTS["ch14-a-health"] = {
  "version": 1,
  "id": "ch14-a-health",
  "title": "A2 · 等待本组主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l14-nrt?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=10s",
  "body": null,
  "predict": "只看本组索引，green 能替代实验前提吗？",
  "expect": "需 status=green、timed_out=false、active_primary_shards=1、active_shards=1。超时先恢复分配再继续；其他索引可让整个集群 yellow。此卡不证明磁盘同步或源码内部路径。"
};
  window.ESEXPERIMENTS["ch14-01-nrt-put"] = {
  "version": 1,
  "id": "ch14-01-nrt-put",
  "title": "A3 · 写入新 ID 1",
  "method": "PUT",
  "path": "/tut-l14-nrt/_doc/1",
  "body": {
    "title": "engine-nrt",
    "views": 14
  },
  "predict": "result 是什么?此刻这篇文档同时躺在哪几处?",
  "expect": "首次 HTTP 201 / created / _version=1；重复为 200 / updated，后续计数不再是初始值。request 写后阶段等待该日志位置同步；不会因此发布 EXTERNAL reader。IndexWriter 可自动落段，不能断言“任何 segment 都没有”。"
};
  window.ESEXPERIMENTS["ch14-02-nrt-get"] = {
  "version": 1,
  "id": "ch14-02-nrt-get",
  "title": "A4 · realtime GET 读回",
  "method": "GET",
  "path": "/tut-l14-nrt/_doc/1?filter_path=found,_id,_version,_source",
  "body": null,
  "predict": "还没 refresh,拿得到吗?_version 是多少?",
  "expect": "新建且只写一次时 found=true、_version=1、_source 原样返回。可能读 translog，也可能按需刷新 INTERNAL 后读 Lucene；API 响应不能辨认内部命中路径。GET 不负责推进 EXTERNAL。"
};
  window.ESEXPERIMENTS["ch14-nrt-nonrealtime"] = {
  "version": 1,
  "id": "ch14-nrt-nonrealtime",
  "title": "A5 · GET realtime=false 对照",
  "method": "GET",
  "path": "/tut-l14-nrt/_doc/1?realtime=false",
  "body": null,
  "predict": "刚刚 realtime GET 成功，外部 reader 也能看到吗？",
  "expect": "在新建索引、无外部 refresh 的前提下 HTTP 404 / found=false。只关闭周期刷新；若已有搜索视图则回 200，先清理重建恢复前提。"
};
  window.ESEXPERIMENTS["ch14-03-nrt-search"] = {
  "version": 1,
  "id": "ch14-03-nrt-search",
  "title": "A6 · 搜索旧的外部视图",
  "method": "POST",
  "path": "/tut-l14-nrt/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "engine-nrt"
      }
    }
  },
  "predict": "GET 都拿到了,match title:engine-nrt 呢?",
  "expect": "首次顺序且没有外部 refresh：hits.total.value=0。严格 keyword 的 term 精确匹配。realtime GET 的内部 refresh 不发布 EXTERNAL；若命中先检查旧数据、外部刷新及执行顺序。"
};
  window.ESEXPERIMENTS["ch14-04-nrt-refresh"] = {
  "version": 1,
  "id": "ch14-04-nrt-refresh",
  "title": "A7 · 显式发布外部视图",
  "method": "POST",
  "path": "/tut-l14-nrt/_refresh?filter_path=_shards",
  "body": null,
  "predict": "refresh 做了什么、没做什么?猜猜下一步 translog 统计会不会变。",
  "expect": "_shards.failed=0、successful=1。refresh 可能落出 Lucene NRT 文件并切换外部 reader；不是 commit 或 translog 同步命令，也不因可搜索而裁日志。"
};
  window.ESEXPERIMENTS["ch14-05-nrt-search-hit"] = {
  "version": 1,
  "id": "ch14-05-nrt-search-hit",
  "title": "A8 · 搜索读回新视图",
  "method": "POST",
  "path": "/tut-l14-nrt/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "engine-nrt"
      }
    }
  },
  "predict": "hits.total 这次是多少?",
  "expect": "hits.total.value=1。这是外部 reader 可见性的证据，不是 Lucene commit、translog fsync 或内部缓存命中的证据。"
};
  window.ESEXPERIMENTS["ch14-06-nrt-stats"] = {
  "version": 1,
  "id": "ch14-06-nrt-stats",
  "title": "A9 · 记录可见后的日志统计",
  "method": "GET",
  "path": "/tut-l14-nrt/_stats/translog?filter_path=indices.tut-l14-nrt.primaries.translog",
  "body": null,
  "predict": "刚 refresh 过,uncommitted_operations 是 0 吗?",
  "expect": "观察 operations、size_in_bytes、uncommitted_operations、uncommitted_size_in_bytes。未后台 flush 的短流程常见 1 条未提交；refresh 自身不推进 commit。计数按 safe commit 后所需 generation 汇总，可包含已提交操作，不能等同精确待重放条数。"
};
  window.ESEXPERIMENTS["ch14-10-tlog-setup"] = {
  "version": 1,
  "id": "ch14-10-tlog-setup",
  "title": "B1 · 新建 tut-l14-tlog",
  "method": "PUT",
  "path": "/tut-l14-tlog",
  "body": {
    "settings": {
      "index.mode": "standard",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "translog.durability": "request",
      "translog.sync_interval": "5s",
      "translog.flush_threshold_age": "1h",
      "translog.flush_threshold_size": "10gb",
      "mapping.source.mode": "stored",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "routing_partition_size": 1,
      "write.wait_for_active_shards": "1"
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "enabled": true
      },
      "properties": {
        "title": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "先清理本课索引；无匹配模板、外部写入或刷新。为什么同时明确刷新与耐久配置？",
  "expect": "HTTP 200，acknowledged=true；若已存在则 400，先清理再从本组开始。普通索引、1 主 0 副、严格 mapping、stored source、无管道；-1 关闭周期 refresh，request 等待日志同步。1h 推迟年龄 flush，不会关闭全部后台维护。"
};
  window.ESEXPERIMENTS["ch14-b-health"] = {
  "version": 1,
  "id": "ch14-b-health",
  "title": "B2 · 等待本组主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l14-tlog?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=10s",
  "body": null,
  "predict": "只看本组索引，green 能替代实验前提吗？",
  "expect": "需 status=green、timed_out=false、active_primary_shards=1、active_shards=1。超时先恢复分配再继续；其他索引可让整个集群 yellow。此卡不证明磁盘同步或源码内部路径。"
};
  window.ESEXPERIMENTS["ch14-11-tlog-flush"] = {
  "version": 1,
  "id": "ch14-11-tlog-flush",
  "title": "B3 · flush 打底",
  "method": "POST",
  "path": "/tut-l14-tlog/_flush?force=true&wait_if_ongoing=true",
  "body": null,
  "predict": "flush 内部按什么顺序动 translog 和 Lucene?",
  "expect": "_shards.failed=0、successful=1。普通成功路径：同步并滚代 → Lucene commit → INTERNAL refresh → 条件裁剪。force=true 与 wait_if_ongoing=true 配套；空日志代次可能不变。"
};
  window.ESEXPERIMENTS["ch14-12-tlog-zero"] = {
  "version": 1,
  "id": "ch14-12-tlog-zero",
  "title": "B4 · 记录空日志基线",
  "method": "GET",
  "path": "/tut-l14-tlog/_stats/translog?filter_path=indices.tut-l14-tlog.primaries.translog",
  "body": null,
  "predict": "uncommitted_operations 现在是多少?",
  "expect": "新建且无其他写入：uncommitted_operations=0。若非 0 先查外部写入、后台恢复和执行顺序，不能把个位数也称为空基线。文件头仍占字节，不要求 size_in_bytes=0。"
};
  window.ESEXPERIMENTS["ch14-13-tlog-put"] = {
  "version": 1,
  "id": "ch14-13-tlog-put",
  "title": "B5 · request 模式写入",
  "method": "PUT",
  "path": "/tut-l14-tlog/_doc/1",
  "body": {
    "title": "before-flush"
  },
  "predict": "201 回来时,这条写已经 fsync 了吗?已经 commit 了吗?",
  "expect": "首次 201 / created。request 等该写入日志位置同步；是否已 commit 由独立 flush 时序决定，单看 201 不知道 commit。重复会 updated，计数和版本随之变化。"
};
  window.ESEXPERIMENTS["ch14-14-tlog-one"] = {
  "version": 1,
  "id": "ch14-14-tlog-one",
  "title": "B6 · 记录写后日志",
  "method": "GET",
  "path": "/tut-l14-tlog/_stats/translog?filter_path=indices.tut-l14-tlog.primaries.translog",
  "body": null,
  "predict": "operations 和 uncommitted_operations 各是多少?会一样吗?",
  "expect": "短流程且无后台 flush：常见 operations=1、uncommitted_operations=1。这份统计不暴露该操作是否 fsync；默认 request 的同步结论来自设置和写后源码，不来自未提交计数。"
};
  window.ESEXPERIMENTS["ch14-15-tlog-async"] = {
  "version": 1,
  "id": "ch14-15-tlog-async",
  "title": "B7 · 临时改 async",
  "method": "PUT",
  "path": "/tut-l14-tlog/_settings",
  "body": {
    "index.translog.durability": "async"
  },
  "predict": "这个设置能在线改吗?改完之后「201」的含义变了吗?",
  "expect": "acknowledged=true。索引级 Dynamic 设置；请求不再因 async 而等待自己的日志 fsync，后台按 sync_interval 调度同步。默认 5s 是周期，不是损失上限或最坏时限；GET 仍可读，是否接受风险取决于业务恢复要求。"
};
  window.ESEXPERIMENTS["ch14-async-put"] = {
  "version": 1,
  "id": "ch14-async-put",
  "title": "B8 · async 写入新 ID 2",
  "method": "PUT",
  "path": "/tut-l14-tlog/_doc/2",
  "body": {
    "title": "async-readback"
  },
  "predict": "async 会拒绝普通写入或阻止 GET 吗？",
  "expect": "首次 201 / created；重复 200 / updated。响应不要求这条请求等待 fsync，但后台同步可能已完成；不能据此断言此时数据尚未落盘。"
};
  window.ESEXPERIMENTS["ch14-async-get"] = {
  "version": 1,
  "id": "ch14-async-get",
  "title": "B9 · async 下实时读回",
  "method": "GET",
  "path": "/tut-l14-tlog/_doc/2",
  "body": null,
  "predict": "读得到能否证明抗掉电？",
  "expect": "found=true、_source.title=async-readback。realtime GET 验证当前可读，不证明 fsync、commit 或崩溃恢复；本课不执行故障注入。"
};
  window.ESEXPERIMENTS["ch14-restore-request"] = {
  "version": 1,
  "id": "ch14-restore-request",
  "title": "B10 · 恢复 request",
  "method": "PUT",
  "path": "/tut-l14-tlog/_settings",
  "body": {
    "index.translog.durability": "request"
  },
  "predict": "恢复设置就能证明此前所有操作同步了吗？",
  "expect": "acknowledged=true。后续请求恢复等待同步的策略；这是设置读回前的恢复步骤，响应本身不提供逐条历史 fsync 证据。课末仍删除此索引。"
};
  window.ESEXPERIMENTS["ch14-tlog-settings"] = {
  "version": 1,
  "id": "ch14-tlog-settings",
  "title": "B11 · 读回恢复后的设置",
  "method": "GET",
  "path": "/tut-l14-tlog/_settings?flat_settings=true&filter_path=*.settings.index.translog.*,*.settings.index.refresh_interval",
  "body": null,
  "predict": "恢复后的实际值是什么？",
  "expect": "核对 index.translog.durability=request、sync_interval=5s、flush_threshold_age=1h、refresh_interval=-1。这些是本课显式设置，不能描述为全部默认值。"
};
  window.ESEXPERIMENTS["ch14-20-fl-setup"] = {
  "version": 1,
  "id": "ch14-20-fl-setup",
  "title": "C1 · 新建 tut-l14-flush",
  "method": "PUT",
  "path": "/tut-l14-flush",
  "body": {
    "settings": {
      "index.mode": "standard",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "translog.durability": "request",
      "translog.sync_interval": "5s",
      "translog.flush_threshold_age": "1h",
      "translog.flush_threshold_size": "10gb",
      "mapping.source.mode": "stored",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "routing_partition_size": 1,
      "write.wait_for_active_shards": "1"
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "enabled": true
      },
      "properties": {
        "title": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "先清理本课索引；无匹配模板、外部写入或刷新。为什么同时明确刷新与耐久配置？",
  "expect": "HTTP 200，acknowledged=true；若已存在则 400，先清理再从本组开始。普通索引、1 主 0 副、严格 mapping、stored source、无管道；-1 关闭周期 refresh，request 等待日志同步。1h 推迟年龄 flush，不会关闭全部后台维护。"
};
  window.ESEXPERIMENTS["ch14-c-health"] = {
  "version": 1,
  "id": "ch14-c-health",
  "title": "C2 · 等待本组主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l14-flush?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=10s",
  "body": null,
  "predict": "只看本组索引，green 能替代实验前提吗？",
  "expect": "需 status=green、timed_out=false、active_primary_shards=1、active_shards=1。超时先恢复分配再继续；其他索引可让整个集群 yellow。此卡不证明磁盘同步或源码内部路径。"
};
  window.ESEXPERIMENTS["ch14-21-fl-put"] = {
  "version": 1,
  "id": "ch14-21-fl-put",
  "title": "C3 · 写入新 ID 1",
  "method": "PUT",
  "path": "/tut-l14-flush/_doc/1",
  "body": {
    "title": "before-flush"
  },
  "predict": "这篇现在在 buffer、translog、segment 各几处?",
  "expect": "首次 201 / created。后续显式 refresh 发布它；不能从响应推断当前段数或 commit 时刻。无外部写入、无外部 refresh，按本组顺序运行。"
};
  window.ESEXPERIMENTS["ch14-22-fl-refresh"] = {
  "version": 1,
  "id": "ch14-22-fl-refresh",
  "title": "C4 · 先 refresh",
  "method": "POST",
  "path": "/tut-l14-flush/_refresh?filter_path=_shards",
  "body": null,
  "predict": "refresh 之后 SEARCH 能看到了;translog 呢?",
  "expect": "_shards.failed=0、successful=1。发布 EXTERNAL 新视图；不以这次动作推进 Lucene commit 或裁日志。"
};
  window.ESEXPERIMENTS["ch14-23-fl-stats-refresh"] = {
  "version": 1,
  "id": "ch14-23-fl-stats-refresh",
  "title": "C5 · refresh 后记录未提交日志",
  "method": "GET",
  "path": "/tut-l14-flush/_stats/translog?filter_path=indices.tut-l14-flush.primaries.translog",
  "body": null,
  "predict": "都能搜到了,uncommitted_operations 归零了吗?",
  "expect": "短流程无后台 flush 时常见 uncommitted_operations=1；refresh 不负责减少它。若为 0 检查后台 flush 和运行间隔，清理重建恢复对照；不能把 -1 当成关闭 flush。"
};
  window.ESEXPERIMENTS["ch14-24-fl-search"] = {
  "version": 1,
  "id": "ch14-24-fl-search",
  "title": "C6 · flush 前验证搜索",
  "method": "POST",
  "path": "/tut-l14-flush/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "before-flush"
      }
    }
  },
  "predict": "flush 还没做,能搜到吗?",
  "expect": "hits.total.value=1。已可搜不能推出 Lucene 已 commit；日志统计与外部 reader 是不同观测维度。"
};
  window.ESEXPERIMENTS["ch14-25-fl-flush"] = {
  "version": 1,
  "id": "ch14-25-fl-flush",
  "title": "C7 · 再 flush",
  "method": "POST",
  "path": "/tut-l14-flush/_flush?force=true&wait_if_ongoing=true",
  "body": null,
  "predict": "哪个计数会归零?Lucene 这边多出什么文件?",
  "expect": "_shards.failed=0、successful=1。滚代、提交、内部 refresh、条件裁剪。提交数据含 translog_uuid / local_checkpoint / max_seq_no；无义务再发外部 refresh。"
};
  window.ESEXPERIMENTS["ch14-26-fl-stats-flush"] = {
  "version": 1,
  "id": "ch14-26-fl-stats-flush",
  "title": "C8 · 对照提交后的日志统计",
  "method": "GET",
  "path": "/tut-l14-flush/_stats/translog?filter_path=indices.tut-l14-flush.primaries.translog",
  "body": null,
  "predict": "uncommitted_operations 现在?如果不是 0 呢?",
  "expect": "静止的 1 主 0 副索引通常降到 0；字节不会归零。若仍大于 0，核对 global checkpoint 与恢复/并发活动，等待其追上后再 force flush 并复查。safe commit 与 generation 汇总口径决定保留，重复 flush 不承诺固定次数解决。"
};
  window.ESEXPERIMENTS["ch14-fl-put-two"] = {
  "version": 1,
  "id": "ch14-fl-put-two",
  "title": "C9 · 写入未刷新的 ID 2",
  "method": "PUT",
  "path": "/tut-l14-flush/_doc/2",
  "body": {
    "title": "flush-only"
  },
  "predict": "第一篇已经可搜，第二篇未外部刷新会怎样？",
  "expect": "首次 201 / created。当前外部 reader 仍是 C4 发布的旧视图；新写入恢复了日志增量，本组不再并发写其他文档。"
};
  window.ESEXPERIMENTS["ch14-fl-flush-two"] = {
  "version": 1,
  "id": "ch14-fl-flush-two",
  "title": "C10 · 直接 flush 第二篇",
  "method": "POST",
  "path": "/tut-l14-flush/_flush?force=true&wait_if_ongoing=true",
  "body": null,
  "predict": "Lucene commit 成功会自动让 SEARCH 看见第二篇吗？",
  "expect": "_shards.failed=0、successful=1。普通 InternalEngine.flush 内的刷新作用域为 INTERNAL；接下来搜索外部视图应仍无第二篇。本前提排除其他外部刷新。"
};
  window.ESEXPERIMENTS["ch14-fl-search-old"] = {
  "version": 1,
  "id": "ch14-fl-search-old",
  "title": "C11 · flush 后搜索仍未命中",
  "method": "POST",
  "path": "/tut-l14-flush/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "flush-only"
      }
    }
  },
  "predict": "是否仍是 0？",
  "expect": "hits.total.value=0，限定普通引擎、refresh=-1、未执行外部刷新。flush 没发布 EXTERNAL；若 1，检查外部刷新/旧数据后清理重做，不能用已有第一篇的可见性代替这条对照。"
};
  window.ESEXPERIMENTS["ch14-fl-refresh-two"] = {
  "version": 1,
  "id": "ch14-fl-refresh-two",
  "title": "C12 · 再显式外部 refresh",
  "method": "POST",
  "path": "/tut-l14-flush/_refresh",
  "body": null,
  "predict": "发布第二篇需要哪个动作？",
  "expect": "_shards.failed=0、successful=1。现在外部 reader 接住第二篇；refresh 不要求制造新段，已有 commit 中的数据也能被新 reader 接住。"
};
  window.ESEXPERIMENTS["ch14-fl-search-new"] = {
  "version": 1,
  "id": "ch14-fl-search-new",
  "title": "C13 · 第二篇终于可搜",
  "method": "POST",
  "path": "/tut-l14-flush/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "flush-only"
      }
    }
  },
  "predict": "和 C11 比，哪个条件变了？",
  "expect": "hits.total.value=1。唯一主动改变是 C12 的外部 refresh；用这个对照验证 flush 与外部可见性分开，而不是依靠操作速度或固定段数。"
};
  window.ESEXPERIMENTS["ch14-30-seg-setup"] = {
  "version": 1,
  "id": "ch14-30-seg-setup",
  "title": "D1 · 新建 tut-l14-seg",
  "method": "PUT",
  "path": "/tut-l14-seg",
  "body": {
    "settings": {
      "index.mode": "standard",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "translog.durability": "request",
      "translog.sync_interval": "5s",
      "translog.flush_threshold_age": "1h",
      "translog.flush_threshold_size": "10gb",
      "mapping.source.mode": "stored",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "routing_partition_size": 1,
      "write.wait_for_active_shards": "1"
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "enabled": true
      },
      "properties": {
        "title": {
          "type": "keyword"
        },
        "n": {
          "type": "integer"
        }
      }
    }
  },
  "predict": "先清理本课索引；无匹配模板、外部写入或刷新。为什么同时明确刷新与耐久配置？",
  "expect": "HTTP 200，acknowledged=true；若已存在则 400，先清理再从本组开始。普通索引、1 主 0 副、严格 mapping、stored source、无管道；-1 关闭周期 refresh，request 等待日志同步。1h 推迟年龄 flush，不会关闭全部后台维护。"
};
  window.ESEXPERIMENTS["ch14-d-health"] = {
  "version": 1,
  "id": "ch14-d-health",
  "title": "D2 · 等待本组主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l14-seg?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=10s",
  "body": null,
  "predict": "只看本组索引，green 能替代实验前提吗？",
  "expect": "需 status=green、timed_out=false、active_primary_shards=1、active_shards=1。超时先恢复分配再继续；其他索引可让整个集群 yellow。此卡不证明磁盘同步或源码内部路径。"
};
  window.ESEXPERIMENTS["ch14-31-seg-bulk-a"] = {
  "version": 1,
  "id": "ch14-31-seg-bulk-a",
  "title": "D3 · 第一批三篇并 refresh",
  "method": "POST",
  "path": "/tut-l14-seg/_bulk?refresh=true",
  "body": "{\"index\":{\"_id\":\"1\"}}\n{\"title\":\"seg-a\",\"n\":1}\n{\"index\":{\"_id\":\"2\"}}\n{\"title\":\"seg-b\",\"n\":2}\n{\"index\":{\"_id\":\"3\"}}\n{\"title\":\"seg-c\",\"n\":3}\n",
  "predict": "一批 bulk + 一次 refresh,会造出几个段?",
  "expect": "首次三条 status=201 / created、errors=false；重复 index 为 200 / updated。refresh=true 发布涉及的分片视图，不修改 refresh_interval。落段与后台 merge 时序独立，不能保证恰好一个新段。"
};
  window.ESEXPERIMENTS["ch14-32-seg-bulk-b"] = {
  "version": 1,
  "id": "ch14-32-seg-bulk-b",
  "title": "D4 · 第二批三篇并 refresh",
  "method": "POST",
  "path": "/tut-l14-seg/_bulk?refresh=true",
  "body": "{\"index\":{\"_id\":\"4\"}}\n{\"title\":\"seg-d\",\"n\":4}\n{\"index\":{\"_id\":\"5\"}}\n{\"title\":\"seg-e\",\"n\":5}\n{\"index\":{\"_id\":\"6\"}}\n{\"title\":\"seg-f\",\"n\":6}\n",
  "predict": "第二个段会和第一个合并吗?什么时候合?",
  "expect": "首次三条 created、errors=false。此时外部视图有六个业务 ID；段数受自动落段和后台合并影响。多段与已合并都合法，本组记录实际段名而不赌段数。"
};
  window.ESEXPERIMENTS["ch14-33-seg-segments"] = {
  "version": 1,
  "id": "ch14-33-seg-segments",
  "title": "D5 · 记录实际段与两种状态",
  "method": "GET",
  "path": "/tut-l14-seg/_segments",
  "body": null,
  "predict": "有几个 segment?每段几篇文档、多大?",
  "expect": "逐段记录 num_docs、deleted_docs、size_in_bytes、committed、search。可有 search=true / committed=false，也可已后台 commit。不要依靠恰好 2 段或每段 3 篇；不存在 deleted_in_bytes 字段。"
};
  window.ESEXPERIMENTS["ch14-34-seg-update"] = {
  "version": 1,
  "id": "ch14-34-seg-update",
  "title": "D6 · 修改 ID 1",
  "method": "POST",
  "path": "/tut-l14-seg/_update/1?refresh=true",
  "body": {
    "doc": {
      "n": 99
    }
  },
  "predict": "Lucene 有原地更新吗?旧版本去哪了?",
  "expect": "首次 updated / _version=2。旧版本软删除，再写新版本；重复同一个 doc 可 noop。refresh=true 使新外部视图生效；恢复所需的软删除历史可能继续保留。"
};
  window.ESEXPERIMENTS["ch14-35-seg-deleted"] = {
  "version": 1,
  "id": "ch14-35-seg-deleted",
  "title": "D7 · 记录更新后的删除统计",
  "method": "GET",
  "path": "/tut-l14-seg/_segments",
  "body": null,
  "predict": "删除标记体现在哪个字段?",
  "expect": "观察真实 deleted_docs，可为 0 或正数；后台 merge 与保留策略影响它。不能强求 ≥1，更没有 deleted_in_bytes。判断更新成功用后面的 GET 与业务文档数；段统计只是另一份证据。"
};
  window.ESEXPERIMENTS["ch14-seg-stop-writes"] = {
  "version": 1,
  "id": "ch14-seg-stop-writes",
  "title": "D8 · 合并前停止本索引写入",
  "method": "PUT",
  "path": "/tut-l14-seg/_settings",
  "body": {
    "index.blocks.write": true
  },
  "predict": "为什么先明确停止写入？",
  "expect": "acknowledged=true；后续不再向此索引写文档。write block 不关闭搜索或本课点名 DELETE。只对六篇本课数据做 force merge；不把生产热索引套用这套实验。"
};
  window.ESEXPERIMENTS["ch14-36-seg-forcemerge"] = {
  "version": 1,
  "id": "ch14-36-seg-forcemerge",
  "title": "D9 · 等待强制合并完成",
  "method": "POST",
  "path": "/tut-l14-seg/_forcemerge?max_num_segments=1&flush=true&wait_for_completion=true",
  "body": null,
  "predict": "段数和 deleted_docs 各变成多少?这一步贵在哪?",
  "expect": "这是同步等待请求，返回 _shards，核对 failed=0、successful=1；不是“无响应 body”。max_num_segments=1 请求最多一个段，flush=true 默认还做 flush 与外部 refresh。软删除保留策略仍有效，不能承诺 deleted_docs=0。"
};
  window.ESEXPERIMENTS["ch14-37-seg-after"] = {
  "version": 1,
  "id": "ch14-37-seg-after",
  "title": "D10 · 合并后记录段",
  "method": "GET",
  "path": "/tut-l14-seg/_segments",
  "body": null,
  "predict": "现在几个段?num_docs 总共几篇?deleted 呢?",
  "expect": "静止的本组通常一个段；逐段记录 num_docs/deleted_docs/size_in_bytes/committed/search。六个业务 ID 不等于历史物理文档数；retention lease 与 safe commit 可使软删除继续占空间，不能据此判失败。"
};
  window.ESEXPERIMENTS["ch14-seg-readback"] = {
  "version": 1,
  "id": "ch14-seg-readback",
  "title": "D11 · 业务结果读回",
  "method": "GET",
  "path": "/tut-l14-seg/_doc/1",
  "body": null,
  "predict": "段里留着旧历史会让 GET 读错版本吗？",
  "expect": "found=true、_source.n=99，首次流程 _version=2。这验证当前业务版本；其他五个 ID 未更新。本组业务文档数可用 _count 另查，应为 6，不能把删除历史当成第七篇可见文档。"
};
  window.ESEXPERIMENTS["ch14-90-cleanup"] = {
  "version": 1,
  "id": "ch14-90-cleanup",
  "title": "清理 · 点名删除本课四个索引",
  "method": "DELETE",
  "path": "/tut-l14-nrt,tut-l14-tlog,tut-l14-flush,tut-l14-seg?ignore_unavailable=true",
  "body": null,
  "predict": "只删除这四个本课索引，重复清理会报缺失吗？",
  "expect": "acknowledged=true；显式点名、无通配符，ignore_unavailable=true 允许重复清理。删除四组数据及其 async/写 block 等索引设置。从 A0→A9、B1→B11、C1→C13、D1→D11 全部顺序重做；中途误重复则清理后重建。"
};
  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS["ch14-write-path"] = {
  "version": 1,
  "id": "ch14-write-path",
  "title": "一次写入的完整旅程：写入、可见、提交与合并",
  "speed": 2200,
  "steps": [
    {
      "svg": "<svg viewBox=\"0 0 760 360\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ch14-write-step-1\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><text x=\"380\" y=\"22\" text-anchor=\"middle\" class=\"fig-sub\">一次示例轨迹 · refresh / flush / merge 无固定必经顺序</text><rect x=\"20\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"120.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">客户端请求</text><text x=\"120.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">PUT _doc/1</text><line x1=\"224\" y1=\"76\" x2=\"274\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-1)\"/><rect x=\"280\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"380.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">协调与 IndexShard</text><text x=\"380.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">1 主分片 → shard 0</text><line x1=\"484\" y1=\"76\" x2=\"534\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-1)\"/><rect x=\"540\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"640.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">主分片内部</text><text x=\"640.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">InternalEngine.index</text><text x=\"380\" y=\"145\" text-anchor=\"middle\" class=\"fig-sub\">下层为状态观测 · 各列并非串行调用链</text><rect x=\"20\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"130.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Lucene / IndexWriter</text><text x=\"130.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">可写缓冲、段与 commit</text><text x=\"130.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">尚未写入</text><rect x=\"270\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"380.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Translog</text><text x=\"380.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">操作追加与耐久同步</text><text x=\"380.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">无本例操作</text><rect x=\"520\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"630.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">读取视图</text><text x=\"630.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">INTERNAL 与 EXTERNAL</text><text x=\"630.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">无新搜索视图</text><text x=\"380\" y=\"315\" text-anchor=\"middle\" class=\"fig-key\">第 1 步 · 请求发出</text><text x=\"380\" y=\"342\" text-anchor=\"middle\" class=\"fig-sub\">示例前提无其他写入或外部刷新；统计不是逐条 fsync 证明</text></svg>",
      "note": "前提：9.4.0 新建普通索引，1 主 0 副、显式 ID=1、无摄取管道、stored source、refresh=-1、durability=request；起初无数据。本图只举一次成功写入，箭头分别表示请求传递和操作写入，不代表跨分片总顺序。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 360\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ch14-write-step-2\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><text x=\"380\" y=\"22\" text-anchor=\"middle\" class=\"fig-sub\">一次示例轨迹 · refresh / flush / merge 无固定必经顺序</text><rect x=\"20\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"120.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">客户端请求</text><text x=\"120.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">PUT _doc/1</text><line x1=\"224\" y1=\"76\" x2=\"274\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-2)\"/><rect x=\"280\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"380.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">协调与 IndexShard</text><text x=\"380.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">1 主分片 → shard 0</text><line x1=\"484\" y1=\"76\" x2=\"534\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-2)\"/><rect x=\"540\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"640.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">主分片内部</text><text x=\"640.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">InternalEngine.index</text><text x=\"380\" y=\"145\" text-anchor=\"middle\" class=\"fig-sub\">下层为状态观测 · 各列并非串行调用链</text><rect x=\"20\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"130.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Lucene / IndexWriter</text><text x=\"130.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">可写缓冲、段与 commit</text><text x=\"130.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">计划待执行</text><rect x=\"270\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"380.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Translog</text><text x=\"380.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">操作追加与耐久同步</text><text x=\"380.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">无本例操作</text><rect x=\"520\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"630.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">读取视图</text><text x=\"630.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">INTERNAL 与 EXTERNAL</text><text x=\"630.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">外部视图不变</text><text x=\"380\" y=\"315\" text-anchor=\"middle\" class=\"fig-key\">第 2 步 · 主分片选定</text><text x=\"380\" y=\"342\" text-anchor=\"middle\" class=\"fig-sub\">示例前提无其他写入或外部刷新；统计不是逐条 fsync 证明</text></svg>",
      "note": "协调是角色，可和主分片在同一个节点。本例只有一个主分片，路由到 shard 0；IndexShard 准备 Engine.Index，InternalEngine 对 uid 加锁并制定版本计划。省略 bulk、复制、解析、节流和恢复分支。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 360\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ch14-write-step-3\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><text x=\"380\" y=\"22\" text-anchor=\"middle\" class=\"fig-sub\">一次示例轨迹 · refresh / flush / merge 无固定必经顺序</text><rect x=\"20\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"120.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">客户端请求</text><text x=\"120.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">PUT _doc/1</text><line x1=\"224\" y1=\"76\" x2=\"274\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-3)\"/><rect x=\"280\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"380.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">协调与 IndexShard</text><text x=\"380.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">1 主分片 → shard 0</text><line x1=\"484\" y1=\"76\" x2=\"534\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-3)\"/><rect x=\"540\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"640.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">主分片内部</text><text x=\"640.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">InternalEngine.index</text><text x=\"380\" y=\"145\" text-anchor=\"middle\" class=\"fig-sub\">下层为状态观测 · 各列并非串行调用链</text><rect x=\"20\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box-hot\"/><text x=\"130.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Lucene / IndexWriter</text><text x=\"130.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">可写缓冲、段与 commit</text><text x=\"130.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">写入已执行</text><rect x=\"270\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"380.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Translog</text><text x=\"380.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">操作追加与耐久同步</text><text x=\"380.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">尚未追加</text><rect x=\"520\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"630.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">读取视图</text><text x=\"630.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">INTERNAL 与 EXTERNAL</text><text x=\"630.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">外部视图不变</text><text x=\"380\" y=\"315\" text-anchor=\"middle\" class=\"fig-key\">第 3 步 · 先写 Lucene</text><text x=\"380\" y=\"342\" text-anchor=\"middle\" class=\"fig-sub\">示例前提无其他写入或外部刷新；统计不是逐条 fsync 证明</text></svg>",
      "note": "普通显式 ID 成功主路径：版本检查后分配 seq_no，再按计划写 Lucene。新 ID 可 addDocs，替换可 softUpdate；IndexWriter 可能自动落段，但旧 EXTERNAL reader 没因此切换。版本查找本身也可能需要 INTERNAL refresh。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 360\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ch14-write-step-4\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><text x=\"380\" y=\"22\" text-anchor=\"middle\" class=\"fig-sub\">一次示例轨迹 · refresh / flush / merge 无固定必经顺序</text><rect x=\"20\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"120.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">客户端请求</text><text x=\"120.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">PUT _doc/1</text><line x1=\"224\" y1=\"76\" x2=\"274\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-4)\"/><rect x=\"280\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"380.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">协调与 IndexShard</text><text x=\"380.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">1 主分片 → shard 0</text><line x1=\"484\" y1=\"76\" x2=\"534\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-4)\"/><rect x=\"540\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"640.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">主分片内部</text><text x=\"640.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">InternalEngine.index</text><text x=\"380\" y=\"145\" text-anchor=\"middle\" class=\"fig-sub\">下层为状态观测 · 各列并非串行调用链</text><rect x=\"20\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"130.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Lucene / IndexWriter</text><text x=\"130.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">可写缓冲、段与 commit</text><text x=\"130.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">写入已执行</text><rect x=\"270\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box-hot\"/><text x=\"380.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Translog</text><text x=\"380.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">操作追加与耐久同步</text><text x=\"380.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">Index 已追加</text><rect x=\"520\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"630.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">读取视图</text><text x=\"630.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">INTERNAL 与 EXTERNAL</text><text x=\"630.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">外部视图不变</text><text x=\"380\" y=\"315\" text-anchor=\"middle\" class=\"fig-key\">第 4 步 · 追加与同步分开</text><text x=\"380\" y=\"342\" text-anchor=\"middle\" class=\"fig-sub\">示例前提无其他写入或外部刷新；统计不是逐条 fsync 证明</text></svg>",
      "note": "非 translog 重放来源的成功写入随后追加 Translog.Index，按计划登记最近版本。追加不是 fsync；特定文档失败若已有 seq_no 可补 NoOp，未分配序号的冲突不走同一分支。location 默认不跟踪，不能把 VersionMap 当文档仓库。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 360\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ch14-write-step-5\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><text x=\"380\" y=\"22\" text-anchor=\"middle\" class=\"fig-sub\">一次示例轨迹 · refresh / flush / merge 无固定必经顺序</text><rect x=\"20\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"120.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">客户端请求</text><text x=\"120.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">PUT _doc/1</text><line x1=\"224\" y1=\"76\" x2=\"274\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-5)\"/><rect x=\"280\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"380.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">协调与 IndexShard</text><text x=\"380.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">1 主分片 → shard 0</text><line x1=\"484\" y1=\"76\" x2=\"534\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-5)\"/><rect x=\"540\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"640.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">主分片内部</text><text x=\"640.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">InternalEngine.index</text><text x=\"380\" y=\"145\" text-anchor=\"middle\" class=\"fig-sub\">下层为状态观测 · 各列并非串行调用链</text><rect x=\"20\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"130.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Lucene / IndexWriter</text><text x=\"130.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">可写缓冲、段与 commit</text><text x=\"130.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">可能已自动落段</text><rect x=\"270\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box-hot\"/><text x=\"380.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Translog</text><text x=\"380.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">操作追加与耐久同步</text><text x=\"380.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">同步条件已满足</text><rect x=\"520\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"630.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">读取视图</text><text x=\"630.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">INTERNAL 与 EXTERNAL</text><text x=\"630.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">GET 可读 / SEARCH 0</text><text x=\"380\" y=\"315\" text-anchor=\"middle\" class=\"fig-key\">第 5 步 · request 应答</text><text x=\"380\" y=\"342\" text-anchor=\"middle\" class=\"fig-sub\">示例前提无其他写入或外部刷新；统计不是逐条 fsync 证明</text></svg>",
      "note": "request 且有日志位置时，写后阶段等待同步再成功应答。本例首次为 201。默认 realtime GET 可读，可能读日志或 INTERNAL reader；没有外部 refresh 的 SEARCH 仍不见新数据。async 不要求此请求等同步，但后台可能已经同步。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 360\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ch14-write-step-6\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><text x=\"380\" y=\"22\" text-anchor=\"middle\" class=\"fig-sub\">一次示例轨迹 · refresh / flush / merge 无固定必经顺序</text><rect x=\"20\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"120.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">客户端请求</text><text x=\"120.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">PUT _doc/1</text><line x1=\"224\" y1=\"76\" x2=\"274\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-6)\"/><rect x=\"280\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"380.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">协调与 IndexShard</text><text x=\"380.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">1 主分片 → shard 0</text><line x1=\"484\" y1=\"76\" x2=\"534\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-6)\"/><rect x=\"540\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"640.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">主分片内部</text><text x=\"640.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">InternalEngine.index</text><text x=\"380\" y=\"145\" text-anchor=\"middle\" class=\"fig-sub\">下层为状态观测 · 各列并非串行调用链</text><rect x=\"20\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"130.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Lucene / IndexWriter</text><text x=\"130.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">可写缓冲、段与 commit</text><text x=\"130.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">NRT 文件可供读取</text><rect x=\"270\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"380.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Translog</text><text x=\"380.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">操作追加与耐久同步</text><text x=\"380.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">不因 refresh 裁剪</text><rect x=\"520\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box-hot\"/><text x=\"630.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">读取视图</text><text x=\"630.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">INTERNAL 与 EXTERNAL</text><text x=\"630.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">GET 可读 / SEARCH 1</text><text x=\"380\" y=\"315\" text-anchor=\"middle\" class=\"fig-key\">第 6 步 · 发布外部视图</text><text x=\"380\" y=\"342\" text-anchor=\"middle\" class=\"fig-sub\">示例前提无其他写入或外部刷新；统计不是逐条 fsync 证明</text></svg>",
      "note": "一次显式外部 refresh 让 EXTERNAL reader 接住数据，SEARCH 可见。NRT reader 打开可能落出 segment 文件；这不是 Lucene commit，也不因可搜索而裁日志。内部刷新只服务 INTERNAL，周期刷新不是可见性时限。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 360\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ch14-write-step-7\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><text x=\"380\" y=\"22\" text-anchor=\"middle\" class=\"fig-sub\">一次示例轨迹 · refresh / flush / merge 无固定必经顺序</text><rect x=\"20\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"120.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">客户端请求</text><text x=\"120.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">PUT _doc/1</text><line x1=\"224\" y1=\"76\" x2=\"274\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-7)\"/><rect x=\"280\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"380.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">协调与 IndexShard</text><text x=\"380.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">1 主分片 → shard 0</text><line x1=\"484\" y1=\"76\" x2=\"534\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-7)\"/><rect x=\"540\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"640.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">主分片内部</text><text x=\"640.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">InternalEngine.index</text><text x=\"380\" y=\"145\" text-anchor=\"middle\" class=\"fig-sub\">下层为状态观测 · 各列并非串行调用链</text><rect x=\"20\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box-hot\"/><text x=\"130.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Lucene / IndexWriter</text><text x=\"130.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">可写缓冲、段与 commit</text><text x=\"130.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">commit 含恢复元数据</text><rect x=\"270\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"380.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Translog</text><text x=\"380.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">操作追加与耐久同步</text><text x=\"380.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">按 safe commit 裁剪</text><rect x=\"520\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"630.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">读取视图</text><text x=\"630.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">INTERNAL 与 EXTERNAL</text><text x=\"630.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">外部视图沿用第 6 步</text><text x=\"380\" y=\"315\" text-anchor=\"middle\" class=\"fig-key\">第 7 步 · 提交与可见性分开</text><text x=\"380\" y=\"342\" text-anchor=\"middle\" class=\"fig-sub\">示例前提无其他写入或外部刷新；统计不是逐条 fsync 证明</text></svg>",
      "note": "之后一次普通 flush：日志同步并滚代 → Lucene commit → INTERNAL refresh → 条件裁剪。此前已可搜只是本例的旧状态；直接 flush 未刷新的新文档不会负责发布 EXTERNAL。safe commit 与引用决定日志保留，不承诺计数或字节归零。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 360\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ch14-write-step-8\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><text x=\"380\" y=\"22\" text-anchor=\"middle\" class=\"fig-sub\">一次示例轨迹 · refresh / flush / merge 无固定必经顺序</text><rect x=\"20\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"120.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">客户端请求</text><text x=\"120.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">PUT _doc/1</text><line x1=\"224\" y1=\"76\" x2=\"274\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-8)\"/><rect x=\"280\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"380.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">协调与 IndexShard</text><text x=\"380.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">1 主分片 → shard 0</text><line x1=\"484\" y1=\"76\" x2=\"534\" y2=\"76\" class=\"fig-arrow\" marker-end=\"url(#ch14-write-step-8)\"/><rect x=\"540\" y=\"40\" width=\"200\" height=\"72\" rx=\"9\" class=\"fig-box\"/><text x=\"640.0\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">主分片内部</text><text x=\"640.0\" y=\"91\" text-anchor=\"middle\" class=\"fig-key\">InternalEngine.index</text><text x=\"380\" y=\"145\" text-anchor=\"middle\" class=\"fig-sub\">下层为状态观测 · 各列并非串行调用链</text><rect x=\"20\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box-hot\"/><text x=\"130.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Lucene / IndexWriter</text><text x=\"130.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">可写缓冲、段与 commit</text><text x=\"130.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">段可被合并重写</text><rect x=\"270\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"380.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">Translog</text><text x=\"380.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">操作追加与耐久同步</text><text x=\"380.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">不由 merge 决定同步</text><rect x=\"520\" y=\"166\" width=\"220\" height=\"116\" rx=\"10\" class=\"fig-box\"/><text x=\"630.0\" y=\"194\" text-anchor=\"middle\" class=\"fig-name\">读取视图</text><text x=\"630.0\" y=\"222\" text-anchor=\"middle\" class=\"fig-sub\">INTERNAL 与 EXTERNAL</text><text x=\"630.0\" y=\"255\" text-anchor=\"middle\" class=\"fig-key\">保留完整静态含义</text><text x=\"380\" y=\"315\" text-anchor=\"middle\" class=\"fig-key\">第 8 步 · 合并时保留所需历史</text><text x=\"380\" y=\"342\" text-anchor=\"middle\" class=\"fig-sub\">示例前提无其他写入或外部刷新；统计不是逐条 fsync 证明</text></svg>",
      "note": "merge 是独立的可选后台工作，可在 flush 前后发生，也可能暂时没有可合并段。它重写段并按保留策略回收删除历史；恢复所需软删除可能继续存在。不是每次 refresh 都产生一个新段，也不是每次 merge 都清掉全部旧版本。"
    }
  ]
};
})();
