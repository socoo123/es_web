# F32 内容、图解与阅读验收

只处理F32及必要的目录、F31下一课链接和进度摘要。没有实施F33；模板、稳定入口与错误恢复是本课范围。

- [模型/推理要求记录](reasoning.json)：逐课提示词最新偏好gpt-6.1-sol/max，早期xhigh要求保留。根入口不能设置/读回实际配置，未启动独立代理，不声称已启用。
- [官方依据与固定源码](sources.json)：只核对F32相关5份v9.4.0目标源码，与官方tag字节一致；正文和结果按真实ES9.4.0复核。
- [作者内容自审](content-review.json)：业务问题→概念→样本/请求→结果/错误恢复→能力检查；图、代码、输出和练习一致。不把作者自审称独立审阅。
- [D2生成](../../../framework/diagrams/f32/generation.json)：2份图源、浅深4份SVG，官方CLI fmt/check/validate/export，源与产物哈希，不手改SVG。
- [HTTP阅读检查](http-review.json)：`/es_web/`前缀，1920/1440/1024/768/390/320浅深、880px列与边界、局部滚动、真实剪贴板、折叠区、导航/进度/主题、file/reduced motion/键盘；独立SVG四种桌面宽度。
- [目录摘要补验](directory-review.json)：最终进度摘要更新后，1440/390/320浅深6组合与2张实际截图单列。
- [实际视觉审阅](visual-review.json)：实际查看截图与图解；生成截图或contact sheet不等于已审阅，范围和结论单列。
- [最终必要检查](checks.json)：站点、片段、语法与两轮收据一致性检查；只记录实际运行。
- [原有节点监测](existing-node-monitor.jsonl)：只读观察原es-study-secure容器ID/PID/启动时间/健康，不停止或修改它。

真实ES/Java、构建与浏览器观察窗在[projects收据](../../../projects/travel-search/review/f32/README.md)独立记录。0机制播放器，静态D2没有动画控制验收；没有把Pages当成连接本机Java的业务应用。未验证持续并发/迁移一致性/过滤alias/routing/ILM/data stream/安全/跨机器/性能。

[提交前日志格式检查与修正](staging-whitespace.json)：Maven原始日志行尾空格在暂存检查中发现，按字节无损压缩保留；最终检查覆盖工作区、整轮差异和暂存内容。
