# F35 真实执行证据

`run-01`、`run-02` 是两轮从点名清理开始的正式实验，均通过。每轮37教学REST＋8 Java接口HTTP、2 TLS失败调用；case为c01=13 HTTP、c02=14、c03=18（其中Java8）。身份/guard/cleanup与浏览器附加另计。每轮8观察点×1440/390×浅深=32次浏览器→Java，3成功点另有12次独立DSL REST重放；浏览器直连ES为0。

每轮的events.jsonl保留身份标签、请求路径、经遮盖的请求/响应。所有password/api_key/encoded遮盖；真实秘密仅在Git忽略的本机`.local`。原始私钥、密码、密钥和curl认证配置没有提交。

固定六份资料，p01/6000、p02/0；writer改价/删除后搜索只有p01/6500；修复后两份恢复。错误CA→Java503；错误密钥、writer越权搜索、撤销key与旧客户端→Java502；换文件仍502，重启新key后200。ES原始认证错误401、授权错误403与TLS无HTTP分别记录。

预演与修复单列：`init/summary.json`是OpenSSL默认配置缺失失败，`init-retry`显式openssl.cnf后通过；`setup`记录缺少Docker发布IP SAN的transport full握手失败，随后用固定网段/匹配IP重新签发；`setup-retry`检查误把Nodes Info过滤的verification_mode当成缺失而失败，修正为核对实际容器配置；`setup-verified`通过。`attempt-guard`因ES自动内部日志索引未列入白名单而停止，`attempt-recreate-status`因恢复已删p02实际201、断言只接受200而停止；修正后才完成两轮正式实验。这些尝试没有冒充正式通过。

`pre-fresh-cleanup/down`结束两轮原环境。随后只移除F35三卷、将原`.local`归档至主机受限临时目录，使用最终配置从空卷重新init/start；`fresh-init`、`fresh-setup`与`manual-*`验证读者手工路径和修正后的新环境入口。最终cleanup/down保留新三卷，只停止本课Java；原es-study-secure的身份/PID/启动时间另有前后核对。

应用构建/版本/资源与证书元数据见runtime.json；没有测试源，clean package不称单元测试通过。真实浏览器、HTTP阅读、实际视觉和内容自审见[验收目录](../../../../docs/framework-review/20261029-f35-security/README.md)。同VM/单master/短有效期证书与key仅为本课实验，不证明生产HA、自动轮换、独立故障域或性能。
