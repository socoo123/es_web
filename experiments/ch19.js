/* experiments/ch19.js — 第 19 课:聚合框架实验 + cherry 丢失演算动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:cherry 是怎么丢的 ===== */
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

  /* 步骤 1:请求到达 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s1');
    s += rect(15, 25, 730, 60, 'fig-box');
    s += txt(380, 49, '{"size":0,"aggs":{"top":{"terms":{"field":"fruit","size":2}}}}', 'fig-key');
    s += txt(380, 71, '两个单分片索引 s0 + s1 合搜 = 两次 Query + 一次协调 reduce', 'fig-sub');
    s += rect(15, 112, 730, 58, 'fig-box-hot', 'fp-pop');
    s += txt(380, 134, '聚合跟 hits 同一趟 Query 相位回来', 'fig-name');
    s += txt(380, 156, '塞进 QuerySearchResult.aggregations;Fetch 只搬 Top-N 正文,碰不到这棵树', 'fig-sub');
    s += txt(380, 204, 'size: 0 表示不要 hits,只要聚合——本课只关心桶', 'fig-sub');
    s += txt(380, 228, '主线:每个 shard 送几个桶,决定协调节点能看见谁', 'fig-sub');
    s += txt(380, 262, 'size 是客户端要的全局桶数,不是每个 shard 的配额', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 2:shard 本地计数 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s2');
    s += rect(15, 20, 355, 118, 'fig-box');
    s += txt(192, 44, 'shard 0 · 局部词频', 'fig-name');
    s += txt(192, 72, 'apple:6 banana:3 cherry:2', 'fig-key');
    s += txt(192, 96, 'cherry 本地第 3', 'fig-sub');
    s += txt(192, 120, '11 篇,3 个值', 'fig-sub');
    s += rect(390, 20, 355, 118, 'fig-box');
    s += txt(567, 44, 'shard 1 · 局部词频', 'fig-name');
    s += txt(567, 72, 'date:4 apple:4 cherry:3', 'fig-key');
    s += txt(567, 96, 'cherry 本地第 3', 'fig-sub');
    s += txt(567, 120, '11 篇,3 个值', 'fig-sub');
    s += rect(15, 158, 730, 62, 'fig-box', 'fp-pop');
    s += txt(380, 182, '收集期:出现过的每个值都记账', 'fig-name');
    s += txt(380, 204, '计数器个数跟字段基数走,不跟 size 走(高基数伏笔)', 'fig-sub');
    s += txt(380, 250, 'cherry 在两片都是本地第 3——但全局真实计数 5,是第 2 名', 'fig-sub', true);
    return s + '</svg>';
  }

  /* 步骤 3:shard_size=2 只送 Top-2 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s3');
    s += rect(15, 20, 355, 142, 'fig-box');
    s += txt(192, 44, 'shard 0 只送 Top-2', 'fig-name');
    s += txt(192, 74, 'apple:6 上送 / banana:3 上送', 'fig-key');
    s += txt(192, 104, 'cherry:2 丢弃', 'fig-key', true);
    s += txt(192, 130, '挤进本片 sum_other', 'fig-sub', true);
    s += rect(390, 20, 355, 142, 'fig-box');
    s += txt(567, 44, 'shard 1 只送 Top-2', 'fig-name');
    s += txt(567, 74, 'date:4 上送 / apple:4 上送', 'fig-key');
    s += txt(567, 104, 'cherry:3 丢弃', 'fig-key', true);
    s += txt(567, 130, '挤进本片 sum_other', 'fig-sub', true);
    s += rect(15, 182, 730, 58, 'fig-box-hot', 'fp-pop');
    s += txt(380, 204, 'shard_size=2 的语义', 'fig-name');
    s += txt(380, 226, '用户显式写了 shard_size,启发式不跑;优先队列长度 = min(值数, 2)', 'fig-sub');
    s += txt(380, 268, '截断发生在 buildAggregations,不是收集时只记 2 个', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 4:reduce 看不见 cherry */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s4');
    s += rect(15, 20, 730, 66, 'fig-box');
    s += txt(380, 44, '协调节点 reduce:同 key 相加', 'fig-name');
    s += txt(380, 72, 'apple 6+4=10 banana 3 date 4;cherry 两片都没送,合计当 0', 'fig-key');
    s += rect(15, 112, 730, 66, 'fig-box-hot', 'fp-pop');
    s += txt(380, 136, '截 size=2:apple:10、date:4', 'fig-name');
    s += txt(380, 164, '全局第 2 名 cherry:5 失踪,date:4 顶了上去', 'fig-sub', true);
    s += rect(15, 200, 730, 58, 'fig-box');
    s += txt(380, 222, '账本留痕,不补回', 'fig-name');
    s += txt(380, 244, 'sum_other_doc_count / doc_count_error_upper_bound 记「没送上来的桶」', 'fig-sub');
    s += txt(380, 284, '协调节点看不见的 key,reduce 永远加不回来', 'fig-sub', true);
    return s + '</svg>';
  }

  /* 步骤 5:默认启发式 13 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s5');
    s += rect(15, 25, 730, 64, 'fig-box');
    s += txt(380, 49, 'BucketUtils.suggestShardSideQueueSize', 'fig-name');
    s += txt(380, 77, 'shardSize = size * 1.5 + 10 = 2*1.5+10 = 13', 'fig-key');
    s += rect(15, 112, 730, 62, 'fig-box-hot', 'fp-pop');
    s += txt(380, 136, '13 ≥ 3:两片的桶全送', 'fig-name');
    s += txt(380, 158, 'cherry 两边都进得了队列——过采样保护的就是「本地第 3」', 'fig-sub');
    s += txt(380, 206, '只在用户没写 shard_size 且不是按 _key 排序时套用', 'fig-sub');
    s += txt(380, 228, 'ensureValidity 兜底:shardSize 至少抬到等于 size', 'fig-sub');
    s += txt(380, 262, '+10 是给小 size 的常数垫:只乘 1.5,size=2 才过采样到 3,刚刚好不够', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 6:final 截 2 + 对照 hits */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s6');
    s += rect(15, 20, 730, 62, 'fig-box-hot', 'fp-pop');
    s += txt(380, 44, 'final reduce 截 size=2', 'fig-name');
    s += txt(380, 70, 'apple:10、cherry:5 —— 全局第 2 回来了', 'fig-key');
    s += rect(15, 104, 355, 96, 'fig-box');
    s += txt(192, 128, 'terms 的窗口', 'fig-name');
    s += txt(192, 154, 'shardSize 过采样', 'fig-key');
    s += txt(192, 178, '近似保排名,压小误差上界', 'fig-sub');
    s += rect(390, 104, 355, 96, 'fig-box');
    s += txt(567, 128, 'hits 的窗口', 'fig-name');
    s += txt(567, 154, 'from + size', 'fig-key');
    s += txt(567, 178, '严格:第 k 名必在某片本地前 k', 'fig-sub');
    s += txt(380, 234, 'range / histogram 的桶 key 在请求里就定了,连过采样都不需要', 'fig-sub');
    s += txt(380, 262, '同一个「全局 vs 本地」不变量,hits 用严格窗口保,terms 只能近似保', 'fig-sub');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch19-shard-size'] = {
    version: 1,
    id: 'ch19-shard-size',
    title: 'cherry 是怎么丢的:shardSize 演算',
    speed: 2400,
    steps: [
      { svg: step1(), note: 'terms 的 size=2 是客户端要的全局桶数,不是每个 shard 的配额。聚合跟 hits 同一趟 Query 相位回来、不走 Fetch——没进全局 Top-N 的文档仍可能是某个桶的主力。' },
      { svg: step2(), note: 'shard 0:apple:6 banana:3 cherry:2;shard 1:date:4 apple:4 cherry:3。收集期给出现过的每个值记账(GlobalOrdinals 计数器),计数器个数跟基数走不跟 size 走。cherry 两片都是本地第 3,全局却是第 2。' },
      { svg: step3(), note: '显式写 shard_size=2:启发式不跑,优先队列只留 min(值数, 2) 个。截断发生在 buildAggregations——收集时仍然全记,出结果时才丢。cherry 在两片都被挤出队列,记进本片 sum_other。' },
      { svg: step4(), note: '协调节点只加它看见的桶:apple 6+4=10、banana 3、date 4;cherry 没人送,合计当 0。截 size=2 得 apple:10、date:4——真正的全局第 2 cherry:5 失踪。sum_other 和 error_bound 只是账本,不补回任何 key。' },
      { svg: step5(), note: '默认 shardSize = size×1.5+10 = 13 ≥ 每片 3 个值,全部上送,cherry 回到候选。这条启发式只在没写 shard_size 且非 key 序时启用;ensureValidity 还兜底 shardSize ≥ size。+10 是小 size 的常数垫。' },
      { svg: step6(), note: 'final reduce 才截客户端要的 size:apple:10、cherry:5,排名修正。hits 用 from+size 严格保住第 k 名(分数可比较),terms 按 count 加总,本地第 3 可合计成全局第 2——只能过采样近似。range/histogram 桶 key 事先定,无此问题。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  /* bulk 辅助:fruits([['apple',6,'tut-l19-s0'],...]) → ndjson */
  function fruits(pairs) {
    var out = [];
    pairs.forEach(function (p) {
      for (var i = 0; i < p[1]; i++) {
        out.push('{"index":{"_index":"' + p[2] + '"}}');
        out.push('{"fruit":"' + p[0] + '"}');
      }
    });
    return out.join('\n') + '\n';
  }
  /* card 辅助:20 个唯一 user_id */
  function userIds(n) {
    var out = [];
    for (var i = 1; i <= n; i++) {
      out.push('{"index":{"_index":"tut-l19-card"}}');
      out.push('{"user_id":"u-' + i + '"}');
    }
    return out.join('\n') + '\n';
  }

  window.ESEXPERIMENTS['ch19-00-setup-shop'] = {
    version: 1, id: 'ch19-00-setup-shop',
    title: '实验 0 · 建 tut-l19-shop:category/price/date',
    method: 'PUT', path: '/tut-l19-shop',
    body: {
      settings: { number_of_shards: 1, number_of_replicas: 0 },
      mappings: { properties: {
        category: { type: 'keyword' },
        price: { type: 'float' },
        date: { type: 'date' }
      } }
    },
    predict: 'terms 聚合跑在哪种字段上?text 还是 keyword?',
    expect: 'acknowledged: true。terms 要按字段值分桶,配的是 keyword——第 18 课的词典规则在这里同样成立:桶 key 就是整串。'
  };
  window.ESEXPERIMENTS['ch19-01-bulk-shop'] = {
    version: 1, id: 'ch19-01-bulk-shop',
    title: '实验 1 · 小店 8 篇:electronics/books/clothing',
    method: 'POST', path: '/_bulk?refresh=true',
    body: '{"index":{"_index":"tut-l19-shop"}}\n{"category":"electronics","price":299.99,"date":"2024-01-15"}\n{"index":{"_index":"tut-l19-shop"}}\n{"category":"books","price":19.99,"date":"2024-01-20"}\n{"index":{"_index":"tut-l19-shop"}}\n{"category":"electronics","price":149.99,"date":"2024-02-10"}\n{"index":{"_index":"tut-l19-shop"}}\n{"category":"clothing","price":49.99,"date":"2024-02-15"}\n{"index":{"_index":"tut-l19-shop"}}\n{"category":"books","price":29.99,"date":"2024-03-01"}\n{"index":{"_index":"tut-l19-shop"}}\n{"category":"electronics","price":599.99,"date":"2024-03-10"}\n{"index":{"_index":"tut-l19-shop"}}\n{"category":"books","price":24.99,"date":"2024-03-15"}\n{"index":{"_index":"tut-l19-shop"}}\n{"category":"clothing","price":79.99,"date":"2024-04-01"}\n',
    predict: 'electronics / books / clothing 各几篇?terms 会回几个桶?',
    expect: 'errors: false,8 项。electronics 3、books 3、clothing 2——默认 size=10 足够放下 3 个桶。'
  };
  window.ESEXPERIMENTS['ch19-02-terms-avg'] = {
    version: 1, id: 'ch19-02-terms-avg',
    title: '实验 2 · Bucket 套 Metric:by_category + avg_price',
    method: 'POST', path: '/tut-l19-shop/_search?filter_path=aggregations',
    body: {
      size: 0,
      aggs: {
        by_category: {
          terms: { field: 'category' },
          aggs: { avg_price: { avg: { field: 'price' } } }
        }
      }
    },
    predict: 'avg_price 会对全部 8 篇算,还是只在各自桶内算?hits 一条没有,size 哪去了?',
    expect: '3 个桶:electronics 3(avg 349.99)、books 3(24.99)、clothing 2(64.99);books 与 electronics 同为 3,先后以返回为准(平 count 按 key)。size:0 = 不要 hits 只要聚合——Bucket 改分组,Metric 在桶内算数。'
  };
  window.ESEXPERIMENTS['ch19-03-fixed-keys'] = {
    version: 1, id: 'ch19-03-fixed-keys',
    title: '实验 3 · date_histogram + range:桶 key 事先定',
    method: 'POST', path: '/tut-l19-shop/_search?filter_path=aggregations',
    body: {
      size: 0,
      aggs: {
        by_month: { date_histogram: { field: 'date', calendar_interval: 'month' } },
        price_ranges: { range: { field: 'price', ranges: [{ to: 50 }, { from: 50, to: 200 }, { from: 200 }] } } }
    },
    predict: '这两个聚合需要 shard_size 过采样吗?',
    expect: 'by_month 按 2024-01/02/03/04 出桶,price_ranges 出 *to-50*、*50-200*、*from-200* 三桶。桶的 key 在请求里就定了,各 shard 回同一组 key,协调节点只做加总——没有「全局第 2 被挤掉」,也没有 shardSize。'
  };
  window.ESEXPERIMENTS['ch19-04-setup-s0'] = {
    version: 1, id: 'ch19-04-setup-s0',
    title: '实验 4 · 建 tut-l19-s0(单分片)',
    method: 'PUT', path: '/tut-l19-s0',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 }, mappings: { properties: { fruit: { type: 'keyword' } } } },
    predict: '为什么用两个单分片索引,而不是一个两分片索引?',
    expect: 'acknowledged: true。两个索引合搜 = 确定的两次 Query + 一次协调 reduce;一个两分片索引的路由会受 _routing 哈希影响,词频可能不按预期落片。'
  };
  window.ESEXPERIMENTS['ch19-05-setup-s1'] = {
    version: 1, id: 'ch19-05-setup-s1',
    title: '实验 5 · 建 tut-l19-s1(单分片)',
    method: 'PUT', path: '/tut-l19-s1',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 }, mappings: { properties: { fruit: { type: 'keyword' } } } },
    predict: '两个索引的 mapping 必须一致吗?',
    expect: 'acknowledged: true。合搜时同名字段类型一致才能正常聚合;这里都是 fruit keyword。'
  };
  window.ESEXPERIMENTS['ch19-06-bulk-s0'] = {
    version: 1, id: 'ch19-06-bulk-s0',
    title: '实验 6 · s0:apple×6 banana×3 cherry×2',
    method: 'POST', path: '/_bulk?refresh=true',
    body: fruits([['apple', 6, 'tut-l19-s0'], ['banana', 3, 'tut-l19-s0'], ['cherry', 2, 'tut-l19-s0']]),
    predict: 'shard 0 的本地词频表写好了吗?cherry 排第几?',
    expect: 'errors: false,11 项。apple:6、banana:3、cherry:2——cherry 本地第 3,这就是后面被挤掉的伏笔。'
  };
  window.ESEXPERIMENTS['ch19-07-bulk-s1'] = {
    version: 1, id: 'ch19-07-bulk-s1',
    title: '实验 7 · s1:date×4 apple×4 cherry×3',
    method: 'POST', path: '/_bulk?refresh=true',
    body: fruits([['date', 4, 'tut-l19-s1'], ['apple', 4, 'tut-l19-s1'], ['cherry', 3, 'tut-l19-s1']]),
    predict: 'shard 1 的本地词频里 cherry 又排第几?',
    expect: 'errors: false,11 项。date:4、apple:4、cherry:3——cherry 又是本地第 3。两片都第 3,全局合计 5 却是第 2 名:动画步骤 2 的数字。'
  };
  window.ESEXPERIMENTS['ch19-08-true-global'] = {
    version: 1, id: 'ch19-08-true-global',
    title: '实验 8 · 先看真实全局(size 开大)',
    method: 'POST', path: '/tut-l19-s0,tut-l19-s1/_search?filter_path=aggregations',
    body: { size: 0, aggs: { top: { terms: { field: 'fruit', size: 10 } } } },
    predict: '四个词的全局名次?cherry 应在第几?',
    expect: 'apple:10、cherry:5、date:4、banana:3。这是标准答案——接下来两个实验分别演示「送少了」和「默认过采样」。'
  };
  window.ESEXPERIMENTS['ch19-09-shard-size-2'] = {
    version: 1, id: 'ch19-09-shard-size-2',
    title: '实验 9 · shard_size=2:cherry 被挤掉',
    method: 'POST', path: '/tut-l19-s0,tut-l19-s1/_search?filter_path=aggregations',
    body: {
      size: 0,
      aggs: { top: { terms: { field: 'fruit', size: 2, shard_size: 2, show_term_doc_count_error: true } } }
    },
    predict: '第二名是 cherry 还是 date?cherry 的计数 5 会出现在响应里吗?',
    expect: '桶:apple:10、date:4——cherry 失踪。每片只送本地 Top-2,cherry 两边都被挤出;协调节点看不见的 key,reduce 永远加不回来。sum_other_doc_count > 0、doc_count_error_upper_bound > 0,那是「没送上来的桶」的账,不是修正。'
  };
  window.ESEXPERIMENTS['ch19-10-default'] = {
    version: 1, id: 'ch19-10-default',
    title: '实验 10 · 默认启发式:shardSize=2×1.5+10=13',
    method: 'POST', path: '/tut-l19-s0,tut-l19-s1/_search?filter_path=aggregations',
    body: {
      size: 0,
      aggs: { top: { terms: { field: 'fruit', size: 2, show_term_doc_count_error: true } } }
    },
    predict: '去掉 shard_size,第二名会换人吗?error_bound 呢?',
    expect: '第二名回到 cherry:5。默认 shardSize = 2×1.5+10 = 13 ≥ 每片 3 个值,全部上送:每个 key 都被送来,doc_count_error_upper_bound 归 0;sum_other_doc_count 只剩 final 截掉的 banana:3 一类。过采样买回的是排名正确性。'
  };
  window.ESEXPERIMENTS['ch19-11-size3-shard2'] = {
    version: 1, id: 'ch19-11-size3-shard2',
    title: '实验 11 · size=3 + shard_size=2:被抬回去',
    method: 'POST', path: '/tut-l19-s0,tut-l19-s1/_search?filter_path=aggregations',
    body: {
      size: 0,
      aggs: { top: { terms: { field: 'fruit', size: 3, shard_size: 2 } } }
    },
    predict: 'shard_size=2 小于 size=3,ES 会照单全收地送 2 个吗?',
    expect: '三个桶:apple:10、cherry:5、date:4,全员到齐。ensureValidity 的不变量是 shardSize ≥ size——硬写 2 会被抬到 3,每片至少回 size 个,否则连「填满全局 Top-size」都做不到。shard_size 不是想写多小就多小。'
  };
  window.ESEXPERIMENTS['ch19-12-setup-card'] = {
    version: 1, id: 'ch19-12-setup-card',
    title: '实验 12 · 建 tut-l19-card(user_id keyword)',
    method: 'PUT', path: '/tut-l19-card',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 }, mappings: { properties: { user_id: { type: 'keyword' } } } },
    predict: '每篇文档一个不同 user_id,这叫什么?',
    expect: 'acknowledged: true。高基数字段:20 篇 20 个不同值。下一组实验看「size 只管返回,不管收集」。'
  };
  window.ESEXPERIMENTS['ch19-13-bulk-card'] = {
    version: 1, id: 'ch19-13-bulk-card',
    title: '实验 13 · 20 个唯一 user_id',
    method: 'POST', path: '/_bulk?refresh=true',
    body: userIds(20),
    predict: 'terms size=2,执行期会为几个值分配计数器?',
    expect: 'errors: false,20 项。答案在下一跑:计数器是 20 个,不是 2 个——size 限制返回和传输,不限制收集。'
  };
  window.ESEXPERIMENTS['ch19-14-card-terms'] = {
    version: 1, id: 'ch19-14-card-terms',
    title: '实验 14 · size=2 只回 2 桶,sum_other=18',
    method: 'POST', path: '/tut-l19-card/_search?filter_path=aggregations',
    body: { size: 0, aggs: { users: { terms: { field: 'user_id', size: 2 } } } },
    predict: 'sum_other_doc_count 会是几?这 18 个值是被「没收集」还是「收集后被丢」?',
    expect: '2 个桶(count 全是 1,先后以返回为准),sum_other_doc_count = 18。这 18 是收集了、build 时被优先队列丢掉、没进响应——执行期追踪出现过的全部值。放大到一百万基数,size=2 一样要为百万个计数器扩 BigArrays:先撞的是 request/parent breaker(第 25 课),不是网卡。'
  };
  window.ESEXPERIMENTS['ch19-15-breakers'] = {
    version: 1, id: 'ch19-15-breakers',
    title: '实验 15 · 只看一眼 breaker 的名字和限额',
    method: 'GET', path: '/_nodes/stats/breaker?filter_path=nodes.*.breakers.request,nodes.*.breakers.parent,nodes.*.breakers.fielddata',
    predict: '聚合的字节账记在哪个 breaker 上?现在 tripped 是几?',
    expect: 'request / parent / fielddata 的 limit_size_in_bytes 与 tripped(此刻应为 0)。每个聚合先挂一笔约 5kb 的 DEFAULT_WEIGHT,数组扩张再 addEstimateBytesAndMaybeBreak——怎么撞、95% 水位图,第 25 课拆,本课不调爆它。'
  };
  window.ESEXPERIMENTS['ch19-16-cleanup'] = {
    version: 1, id: 'ch19-16-cleanup',
    title: '清理 · 删 tut-l19-* 四个索引',
    method: 'DELETE', path: '/tut-l19-shop,tut-l19-s0,tut-l19-s1,tut-l19-card',
    predict: '一句话总结本课?',
    expect: 'acknowledged: true。size 是全局要留下的桶数,shardSize 是每片送多少;协调节点看不见的 key,reduce 加不回来。'
  };
})();
