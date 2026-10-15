# 旅游搜索 Elasticsearch 实验工程

用景点/酒店/房型搜索学习 ES，实验在本机运行。教程从 [F01 导学](../../framework/f01.html)开始，F02 概念推演、F03 首次启动、F07 引入 Spring Boot 4 / JDK 25 与本机搜索展示壳。F01–F03 已完成；F04 字段建模正文/脚本已交付，真实 ES 待验收；F05–F45、Java 与展示壳待实施，验收见 [STATUS.md](../../STATUS.md)。

当前入口是 [F03 首搜](../../framework/f03.html)、[F03 手工实验](labs/f03/README.md)与[两轮真实 ES 记录](review/f03/README.md)，无需前端、Java、数据库或 Kibana。[F04 字段设计与 Bulk](../../framework/f04.html)及其[本机步骤](labs/f04/README.md)已提供；[执行状态](review/f04/README.md)明确记录本环境启动阻塞，尚未两轮实测。F04 从新资源独立开始，不依赖 F03 索引。历史文件、资源与案例 ID 保留：

- [历史启动实验正文](../../framework/f01-startup-legacy.html)
- [手工步骤、案例与重做](labs/f01/README.md)
- [两轮真实 ES 验收](review/f01/README.md)
- [45 课路线](../../FRAMEWORK_PLAN.md)

下面命令对应当前资源 `tut-f03-attractions` 与 `labs/f03`，配置和脚本保持原实验约定。

需要 Docker Engine/Desktop、Compose v2+、Bash 与 curl（7.76+，支持 `--fail-with-body`）。Docker Desktop 至少分配 4GB 内存；本课一个容器上限 1GB、堆 512MB。这是几条文档的教学配置；更多语料和多节点另做容量测量。Windows 可在 WSL2 中运行；当前实际验收为 macOS arm64 + Docker，未声称 Windows/Linux 全平台验收。

在仓库根目录执行：

```bash
cd projects/travel-search
bash labs/f03/run.sh
```

它按顺序启动隔离 ES、观察、建索引、写文档、刷新、搜索和核对。第二次先按本课清理步骤删除 `tut-f03-attractions`；脚本不会暗中删除已有索引。脚本默认只访问 `http://127.0.0.1:19200`，Compose project 为 `es-framework-single`；不复用源码篇 9200/9201 服务，不发布 transport 9300。

本课显式关闭安全，仅绑定本机。正式安全连接在 F35 学习；Docker 官方默认安全启动流程不同。本课不需要 CORS，因为 curl 直接访问 ES，Pages 只用于阅读。

```bash
# 保留容器和数据，暂时停止本工程 ES。
docker compose -f infra/single-node/compose.yaml stop es
# 再次启动仍保留数据。
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
```

数据保存在 Compose 卷 `es-framework-single_es-data`；停止/重启容器不会删除该卷。不要为了重做一课运行 `down -v`，按课次点名清理索引即可。
