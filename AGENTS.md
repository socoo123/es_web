# 仓库协作入口

修改章节前，依次读取 [STATUS.md](STATUS.md)、[PLAN.md](PLAN.md) 和 [CHAPTER_STANDARD.md](CHAPTER_STANDARD.md)。补充工作纪律见 [CLAUDE.md](CLAUDE.md)。

- 源码篇后续章节的内容与 Archify 图解改造遵循 CHAPTER_STANDARD；第一章是已验收的基线。保留 880px 阅读列、双主题、动画控制、实验重做流程及真实验收记录。
- 框架篇 F01–F45 另读 [FRAMEWORK_STANDARD.md](FRAMEWORK_STANDARD.md)：先理解 ES 的用途与旅游搜索问题，再学机制、REST/DSL 与 Java；F01 导学、F02 概念推演、F03 首搜、F07 Java，八阶段路线见 FRAMEWORK_PLAN，不贴前端代码或建设门户；应用用 Boot 4/JDK 25，实验项目由读者本机启动，Pages 只承载教程。图解优先 D2、可用 Mermaid，复杂机制可用 SVG。
- 每次只处理用户指定的章节，不通读全部 tutorial 或批量改造未指定章节。用户明确要求优先于仓库规范。
- Archify 图源改 JSON 后用官方技能重新生成，不手改 Archify HTML；D2/Mermaid 保留图源并重新生成产物。图解生成检查、HTTP 浏览器验证、真实 ES 实验分别记录。
- 每次章节重构完成后，更新 STATUS 的图解重构进度、勘误和实际验证状态，运行 `node tools/check.mjs`；将本轮代码、图源、产物与验收记录提交并推送到 GitHub `origin/main`（本仓库现有 Pages 发布分支）。用户已授权每次重构后自动提交与推送，无需逐次确认。
- 交付时提供 GitHub 提交链接；若推送失败，明确区分本地已提交与 GitHub 未更新，并记录原因。
