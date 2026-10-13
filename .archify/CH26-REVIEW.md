# ch26 脚本引擎重构验收

本轮仅重构 ch26、首页对应卡片与 STATUS；保留原20实验ID与机制ID `ch26-script-compile`，七步解说同步重写。七段式正文含3目标、5折叠问题、6陷阱与速记；5组实验/45操作卡（含前置与清理），2交互图/2trace/1七步机制。

## 版本依据与关键校正

官方 ES v9.4.0 对应提交 `2e8528e92361c3399724226deaf2b46f933e925b`，Lucene10.4.0。干净局部checkout `/workspace/scratch/es-v9.4.0`；本轮只沿脚本编译、执行、摄取与设置来源的相关文件检查。`review/ch26-source-review.json` 绑定29文件/55精确行段，核对本地字节等于固定提交；字节审计不替代实际方法语义审阅。

- Compiler.Loader 继承 ClassLoader，存在父加载器委派，不能声称 JVM 只能加载 txt 的类型。默认 File 拒绝位于 visitNewObj 的 Lookup 检查，未继续 IR/ASM；数组类型分支会在元素类型已识别后使用 Class.forName，不能说实现完全无该调用。
- 编译键是 project/lang/解析后的source/context/options；执行 params 不在键中。缓存是节点内 factory，general/context 配置、淘汰、过期、重启与配置替换影响复用，不能保证整个集群生命周期只编一次。
- 静态 String.getClass 在语义分析查成员失败；def Integer.getClass 延迟到执行期查 runtime Lookup。修正“执行期没有查表”和泛化 eval 的表述，不保证生成常量池只含 txt 类型。
- script_score 返回 float 分数并应用外层 boost；本课 boost=1 才有1.0/0.1与90/72。function_score 组合由配置决定。COMPLETE_NO_SCORES 且无 minScore 存在跳过脚本评分的分支，不强求执行次数等于总命中数。
- inline ScriptProcessor 创建时调用 compile；stored processor 不长期保留 factory，执行重新解析最新 stored source，ScriptCache 仍可命中。test execute 的 result 在本版本为字符串；simulate 是 docs[0].doc._source；context API 是内部调试入口，类数不固定404。
- 实验明确 doc values/fielddata 条件，显式数值 mapping，views 预先声明；不写死更新版本与错误 offset，不虚构磁盘实测。null 仅移除指定层，不等于强制true。

16条旧说法与固定证据已登记于 STATUS 的「第二十六章重构校对」，保留旧会话历史。

## 实验、前置与重做

专用匿名单节点localhost:9200；启用安全须选择认证别名并具备相应权限。前置6卡读取版本、两层集群设置、节点配置/角色/脚本限制，并确认 tut-l26-score、tut-l26-script、tut-l26-file 原先不存在。

A11：显式1P0R/auto_expand=false/strict mapping → 本索引Green等待 → 回看创建配置 → 固定cheap/popular ID Bulk+refresh → count2 → 分数/field参数/update/GET对照。重复bulk是updated且替换文档源，版本随历史变化；查询显式request_cache=false仅影响本次搜索结果缓存，不改索引或编译缓存。

B2：正常inline管道与模拟（不写索引）。C8：File三个入口、坏管道仍404、声明类型、静态与def方法、当前context允许项。失败PUT不证明同名旧资源消失，因此起步必须确认404。D5：同节点累计脚本统计 → 同一source参数2 → 统计 → 参数3 → 统计；test result预期字符串52/78，无并发且缓存未失效时第二次不新增编译，第一次可能已命中历史缓存。

E6只在该键transient/persistent均无覆盖且节点有效基线true时执行：false → 来源确认 → 无害script_score拒绝 → 立即null → 来源核对 → 同脚本成功对照。有原覆盖则整组及相应设置清理跳过，不丢失未知原值。清理7卡条件性移除本次临时键、读回基线、点名删索引/正常管道、逐项确认404；失败演示名字再确认不存在。重做从前置开始，累计统计不因删索引归零。

## 真实 ES：本轮未运行 API

已真实尝试官方Compose启动9.4.0镜像。容器本轮 `2026-10-13T09:05:23.13002633Z` 启动、`09:05:26.510366235Z` 退出1，报 Could not set coredump filter，原因为 NoSuchFileException `/proc/self/coredump_filter`。9200 curl探测退出7；只记录当前启动后的错误，见 `review/ch26-es-runtime.json`。

