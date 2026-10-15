# F06 真实 ES 验收状态

**blocked_before_http：0 个成功 F06 API，0 轮完成。** 原专用 Compose 在本轮重新启动 ES9.4.0，仍因云容器缺少 `/proc/self/coredump_filter` 而退出1，OOMKilled=false，19200 curl 退出7。没有修改 ES 二进制、读者 Compose 或云安全策略，也没有借用 F03/F04/F05 的响应证明本课通过。

- [本轮启动命令、状态、仅本次日志与探测](runtime-attempt.json)
- [实际运行作者验收的结果](es-review.json)、[原始退出码/stdout/stderr](verifier-attempt.json)
- [两轮验收脚本](verify.py)
- [16 组预测](../../search/f06/expected.json)：不是 API 响应
- [正文与 HTTP 阅读记录](../../../../docs/framework-review/20261015-f06-bool/README.md)

在能启动原专用环境的读者本机，从仓库根目录执行：

```bash
docker compose -f projects/travel-search/infra/single-node/compose.yaml up -d
bash projects/travel-search/infra/single-node/wait.sh
python3 projects/travel-search/review/f06/verify.py
```

脚本只访问127.0.0.1:19200，先核对 ES9.4.0 / travel-search-lab，并拒绝自动删除初始已存在的 `tut-f06-attractions`。确认本课资料可删后，可先手工运行 `bash projects/travel-search/labs/f06/cleanup.sh`。

每轮原样执行01→02→03→04，核对显式 mapping、12条 Bulk 的 created/version1、refresh零失败、16组完整 ID/total/投影字段/稳定 sort/无超时与分片失败。near、两组主查询should检查正分；filter-only检查全部零分，不承诺具体 BM25 或相关性次序。缺字段的投影仍缺失，null价格仍是null。

每轮末仅删除本课索引并确认不存在，再重做第二轮；失败保留现场，不自动清理，原始stdout/stderr（包括非零退出）保存在raw目录。脚本不启停节点、不删除卷。作者预检、断言读取和探活不计入每轮22条教学请求；点名清理另1条。

当前实际预检在HTTP连接前失败，没有进入任何教学请求。源码核对、手算、截图和静态检查各有用途，均不能补记这两轮为通过。
