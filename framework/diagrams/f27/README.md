# F27 · 分层排序与覆盖范围图

两幅静态概念图：[两层排序](layers.d2)、[候选范围](coverage.d2)。箭头表示检索、逐晚核对与展示的处理关系，不是订单事务或实际延迟；未表达分片、供价系统或并发更新。

官方D2 CLI v0.9.0，dagre布局，浅色主题4/深色主题201；只改D2源，用CLI重新导出4份SVG，不手改生成产物。来源：[D2导出](https://d2lang.com/tour/exports/)。

从仓库根目录：

~~~bash
python3 docs/framework-review/20261027-f27-ranking/generate-diagrams.py
~~~

设置D2_BIN可指定同版本CLI。[生成收据](generation.json)保存fmt、fmt --check、validate、实际命令、CLI版本/哈希及2源4产物SHA-256。浏览器主题同步与实际视觉审阅另记于本课审阅目录；不将生成成功当作视觉或ES实测通过。
