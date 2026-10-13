# ch27 管道查询语言重构验收

本轮仅重构 ch27、首页对应卡片与 STATUS。原14个实验ID及 ch27-esql-pipeline 机制ID保留；四组实验42操作卡（前置3、A14、B7、C6、D8、清理4），两幅交互图与两条有限trace，七步机制动画同步校正。

## 内容依据

Elasticsearch9.4.0固定提交 2e8528e92361c3399724226deaf2b46f933e925b / Lucene10.4.0。使用真正的干净源码checkout，按目标文件核对字节与行段。主要修正：管道是输入关系与结果语义，物理计划可等价优化；逻辑过滤移动与物理下推分开，剩余条件保留；普通long AVG为SUM/有效值COUNT，忽略缺失/null、计入多值；Page可携带文档位置等辅助列，256KiB为估算目标；Driver单链不表示全查询单线程；输出表不代表没有MATCH/_score/_source能力；前置LIMIT与输出截断不同。

## 真实 ES 验收

本机localhost:9200匿名单节点可用，根响应确认9.4.0/10.4.0及固定build_hash。两轮每轮42真实请求通过，另13补充观察通过，两索引最后HEAD404；完整请求与原始响应见 review/ch27-es-review.json，初始旧14卡实测见 ch27-original-responses.json。

A组均值200/175/150、降序LIMIT两行225、STATS后LIMIT仍200；类型错误400；profile出现INITIAL/FINAL/SumLong/Count/DivDoublesEvaluator及额外中转Driver，无FilterOperator。B组DSL平均200/175、默认三hits真实_source、size1仍AVG200、三种方法冲突405。C组四篇有效值三项，sum70/count3/rows4/mean≈23.333333；空输入一行null/0。D组MATCH返回b/a正分数、_score列double，未刷新GET可见但FROM五篇，refresh后平均225，删除并refresh恢复200/3。

补充验证重复创建400、重复固定ID写updated200、strict未知字段400且正确查询仍200、LENGTH(description)>9残留FilterOperator且AVG162.5、重复清理404与最终两个HEAD404。查询全部显式allow_partial_results=false；本课索引refresh_interval=-1、固定ID、显式刷新，不改集群设置，不创建异步结果。

真实失败保留：旧卡filter_path只取_id却宣称源字段；新验收初稿只保留hits子字段导致size0空hits数组被裁掉，改为保留hits.hits。第一次_score按文档float断言失败，真实响应double，MetadataAttribute注册DOUBLE；校正后清理完整重跑。诊断响应各自保留，没有合成成功数据。

## 图解与原生门禁

官方Archify3.0.1：两幅workflow v2：query-plan、avg-pages（初版dataflow及失败诊断另存）；zh-CN/showcase/trace，固定仓库身份、逐节点源码证据、真实 --repo-root。只改JSON并正式finalize生成，不手改HTML。两幅当前validate/deliver/strict check/browser-check均通过，showcase9/9、0错误0警告。当前本机file浏览器检查可用，旧云环境限制不继承为本轮结果；update.noticeRequired=false。复用ARCHIFY-LICENSE.txt并保留HTML内字体许可。

原稿与诊断保留：query-plan主路径rank回退拒绝后去掉可选mainPath，第二次viewport高度诊断后合并解析/分析阶段并启用纵向测量。AVG初版dataflow按固定stage宽度及标签重叠诊断修复后通过原生门禁，但HTTP手机检查发现宽图裁切；保留初版产物并改用两列workflow，同一组8节点、7关系与源码证据保留，箭头明确表示Page数据方向。两列初版仍触发窄屏宽画布裁切，保存失败JSON/截图，按实测将纵向间距展开为更高的画布重新finalize；当前收据为review-2，旧候选/收据未覆盖。没有手改生成HTML或放宽门禁。

## HTTP 与视觉

独立HTTP Chromium：两图1440/1600/1920/2048桌面×浅深；章节1920/1440/1024/768/390/320×浅深全部通过。阅读列最大880px、左右对齐差≤1px；整页/iframe不横溢、所有节点完整包含、说明卡无截断。两图桌面嵌入900px，≤800px为600/560px；这是本轮实测高度。桌面最小SVG字约6.742px，普通节点字约7.705px。

主题同步、节点源码探索/关闭、Enter/Escape焦点、暂停后外层重播、键盘重播、展开无present、reduced-motion静止与手动步进、无平滑滚动、目录/已读/上下课、42条控制台请求method/path/body、端点/认证别名/raw、Pages前缀与相对资产均通过，无未处理JS错误或失败HTTP资产。HTTP中控制台自动请求明确abort，只验证导航和请求内容；真实ES请求在独立API记录中验收，两者分开。

**已实际通过view_image查看全部七张联系表（24张最终截图与7个完整机制步骤），另看完整浅色计划图、深色AVG图与裁切失败图。** 双主题与390px完整路径均已审阅，未观察到文字越框、节点遮挡或卡片截断；手机图是总览，细字通过节点探索/展开/正文读取，不声称完整桌面细节在小屏全部可读。旧SVG/源码表仅容器内横滑，播放器控制与解说可读。截图哈希及审阅范围见ch27-visual-review.json。截图生成与实际审阅分别记录。

## 当前图源与产物

| 图 / 模式 | 路径 | candidate SHA-256 | HTML SHA-256 |
| --- | --- | --- | --- |
| query-plan / workflow v2 | `.archify/workflow-ch27-query-plan-20261013-213102/query-plan.html` | `d9a042a278cf54ac8bfb372f11635aec44c6746eab28b081ea755ccea1a2b729` | `b246b87530536fd7f37b9020d0da59272069988548578d767b757a41f0076af1` |
| avg-pages / workflow v2 | `.archify/workflow-ch27-avg-pages-20261013-213102/avg-pages.html` | `a183af8ef4b5fc11f04c5cb716f8ff3401848b063f9c8fa1fd88efe12e2f86d7` | `e99810b81dc58b7e1e5b14fea246af3290778e52a501a8189f087c5fdaee2864` |

query-plan当前根目录收据；avg-pages当前review-2收据，根收据属旧候选。各完整/简版收据与delivery保留，最终binding验证候选/HTML与当前收据SHA一致。废弃dataflow只作诊断历史，不作为本章当前交付图。

## 检查与复现

19目标文件 / 31精确源码区间字节与行号核对通过；关键方法实际阅读与字节审计分开。node tools/check.mjs：30正式页 / 783操作卡 / 22机制播放器；node --check、figwidth、git diff --check通过。ch27-source/scroll/mechanism/http/visual均对应当前本章文件；原14ID和有序42槽位保留、GET/HEAD无body、.nojekyll存在。

源码审计：python .archify/review/ch27-source-audit.py（ES_SOURCE_ROOT可覆盖真实固定checkout）。浏览器：Python Playwright与Chromium、Pillow；分别运行ch27-http-review.py、scroll-review.py、mechanism-review.py与visual-sheets.py。拼图只生成截图，须实际审阅再填写visual记录。真实API：ch27-es-review.py，使用专用匿名单节点localhost:9200且两个本课索引不存在；会创建并点名清理本章资源。图解使用官方Archify3.0.1 finalize workflow、--quality showcase、真实--repo-root，已有证据修复用新的--out-dir。

当前单节点实验未验证跨机器Exchange、真实分片并行/内存上限/性能、真实异步提交与结果生命周期、安全认证及权限失败。默认实验与原生file浏览器均在本机实际通过，不沿用上一轮云环境受限结论。最终产物与证据SHA见review/ch27-artifacts.json。
