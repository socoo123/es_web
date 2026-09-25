# ES 源码精读站 — 工作协议

把 30 课 ES 9.4.0 源码精读教程(tutorial/)转写成一个可操作的静态学习站:
真实 ES 动手实验 + 架构图 + 机制动画。**聊天记录不是记忆**,一切规范与进度落盘在本目录。

## 每次会话三步走

1. **读 `STATUS.md`** — 知道做到哪了、上次留下什么
2. **读 `PLAN.md`** — 章节模板 / 实验 schema / 动画 schema / 命名与校验规范
3. **做完就更新 `STATUS.md`,然后跑 `node tools/check.mjs`** — 必须全绿才算完

## 常用命令

```bash
bash docker/start.sh        # 启动本地 ES 9.4.0(CORS 已配好)
bash docker/start-secure.sh # 另起 9201 安全节点(ch29 实验用,elastic/elastic-password)
node tools/check.mjs        # 站点结构与注册表校验,任何改动后必跑
open index.html             # 纯静态,file:// 直接可用
```

## 硬纪律(token 经济,2026-09-21 事故后确立)

- **禁止**再用广度探索 agent 通读 tutorial/ 全量;单次只读当前正在转写的那一课
- 每课原文**只读一遍**,当场转写,不回头重读
- 源码论断存疑时:先用本地 ES **实测** API 行为(零成本),仍存疑查本地源码 `es-src/`(v9.4.0 全量)——只 grep/读目标文件,勿整目录通读
- 按 PLAN.md 分期推进,每篇(5 课)一个可停点;跨会话靠 STATUS.md 恢复,不靠聊天记录

## 内容红线

- 不照抄 tutorial 原文措辞——按 STYLE_GUIDE 的结构重排、用自己的话重写
- 发现原文错误:网页里写对的,并在 STATUS.md 勘误表登记
- 版本锚定 9.4.0:线程池参数等易变数字,以本地实测 + `DefaultBuiltInExecutorBuilders` 为准
- 图不搬运 ASCII/mermaid 原图,重画为主题感知的 SVG(fig-* 类)
