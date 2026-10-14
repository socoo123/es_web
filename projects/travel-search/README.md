# 旅游搜索 Elasticsearch 实验工程

用景点/酒店/房型搜索学习 ES，实验在本机运行。当前只交付 **F01**，不需要前端、Java、数据库或 Kibana。后续 F02 的应用基线是 Spring Boot 4 / JDK 25；本目录现在没有旧 Boot 3 / Java 21 工程，也没有声称新 Java 基线已构建。

- [F01 教程](../../framework/f01.html)
- [F01 手工步骤、案例与重做](labs/f01/README.md)
- [作者真实验收](review/f01/README.md)
- [45 课规划](../../FRAMEWORK_PLAN.md)

需要 Docker Engine/Desktop、Compose v2+、Bash 与 curl（7.76+，支持 `--fail-with-body`）。Docker Desktop 至少分配 4GB 内存；本课一个容器上限 1GB、堆 512MB。这是几条文档的教学配置；更多语料和多节点另做容量测量。Windows 可在 WSL2 中运行；当前实际验收为 macOS arm64 + Docker，未声称 Windows/Linux 全平台验收。

在仓库根目录执行：

```bash
cd projects/travel-search
bash labs/f01/run.sh
```

它按顺序启动隔离 ES、观察、建索引、写文档、刷新、搜索和核对。第二次先按本课清理步骤删除 `tut-f01-attractions`；脚本不会暗中删除已有索引。脚本默认只访问 `http://127.0.0.1:19200`，Compose project 为 `es-framework-single`；不复用源码篇 9200/9201 服务，不发布 transport 9300。

F01 显式关闭安全，仅绑定本机。正式安全连接在 F35 学习；Docker 官方默认安全启动流程不同。本课不需要 CORS，因为 curl 直接访问 ES，Pages 只用于阅读。

```bash
# 保留容器和数据，暂时停止本工程 ES。
docker compose -f infra/single-node/compose.yaml stop es
# 再次启动仍保留数据。
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
```

数据保存在 Compose 卷 `es-framework-single_es-data`；停止/重启容器不会删除该卷。不要为了重做一课运行 `down -v`，按课次点名清理索引即可。
