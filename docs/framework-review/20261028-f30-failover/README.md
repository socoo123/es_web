# F30 内容、图解与阅读验收

[正文](../../../framework/f30.html) · [本机实验](../../../projects/travel-search/labs/f30/README.md) · [真实两轮](../../../projects/travel-search/review/f30/README.md)。只实施F30及必要目录/前课导航/当前摘要，未实施F31；共享Java与前端未改。

- **内容**：[作者自审与响应交叉核对](content-review.json)。约5400汉字（不含代码），3案例、每轮75教学REST＋7 Java接口HTTP、1独立SDK诊断、2静态D2、8练习、4陷阱。先讲入口、投票、目标分片，再看REST/Java与恢复。无独立代理，不能把作者自审称为独立审阅。
- **依据**：[sources.json](sources.json)保存5份官方v9.4.0源码与本地字节SHA一致的核对。官方动态文档与固定源码、实测分别记录；没有以源码代替运行。
- **图解**：[generation.json](../../../framework/diagrams/f30/generation.json)：D2v0.9.0、dagre、主题4/201，fmt/fmt --check/validate/四次导出及2源4SVG哈希；只修改D2、正式重新生成。初版过宽导致嵌入文字小，已改纵向分类。静态图不宣称动画。
- **HTTP阅读**：[http-review.json](http-review.json)：1920/1440/1024/768/390/320×浅深=12组；最大880px、主区边界差≤1px、整页零横向溢出。16独立图组、12必要关联页、29锚点、13折叠、23次真实剪贴板复制、主题同步/重载、已读设置/目录反映/前课隔离/取消、file双主题、reduced-motion与键盘焦点通过。最终JS/HTTP/非预期请求错误=0，Pages业务请求=0。检查器单列图源切换可取消的SVG请求，最终运行该项也为0。
- **实际视觉**：[visual-review.json](visual-review.json)。54阅读PNG与28真实观察窗PNG通过7份总览实际查看；4整图与8 Java代码截图另逐份查看。限定布局、图文与左右滚动可读性，非所有原图逐像素或完整代码逐字审阅。首次代码截图受平滑滚动影响取到页首，已改瞬时定位并重拍、复看；截图存在不等于自动通过。
- **Java与展示壳**：[构建/运行](../../../projects/travel-search/review/f30/runtime.json)、[浏览器汇总](shell-review-summary.json)。28真实Java请求中20成功/8错误，20独立REST重放。原始ES503在本客户端实际进入ResponseException/IOException分支，和m1断线一样被服务转为503；作者稿502预期已改。未新增前端或Controller，未声明多入口HA。
- **资源异常与恢复**：初始五进程试案在master384MiB限制下先OOM；调512MiB后VM压力于2026-10-28 10:35:48上海时间意外OOM原安全节点。[中断](existing-node-oom.json)有原始Docker状态。停止本课容器后，于10:38:17启动原容器，[恢复](existing-node-restored.json)验证原容器ID/原UUID与healthy。原业务字段没有事前基线，未逐项对账。改用四进程完成正式两轮；[后续监测](existing-node-monitor.jsonl)268次采样保持同PID/StartedAt/healthy，[最终状态](workspace-state.json)证明仅清本课资源、保留四卷与原安全节点。
- **运行入口偏好**：[reasoning.json](reasoning.json)。AGENTS记录xhigh；逐课提示词保存后来的gpt-6.1-sol/max。当前入口无法设置或自行读回，不声称实际切换；本轮作者实施、自审，不启动子代理。
- **边界**：单Docker VM、固定6份资料、进程SIGKILL、原卷回归；没有网络分区、磁盘丢失、随机并发、跨机器、快照、性能或恢复时间承诺。准备步骤与轮询另计，单入口失败不能推导所有data不可读。

[最终检查](checks.json)分列站点/片段/Python/JSON/Compose/图哈希；GitHub提交推送与Pages发布在实际执行后核对，发布收据保存于工作树外，避免把待执行状态写成成功。
