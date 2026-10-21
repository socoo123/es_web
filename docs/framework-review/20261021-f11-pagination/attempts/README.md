# 作者尝试与修正

1. 最初写Java文件时工作目录已为backend却仍加仓库前缀，文件写入失败；随后用绝对路径创建。那次旧工程构建不记作F11构建。
2. 新服务首次编译缺TotalHitsRelation所属core.search显式导入，[原日志](build-missing-import.json)保留；补导入后重新构建。
3. REST视图案例已关闭PIT，finally又关闭同一id，原生ES返回404导致恢复被中断。[原请求响应](view-double-close.json)保留；改为显式closed状态且嵌套finally保证尝试恢复，重跑通过。Java本地幂等关闭与ES原生关闭返回不同，正文/入口分别说明。

4. 教学HTML生成器用READ作为未限定占位符，误替换三处README链接；站点静态检查与HTTP链接检查抓出。改为有边界的占位匹配，重新同步片段并重跑全部阅读检查。[原静态检查](check-placeholder-link.log)与[原HTTP收据](http-before-link-fix.json)保留。
5. 首轮展示壳矩阵通过后，视觉审阅补足排序首值单位和缺坐标“待定位”。旧收据[shell-before-sort-label.json](shell-before-sort-label.json)留作历史，最终收据按更新后产物重新运行。

6. 排序单位新增断言把Python的0.0格式与JavaScript显示0作字符串比较，误判距离首值；实际API/DOM数值一致。改为校验单位与数值相等，待定位仍逐字比较；[原收据](shell-unit-check-format.json)保留，重新跑最终矩阵。
