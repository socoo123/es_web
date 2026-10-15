# F05 · 名称关键词、精确条件与短语

对应 [F05 正文](../../../../framework/f05.html)。用 F04 相同的五份正确文档，解释“西湖”名称搜索、HZ 精确编码和词序条件。3 个执行案例，22 条教学 HTTP 请求，点名清理另1条；等待探活与作者断言读取另计。没有 Java、展示壳或中文插件。

**当前状态：脚本和预测已交付，真实 ES 两轮未完成。**本次云环境重试 ES9.4.0，因缺少 `/proc/self/coredump_filter` 在 HTTP 前退出。下面的命中与 token 都是预测；原始启动诊断见 [review/f05](../../review/f05/README.md)，不能用 F03/F04 的记录替代本课实测。

## 前提与资源

- Bash、curl（支持 `--fail-with-body`）、Docker Compose；专用 `http://127.0.0.1:19200`，无认证，ES9.4.0 / travel-search-lab。
- 使用 [原有隔离 Compose](../../infra/single-node/compose.yaml)，1主/0副本，持久卷；不连接源码篇9200/9201。
- 只新建 `tut-f05-attractions`，不依赖 F04 已执行。数据与 mapping 独立放在本课目录，与 F04 的正确版本逐字一致。
- [固定数据](../../data/f05/attractions.json)与 [NDJSON](../../data/f05/attractions.ndjson)，[完整 mapping](../../search/f05/index.json)：name=text/standard，name.raw、city_code=keyword；没有搜索分析器覆盖或 normalizer，dynamic=strict。
- 样本日期、坐标、价格与营业状态只作教学。金额单位为分、币种 CNY；名称、业务 ID 与 F02/F04 一致。

| 字母 | ID | 名称 | 城市 | 价格（分） | 状态 |
| --- | --- | --- | --- | --- | --- |
| A | a-hz-xihu | 杭州西湖 | HZ | 0 | open |
| B | a-hz-tea | 湖畔茶园 | HZ | 8000 | open |
| C | a-fz-xihu | 福州西湖 | FZ | 0 | open |
| D | a-hz-night | 西湖夜游 | HZ | 26000 | open |
| E | a-hz-old | 西湖旧展馆 | HZ | 6000 | offline |

## 首次执行

