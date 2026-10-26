# F20 · 点评质量、热度与 function_score

[正文](../../../../framework/f20.html)先解释固定信号的来源、平滑、量纲与候选门槛。[11份虚构资料](../../data/f20/attractions.json)、[审核/窗口/缺值契约](../../data/f20/signals.json)。不是实际商户质量或生产规则推荐。

独立ES9.4.0/Lucene10.4.0、19220/tut-f20-attractions，一主零副本/strict/refresh=-1，无插件。简介whitespace/lowercase，显式BM25 k1=1.2/b=.75/discount_overlaps=true；空格给定中文整词，不评名称。默认HZ/open/CNY/0–10000整数分，_score降序＋业务ID升序，前20/精确计数/完整解释。

需要Docker/Compose、Bash、curl、Python3；Java需要JDK25。终端一从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19220
docker compose -f infra/f20/compose.yaml up -d es
bash infra/f20/wait.sh
# 已有本课索引先cleanup再从01重做
bash labs/f20/01-quality.sh
bash labs/f20/02-popularity.sh
bash labs/f20/03-boundaries.sh
```

| 案例 | 教学HTTP | 判断 |
| --- | --- | --- |
| f20-c01 / 01 | 14 | 版本/插件/green/Bulk11/refresh/count/有效mapping/settings；text/均分/平滑及两次完整解释 |
| f20-c02 / 02 | 11 | text/raw/quality/compressed/bounded，逐份公式核对，六次解释：热度压倒/压缩仍坏/整个函数封顶 |
| f20-c03 / 03 | 21 | rank与rank-only、编码S/饱和、硬条件、缺值/ln零错误、特征0/负/多值拒绝、sort/聚合拒绝、factor位置、预算/异城/空集 |
| Java↔REST / 04 | 33 | 11输入，每组Java＋实际搜索DSL重放＋完整query解释重放；卡片、信号、原文、价格、解释树 |
| 合计 | 79 | 清理/探活/构建/Java内部调用/作者附加/浏览器另计 |

终端二从仓库根目录：

```bash
cd projects/travel-search/backend
# JAVA_HOME/PATH先选择JDK25
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19220 APP_PORT=18080 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f20/04-java.sh
# 可选手工请求，不计79
curl --fail-with-body -sS -X POST http://127.0.0.1:18080/api/attractions/signal-search -H 'Content-Type: application/json' --data-binary @search/f20/input-bounded.json
```

打开http://127.0.0.1:18080/f20.html。text/raw/average/quality/compressed/bounded/rank/rank-only八模式。质量Q=(vR+80)/(v+20)，在上游算好再写入；缺Q用4、缺H用0。compressed函数F=0.2Q+0.15ln(1+H)，bounded最终B+min(F,1.5)。显式score_mode=sum/boost_mode=sum；不是默认multiply，也不是限制最终分。ln1p压缩仍把弱相关展厅排第一；封顶降到第五，但仍高于缺信号者。huge与steady都达封顶、文本相同，由ID排序。

rank文本must、特征should，S/(S+4)，缺特征只不加分；rank-only改成特征must，山林进入、missing退出。特征编码S与原Q存在约0.4%精度误差，断言用解释中S。单值正数、普通double与rank_feature边界分别实测，不据本课宣布性能收益。

每次显示实际输入、DSL、客户端完整响应/DTO与完整_explain；两次请求非并发原子视图。条件变化/失败清空旧内容。非法输入400、ES拒绝502、连接/transport503、不完整结果502；未构造超时/分片部分失败。浏览器→Java→ES，不直连ES，不把凭据放浏览器或URL。

点名清理和重做：

```bash
bash labs/f20/cleanup.sh
bash labs/f20/01-quality.sh
bash labs/f20/02-popularity.sh
bash labs/f20/03-boundaries.sh
bash labs/f20/04-java.sh
# 结束；另关闭自己启动的Java
bash labs/f20/cleanup.sh
docker compose -f infra/f20/compose.yaml stop es
```

cleanup只DELETE tut-f20-attractions、GET404，不删其他索引/卷；重复建索引400，重复Bulk create条级409，停止不清持久数据。没有真实凭据，本课ES关闭安全且仅回环端口，不是生产安全配置。

[完整查询](../../search/f20)、[真实两轮](../../review/f20/README.md)、[图解/HTTP/观察窗](../../../../docs/framework-review/20261026-f20-signals/README.md)分列。未测整体质量/留出指标、性能、多节点、生产安全或持续更新。只实施F20，未实施F21。
