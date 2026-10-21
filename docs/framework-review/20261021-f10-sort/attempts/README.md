# F10 作者检查中的失败与修正

- dependency-filter.json：作者过滤依赖树时误用了Rest5 group；Maven成功，改为co.elastic.clients后确认为9.4.8。不是依赖降级。
- http-before-progress-fix.json：F10目录入口缺card类，已读徽标失败；加回既有进度钩子，重跑通过。该轮截图原件迁至screenshots-before-progress-fix/，JSON内仍保留生成时路径及原哈希，按同名在迁移目录查找；均未声称视觉已审阅。
- http-rapid-navigation-abort.json：立即离开F09时两份浅色SVG请求取消，保留原错误；等导航networkidle/图解同步后重跑无请求失败。
- http-before-evidence-finalization.json：运行时阅读检查均通过，但最后检查的workspace-state.json尚未写入，静态链接失败；实际还原环境并完成证据后重跑。
- shell-first-retry-after-es-ready.json：ES探活刚恢复后第一次业务请求仍503。保留该真实观察，随后同一Java进程请求成功；最终脚本允许在90秒边界内记录重试，不虚称探活即业务立即恢复，不推断底层具体原因。

这些记录保留初次失败，不能当成最终验收。最终结果以父目录http-review.json、shell-review.json及repository-checks.json为准；pending截图均表示只生成。
