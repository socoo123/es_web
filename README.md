# ES 源码精读站

> **🚀 在线阅读**:https://socoo123.github.io/es_web/
> (实验需配合本机 docker 里的 ES,见下文「部署到 GitHub Pages」)

30 课读完 **Elasticsearch 9.4.0** 的骨架与血肉:请求链路、Lucene 存储、搜索聚合、分布式共识。纯静态、零构建、零依赖——双击 `index.html` 即用;实验跑在你本机 docker 拉起的真实 ES 上。

- **30 课 · 六篇**,每课:架构图(SVG)+ 机制动画 + 动手实验(预测 → 操作 → 对照)
- **431 张实验操作卡 / 22 个机制播放器**，面向 ES 9.4.0；各章的实测范围与未验证项目见 [STATUS.md](STATUS.md)，Archify 路径动画另计。
- 双主题(暖白纸面 / 深海蓝),`file://` 直接可用

第一章已采用 [Archify 3.0.1](https://github.com/tt-a1i/archify) 重画倒排索引、分析链、分片副本三幅交互图，支持路径动画、暂停、重播和节点探索。[在线阅读第一章](https://socoo123.github.io/es_web/chapters/ch01.html)；可编辑图源、再生成方法和验证记录见 [.archify/README.md](.archify/README.md)。原有 11 个实验操作及近实时机制动画保留。

## 框架学习篇：用旅游搜索学会 ES

第一部分用同一个旅游搜索网站学习 ES，分为 **八阶段、45 课**：认识 ES 与首搜 → 景点搜索 → 中文召回 → 评分排序 → 酒店房型 → 集群运行 → 数据同步 → 独立实现与诊断。先讲 ES 干什么、解决什么问题和与数据库的分工，再进入请求和代码。完整目录见[框架篇入口](framework/index.html)。

[从 F01 导学开始](framework/f01.html)，先理解 ES 的用途、职责和学习方法；F02 解释数据怎样成为结果，F03 启动 ES，F07 用 Spring Boot 4/JDK 25 接入课程提供的本机搜索展示壳。网站帮助对照同样输入的命中、次序、计数和价格；正文讲 ES 概念、DSL、Java 与反例，读者不用开发前端。Pages 承载教程，真实实验与展示壳在本机运行。

**F12 基础结业、F22 实用搜索结业、F45 完整复现**，各自有独立新样本/需求检验。详情见 [FRAMEWORK_PLAN.md](FRAMEWORK_PLAN.md)、[FRAMEWORK_CASES.md](FRAMEWORK_CASES.md)、[FRAMEWORK_STANDARD.md](FRAMEWORK_STANDARD.md)与[逐课提示词](docs/framework-lesson-prompt.md)。

F01 导学、[F02 概念推演](framework/f02.html)与 [F03 首搜](framework/f03.html)已完成；[F04 字段建模](framework/f04.html)、[F05 关键词查询](framework/f05.html)与 [F06 组合筛选](framework/f06.html)可阅读、真实 ES 待验收，[F07 Java接口与本机展示壳](framework/f07.html)、F08多字段与高亮、F09聚合与筛选计数、F10显式排序、F11稳定分页与PIT、F12更新与基础结业及[F13 分析链与中文召回](framework/f13.html)、[F14 中文分词方案比较](framework/f14.html)、[F15 专有词与词典](framework/f15.html)、[F16 别名/同义词与繁简](framework/f16.html)已交付，F17–F22中文召回与评分质量已交付，[F23酒店/房型/offer文档边界](framework/f23.html)已交付，[F24同房型条件/inner_hits与nested排序](framework/f24.html)已交付，[F25多晚库存与总价](framework/f25.html)、[F26酒店去重与最低价范围](framework/f26.html)已交付，F27–F45待实施，实际验收范围见 [STATUS.md](STATUS.md)。F07最小Java接口与本机展示壳已交付，多节点与CDC尚未实施。[历史启动实验](framework/f01-startup-legacy.html)与[工程验收记录](projects/travel-search/review/f01/README.md)保留；[F03 实测](projects/travel-search/review/f03/README.md)已用新资源独立执行两轮。现有源码篇 ch01–ch30 保持原编号和链接。

## 快速开始

```bash
git clone https://github.com/socoo123/es_web.git
cd es_web

# 可选但推荐:启动本地 ES 9.4.0(不启动也不影响阅读,只是做不了实验)
bash docker/start.sh

open index.html        # 或双击 index.html
```

第 29 课(安全机制)另需安全节点:`bash docker/start-secure.sh`(9201 端口,`elastic / elastic-password`)。

## 站点地图

| 页面 | 内容 |
|---|---|
| `index.html` | 课程总览:六篇 30 课卡片、进度记录 |
| `architecture.html` | **架构总览**:一张全景图串起 30 课(每块可点击)+ 四条走读路线 + 源码地图 |
| `chapters/ch01-30.html` | 30 课正文 |
| `console.html` | REST 控制台:直连本机 ES,实验可深链跳入 |
| `cheatsheet.html` | API 速查表 |

## 课程结构

| 篇 | 课 | 一句话 |
|---|---|---|
| 一 · 全局认知 | 01–05 | 是什么 / 代码库全景 / 节点启动 / 插件体系 / 配置框架 |
| 二 · 请求处理 | 06–10 | REST 入口 / 动作框架 / 异步与线程池 / 传输层 / 实时 GET |
| 三 · 数据写入 | 11–15 | 映射 / 摄取管道 / 批量写入 / 存储引擎 / 分片路由 |
| 四 · 搜索查询 | 16–20 | 两阶段搜索 / 搜索上下文 / 查询语法 / 聚合 / 评分排序 |
| 五 · 分布式机制 | 21–25 | 集群状态 / 选举共识 / 分片分配 / 恢复与快照 / 熔断背压 |
| 六 · 高级专题 | 26–30 | 脚本引擎 / ES\|QL / 索引生命周期 / 安全 / 全景回顾 |

不想线性读?打开 [`architecture.html`](architecture.html) 挑一条走读路线:写一篇文档 / 搜一次 `_search` / 集群自愈 / 系统怎么搭起来。

## 版本锚点

一切数字以**本地实测 + v9.4.0 tag 源码**为准:

| 组件 | 版本 |
|---|---|
| Elasticsearch | 9.4.0(docker 镜像) |
| Lucene | 10.4.0 |
| bundled JDK | 26.0.1+8 |
| Netty | 4.1.132.Final |

## 工具

```bash
node tools/check.mjs                        # 站点结构与注册表校验(改动后必跑)
node tools/figwidth.mjs chapters/ch01.html  # SVG 文本估宽检查
bash docker/start.sh                        # 本地 ES 9.4.0 @ 127.0.0.1:9200
bash docker/start-secure.sh                 # 安全节点 @ 127.0.0.1:9201(ch29 用)
```

## 部署到 GitHub Pages

本站纯静态、零构建,可直接托管:

1. 仓库 **Settings → Pages**,Source 选 **Deploy from a branch**,分支 `main`、目录 `/(root)`,Save
2. 访问:**https://socoo123.github.io/es_web/**(本仓库已上线,push 到 main 自动重新部署)

阅读与实验要分清:

- **阅读**(30 课、架构总览、动画、速查表):托管后完整可用,双主题、进度都在
- **实验**:页面请求要连你本机的 `localhost:9200`——
  - docker compose 的 CORS 白名单已包含 Pages 域;改过 compose 后用 `docker compose up -d` 重建容器才生效
  - 浏览器对「公网页面 → 本机回环」有本地网络权限管控(Chrome/Edge 会弹一次授权;ES 9.4.0 的 `CorsHandler` 不回 PNA 响应头,严格模式的浏览器可能直接拦截)
  - 被拦时退回本地环境:`open index.html`,实验零阻力

## 仓库约定

- `es-src/`(453MB 的 v9.4.0 源码参考库)与 `tutorial/`(原始教程)**不入库**,见 `.gitignore`。需要源码对照时自行下载:

  ```bash
  mkdir es-src && curl -L https://github.com/elastic/elasticsearch/archive/refs/tags/v9.4.0.tar.gz \
    | tar xz --strip-components=1 -C es-src
  ```

- 进度与勘误的唯一真相在 `STATUS.md`；基础规范在 `PLAN.md`，后续逐章重构统一遵循 [CHAPTER_STANDARD.md](CHAPTER_STANDARD.md)，协作入口为 [AGENTS.md](AGENTS.md)
- 端口只绑 `127.0.0.1`,CORS 放行配置中的本机页面、`file://` 和本站 Pages 域——这是学习机配置,别暴露到局域网
