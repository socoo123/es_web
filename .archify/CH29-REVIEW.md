# ch29 安全机制重构验收

本轮范围：ch29、首页对应卡片、STATUS与本章图源/产物/验收证据。按序读取AGENTS/STATUS/PLAN/CHAPTER_STANDARD/CLAUDE；未重读tutorial，未使用子代理。原有.gitignore修改，以及工作期间另行出现的课程规划/规范修改均保留，不纳入本轮提交。复用共享chapter-diagrams.css/js，未修改共用样式或生成HTML。

## 内容与依据

Elasticsearch 9.4.0固定提交 `2e8528e92361c3399724226deaf2b46f933e925b` / Lucene 10.4.0。真实干净Git源码checkout验证原始committed bytes；只阅读本章目标方法，19个文件/37段固定行号的字节与引用检查见 `review/ch29-source-review.json`。图中各语义节点都有具体证据，正式finalize传真实 `--repo-root`。字节检查不代替语义走读。

修正：普通HTTP在头层认证，Action过滤器随后按动作授权；保留OPTIONS/CORS、内部系统请求、run-as、附加认证的抽象边界。CONTINUE也可携带失败信息，SUCCESS停止后续认证器，TERMINATE或异常结束。认证器顺序与Realm默认列表/缓存重排分开；LDAP/AD也可认Basic。不把一次Authentication概括为所有请求只能有一个主体。

错Basic密码由Realms.consumeNullUser→authenticationFailed返回用户文案，不写成“Realms最后CONTINUE、链统一生成”。伪造ApiKey已抽出却未通过，仍可能到handleNullToken；该方法不等于从未抽过任何凭据。本课关闭匿名、token service关闭、API Key开启，401有Basic+ApiKey双挑战；挑战集合受配置影响。双Authorization请求头真实返回400，不存在“ApiKey赢、Basic后备”示例。

RBAC不只检查动作名，还解析索引资源并建立访问控制；本课普通索引用资源名称与动作权限对照。_authenticate经过同用户授权分支获准，不叫“免授权”。多角色普通权限合并、FLS/DLS组合边界明确；本章不实测更高许可功能。9200关闭安全不会构造匿名superuser，available含许可可用性，安全Handler不注册的两个具体请求400不概括所有URL/方法。

## 实验、清理与真实ES

原19实验ID与 `ch29-auth-chain` 七步ID保留。5组32卡：认证6 / 准备5 / 授权9 / 端点4 / 清理8。所有卡显式endpoint/auth；9200安全关闭、9201安全开启，均真实确认9.4.0/10.4.0与固定build_hash。9201通过仓库start-secure.sh启动，HTTP TLS显式关闭、默认token service关闭、无匿名访问。两个独立集群不共享身份与数据。

本章日志1P0R、strict keyword mapping、refresh_interval=-1，固定ID与refresh=true。reader仅授予tut-l29-*的read；alice文档GET/搜索200、根cluster动作/CAT监控/创建/写入/名称外明确搜索403、自查身份/权限200。_has_privileges里的false不是该请求失败。CAT限定本章资源并说明复合动作拒绝点；未创建真实API Key。

**清理后两轮各32张卡全部真实通过**，每轮另10项观察：角色/用户重复更新created=false、固定IDupdated200、重复建索引400、拒绝写入后count仍1/ID2不存在、重复删除用户/角色404 found=false、重复删索引404、双Authorization400。原始请求/响应/响应头分别保存，含三种401双挑战与403不挑战；`review/ch29-es-review.json`。finally逐项点名清理并确认日志/拒绝创建索引/用户/角色均不存在。两个教学节点留跑；Docker down保留数据卷，不当成清理。

初始验收两次失败如实保留：旧alice自查卡filter_path隐藏Realm字段，随后补全；重复删除用户/角色的HTTP实际是404，校正预期后完成最终两轮。历史失败收据不充当当前API成功证据。

本轮未验证多节点、HTTP/Transport TLS、匿名角色、外部Realm、真实access token/service account/API Key、run-as、secondary authentication、自定义授权、FLS/DLS或性能；普通路径以外的机制按固定源码与适用条件说明。

## 官方Archify门禁与图义

