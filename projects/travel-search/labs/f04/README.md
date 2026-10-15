# F04：字段设计、Bulk 部分失败与恢复

[正文](../../../../framework/f04.html)先解释字段用途和判断方法。前置为 F03；仍用 ES 9.4.0、单节点、127.0.0.1:19200、无认证、1 主/0 副本和持久卷。只操作本课四个 `tut-f04-` 索引，不依赖 F03 索引中还有数据。

在仓库根目录进入工程（Bash、curl 7.76+、Docker/Compose v2+）：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
bash labs/f04/01-create.sh
bash labs/f04/02-mixed.sh
bash labs/f04/03-retry.sh
bash labs/f04/04-reimport.sh
bash labs/f04/05-boundaries.sh
bash labs/f04/06-dynamic.sh
```

| 案例 | 预测与观察 | 请求数 |
| --- | --- | --- |
| f04-c01 | 显式 strict mapping；混合 Bulk 五条中三成功两失败；刷新计数3；只修复 B/E 后核对五个 ID、全部字段与 name.raw；完整重导入后 updated/version=2/count=5 | 14 |
| f04-c02 | 专用边界索引：拒绝数字字符串/小数/非法日期/越界纬度；业务非法枚举与负数、缺价、null、0 的四份文档可写入 | 5 |
| f04-c03 | 动态索引把城市/错误金额字符串建成 text+keyword；改 integer 失败；新显式索引重新导入一条正确记录并核对 mapping/count=1 | 9 |

28 条教学 HTTP 请求，点名清理另1条；探活和作者断言读取另计。前三步构成部分失败与修复主线，后面是重导入和类型边界对照。每一步前先预测，后读响应；`--fail-with-body` 仍无法发现 HTTP200 的 Bulk 条级错误，必须检查 `errors` 与每个 `items`。

`data/f04/attractions.json` 是五份完整资料；NDJSON 为相同资料的传输格式。`mixed.ndjson` 故意破坏 B 金额与 E 字段名；`retry.ndjson` 仅包含修正后的 B/E；`attractions.ndjson` 才是全部正确数据。每个 index 动作跟一行完整文档，文件末尾有换行。金额单位是分、币种 CNY；日期和坐标均为教学数据。

当前云环境 ES 在启动时因缺少 `/proc/self/coredump_filter` 退出，**本课真实运行待验收**。上述结果是预测，不能引用 F03 的旧验收来证明本课通过。[限制与作者复现](../../review/f04/README.md)。

## 点名清理与重做

```bash
bash labs/f04/cleanup.sh
bash labs/f04/run.sh
```

cleanup 仅点名删除 `tut-f04-attractions`、`tut-f04-boundaries`、`tut-f04-dynamic`、`tut-f04-rebuilt`，以及它们的全部文档。允许其中某些索引不存在；不吞掉连接失败，不使用通配符、不删卷。run 不自动清理，因此已有资源会让创建步骤失败；先确认本课资源可删，再 cleanup。第二轮应重新得到 created/version=1，完整重导入后才为 version=2。保留下一课数据时停在重导入后即可。

实验完成后可停止这个专用工程：

```bash
docker compose -f infra/single-node/compose.yaml stop es
```

共享本工程节点的其他实验也会停止；数据卷保留。无需 Java、数据库、中文插件、前端开发或验收工具。作者 `review/f04/verify.py` 在已启动的 ES 上执行三案例两轮、点名清理并保存响应；不会自动删除起始时已存在的本课索引。
