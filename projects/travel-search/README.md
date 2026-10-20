# 旅游搜索 Elasticsearch 实验工程

用景点/酒店/房型搜索学习 ES，实验在本机运行。教程从 [F01 导学](../../framework/f01.html)开始，F02 概念推演、F03 首次启动、F07 引入 Spring Boot 4 / JDK 25 与本机搜索展示壳。F01–F03 已完成；F04 字段建模、F05 关键词查询与 F06 组合筛选正文/脚本已交付，真实 ES 待验收；F07 Java接口与本机展示壳及F08多字段与高亮已交付，F09–F45待实施，验收见 [STATUS.md](../../STATUS.md)。

当前入口是 [F03 首搜](../../framework/f03.html)、[F03 手工实验](labs/f03/README.md)与[两轮真实 ES 记录](review/f03/README.md)，无需前端、Java、数据库或 Kibana。[F04 字段设计与 Bulk](../../framework/f04.html)及其[本机步骤](labs/f04/README.md)已提供；[执行状态](review/f04/README.md)明确记录本环境启动阻塞，尚未两轮实测。F04 从新资源独立开始，不依赖 F03 索引。历史文件、资源与案例 ID 保留：

- [历史启动实验正文](../../framework/f01-startup-legacy.html)
- [手工步骤、案例与重做](labs/f01/README.md)
- [两轮真实 ES 验收](review/f01/README.md)
- [45 课路线](../../FRAMEWORK_PLAN.md)

下面命令对应当前资源 `tut-f03-attractions` 与 `labs/f03`，配置和脚本保持原实验约定。

需要 Docker Engine/Desktop、Compose v2+、Bash 与 curl（7.76+，支持 `--fail-with-body`）。Docker Desktop 至少分配 4GB 内存；本课一个容器上限 1GB、堆 512MB。这是几条文档的教学配置；更多语料和多节点另做容量测量。Windows 可在 WSL2 中运行；F03 实际 ES 验收为 macOS arm64 + Docker，F04/F05/F06 云环境启动受阻，未声称 Windows/Linux 全平台验收。

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

## F05 · 名称关键词与精确条件

[F05 正文](../../framework/f05.html)沿用五份固定景点，比较 term/match 的 OR、AND、keyword 完整值与 slop=0 短语。新增独立索引 `tut-f05-attractions`，3案例、22条教学请求；与F04正确数据/mapping一致，可独立准备。

- [固定资料](data/f05/attractions.json)、[完整查询与预测](search/f05/expected.json)
- [本机入口、ID对照与点名重做](labs/f05/README.md)
- [真实执行状态与两轮验收脚本](review/f05/README.md)

正文、图解与阅读记录已交付；本轮云环境 ES9.4.0 在HTTP前因缺少 `/proc/self/coredump_filter` 退出，真实API/两轮未通过。预测不是响应，未交付本机展示壳或Java功能；F06将组合城市/预算/状态/距离条件。


## F06 · bool 与组合筛选

[F06 正文](../../framework/f06.html)将名称、城市、CNY预算、开放和3km组合起来；独立索引 `tut-f06-attractions`，保留原五份资料，新增七份边界，3案例、22条教学请求。

- [固定12份资料](data/f06/attractions.json)、[16组查询与预测](search/f06/expected.json)
- [本机步骤、完整请求与点名重做](labs/f06/README.md)
- [真实执行状态与两轮脚本](review/f06/README.md)

包含20000/20001分、免费/缺价/null、未知状态/无坐标、半径外，以及should默认门槛和过滤评分对照。正文与阅读可交付；云环境原Compose本轮仍在HTTP前启动失败，真实ES待验收。F07才引入Java与配套本机展示壳。

## F07 · Java接口与本机展示壳

[F07正文](../../framework/f07.html)将F06已理解的条件接入Boot4.0.8 / JDK25 / 官方Java与Rest5 Client9.4.8。使用独立tut-f07-attractions，沿用十二份固定资料；浏览器只调用本机Java，Pages只承载教程。

- [应用构建、版本与契约](backend/README.md)，同源展示壳随应用提供，默认127.0.0.1:18080
- [三案例/17条教学请求与点名重做](labs/f07/README.md)，[完整输入与DSL](search/f07/near.json)
- [ES/Java两轮、依赖树与制品](review/f07/README.md)，[本机展示壳与阅读验收](../../docs/framework-review/20261020-f07-java/README.md)

REST/Java逐项核对ID、价格、total/relation与实际序列化DSL；200元→80元、空结果、非法输入、索引缺失、ES停机/同进程恢复分别验证。本课不提供多字段/高亮/聚合/分页；F04–F06历史云环境受阻状态不回填。


## F08 · 多字段与高亮

[F08正文](../../framework/f08.html)在同一F07工程增加普通业务aliases字段、multi_match/best_fields AND、copy_to对照与安全文本段DTO。独立tut-f08-attractions，保留十二份原资料并补别名，新增三份边界，共十五份。

- [三案例/15条教学请求、启动与重做](labs/f08/README.md)，[固定资料](data/f08/attractions.json)、[主DSL](search/f08/multi.json)
- 新接口`POST /api/attractions/multi-search`，展示壳`http://127.0.0.1:18080/f08.html`；原F07接口与根路径保留
- [ES/Java两轮](review/f08/README.md)、[真实浏览器/阅读/图解验收](../../docs/framework-review/20261020-f08-multifield/README.md)

西湖多字段5条、钱塘湖别名1条、copy_to额外split、片段缺失回退、原文HTML纯文本显示分别核对；不把显示高亮当成评分解释或实体识别。F09再学习聚合计数。
