/* experiments/ch03.js — 第 3 课:实验 + 启动时序动画 */
(function () {
  'use strict';

  /* ===== 动画:Node.start() 点亮顺序(竖版时间线)===== */
  var STATIONS = [
    { name: '构造完成 · INITIALIZED', sub: '上百个组件已由 Guice 装配,但没有对外端口',
      note: 'new Node() 走完:线程池、脚本、分析器、集群服务都在内存里了。此时 curl 9200 一定不通。' },
    { name: 'TransportService.start()', sub: '节点间 TCP 通道打开(9300)',
      note: '先有节点间通信,后面的选主/入群才有物理载体。' },
    { name: 'GatewayMetaState.start()', sub: '读出磁盘上上次的集群元数据',
      note: '源码注释写明:读全局状态是 to pass it to the bootstrap checks——检查要看「这节点以前管过什么」。' },
    { name: 'Bootstrap Checks', sub: '堆 / fd / mlockall / mmap…(非 loopback 才强制)',
      note: '开发绑 127.0.0.1 时检查失败只 WARN;0.0.0.0 + 非 single-node 才会拒绝启动。' },
    { name: 'Coordinator.startInitialJoin()', sub: '加入(或组建)集群',
      note: '选主/入群。第 22 课会拆开这段的共识细节。' },
    { name: 'HttpServerTransport.start()', sub: '最后一扇门:9200 打开',
      note: '源码注释:DO NOT ADD NEW START CALLS BELOW HERE。此刻才给 CLI 发 READY——curl 通了。' }
  ];

  function stepSvg(hotIx) {
    var s = '<svg viewBox="0 0 760 320" xmlns="http://www.w3.org/2000/svg">';
    var y0 = 30, gap = 47;
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
      s += '<rect x="80" y="' + (y - 6) + '" width="666" height="38" rx="8" class="' + (hot ? 'fig-box-hot' : 'fig-box') + '"/>';
      s += '<text x="96" y="' + (y + 11) + '" class="fig-name">' + (i + 1) + '. ' + STATIONS[i].name + '</text>';
      s += '<text x="420" y="' + (y + 11) + '" class="fig-sub">' + STATIONS[i].sub + '</text>';
      s += '</g>';
    }
    s += '</svg>';
    return s;
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch03-boot'] = {
    version: 1,
    id: 'ch03-boot',
    title: 'Node.start() 点亮顺序:HTTP 是最后一扇门',
    speed: 2000,
    steps: STATIONS.map(function (st, i) {
      return { svg: stepSvg(i), note: st.note };
    })
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch03-01-nodes'] = {
    version: 1, id: 'ch03-01-nodes',
    title: '实验 1 · curl 得通 = 最后一扇门已开',
    method: 'GET', path: '/_cat/nodes?v&h=name,id,pid,http,version',
    predict: '这行命令成功,说明启动链走到了哪一站?http 列会显示什么地址?',
    expect: '成功 = 走到了最后一站(HttpServerTransport.start 之后)。http 列是绑定地址:docker 容器里通常非 loopback,但 discovery.type=single-node 让 enforceLimits 仍为 false——强制检查的三条件(非 loopback + 非 snapshot + 非 single-node)缺一不可。'
  };
  window.ESEXPERIMENTS['ch03-02-process'] = {
    version: 1, id: 'ch03-02-process',
    title: '实验 2 · 进程号与 mlockall',
    method: 'GET', path: '/_nodes/process?filter_path=nodes.*.process.id,nodes.*.process.mlockall',
    predict: 'process.mlockall 是 true 还是 false?它对应哪个 bootstrap 配置?',
    expect: '通常 false:我们没配 bootstrap.memory_lock(生产建议开,防堆被换出导致 GC 暂停从毫秒变秒级)。同时能看到进程 pid——正是拿 node.lock 的那个进程。'
  };
})();