从仓库根目录进入工程。`env.sh` 会固定工作目录和本课专用端点，不读取读者其他 ES 地址。

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
bash labs/f05/01-prepare.sh
bash labs/f05/02-keywords.sh
bash labs/f05/03-exact.sh
bash labs/f05/04-phrase.sh
```

也可以执行 `bash labs/f05/run.sh` 启动、等待并顺序运行相同脚本。它不自动删除已存在的索引。已有同名资源时，先确认资料可删，再按下节清理；不能忽略创建失败继续查旧语料。

| 脚本 | HTTP 条数 | 输入与检查 |
| --- | --- | --- |
| [01-prepare.sh](01-prepare.sh) | 6 | 版本、创建、限定索引健康、mapping、Bulk、refresh。核对9.4.0/集群名、acknowledged、green/timed_out=false、九个字段；Bulk errors=false且五项created、refresh failed=0 |
| [02-keywords.sh](02-keywords.sh) | 7 | match_all、三次 _analyze、term(name)、match OR/AND |
| [03-exact.sh](03-exact.sh) | 5 | HZ/hz、name.raw 部分/完整值、term(name, 西)正例 |
| [04-phrase.sh](04-phrase.sh) | 4 | 逆序 AND、正序/逆序/长短语，显式 slop=0 |
| [cleanup.sh](cleanup.sh) | 1（另计） | 只删除 tut-f05-attractions，缺失可忽略 |

HTTP 成功后还要读 JSON。Bulk 逐项判断；搜索必须 timed_out=false、_shards.failed=0，再核对 total 的 value/relation=eq、全部 _id、name/city_code/status 等源字段。curl 不能识别 HTTP200 内的条级失败或语义错误。

## 三个案例与预测

案例定义见 [cases.json](cases.json)。所有搜索请求都为 `POST /tut-f05-attractions/_search`，请求体位于 [search/f05](../../search/f05)，有完整 size/track_total_hits/_source/query/sort；显式 ID 升序仅便于核对，不能据此次序判断相关性。字母表示集合，实际返回 ID 为字典升序，见 [expected.json](../../search/f05/expected.json)。该文件是预测，不是 ES 响应。

f05-c01 先看规则：三次 `POST /tut-f05-attractions/_analyze` 分别用 field=name 分析“西湖”“杭州西湖”“湖畔茶园”。预测 token/position 为西0湖1、杭0州1西2湖3、湖0畔1茶2园3。_analyze 是对输入应用规则，不读取已存文档的 token。

| 案例 | 请求文件 | 预测集合 / total | 判断原因 |
| --- | --- | --- | --- |
| c01 | [all.json](../../search/f05/all.json) | ABCDE / 5 | 全量搜索基线 |
| c01 | [term-name.json](../../search/f05/term-name.json) | 空 / 0 | name 没有完整的“西湖”词项 |
| c01 | [match-or.json](../../search/f05/match-or.json) | ABCDE / 5 | 默认 OR，B 也有湖；没有查询 description |
| c01 | [match-and.json](../../search/f05/match-and.json) | ACDE / 4 | 两项都要有，排除 B |
| c02 | [term-city.json](../../search/f05/term-city.json) | ABDE / 4 | keyword 完整编码 HZ |
| c02 | [term-city-lower.json](../../search/f05/term-city-lower.json) | 空 / 0 | 本课无 normalizer，hz 不等于 HZ |
| c02 | [term-name-raw.json](../../search/f05/term-name-raw.json) | 空 / 0 | name.raw 没有完整值“西湖” |
| c02 | [term-name-full.json](../../search/f05/term-name-full.json) | A / 1 | name.raw 完整等于杭州西湖 |
| c02 | [term-name-token.json](../../search/f05/term-name-token.json) | ACDE / 4 | name 中确实有西这个单字词项 |
| c03 | [match-and-reversed.json](../../search/f05/match-and-reversed.json) | ACDE / 4 | AND 湖西不管顺序 |
| c03 | [phrase.json](../../search/f05/phrase.json) | ACDE / 4 | 西后紧接湖，比较相对位置 |
| c03 | [phrase-reversed.json](../../search/f05/phrase-reversed.json) | 空 / 0 | 没有湖后紧接西 |
| c03 | [phrase-full.json](../../search/f05/phrase-full.json) | A / 1 | 有杭、州、西、湖的相邻序列 |

本课无城市/价格/状态的组合条件。C、D、E 的存在是教学反例；名称命中不能证明满足杭州、预算或仍开放。AND 不等于 phrase，phrase 不等于完整字符串相等；新增更长名称或更换分析器后，集合可能改变。

## 清理、恢复与第二轮

确认本课资料可删后：

```bash
bash labs/f05/cleanup.sh
bash labs/f05/01-prepare.sh
bash labs/f05/02-keywords.sh
bash labs/f05/03-exact.sh
bash labs/f05/04-phrase.sh
```

清理仅点名 `tut-f05-attractions`；没有通配符、卷删除或 F03/F04 操作。第一轮与清理后第二轮应得到相同 token、ID 和计数。02–04 是只读查询，可重复；01 不应忽略重复创建错误。

如果总数不对，先核对 Bulk 每项、refresh 与 match_all；如果 term 为空而 match 有值，核对字段和 token；如果 phrase 与预测不同，核对 mapping、查询词序和 slop。不要靠改索引名或放宽查询掩盖旧数据。连接失败先处理节点/端口，不是把 query 从 term 换成 match。

结束时可手工 `docker compose -f infra/single-node/compose.yaml stop`，停止课程专用节点并保留卷。作者验收执行 `python3 review/f05/verify.py`，会拒绝自动删除首次已存在的 F05 索引，再执行两轮和每轮的点名清理；详见 [执行说明](../../review/f05/README.md)。
