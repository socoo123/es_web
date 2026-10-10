/* experiments/ch03.js — 第 3 课:实验 + 启动时序动画 */
(function () {
  'use strict';

  /* ===== 动画:正常启动的关键门禁(省略部分内部服务) ===== */
  var STATIONS = [
    { name: '构造完成 · INITIALIZED', sub: '目录锁已取得，服务对象已装配',
      note: 'NodeConstruction 完成构造并取得 node.lock；当前节点尚未通过 Node.start 打开 HTTP。改端口不能绕过目录互斥。' },
    { name: 'moveToStarted()', sub: '先设置 STARTED，再启动组件',
      note: 'STARTED 是 start() 开头的标志，不是对外服务已就绪的证据；随后才启动插件及索引、搜索等服务。' },
    { name: 'TransportService.start()', sub: '绑定节点通信地址，尚待接收请求',
      note: '先绑定 Transport，再建立后续协调所需的本地节点信息。acceptIncomingRequests() 位于校验与集群服务启动之后；端口常用 9300，但可配置。' },
    { name: 'GatewayMetaState.start()', sub: '读取磁盘元数据，交给启动检查',
      note: '恢复的持久化集群元数据传给 BootstrapContext，让内置及插件检查能判断历史状态相关的前置条件。' },
    { name: 'Bootstrap Checks', sub: '按地址、构建、发现模式及例外决定强制',
      note: '普通自动强制看 Transport 的 bind/publish 非 loopback、非 snapshot、非 single-node；显式强制及 alwaysEnforce 另算。非强制失败可告警后继续。' },
    { name: 'acceptIncomingRequests / startInitialJoin', sub: '接收 Transport，发起选主或入群',
      note: 'coordinator 与 cluster service 启动后接收 Transport 请求，再发起初始入群。方法调用表示开始推进，不代表入群已经成功。' },
    { name: '初始集群状态等待', sub: '默认 30s；超时告警继续，0 跳过',
      note: '等待含 master 的状态；超时仅告警并结束等待。配置为 0 时跳过；关闭中断另有提前返回路径。本动画只画正常继续启动。' },
    { name: 'HttpServerTransport.start()', sub: 'HTTP 开启；返回及后处理后才发 READY',
      note: 'HTTP 后还有可选 ReadinessService、端口文件及插件回调；入口在启动返回及自己的后处理后才通知 READY。HTTP 与 READY 都不能替代集群健康判断。' }
  ];

  function stepSvg(hotIx) {
    var s = '<svg viewBox="0 0 760 612" xmlns="http://www.w3.org/2000/svg">';
    var y0 = 34, gap = 72;
    for (var i = 0; i < STATIONS.length; i++) {
      var y = y0 + i * gap;
      var done = i < hotIx, hot = i === hotIx;
      // 竖线
      if (i < STATIONS.length - 1) {
        s += '<line x1="46" y1="' + (y + 13) + '" x2="46" y2="' + (y + gap - 6) + '" class="fig-arrow"'
          + (i < hotIx ? '' : ' opacity="0.3"') + '/>';
      }
      // 圆点
      s += '<circle cx="46" cy="' + (y + 7) + '" r="8" class="' + (hot ? 'fig-box-hot fp-pop' : 'fig-box') + '"/>';
      if (done) s += '<text x="46" y="' + (y + 11) + '" text-anchor="middle" class="fig-key">✓</text>';
      // 站台框
      var op = hot || done ? 1 : 0.42;
      s += '<g opacity="' + op + '">';
      s += '<rect x="80" y="' + (y - 8) + '" width="666" height="60" rx="8" class="' + (hot ? 'fig-box-hot' : 'fig-box') + '"/>';
      s += '<text x="96" y="' + (y + 11) + '" class="fig-name">' + (i + 1) + '. ' + STATIONS[i].name + '</text>';
      s += '<text x="96" y="' + (y + 36) + '" class="fig-sub">' + STATIONS[i].sub + '</text>';
      s += '</g>';
    }
    s += '</svg>';
    return s;
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch03-boot'] = {
    version: 1,
    id: 'ch03-boot',
    title: '启动八步:HTTP、READY 与集群健康分开判断',
    speed: 2000,
    steps: STATIONS.map(function (st, i) {
      return { svg: stepSvg(i), note: st.note };
    })
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch03-01-nodes'] = {
    version: 1, id: 'ch03-01-nodes',
    title: '实验 1 · 节点身份与 HTTP 发布地址',
    method: 'GET', path: '/_cat/nodes?v&h=name,id,pid,http,version',
    predict: '连接 ES 9.4.0，按端点配置认证。会有几行？http 列是绑定地址、发布地址还是浏览器连接的地址？',
    expect: '每行对应集群视图中的节点；http 取该节点的 HTTP publishAddress，可能不同于代理或容器映射入口。PID 属于服务器进程所在的命名空间。成功不能证明 green，也不能还原完整启动时序；多节点行数随实际集群变化。本请求只读，可重复，无需清理。'
  };
  window.ESEXPERIMENTS['ch03-02-process'] = {
    version: 1, id: 'ch03-02-process',
    title: '实验 2 · 进程号与 mlockall',
    method: 'GET', path: '/_nodes/process?filter_path=nodes.*.process.id,nodes.*.process.mlockall',
    predict: 'process.mlockall 报配置值还是实际锁定结果？false 能否证明没有设置 bootstrap.memory_lock？',
    expect: 'id 是服务器 JVM 的 PID；mlockall 是实际内存锁定状态。false 可能未请求锁定，也可能请求后未成功；结合 bootstrap.memory_lock、系统限制和启动日志判断。多节点各有一个对象；本请求只读，可重复，无需清理。'
  };
})();
