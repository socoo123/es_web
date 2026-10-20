# F09 · 两轮真实ES/Java验收

本轮在macOS arm64运行原Compose ES9.4.0 / Lucene10.4.0；Boot4.0.8 / Temurin25.0.4.1+1 / 官方Java与Rest5 Client9.4.8。没有修改ES二进制、Compose或安全策略。应用构建与运行分开记录。

- [原始请求、响应与两轮断言](es-java-review.json)，[作者验收脚本](verify.py)
- [实际clean package](build.json)、[实际依赖树](dependency-tree.json)、[Java运行日志](java.log)
- [读者手工入口](../../labs/f09/README.md)、[教程](../../../../framework/f09.html)
- [HTTP阅读/真实展示壳](../../../../docs/framework-review/20261020-f09-facets/README.md)分别记录，不替代ES断言

每轮独立创建tut-f09-attractions，green、完整mapping、Bulk16项created、refresh/count；F08原十五份全部已有字段和值保持不变。全国共同候选9份；选HZ+lake或culture命中boundary/far/guide/xihu，城市范围6、主题范围7、价格3/0/1。五组REST↔Java精确DSL、提交条件、ID/次序/total/relation、源字段、价格/主题、scopeTotal/全部桶/逐桶与整体误差/sum_other/缺主题/range边界全部核对。另有all-query/post-only、size2/0和九种非法输入400。

每轮独立创建tut-f09-candidates，2主0副本、同节点；Bulk20项created、routing=a/b确认shard0/1。窄候选返回A5（整体上界10、A桶上界5、sum_other15），宽候选返回C8（上界0、sum_other12），全桶C8/A6/B6（上界0、sum_other0）。最后两个索引点名删除并确认404，Java缺索引502，再开始下一轮。

三案例28条是教学HTTP统计；作者额外读取mapping/预检/分页/非法输入/清理探测与浏览器重复请求不混入教学数。脚本只允许两个固定F09名字，不接收任意删除目标，已有资源时拒绝。可选作者运行：准备ES与Java后`python3 projects/travel-search/review/f09/verify.py`，不要在保留本课索引时直接执行。

未测试真实搜索执行超时、部分分片失败、高基数性能、多节点、TLS/权限、插件或DB/CDC。无单元测试；实际构建成功与API通过分别保存。不回填F04–F06历史受阻状态。应用日志完整保留，含Maven依赖的Unsafe提示；未将提示当失败或删改日志。