45卡首次运行、清理重做、真实错误链、编译统计、临时设置恢复及磁盘观察均未实测。没有合成响应、没有用旧实测替代本轮记录，也没有修改策略/运行时绕过失败。网页明确标注源码预期。HTTP控制台验证显式abort localhost:9200流量，只证明请求内容和深链。

## 图源、产物与原生门禁

两图使用官方Archify3.0.1，workflow v2、zh-CN/showcase/trace，固定仓库身份、节点源码与真实 --repo-root。只编写JSON并正式finalize生成，无手改HTML；两幅首次静态布局均通过，0次JSON布局修复。复用 `.archify/ARCHIFY-LICENSE.txt`，生成HTML保留字体许可。

| 图 / 模式 | 产物路径 | candidate SHA-256 | HTML SHA-256 |
| --- | --- | --- | --- |
| compile-gates / workflow v2 | `.archify/workflow-ch26-compile-gates-20261013-170836/compile-gates.html` | `a7ef3e60b56baef51c01a706f86b0121fa62dae4337a9211b5edd74d666146e8` | `fe11ae9b8b6b8a81f4bc5d3ac36325f5dc82f104e40bf745aea4deba0644ed86` |
| cache-params / workflow v2 | `.archify/workflow-ch26-cache-params-20261013-170836/cache-params.html` | `11c2468d327c1bcc9726e3a8139beb0e4f2240eac45bd34105d2443bbc0e9ba3` | `255f127c55f7a4f8da950bcf69a027d55adf12b0ac43a6c9491aea1951258938` |

两图validate/deliver/strict check都是showcase9/9、零错误/警告；原生browser-check均返回 net::ERR_BLOCKED_BY_ADMINISTRATOR（file导航），因此两个finalize整体为fail。独立HTTP通过不替代该失败，未修改管理策略。原始完整/简版收据保存在各图目录，update.noticeRequired=false。

## 独立 HTTP、交互与视觉

`review/ch26-http-review.json` pass：独立图1440/1600/1920/2048双主题；章节1920/1440/1024/768/390/320双主题。阅读列≤880px、各区边界差≤1px；页面/iframe无横向溢出、所有节点完整包含、说明卡无截断。两图嵌入1080px、≤800px640px。桌面最小SVG字约6.888px（含小徽标），普通节点字约7.872px。

已检查节点源码探索与关闭、Enter/Escape焦点、暂停后外层重播、键盘重播、主题同步、无present展开、reduced-motion静止与手动步进、页面无平滑滚动、七步文字BBox/唯一ID、目录/已读、45卡实际控制台method/path/body、endpoint/auth别名/raw标记、Pages前缀与相对资产；无未处理JS错误或失败HTTP资产。复制验收脚本时的建索引卡选择器从旧序号修正为稳定ID ch26-01-setup；完整重跑通过。源码补充链接与末尾空白规范化后又完整重跑，使最终收据绑定当前字节。

`ch26-scroll-review.json` pass：390/320双主题下表/旧机制只在自身容器滚动，整页保持包含。`ch26-mechanism-review.json` pass：捕获7张完整760×350快照；交互与文字边界另由HTTP检查。快照捕获与实际审阅分开。

**实际通过image reader查看全部7张联系表：24张最终章节/图解截图与7张机制快照。** 浅深主题桌面/880px嵌入、手机标题/图/实验/源表及七步均已检查，没有观察到节点遮挡、文字越框或说明卡截断。手机图提供主路径总览，完整标签需探索/展开/正文，不声称小屏完整桌面可读性；旧机制SVG与源码表允许局部横滚，机制标题省略但解说与控制完整。联系表灰色空白属于拼版。0次视觉修正，记录及38个截图/联系表哈希见 `ch26-visual-review.json`。

## 检查与复现

站点 `node tools/check.mjs`：30正式页 / 755操作卡 / 22机制动画；JS语法、figwidth、git diff检查通过。源码/45卡审计、HTTP、局部滚动、七步捕获通过；实际视觉审阅完成，API/原生浏览器限制保留。

从仓库根运行 `python .archify/review/ch26-source-audit.py`、http-review.py、scroll-review.py、mechanism-review.py；visual-sheets.py只拼截图，必须真实查看后填写visual-review。依赖现有Python Playwright/Pillow与 `/usr/bin/chromium`，ES源码路径可用ES_SOURCE_ROOT。图的candidate.json可用官方CLI finalize workflow重新生成（带 --repo-root）；当前环境原生浏览器仍会失败。

最终 `review/ch26-artifacts.json` 绑定本章正文/JS、首页、STATUS、图源/HTML/完整收据、许可与独立检查证据，拒绝把未运行API或原生失败标成通过。
