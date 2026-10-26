# F23 · 内容、图解、HTTP与实际视觉验收

[阅读正文](../../../framework/f23.html) · [本机实验](../../../projects/travel-search/labs/f23/README.md) · [真实ES/Java两轮](../../../projects/travel-search/review/f23/README.md) · [固定样本](../../../projects/travel-search/data/f23/catalog.json)。只实施F23及必要导航/共享工程；F24未启动，没有回填F04–F06未测事项。

[内容自审](content-review.json)：正文约4642汉字（不含代码），七段式、7折叠练习/3陷阱，3案例/90教学HTTP，2静态D2/0播放器。先区分酒店/房型/报价身份，再解释模型、查询单位和更新代价，REST后给完整Java关键实现。单人作者自审，未声称独立同行审阅。[实际运行配置](reasoning.json)为父入口实际spawn gpt-6.1-sol/max/fork_turns=none的报告，子agent无独立读回API；旧xhigh历史要求保留，本课按最新max。父agent只调度，全部实施、自审、实验、截图审阅、提交与上线核对由本课作者完成。

[四份固定v9.4.0源码](sources.json)逐字节等于官方tag；UpdateHelper合成完整IndexRequest、DocumentParser/Context创建nested文档、InternalEngine.updateDocs软更新文档块。当前在线官方文档只作API解释，不拿未来默认限制充当9.4.0事实。完整_source相同的object/nested与展开offer对照，身份、日期、币种、两层状态、rates仍object的限制和单晚快照范围一致。没有通用性能或可订保证。

[图源与生成](../../../framework/diagrams/f23/README.md)：D2v0.9.0/dagre/主题4与201，fmt、fmt --check、validate、官方CLI四SVG导出通过，命令与SHA见[generation.json](../../../framework/diagrams/f23/generation.json)。只改源文件。boundaries为业务归属/对照阅读，updates为不同模型的更新对照，非ES调用先后。320px初图标签偏密，已缩短源标签、重新生成并完整重跑HTTP矩阵；[旧图与探索](attempts/README.md)保留。

[最终HTTP记录](http-review.json)：1920/1440/1024/768/390/320×浅深=12组；每组16锚点、14折叠，目录与F22下一课共24组回归，独立图1440/1600/1920/2048×浅深×2=16组。16段代码逐段真实剪贴板精确一致，Tab焦点、主题/图与展开链接同步、重载持久化、已读f23键与旧键保留、前后导航、实际弹窗、file双主题、reduced-motion通过。桌面最大880px，各被测区左右差≤1px，整页无横溢；窄表/代码只在自身横滚，图完整缩放且有展开入口。无未处理JS错误、失败静态资源或Pages到业务端口请求。

[最终提示与横向细节](visual-detail.json)另复验12布局组，截图三表右端、Java查询/投影左右端、320px滚动提示；可发现表格/代码横滚操作。浏览器工具版本与显式复用的既有Chromium路径见[tooling.json](tooling.json)，没有声称安装了默认浏览器。

[真实观察窗记录](shell-review.json)：40矩阵＋10失败/恢复=50次Java调用，完整原始DTO场景另存[shell-review-full.json.gz](shell-review-full.json.gz)。与静态教程HTTP分别验收，均非mock；Pages不运行Java或ES。[结束资源状态](workspace-state.json)保留既有安全节点、卷和镜像，只清理本课。

[实际视觉审阅](visual-review.json)：86PNG全部通过15张清晰总览实际打开查看，其中9张另打开原图；其余77张只看总览。改图后重生总览2/3/5/6/7再次打开，并复看320浅/390深原图。检查浅深对比、节点/箭头文字、三张表左右端、Java横滚、窄屏表单、真实报价金额/计划/日期/状态和错误清空；不冒充每张原图逐字或全部像素审阅。[总览映射](montage-manifest.json)记录源截图与实际打开方式。

[开发失败保留](attempts/README.md)包括stats层级、mapping表达归一化、旧搜索视图引发的部分更新409、typed客户端null字段省略、图源/生成与本机编码过程，均未算作最终通过。最终站点/语法/片段/投影检查另见[checks.json](checks.json)。未测代表性负载、容量、性能、多节点、真实库存/订单/CDC、安全部署；部分分片失败/超时只有代码防护。最终提交的远端SHA、Pages精确构建和线上交互由交付时另核对，推送成功本身不等于上线完成。
