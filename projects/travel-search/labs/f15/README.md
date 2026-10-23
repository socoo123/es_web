# F15 · 本地词典、历史词项与受控重建

[正文](../../../../framework/f15.html)先解释词典与历史索引表达。全部名字均为虚构；固定判断在[judgments.json](../../data/f15/judgments.json)。只操作独立19215节点与`tut-f15-v1/v2`，不修改前课节点/索引。需要Docker/Compose、Bash、curl、Python3.10+；Java观察需JDK25。无远程词典服务，无CDN，无浏览器ES凭据。

从仓库根目录开始，下载与构建先于清理已有实验。IK沿用F14的9.4.0维护方制品及本地SHA512（不是独立发布签名），[锁文件](../../infra/f15/plugins.lock.json)与descriptor核对后才安装。派生镜像只装IK；默认主词典保留，本地`ext_dict`指向UTF-8逐行文件。修改配置/词条后，本课通过重启节点加载；不宣称本地文件自动热更新。

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19215
python3 infra/f15/fetch.py
docker compose -f infra/f15/compose.yaml build es
python3 infra/f15/select-dictionary.py empty
docker compose -f infra/f15/compose.yaml up -d es
docker compose -f infra/f15/compose.yaml restart es
bash infra/f15/wait.sh
# 若本课索引已存在，先执行下方点名清理，再恢复empty并重启
bash labs/f15/01-baseline.sh
bash labs/f15/02-file-only.sh
bash labs/f15/03-load-and-new.sh
bash labs/f15/04-rebuild.sh
```

三个执行案例与实际请求数：

| 案例/阶段 | 请求数 | 手工观察 |
| --- | --- | --- |
| c01 / 01基线 | 23 | 版本/插件/空扩展预检、创建/green/Bulk9created/refresh/count9、完整配置；六份分析、四份已存向量、两查询 |
| c02 / 02仅文件 | 4 | 写travel.dic，不重启；两查询token与ID仍旧 |
| c02 / 03重启及新资料 | 21 | 重启后分析已变、旧向量不变、旧九份两查询0；Bulk2created/refresh/count11后只新ID命中 |
| c03 / 04重建 | 20 | v1写阻塞、预建v2/green、同步_reindex、refresh/count11/完整配置、分析/已存向量/搜索 |
| 05 Java↔REST | 16 | 两查询×两索引：实际分析、已存词向量、搜索DSL分别重放REST |
| 合计 | 84 | 清理/探活/下载构建、Java内部ES调用、手工重复、浏览器/作者附加另计 |

[完整mapping](../../search/f15/index.json)：一主零副本/strict/refresh=-1，name索引与查询都用ik_smart，显式`term_vector=with_positions_offsets`。9旧+2新资料固定业务ID，票价整数分。相同城市/open/CNY/0–10000分、AND、ID升序；不比较评分策略。存储向量请求不传`doc/per_field_analyzer`，避免把当前临时分析误称历史证据。

| 阶段 | 云栖里/HZ | 星澜湾/NJ |
| --- | --- | --- |
| 空扩展基线/只改文件 | hz-brand | nj-bay、nj-scattered |
| 加载后仅旧资料 | 空 | 空 |
| 加载后写入两份 | hz-new | nj-new |
| 重建 | hz-brand、hz-new | nj-bay、nj-boundary、nj-new |

nj-scattered是原串字误入；nj-boundary是新误入：“星澜”场馆的“湾流”科普与目的地无关，`星/澜/湾流`在加词后变为`星澜湾/流`。词典不能认证实体。所有原文/ID在v1与v2保持相同，旧词项不会因文件更新、refresh或重启自动改写。

Java第二终端：

```bash
cd projects/travel-search/backend
# JAVA_HOME和PATH使用JDK25；沿用Boot4.0.8与官方客户端9.4.8
./mvnw clean package
ES_URL=http://127.0.0.1:19215 APP_PORT=18080 java -jar target/travel-search-0.7.0.jar
```

第一终端继续：

```bash
bash labs/f15/05-java.sh
curl --fail-with-body -sS -X POST http://127.0.0.1:18080/api/attractions/dictionary-search -H 'Content-Type: application/json' --data-binary @search/f15/input-bay.json
```

可选末条curl不加入84。打开`http://127.0.0.1:18080/f15.html`；只读观察窗显示当前查询与固定旧ID的已存词项。original/rebuilt只是服务端两个索引白名单，不切词典。所有请求经Java；Pages不连接本机。输入400、ES拒绝/缺索引502、连接不可用503；恢复实验前提后可在同一Java进程重试。临时空token/0候选是成功，错误会清空旧卡片、token与请求。

重做必须清理本课索引，恢复empty并重启。否则索引已存在报400、冻结v1写入报403、重复create重建会冲突；不要吞错误继续。

```bash
bash labs/f15/cleanup.sh
python3 infra/f15/select-dictionary.py empty
docker compose -f infra/f15/compose.yaml restart es
bash infra/f15/wait.sh
bash labs/f15/01-baseline.sh
bash labs/f15/02-file-only.sh
bash labs/f15/03-load-and-new.sh
bash labs/f15/04-rebuild.sh
bash labs/f15/05-java.sh
# 结束：只删本课索引，逐个GET404；关闭自己启动的Java
bash labs/f15/cleanup.sh
docker compose -f infra/f15/compose.yaml stop es
```

本课用写阻塞与固定样本消除重建期间的变化，未完成持续写入/alias切流/在线恢复，后续F33/F41再学。远程词典、集群传播、性能、全站中文质量不在本轮通过范围。[实际两轮](../../review/f15/README.md)、[阅读/观察窗](../../../../docs/framework-review/20261024-f15-dictionary/README.md)独立记录。
