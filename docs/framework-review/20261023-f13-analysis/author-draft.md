# F13｜明明有“北京故宫博物院”，为什么搜不到？

> 作者说明：当前作者子进程实际使用的 reasoning 运行元数据由主作者日志核验，本稿不自行声称已设置 xhigh。本文未运行 ES、构建 Java 或启动服务；所有 token、命中与恢复结果均为**待实测预期**，须由主作者在实际 ES 环境中完成两轮验收后校正。

前置：已理解 `text/keyword`、`match/match_phrase`、组合过滤与 Java 搜索接口。

学完本课，你应能：

- 用 token、position、offset 解释文本经过分析后发生了什么。
- 找出索引分析链与查询分析链的故意失配，并验证一次局部恢复。
- 区分“满足查询规则”与“符合游客意图”，解释恢复召回后留下的误匹配。

## 1．先把“搜不到”变成可以解释的问题

游客选择北京，预算不超过 100 元，输入“故宫”。运营确认资料里有“北京故宫博物院”，搜索却返回空集。

名称里看得见这两个字，为什么没有命中？

全文查询需要关注两次文本处理：写入时，名称怎样形成可检索的词项；搜索时，“故宫”怎样形成查询词项。两边产生的词项能否对应，会影响结果。原文中出现了某段文字，并不能单独证明当前字段、当前请求一定命中。

本课故意准备一个失配字段：写入时把“故宫”分析为“故”和“宫”，查询时却把它作为完整的“故宫”词项。我们只修复这个明确的漏召回原因。

这也不是“standard 默认搜中文会失败”的证明。后面的对齐字段恰恰用于说明：在本课语料和配置下，它能够召回包含相关字项的文档；真正需要继续追问的是，召回的是否都是游客想找的景点。

## 2．分析链：先处理字符，再切分，再处理词项

把“故宫 Palace-MUSEUM（东门）”交给本课的 `travel_text`，可以沿着三个环节观察：

**输入文本 → 字符过滤 → 分词 → 词项过滤 → token。**

字符过滤器先处理字符流，例如 `html_strip` 去掉 HTML 标签。随后，tokenizer 按规则切分文本。最后，token filter 处理已经切出的 token，例如 `lowercase` 将英文归一为小写。

