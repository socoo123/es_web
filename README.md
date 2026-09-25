# ES 源码精读站

30 课读完 **Elasticsearch 9.4.0** 的骨架与血肉:请求链路、Lucene 存储、搜索聚合、分布式共识。纯静态、零构建、零依赖——双击 `index.html` 即用;实验跑在你本机 docker 拉起的真实 ES 上。

- **30 课 · 六篇**,每课:架构图(SVG)+ 机制动画 + 动手实验(预测 → 操作 → 对照)
- **414 个实验 / 22 个动画**,全部对齐 9.4.0 真实行为(本地实测,存疑查源码)
- 双主题(暖白纸面 / 深海蓝),`file://` 直接可用

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
2. 约 1 分钟后访问:**https://socoo123.github.io/es_web/**

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

- 进度与勘误的唯一真相在 `STATUS.md`;规范在 `PLAN.md`
- 端口只绑 `127.0.0.1`,CORS 只放行本机页面与 `file://`——这是学习机配置,别暴露到局域网
