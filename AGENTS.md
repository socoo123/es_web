# 仓库协作入口

修改章节前，依次读取 [STATUS.md](STATUS.md)、[PLAN.md](PLAN.md) 和 [CHAPTER_STANDARD.md](CHAPTER_STANDARD.md)。补充工作纪律见 [CLAUDE.md](CLAUDE.md)。

- 后续章节的内容与 Archify 图解改造遵循 CHAPTER_STANDARD；第一章是已验收的基线。保留 880px 阅读列、双主题、动画控制、实验重做流程及真实验收记录。
- 每次只处理用户指定的章节，不通读全部 tutorial 或批量改造未指定章节。用户明确要求优先于仓库规范。
- 图源改 JSON 后用官方技能重新生成，不手改 Archify HTML。原生门禁、HTTP 浏览器验证、真实 ES 实验分别记录。
- 每次章节重构完成后，更新 STATUS 的图解重构进度、勘误和实际验证状态，运行 `node tools/check.mjs`；将本轮代码、图源、产物与验收记录提交并推送到 GitHub `origin/main`（本仓库现有 Pages 发布分支）。用户已授权每次重构后自动提交与推送，无需逐次确认。
- 交付时提供 GitHub 提交链接；若推送失败，明确区分本地已提交与 GitHub 未更新，并记录原因。