一个 analyzer 恰好包含一个 tokenizer，可以有零到多个字符过滤器和零到多个词项过滤器。执行顺序影响结果，三者的职责也不能互换。[官方自定义分析器说明](https://www.elastic.co/docs/manage-data/data-store/text-analysis/create-custom-analyzer)

本课显式定义：

| 名称 | 配置与用途 |
|---|---|
| `travel_text` | `custom`；`html_strip` → `standard` tokenizer → `lowercase` |
| `case_sensitive` | 自定义 analyzer；使用 `standard` tokenizer，无 token filter；仅供对照查询覆盖 |

这里的 `lowercase` 是 filter 的工作。只指定 `standard` **tokenizer**，不会因此自动得到小写归一。

也不要把 `standard` 描述成理解“故宫”这一旅游实体的中文语义分词器。本课预期观察到的中文单字 token，只能说明当前切分规则怎样处理这些字符，不能证明它理解了景点名称。

索引与搜索也不要求永远采用完全相同的 analyzer；需要判断的是两边的设计能否支持目标查询。本课先用相同链建立容易解释的基线，再单独观察故意失配。[官方 `search_analyzer` 说明](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/search-analyzer)

【插入图解位置 A：同一份文本经过索引链、查询链的对照。箭头表示文本处理；注明省略底层索引格式。】

## 3．固定八份资料，让每个命中都有来由

实验锚定 ES 9.4.0 / Lucene 10.4.0，使用独立索引 `tut-f13-attractions`：一主分片、零副本、`refresh_interval=-1`、`dynamic: strict`。八份文档的币种均为 CNY，金额单位为整数分。

| 业务 ID | name | 城市 | 状态 | 价格／分 |
|---|---|---|---|---:|
| bj-palace | 北京故宫博物院 | BJ | open | 6000 |
| bj-mixed | 北京故宫博物院 Palace-MUSEUM（东门） | BJ | open | 6000 |
| bj-separated | 故城宫苑 | BJ | open | 3000 |
| bj-punctuation | 故，宫主题展 | BJ | open | 1000 |
| sy-palace | 沈阳故宫博物院 | SY | open | 5000 |
| bj-closed | 北京故宫夜游 | BJ | closed | 7000 |
| bj-other | 北京国家博物馆 | BJ | open | 0 |
| bj-dash | Palace Museum | BJ | open | 4000 |

同一个 `name` 输入建立三种字段表达：

- `name`：`text`，索引与搜索均显式使用 `travel_text`。
- `name.mismatch`：`text` 多字段，索引用 `travel_text`，`search_analyzer` 故意设为 `keyword`。
- `name.raw`：`keyword`，保留名称整值的精确表达。

`name.mismatch` 仍是文本字段；它的搜索 analyzer 叫 `keyword`，不意味着字段类型变成了 `keyword`。

【插入代码位置 A：完整 settings/mapping、八份固定数据与准备入口。导入后显式 refresh，再核对八份资料。重做时只点名删除本课索引并重新准备。】

以下主查询始终限定 **BJ、CNY、open、价格 0–10000 分，包含两端**，按可排序的 keyword 业务 ID 升序返回。这个顺序用于稳定核对，本课不解释评分高低。

## 4．先分析输入，再解释真实搜索

### 4.1 看清 token、position 与 offset

向本课索引的 `_analyze` 提交 `field: name`，文本使用：

```text
故宫 Palace-MUSEUM（东门）
```

**待实测预期：**

| token | position | offset 半开区间 |
|---|---:|---|
| 故 | 0 | [0, 1) |
| 宫 | 1 | [1, 2) |
| palace | 2 | [3, 9) |
| museum | 3 | [10, 16) |
| 东 | 4 | [17, 18) |
| 门 | 5 | [18, 19) |

`token` 是分析得到的词项文本。`position` 表示词项位置，可用于解释短语关系。`offset` 则指向原始输入中的文本范围，可用于定位原文；它不是第几个词，也不是字节偏移。

本课 offset 按 UTF-16 单位理解，区间包含起点、不包含终点。再分析“故宫😀 Palace”：😀占两个 UTF-16 单位，因此 `Palace` 对应范围预期为 `[5,11)`，不能按照肉眼数出的字符个数直接推算。

接着保持第一份文本不变，做三次临时对照：

1. 只指定 `standard` tokenizer：英文预期仍为 `Palace`、`MUSEUM`。
2. 加入 `lowercase` filter：英文预期变成 `palace`、`museum`。
3. 换成 `whitespace` tokenizer：预期按空白切成“故宫”和“Palace-MUSEUM（东门）”，连字符、括号不会按前一种规则拆开。

第三次改变的是切词规则，不能解释成“只是关闭了小写转换”。

再显式指定 `analyzer: travel_text`、`explain: true`，分析：

```text
<b>故宫</b> Palace-MUSEUM（东门）
```

观察字符过滤后的文本、tokenizer 的输出，以及 lowercase 后的输出。offset 仍应对照原始字符串核对，不能在去标签后的短串上重新编号。分析过程不会把 `_source` 中的原文改成小写或去标签后的文本。

【插入代码位置 B：上述 `_analyze` 对照、UTF-16 样本及纯标点样本；实际响应由主作者补入。】

### 4.2 为什么分析结果看起来正常，搜索仍然为空？

对 `field: name.mismatch` 调用 `_analyze`，预期仍能看到“故”“宫”。这里推导的是字段的**索引 analyzer**，不会自动模拟它的 `search_analyzer`。

要观察故意失配的查询链，应显式使用 `analyzer: keyword`，对同一个输入“故宫”分析。预期只有一个完整 token：“故宫”。

于是问题具体了：文档写入时形成的是“故”和“宫”，查询寻找的却是完整词项“故宫”。把 `operator` 改成 AND 也无法补救，因为查询分析后只有一个词项，AND 不会替你重新切词。

`_analyze` 的职责是分析提交的文本并返回 token。[官方 Analyze API 说明](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-analyze) 它没有直接读取这些文档已经存下的词项，也不能证明真实搜索一定命中。判断必须同时对照 mapping/settings、固定数据、refresh 前提和实际 search。

### 4.3 六个对照，分别回答什么？

下表全部是**待实测预期**，共同使用前述业务过滤与 ID 排序：

| 查询 | 预期命中 ID |
|---|---|
| `name.mismatch`，`match 故宫`，AND | 空集 |
| `name`，`match 故宫`，AND | bj-mixed、bj-palace、bj-punctuation、bj-separated |
| `name`，`match_phrase 故宫`，`slop: 0` | bj-mixed、bj-palace、bj-punctuation |
| `name`，`match PALACE-MUSEUM`，AND，使用 `travel_text` | bj-dash、bj-mixed |
| 同一英文查询，局部覆盖 `analyzer: case_sensitive` | 空集 |
| `name.mismatch`，局部覆盖 `analyzer: travel_text`，`match 故宫`，AND | 与第二行相同的四份 |

第二行中，AND 要求分析得到的“故”和“宫”都能匹配，不要求二者相邻。因此，“故城宫苑”也满足规则。按照本课“寻找故宫景点”的人为相关性判断，它属于误召回。

第三行增加了词序和位置约束，“故城宫苑”被排除。但“故，宫主题展”的逗号在当前分析链中被丢弃，“故”和“宫”预期仍占相邻位置，所以 `slop: 0` 仍会命中。**短语匹配分析后的词项位置，不等于原文逐字包含“故宫”。** 这份主题展在本课标注下仍是误召回。

英文对照则展示归一化的作用：`PALACE-MUSEUM` 经 `travel_text` 预期成为 `palace`、`museum`，能对应两份英文名称。覆盖为 `case_sensitive` 后，查询保留大写，无法对应索引侧的小写词项。

最后一行只改变当前请求的查询分析方式，预期恢复四份结果。它没有修改 mapping、字段的默认搜索配置或历史 token；下一次不带覆盖参数的失配查询，仍预期为空。

沈阳资料被城市排除，夜游资料被状态排除；“北京国家博物馆”缺少所需词项。不要把这些未命中都归因于分析链。

【插入代码位置 C：六组关键 DSL 与实际 ID、价格对照。保留相同过滤条件，仅改变表中指定部分。】

## 5．Java 对应：返回分析证据，也执行同一份查询

复用 Boot 4.0.8 / JDK 25、官方 Java 与 Rest5 Client 9.4.8 的既有工程，新增独立端点：

```text
/api/attractions/analysis-search
```

输入为 `q`、`cityCode`、`maxPriceFen`、`mode`。服务端校验非空查询和合法条件，并把 mode 限定为四种；字段、索引与 analyzer 由服务端选择。

下面是关键 Java 草稿，导包、Controller 与既有异常映射在工程位置补齐：

```java
record Plan(String field, String queryAnalyzer, boolean phrase) {}

Plan p = switch (mode) {
    case "mismatch" ->
        new Plan("name.mismatch", "keyword", false);
    case "aligned" ->
        new Plan("name", "travel_text", false);
    case "phrase" ->
        new Plan("name", "travel_text", true);
    case "case-sensitive" ->
        new Plan("name", "case_sensitive", false);
    default -> throw new ResponseStatusException(
        HttpStatus.BAD_REQUEST, "未知 mode");
};

var indexAnalysisRequest = AnalyzeRequest.of(a -> a
    .index("tut-f13-attractions").field(p.field()).text(q));

var queryAnalysisRequest = AnalyzeRequest.of(a -> a
    .index("tut-f13-attractions")
    .analyzer(p.queryAnalyzer()).text(q));

var indexAnalysis = client.indices().analyze(indexAnalysisRequest);
var queryAnalysis = client.indices().analyze(queryAnalysisRequest);

var match = new MatchQuery.Builder()
    .field(p.field()).query(q).operator(Operator.And);

if ("case-sensitive".equals(mode)) {
    match.analyzer("case_sensitive");
}

Query nameQuery = p.phrase()
    ? MatchPhraseQuery.of(m -> m
        .field(p.field()).query(q).slop(0))._toQuery()
    : match.build()._toQuery();
```

两份分析请求都输入同一个 `q`：第一份观察字段索引链怎样处理它，第二份观察本模式查询链怎样处理它。返回说明应写“对输入 q 的分析”，不能声称“读到了文档存量词项”。

普通模式的搜索由 mapping 选择搜索 analyzer；只有 `case-sensitive` 模式显式覆盖。`queryAnalyzer` 同时用于构造第二份分析请求，必须与实际查询语义一致。

【插入代码位置 D：将 `nameQuery` 放入固定索引的搜索请求，补齐城市、币种、状态、价格过滤及业务 ID 排序；返回两份分析请求及实际 token、实际发送的搜索 DSL、命中 ID 与价格。】

观察区应序列化实际发送的同一个 `SearchRequest`，避免另写一份展示用 DSL。实际调用仍是**浏览器 → Java → ES**；Pages 只承载教程。Java 构建、实连与结果一致性均待主作者验收。

## 6．误匹配与能力检查

以下答案同样基于待实测预期。先解释原因，再查看答案；实际结果不同，应先核对实验前提。

<details>
<summary>练习一：name.mismatch 的 _analyze 已返回“故”“宫”，能否据此断定查询链没有问题？</summary>

不能。`field` 分析观察的是索引链。应再显式使用 `keyword` 分析相同查询，核对它产生完整“故宫”，并对照 mapping 与实际失配搜索。

</details>

<details>
<summary>练习二：把失配查询的 operator 从 OR 改成 AND，为什么预期仍是空集？</summary>

`keyword` 将“故宫”保留为一个词项。AND 约束的是分析后的词项，并不负责拆字；它无法把完整词项变成索引侧的“故”和“宫”。

</details>

<details>
<summary>练习三：对齐后四份命中，为什么不能直接说中文搜索已经正确？</summary>

“故城宫苑”和“故，宫主题展”满足当前查询规则，却不符合本课寻找故宫景点的标注。恢复了漏掉的候选，不代表误召回同时消失。

</details>

<details>
<summary>练习四：slop 为 0，为什么仍预期命中“故，宫主题展”？</summary>

当前链丢弃逗号后，“故”和“宫”的词项位置仍相邻。短语查询检查分析后的顺序与位置，不能据此断言原文存在连续的“故宫”子串。

</details>

<details>
<summary>练习五：英文改成小写后，是否意味着 _source 也变成了小写？</summary>

没有。lowercase 处理分析链中的 token，`_source` 保留输入原文。只指定 standard tokenizer 的对照应保留大写，由此定位归一化发生在哪一步。

</details>

<details>
<summary>练习六：局部覆盖 travel_text 恢复命中后，删除覆盖参数再查，会怎样？</summary>

预期重新变为空集。局部参数没有修改 `name.mismatch` 的 `search_analyzer`，也没有重新处理历史文档；恢复作用仅限带覆盖的请求。

</details>

<details>
<summary>能力题：使用 aligned 搜“故宫”，只把预算上限降到 5000 分，预期剩谁？这能证明分析链更准确了吗？</summary>

预期剩 bj-punctuation（1000 分）与 bj-separated（3000 分）。两份 6000 分资料被预算排除；分析链没有变化，剩余两份在本课标注下仍是误召回。结果变少本身不是质量改善的证据。

</details>

## 7．陷阱、速记与下一课

**陷阱一：用纯标点的空 token 推导所有空结果。**
“，！？”经过 `travel_text` 预期没有 token，它与本课故意失配是不同原因。实际搜索为空还应检查城市、状态、预算、数据可见性与被查询字段。

**陷阱二：把 offset 当成字节数或词序号。**
中文、英文和 emoji 不能按同一种字节长度推算。position 用于解释词项位置关系，offset 用于定位原始文本；经过字符过滤后，还要考虑向原串的偏移校正。

**陷阱三：用一次 `_analyze` 代替存量数据验收。**
它说明当前配置如何处理所给输入。只有把配置、固定数据和实际 search 连起来，才能支持“这次漏召回由分析链失配造成”的结论。

| 要记住的对象 | 本课判断方法 |
|---|---|
| analyzer | 字符过滤 → 一个 tokenizer → 词项过滤 |
| lowercase | 属于 filter，不是 standard tokenizer 自带动作 |
| AND | 检查分析后的词项是否都能匹配 |
| phrase | 检查词项顺序与位置，不保证原文连续子串 |
| `_analyze` | 分析输入，不直接证明历史词项或命中 |
| 请求覆盖 | 改变本次查询，不修改字段配置与历史 token |

本课解决的是一个边界清楚的问题：索引链与查询链故意失配，导致应有候选漏掉；对齐后能够恢复，并解释新增候选为何出现。

遗留问题也已显现：“故城宫苑”为什么被召回？什么样的切词规则更适合旅游名称？下一课 F14 才在同一语料上比较分析方案与插件。本课保留这套内置基线；词典、同义词和评分分别留到 F15、F16、F18。先能解释词项怎样产生，后面的比较才有依据。
