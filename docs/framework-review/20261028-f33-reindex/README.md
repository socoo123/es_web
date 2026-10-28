# F33 内容、图解与阅读验收

仅实施F33及必要的目录、F32下一课链接和进度摘要；未实施F34或F41。

- [模型与推理配置限制](reasoning.json)：最新偏好gpt-6.1-sol/max，早期xhigh保留；根入口无法设置/读回，没有启动独立代理，不声称已启用。
- [官方依据与固定源码](sources.json)：4个F33目标文件与官方v9.4.0字节核对，API以真实ES9.4.0输出校验；没有通读源码或tutorial。
- [作者内容自审](content-review.json)：业务问题、概念、因果、固定样本、完整实现、输出与反例、重做、练习和下一课边界。作者自审不是独立审阅。
- [图源生成](../../../framework/diagrams/f33/generation.json)：2份D2、浅深4份SVG；fmt/check/validate/export与SHA-256，不手改产物。
- [HTTP/file阅读](http-review.json)：`/es_web/`前缀、多宽度双主题、880px列、局部滚动、剪贴板、折叠、进度、导航、主题、file/reduced motion/焦点与独立SVG。
- [完整嵌入图/最终目录补验](supplement-review.json)：4幅完整嵌入图与目录6宽度/主题组合，实际点击F33入口。
- [实际视觉审阅](visual-review.json)：实际查看范围单列，不把截图生成当成查看。
- [最终必要检查](checks.json)：站点、代码片段、语法、两轮事件一致性及完整差异检查，记录实际执行。
- [原有服务监测](existing-node-monitor.jsonl)：只读核对es-study-secure容器身份、PID、启动时间与健康，不修改它。

[ES/Java/构建与真实观察窗](../../../projects/travel-search/review/f33/README.md)独立记录。无新增前端或Controller；Pages只用于阅读。未验证持续并发、长任务/失败续作、持续CDC追平、安全授权、跨机器、性能或恢复时限。安全回滚实测严格位于业务写入暂停窗口；p08写入后不执行不安全回滚。