官方3.0.1、workflow v2、zh-CN/showcase/trace。只修改JSON、正式finalize，不手改生成HTML。当前两幅validate、deliver、strict check和原生file:// browser-check均通过，showcase **9/9、0错误0警告**；本机原生浏览器可用，不沿用旧云限制。update.noticeRequired=false。

当前收据：basic-path `review-2`，rbac-actions `review-4`。保留初稿/旧revision诊断：共享泳道高度造成composition/viewport-height，按v2同列纵向步骤修复；RBAC一次交叉通过指定role→cluster的直连端口修复。HTTP另发现原RBAC宽高比触发手机720px最小SVG，390px左侧裁切；从JSON调整纵向身份堆叠、重新finalize后各节点在390/320的初始面板内完整包含，未靠注入样式改生成文件。

Basic图解释本课Basic路径；有效Bearer/ApiKey或可选插件可更早成功，必要条件同时在正文/图注/说明卡。RBAC图是两次不同请求结果的对照，不画成同一请求先读根再搜索。Basic的Realms→身份有左侧绕行，实际查看后可追踪且不遮挡，原生建议与通过状态分别记录。当前独立1440px最小SVG字7.258/7.466px、普通节点字8.295/8.533px。

复用 `.archify/ARCHIFY-LICENSE.txt`；保留生成HTML字体许可与delivery哈希。当前图源/HTML、当前门禁收据和各项证据的SHA-256绑定见 `review/ch29-artifacts.json`；旧revision不代表当前产物。

## HTTP、无障碍与视觉

两独立图：1440/1600/1920/2048 × 浅深；章节：1920/1440/1024/768/390/320 × 浅深。阅读列桌面880px，390为362px、320为292px，各区边界差≤1px；整页与iframe无横向溢出，图节点完整包含，独立说明卡无截断。两幅嵌入高度桌面900px、≤800px620px，按实际面板测量。窄屏提供总览/探索/展开，未宣称小屏能直接读全部图内细字。

节点源码探索/关闭、Enter/Escape、主题同步、展开不带present、暂停后外层重播与键盘重播、reduced-motion静止且禁动态切换、七步/回退/播放/重置、目录、已读与前后章导航通过。源码表和760px机制SVG在390/320自身容器内可横滑，不产生整页滚动。原机制快照重排为三段大框，修正旧文字溢出与解说；文本实际BBox/唯一marker/步进检查通过。

31条请求深链与1条含密码body的手动控制台入口，端点/认证别名/raw、/es_web/资源前缀均验证。用户创建卡直接运行完整发送；控制台入口只带端点与elastic别名，手动填写method/path/body，避免固定教学密码进入URL。伪造ApiKey卡深链不携带自定义头，按钮/正文明确说明等价请求用直接运行或curl；不声称深链可自动带该头。所有控制台链接检查无密码。HTTP浏览器中的ES自动请求明确abort，导航/UI检查与真实API记录分开；无未处理JS或失败HTTP资产。

已实际通过view_image审阅7张联系表：24张章节/独立图/嵌入图双主题及窄屏截图、全部7个完整机制快照；另查看完整浅色Basic与深色RBAC独立图。文本、箭头、层次、主题与控件可读；手机号图内细字通过探索/展开/正文读取，局部横滑的机制解说与控制完整。实际审阅记录与捕获哈希在 `review/ch29-visual-review.json`，截图生成不当作实际审阅。

## 检查与复现

`node tools/check.mjs` 全绿：30正式页、816卡、22机制播放器；注册JS语法、figwidth、diff检查、19原ID/32有序唯一槽位、GET/HEAD无body、相对资产/章节导航和.nojekyll通过。只修改本章及对应首页卡片；自动提交推送origin/main，远端提交与Pages状态交付时另核对。

本目录Python脚本可用Python+Playwright/Pillow复现。`ch29-es-review.py`需本章资源不存在的专用教学节点，只变更本章身份与日志；`source-audit.py`验证固定Git源（ES_SOURCE_ROOT可覆盖）；HTTP/scroll/mechanism脚本独立验证；visual-sheets只生成联系表，不替代查看；bind绑定当前收据与实际证据。接口、原生门禁、HTTP测量与视觉审阅分别记录。
