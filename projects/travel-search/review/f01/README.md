# F01 实际验收

作者证据，读者按 [labs/f01](../../labs/f01/README.md) 操作即可。

## 真实 ES

[verify.py](verify.py) 直接执行正文对应的 shell 文件，使用真实隔离 ES 9.4.0；[es-review.json](es-review.json) 保存两轮响应、版本/镜像、资源条件、案例结果与工程文件哈希。[outputs/](outputs/) 是首轮真实响应的投影，搜索响应完整保留，其余明确为摘录；由验收脚本生成，不手工编造。

- `f01-c01`：版本/节点；创建确认；索引健康 1 主 / 0 副本；固定 ID 写入；refresh 后搜索；mapping / count / GET。
- `f01-c02`：空闲错误端口与实际停机均 curl exit 7；恢复本工程服务，等待本课索引，再搜索仍命中固定 ID。
- `f01-c03`：重复建索引 400 / resource_already_exists_exception；相同 ID 完整覆盖 updated / version=2；刷新后计数仍 1。
- 两轮之间点名删索引；第二轮首次写入重新 created / version=1。最终索引已清理，自己的容器已停止，持久卷保留；未操作源码篇 9200 / 9201。

首次试跑发现重启后 HTTP 可用早于持久索引恢复，立即 refresh 短暂返回 404；已在恢复代码加入限定索引的健康等待与临时 404 重试。该现象同步写入正文，最终两轮按修正流程通过。

工程需要 curl 7.76+、Bash、Docker / Compose；作者验收 Python 只用标准库。重跑时要求本课索引不存在，不自动清理已有数据：

```bash
cd projects/travel-search
python3 review/f01/verify.py
# 随后在仓库根目录同步真实输出到静态正文。
```

## 图解与阅读

[D2 生成记录](../../../../framework/diagrams/f01/generation.json)与 [HTTP 检查脚本](http-review.py) / [实际记录](http-review.json)分别保留。HTTP 脚本需作者已有的 Playwright / Chromium，启动自己的临时静态服务，检查 `/es_web/` 前缀；这些依赖不进入读者实验工程。

阅读检查覆盖 1920 / 1440 / 1024 / 768 / 390 / 320px × 浅深主题、最大 880px 列、图/代码局部滚动、复制、展开图、目录、已读进度、file 预览与 reduced motion。截图实际审阅范围与结论写入 HTTP 记录，截图生成本身不算人工审阅。

## 范围

本课只有单节点配置/curl，未实现或验收 Boot 4/JDK 25、中文插件、多节点、CDC。站点门禁和片段一致性通过，也不能替代这些后续实验。
