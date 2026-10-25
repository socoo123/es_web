# F17 · 探索与失败修正

- probe.jsonl/probe-summary.json：写作前真实机制探索，用于选择可解释样本；不当成盲评。包括query不能约束completion、文字去重、同音、短词与bool_prefix最后词项边界。
- bool-prefix-rewrites.json：探索阶段真实改写；正式两轮另有两份完整改写。输入天谈公园在逐字根字段会广泛扩展，最后园仍为前缀。
- mapping-defaults.jsonl：初版严格mapping比较因ES显式doc_values=false与context类型CATEGORY大小写失败；按已知等价序列化规范化后仍比较完整mapping。
- validation-property.jsonl：Bean校验isPinyinValid被当作JSON属性返回，加入@JsonIgnore后保留校验且输入契约只返回三字段。
- build-parenthesis.log：初版Java多一枚括号导致编译失败，修复后clean package通过。
- source-wrong-path.json：首次固定源码路径少extras子目录404；定位正确路径后四文件官方200且本地字节一致。未把404当校验通过。
- 初次写Java文件曾误用backend工作目录配仓库相对路径，文件未写入；切回仓库根后完成。该次成功构建只覆盖旧工程，不作为F17构建证据。

最终两轮、最终构建、HTTP与浏览器均独立记录；不改检查器或伪造响应。正式浏览器测量后如有改动，其必要回归单列。

- 浏览器初版主题脚本在每次reload都写回初始主题，导致持久化误报；改为仅首次初始化，应用源码未变。原收据shell-theme-init-reset.json保留。
- 首次HTTP阅读交互已完成，最终链接检查因runtime.json尚未生成失败；原收据http-before-runtime-artifact.json保留，全部收据写入后重跑。
- DSL一致性补充term单value对象与标量简写的等价归一；原始DSL与响应不改，22份实际请求仍逐份比较完整结构。

- 失败编译日志只去除行尾空白以通过git diff --check；原始字节的文本与SHA256保留在build-parenthesis-original.json。
