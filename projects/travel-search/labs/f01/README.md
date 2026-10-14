# F01：启动 ES，第一次写入与搜索

[阅读完整讲解](../../../../framework/f01-startup-legacy.html)。下面是同一套可运行代码，手动复制正文命令或依次运行脚本均可。JSON/脚本与正文由 `node tools/sync-framework-code.mjs --check` 核对，不依赖教程页面执行网络请求。

## 固定前提

ES 9.4.0、单节点 `travel-search-01`、cluster `travel-search-lab`、HTTP `127.0.0.1:19200`、无认证、1GB 容器/512MB 堆、持久卷。索引 `tut-f01-attractions`：1 主分片/0 副本，名称 `text + standard`，ID/城市 `keyword`，门票整数分。教学样本西湖记为 0 分，只表示实验数据，不是景区价格承诺。

在工程根目录操作：

```bash
cd projects/travel-search # 如果已在此目录，不要重复 cd
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
bash labs/f01/01-observe.sh
bash labs/f01/02-create.sh
bash labs/f01/03-write.sh
bash labs/f01/04-search.sh
bash labs/f01/05-inspect.sh
```

## 三个案例

| 案例 | 执行/输入 | 核对结果 | 恢复 |
| --- | --- | --- | --- |
| f01-c01 | 上述主流程；index.json / xihu.json / search-xihu.json | 节点 9.4.0；索引 green，主/总活动分片均 1；写入 `created`；搜索只有 `a-hz-xihu`；mapping 对应字段；count=1；GET found=true | 点名清理后重跑主流程 |
| f01-c02 | 保留 C01 的数据，`bash labs/f01/08-connection-errors.sh` | 空闲错误端口 19299 与停止 ES 后 19200 均 curl exit 7；不是 ES HTTP 404；恢复后等待本课索引，再 refresh/search 仍命中固定 ID | 脚本 EXIT trap 尝试重新启动本工程 ES；若失败手工 up/wait/等待本课索引/search |
| f01-c03 | `bash labs/f01/06-existing-index.sh`，然后 `bash labs/f01/07-write-again.sh` | 重复建索引：HTTP 400 / resource_already_exists_exception；同 `_id` 完整覆盖：updated / version=2；刷新后 count 仍 1 | 清理并重跑 C01，恢复到 version=1；继续重复写则 version 继续增加 |

主流程包含 11 条 HTTP 操作（观察 3、建索引与健康 2、写入 1、刷新搜索 2、核对 3），启动等待探测不计。C02、C03 是额外对照，不能只执行它们而跳过 C01。

19299 如已有服务，改错误端口后再做 C02；教学脚本会拒绝把连通误报为通过。连接拒绝时 curl 返回 7，其他网络环境可能超时返回 28，先按实际诊断。普通操作使用 `--fail-with-body`，HTTP 4xx/5xx 会保留正文并令脚本失败；C03 的预期 HTTP 400 刻意省略该选项，需阅读 JSON 内的 `status/error.type`。

## 清理与重做

```bash
bash labs/f01/cleanup.sh
# 删除确认 acknowledged=true；只删除本课索引及其文档。
bash labs/f01/run.sh
```

如果索引本来不存在，cleanup 会返回 HTTP 404、curl exit 22，不是节点不可用。此时直接 run 即可。`run.sh` 不包含 C02/C03；要重做全部三个案例，再按表执行对应文件。最后清理索引并停止本工程服务：

```bash
bash labs/f01/cleanup.sh
docker compose -f infra/single-node/compose.yaml stop es
```

## 启动排查

- Docker 未启动：先 `docker info`；拉取镜像失败与 ES 启动失败分开诊断。
- 19200 被占用：Compose 会报绑定失败。检查占用，不停止你已有的业务服务；调整本工程端口时要同步 env.sh / wait.sh / 教程命令。
- HTTP 未就绪：`docker compose -f infra/single-node/compose.yaml logs --tail=100 es`；`docker compose -f infra/single-node/compose.yaml ps -a`。退出码 137 需结合日志/`OOMKilled` 判断内存，不仅凭 curl 报错推断。
- Linux 主机内核条件不足：按日志和[官方 Docker 运行要求](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-prod)检查 `vm.max_map_count` 等；不要为本课修改已有集群。

作者验收脚本放在 review 下，只用于执行两轮并保存证据。读者不需要安装 Playwright 或掌握测试框架。
