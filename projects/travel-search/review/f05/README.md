# F05 真实执行状态

**当前未通过真实 ES 验收。**本轮按原有隔离 Compose 重试9.4.0，容器 exited/exit1、OOMKilled=false；启动报 `Could not set coredump filter`，原因是云容器缺少 `/proc/self/coredump_filter`。HTTP 尚未建立，curl exit7。没有成功的 F05 写入、分析或搜索，完成轮数为0。

- [本轮启动与连接诊断](runtime-attempt.json)保留实际命令、容器状态和错误；不修改 ES 二进制、读者 Compose 或云安全策略。
- [作者验收脚本](verify.py)使用原样 `labs/f05/*.sh`、固定数据与查询，计划核对3案例×2轮。运行结果由 `es-review.json` 记录实际通过、失败或阻塞，不能由计划推定完成。
- [预期 token、ID 与计数](../../search/f05/expected.json)仅为预测，不是实际响应；固定版本依据见 [内容自审](../../../../docs/framework-review/20261015-f05-keywords/content-review.json)。F03/F04 的旧输出不算本课证据。
- [HTTP与截图审阅](../../../../docs/framework-review/20261015-f05-keywords/README.md)只证明教程阅读状态，与本文件分开。

## 在可运行 ES 的本机执行

从仓库根目录进入工程，先启动本课专用服务。验收脚本只用 Python 标准库和 Bash/curl，不启动/停止节点；若已有 F05 索引，会在写入前拒绝自动清理，避免无意删除资料。

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
python3 review/f05/verify.py
```

已有索引时，确认其资料可删后，手动执行 `bash labs/f05/cleanup.sh`，再运行验收。脚本每轮准备空索引、执行三组对照，最后仅删除 `tut-f05-attractions`，并确认索引不存在后开始第二轮。失败会保留已执行的原始响应和当前资源供诊断，不静默删掉失败现场；修复后再点名清理重跑。

脚本成功时才写 `status=passed`：两轮的原始标准输出/错误保存在 `raw/`，结构化摘录、实际版本/镜像、输入 SHA-256 和每个查询的 ID 集合保存在 `es-review.json`。探活、资源存在性与断言读取不混入每轮22条教学请求；清理另1条。使用已有卷、1主/0副本，未运行 Java、插件、多节点或 CDC。

验收范围包括 mapping/版本/健康，五条 Bulk 全成功与 refresh，三次 token/position/offset，13个完整搜索请求的所有 ID、精确总数、投影字段、排序与零超时/分片失败，以及两轮点名清理。它不验证 BM25 浮点值或相关性次序，也不将清理后无索引称为“数据已备份”。
