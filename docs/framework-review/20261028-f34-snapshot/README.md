# F34 内容与阅读验收

范围仅F34及必要目录/前课导航/进度摘要；没有实施F35。正文采用七段式、880px阅读列、双主题、折叠练习、代码复制、独立阅读进度；两幅静态D2，无播放器。

[真实ES/Java记录](../../../projects/travel-search/review/f34/README.md)与阅读验证分列；图源/生成收据见[图解目录](../../../framework/diagrams/f34/README.md)。[reasoning.json](reasoning.json)如实记录当前根入口不能设置或读回最新gpt-6.1-sol/max，作者自审不称独立审阅。

四个目标源码与官方v9.4.0字节相等，见[sources.json](sources.json)。特别核对TransportSnapshotsStatusAction中SUCCESS/PARTIAL到完成态SUCCESS的映射；它不能替代失败分片和恢复核对。

HTTP双主题、桌面窄屏、真实剪贴板、路径/导航/进度、独立图、file/reduced motion与焦点由[reading-review.py](reading-review.py)实际运行并记录；实际视觉查看范围另记，不以生成截图冒充审阅。最终结果写入本目录JSON收据及STATUS。

已完成的验证：

- [内容自审](content-review.json)：约4812汉字、24代码块、8能力检查/4陷阱；业务问题、术语/因果、API/工程、输出/反例、重做与下一课边界逐项对应实际证据。
- [HTTP/file阅读](http-review.json)：六宽×浅深12组合，桌面列880px/左右对齐，320/390无整页溢出；24真实剪贴板、14折叠、锚点、主题刷新、独立进度、前课导航、file/reduced motion/焦点、16独立SVG视图。
- [完整嵌入图与最终目录](supplement-review.json)：4幅完整图、目录6宽度/主题组合，实际点击F34入口。完整图截图仅在浏览器捕获时隐藏粘顶栏，产品/图源/资产不变。
- [实际视觉](visual-review.json)：62阅读+32正式观察窗截图通过12张contact逐张查看；4完整图+4最终目录截图逐张单独查看，总102原图覆盖。失败预演截图不计入此范围。
- [手工curl](../../../projects/travel-search/review/f34/manual/summary.json)：完整requests.sh独立执行一次，53响应、3预期500、4 Java观察点，未发生等待超时；非第三轮正式lab。
- [最终结构/语法/片段检查](checks.json)与[只清本课的收尾状态](../../../projects/travel-search/review/f34/shutdown.json)分列。健康等待中的408及主题切换取消旧图片请求分别留证，不当作页面故障。

已修正四次预演问题，见[attempts](../../../projects/travel-search/review/f34/attempts/README.md)。作者事后检查脚本还曾漏计带class的目录折叠，改为统计details起始标签；两个正式ES轮次与正文没有因此改动。没有旧课内容勘误。

未验证独立故障域/异地容灾、仓库损坏/只读访问故障、跨版本、SLM、系统/功能状态、安全、持续来源追平、性能与恢复时限。当前根入口无法设置或读回最新gpt-6.1-sol/max，作者自审，无独立代理。
