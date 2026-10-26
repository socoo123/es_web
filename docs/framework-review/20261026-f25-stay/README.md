# F25 · 验收记录

仅F25及必要的F24下一课链接、目录、共享Java工程/当前进度摘要。正文约4432汉字（不含代码），3案例/21教学HTTP、2静态D2/7练习/3陷阱/0播放器；没有独立审阅代理。

- [内容自审](content-review.json)：业务体验→ES摘要边界→逐晚表与身份→REST/Java→金额/拒绝→重做与下一课；单位/日期/最短入住与快照边界一致。
- [官方固定版本依据](sources.json)：v9.4.0 RangeQueryBuilder与SearchSourceBuilder，本地与官方逐字节相等；住宿业务规则来自明确数据契约。
- [图生成](../../../framework/diagrams/f25/generation.json)：D2v0.9.0、dagre、4/201，2源4SVG，fmt/validate/正式CLI与SHA256，仅改图源。
- [正式两轮ES/Java](../../../projects/travel-search/review/f25/README.md)：每轮先点名清理，再21教学＋29附加HTTP，Java内部4次教学搜索另计；实际构建、完整DSL/全部源/每晚/手工金额核对。
- [HTTP阅读](http-review.json)：1920/1440/1024/768/390/320×浅深=12组，F24/目录24组回归，独立图4桌面宽×2主题×2图=16组；16锚点/11折叠/13段实际剪贴板，主题同步/展开/重载/已读隔离/键盘/file双主题/reduced-motion，零JS与网络错误。880px/边界差≤1px，无整页横溢，代码/表格局部滚动。
- [真实观察窗](shell-review.json)：32矩阵场景＋400/502/503与恢复共40次Java调用，同一PID；原文/卡片/每晚/金额逐项相等，切换/失败清空旧结果，无浏览器直连ES。另[视觉补证](visual-followup.json)8次真实Java与15次ES操作，补拍错误区域，单列计数。
- [实际视觉](visual-review.json)：78张原PNG，68张经12组总览实际查看，10张补证逐张原图查看；另5张原图单开。图注在320px/1000高的组合截图少截末行，DOM完整，1600高及单独图注补证完整；表/代码右滚动及错误区域截图补齐。不声称每像素或代码全文逐字视觉审阅。
- [初始状态](workspace-before.json)、[最终清理](workspace-state.json)：全部12源精确复核/open_contexts0，点名DELETE与GET404，Java/本课容器网络停止移除，18081/19225关闭，保留卷/镜像与旧安全节点。
- [最终检查](checks.json)：站点/片段、JS/Bash/Python、数据生成一致性、图/截图/制品哈希与两轮收据；[探索修正](attempts/README.md)保留脚本错误，不计入最终通过。

最新逐课提示词要求gpt-6.1-sol/max。当前根入口没有设置或读回模型/推理档位API，没有另起代理，不以提示词声称配置生效；[reasoning.json](reasoning.json)如实记录。

未测代表性负载/性能/容量、多节点与生产安全、实时供价/CDC、税费/取消罚金/儿童/CTA/CTD、订单扣库存。超时/部分分片失败仅代码防护、无注入。固定快照合格不证明实时可订，不宣称酒店最低价或全局排名，F26未实施。

按用户持续授权提交推送origin/main。提交后运行[发布核对](publication-check.py)，精确远端SHA/Pages对应构建/14项线上字节和6组实际阅读交互；结果写工作树外/tmp/es-f25-publication.json，完成状态以最终交付消息和发布收据为准，不提前标为通过。
