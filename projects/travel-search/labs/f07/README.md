# F07 · Java 接口、本机展示壳与重做

[F07正文](../../../../framework/f07.html)解释业务、契约、完整DSL/Java与错误。此目录是手工入口，作者验收工具不是读者前置。

资源：ES9.4.0 / `127.0.0.1:19200` / `tut-f07-attractions`，1主0副本、无认证、本机绑定、持久卷。样本继承F06十二份合成资料，不借旧索引或旧响应。应用Boot4.0.8 / JDK25 / 官方Client9.4.8，Java和展示壳同源 `127.0.0.1:18080`。

## 首次运行

从仓库根目录：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
bash labs/f07/01-prepare.sh
```

检查节点9.4.0 / travel-search-lab、创建确认、限定健康green且未超时、Bulk十二项created/errors=false、refresh零失败、count12。已有索引时脚本拒绝创建，不暗中清理。mapping/data完整文件分别在search/f07与data/f07。

另一终端按 [backend说明](../../backend/README.md)选JDK25、构建并运行；再打开本机页面。保留Java进程，回到projects/travel-search目录：

```bash
bash labs/f07/02-compare.sh
```

| 输入文件 | REST请求 | 应有完整ID次序 | 价格/分 |
| --- | --- | --- | --- |
| input-near.json | near.json | a-hz-boundary, a-hz-tea, a-hz-xihu | 20000,8000,0 |
| input-budget-80.json | budget-80.json | a-hz-tea, a-hz-xihu | 8000,0 |
| input-empty.json | empty.json | 空集合 | 无 |

逐项核对REST hits、Java items、total/relation、投影以及esRequest，不固定took或评分小数。ID升序只是核对顺序。展示壳分别提交同条件，展开观察区，核对预算元→分及卡片，不要求编写前端。请求的_source includes和term value对象与Java实际序列化一致。

## 故障与恢复

```bash
bash labs/f07/03-errors.sh
```

脚本将短暂停止框架篇专用ES，先结束依赖该节点的其他操作。它不操作9200/9201或删除持久卷。先看Java health200、负预算400；ES停止后Java health仍200但搜索503；重新启动ES并等就绪，再搜三ID。Java进程与Client保持不变。EXIT trap尝试恢复ES；中途退出后仍需确认容器/索引就绪。

在展示壳另做一次：先有卡片，再停ES并点搜索，故障应清空旧卡片；恢复后重试回到三ID。空结果200与失败503分开。错误端点可用服务端启动变量ES_URL=http://127.0.0.1:19299对照，修正变量需重启Java；勿修改浏览器访问ES。

3案例：f07-c01 REST↔Java，f07-c02校验/故障/恢复，f07-c03展示壳调用与结果。教学主流程17请求=准备6+比较6+诊断5；清理1，探活重试、作者附加边界与浏览器重复调用另计。脚本中的预期400/503用curl保留body/status，不以curl返回0判定成功。

## 清理与第二轮

结束Java（Ctrl+C），在projects/travel-search目录执行：

```bash
bash labs/f07/cleanup.sh
```

仅删除tut-f07-attractions；不删其他课索引或卷。然后从01-prepare重新开始；十二项应再次created，所有对照可重做。只想停止专用ES可用 `docker compose -f infra/single-node/compose.yaml stop es`。

[实际两轮证据](../../review/f07/README.md)；[案例清单](cases.json)。
