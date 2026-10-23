# F14 作者尝试与修正

- 首次用GitHub v9.4.0 Release查询IK得到404；随后读取维护方Latest公告，按其迁移指向访问get.infini.cloud，真实9.4.0制品200。没有把GitHub标签不存在写成插件不可用。
- 节点首次启动尚未就绪时curl得到empty reply；后续使用wait.sh等待可响应，再验版本/目标索引green，不把启动窗口当作成功。
- 首次错包实验用Docker bind mount，安装器报missing descriptor，不能证明版本校验。改用隔离Docker构建COPY真实SmartCN9.3.0 ZIP，得到明确built for9.3.0/running9.4.0和退出70；只以后者作为版本证据，失败构建容器已删除。
- 初稿生成脚本有多行字符串语法错误；修复后运行。Java片段初选范围至105行，但文件仅90行；改为27–89。HTML生成时默认转义引号与同步器规则不同；改为只转义&/</>，之后片段检查通过。未修改检查器绕过差异。
- [初次HTTP](http-before-mobile-layout.json)在390px发现图继承700px最小宽度；新增仅作用于#f14的纵向图样式，最终12组重新执行。既有章节样式不改。
- [后续HTTP](http-before-runtime-link.json)完成12组/交互/离线检查后，仅末尾静态链接检查发现runtime.json尚未归档。最终补齐实际构建、资源恢复与本文件后，重新检查全部相对链接；没有重跑已通过的整套浏览器检查。过程中的资源恢复/attempts链接也在最终收尾前尚不存在，未称当时通过。
- 最终自审把插件下载/构建放到cleanup之前，避免下载失败时丢失基线；阅读复验包含最终命令顺序。另补窄屏表格/Java横向滚动提示，2组最终文本/布局核对单独记收据。

作者初次探索结果保留于工程baseline-initial/plugins-initial；最终固定expected与两轮断言均成功。未用改ES行为、手改D2产物、伪响应或修改管理策略修复失败。
