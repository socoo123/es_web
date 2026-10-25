# F16 · 别名、查询同义词与繁简

[正文](../../../../framework/f16.html)先解释三种关系。11份虚构目录与[固定意图](../../data/f16/judgments.json)，独立ES9.4.0/Lucene10.4.0、端口19216、索引tut-f16-attractions、同义词集tut-f16-names；一主零副本、strict、refresh=-1。只装官方ICU9.4.0，standard逐字中文基线，不改F15的IK词典。

需要Docker/Compose、Bash、curl、Python3.10+，Java需要JDK25。先验证/下载及构建，再清理已有课次资源；ICU锁定[官方SHA512与descriptor](../../infra/f16/plugins.lock.json)，可复用F14缓存但重新核验，不把缓存读取称作新下载。

终端一，从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19216
python3 infra/f16/fetch.py
docker compose -f infra/f16/compose.yaml build es
docker compose -f infra/f16/compose.yaml up -d es
bash infra/f16/wait.sh
# 已存在本课资源时，先执行下文cleanup再运行01
bash labs/f16/01-aliases.sh
bash labs/f16/02-graph.sh
bash labs/f16/03-normalize-and-update.sh
```

| 案例 | 教学HTTP | 观察证据 |
| --- | --- | --- |
| c01 / 01 | 22 | 版本/插件、先建规则、索引green、Bulk11全created/refresh/count、完整配置、中文token与别名/同义词/城市 |
| c02 / 02 | 12 | 英文位置图、AND默认/放宽/phrase、三个validate改写、无效stop规则400与正常查询恢复 |
| c03 / 03 | 21 | 繁简/原文/已存向量、实体别名更新前后/refresh、完整规则集替换与实际重载、不变历史词项、删除引用集400 |
| 04 Java↔REST | 32 | 8组：1 Java API + 2实际分析请求重放 + 1实际DSL重放；完整DTO与token位置/跨度/offset/类型一致 |
| 合计 | 87 | 清理、探活、下载/构建、Java内部ES调用、可选重复、浏览器/作者附加另计 |

终端二，从仓库根目录：

```bash
cd projects/travel-search/backend
# JAVA_HOME与PATH先选择JDK25
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19216 APP_PORT=18080 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f16/04-java.sh
# 可选手工重复，不计87
curl --fail-with-body -sS -X POST http://127.0.0.1:18080/api/attractions/synonym-search -H 'Content-Type: application/json' --data-binary @search/f16/input-en.json
```

打开http://127.0.0.1:18080/f16.html。只读观察窗经Java访问ES；Pages不连接本机。plain不转繁简；aliases在name/name_en/aliases用基础链和phrase；graph在name/name_en用同义词+AND/自动短语true；loose将自动短语改false；phrase约束完整路径；late把小写/繁简放在同义词后。全部固定城市、open、CNY、非负预算与业务ID升序。

- 紫禁城/BJ：plain=bj-wall；aliases=bj-palace,bj-wall；graph=bj-palace,bj-theme,bj-traditional,bj-wall，后两商户为误入。
- 紫禁城/SY：aliases空；graph=sy-palace，城市过滤正确但实体意图不合。
- PALACE museum/BJ：graph=bj-palace,bj-tail；loose=bj-gap,bj-palace,bj-reverse,bj-tail；phrase=bj-palace；late空。
- 故宮/BJ：plain空；aliases/graph四个中文候选；late缺bj-wall。
- 03更新后：皇家旧宫/aliases仅bj-palace；皇城旧称/graph四个中文候选。修改资料与发布查询集分开，只有后者无需重写已有名称词项。

观察窗两列都分析本次输入，不读取历史词项；03才用显式已存向量核对历史。Java explain=true保留完整详细属性，不用裁剪属性触发客户端必填错误；服务端固定字段/analyzer/索引。输入400，ES拒绝502，连接/transport503；条件或错误清空旧卡片与请求。0命中为200。

完整规则集PUT会替换整集，别漏掉旧规则。先创建同义词集再建引用索引；清理顺序反过来。重做时仅点名本课资源，恢复初始别名与规则：

```bash
bash labs/f16/cleanup.sh
bash labs/f16/01-aliases.sh
bash labs/f16/02-graph.sh
bash labs/f16/03-normalize-and-update.sh
bash labs/f16/04-java.sh
# 结束；另外关闭自己启动的Java
bash labs/f16/cleanup.sh
docker compose -f infra/f16/compose.yaml stop es
```

[真实两轮](../../review/f16/README.md)、[内容/图解/阅读/观察窗](../../../../docs/framework-review/20261025-f16-synonyms/README.md)分列。整体中文质量、性能、多节点传播、在线发布与权限不在本课实测范围；不预先实现F17。
