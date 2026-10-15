# F04 执行验收状态

日期：2026-10-15。**真实 ES 两轮验收未完成**。云环境的 Docker 引擎与本地 ES 9.4.0 镜像可用，但按现有 Compose 启动后 ES 退出1、OOMKilled=false，根因为 `/proc/self/coredump_filter` 不存在。见 [启动记录](runtime-attempt.json)。这发生在 HTTP 入口建立之前，未执行 F04 写入，也没有产生实际 Bulk/搜索响应。

已核对固定 v9.4.0 的 `Elasticsearch.initializeNatives → setCoredumpFilter` 为 Linux 上的启动调用。一次提供该文件的挂载尝试也被 OCI `/proc` 挂载检查拒绝，未修改 ES 二进制、源代码、安全策略或读者 Compose。该失败不是本课 mapping/查询实验的结果。

[expected.json](../../search/f04/expected.json)只保存教学预测；`outputs/` 在成功验收后才写入真实摘要。F03 的旧响应、截图与通过状态不用于本课。

作者在可运行 ES 的环境从仓库根目录复现：

```bash
docker compose -f projects/travel-search/infra/single-node/compose.yaml up -d
bash projects/travel-search/infra/single-node/wait.sh
python3 projects/travel-search/review/f04/verify.py
```

脚本拒绝删除起始已存在的本课索引；确认可删后按 labs/f04/cleanup.sh 点名清理。它执行原样实验脚本，验证五份完整资料、子字段、3→5→5 计数、条级失败与固定 ID 版本、四项边界拒绝及四项允许、动态类型误判和新索引恢复，清理后再做一轮。成功后生成 `es-review.json`、两轮 raw JSON 和首轮 outputs；没有这些成功结果就不能将状态改为实测通过。

[阅读、图解与静态检查](../../../../docs/framework-review/20261015-f04-model-bulk/README.md)单列；Java/展示壳、插件、多节点与 CDC 不属于本课。
