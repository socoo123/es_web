window.FPROJECTREQUESTS = window.FPROJECTREQUESTS || {};
window.FPROJECTREQUESTS['f01-01-health'] = {
  version: 1, id: 'f01-01-health', title: '请求 Java 健康 API',
  method: 'GET', endpoint: 'http://127.0.0.1:8080', path: '/api/health',
  command: 'curl -i http://127.0.0.1:8080/api/health',
  predict: 'Java 启动后应返回什么？只看到 HTTP 200，能证明 ES 也健康吗？',
  expect: 'HTTP 200；JSON 为 {"status":"UP","service":"travel-portal","stage":"F01"}。这里只检查 Java 请求处理；本课没有接入 ES、数据库或库存。停止 Java 后请求失败，重新启动后恢复。',
};
