# F26 审阅与验收

本轮只实施F26，必要修改F25下一课链接、目录、当前进度摘要与共享Java工程；未写F27正文/实验。正文约4842汉字（不含代码），七段式、3案例/24教学HTTP、2静态D2/0机制播放器、7折叠练习、3陷阱。

- [内容作者自审](content-review.json)：正文/图/固定表/REST/Java/错误/练习/速记一致性及适用条件。当前根入口不能设置或读回模型/推理强度；[reasoning.json](reasoning.json)如实记录gpt-6.1-sol/max偏好，未声称实际已启用，未启动代理或独立审阅。
- [官方依据](sources.json)：固定v9.4.0的CollapseBuilder与ExpandSearchPhase两文件与官方逐字节一致；当前文档与固定版本真实行为分列。业务价格规则来自固定契约。
- [D2生成](../../../framework/diagrams/f26/generation.json)：D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/CLI导出与哈希。只改图源，不改SVG产物。
- [ES与Java两轮](../../../projects/travel-search/review/f26/README.md)：每轮先清理2HTTP，再24教学+29附加HTTP，真实结果与限制见该记录。
- [HTTP阅读](http-review.json)：6宽×双主题、必要前课/目录、独立图、实际剪贴板、导航/已读隔离/主题重载/file/reduced-motion；截图与实际视觉审阅范围见visual-review.json。截图生成不等于逐字或逐像素审阅。
- [本机观察窗](shell-review.json)：真实浏览器→Java→ES，各范围与错误恢复，页面调用与ES操作分列；没有浏览器直连ES。
- [检查](checks.json)与[最终资源状态](workspace-state.json)分别保存。各项只以实际收据标通过，最终提交/推送及线上核对在交付消息与工作树外发布收据记录。

新F26无已发布历史勘误。探索时修正了验收器对默认doc_values省略、Java inner_hits数组序列化的预期，最终补强组内溢出分支验证并重新完成两轮；两次工作目录误用已纠正。[attempts](attempts/README.md)保留探索收据，不计入最终两轮。固定快照不是实时可订，未测性能、多节点、并发快照、生产安全/实时供价/订单。F27新需求推演未落地或计通过。
