# F10 · 显式排序（本机手工入口）

先读[正文](../../../../framework/f10.html)。沿用Boot4.0.8 / JDK25（作者Temurin25.0.4.1+1）/ 官方Java与Rest5 Client9.4.8；ES9.4.0 / Lucene10.4.0。应用JDK与ES bundled JVM分开。先让JAVA_HOME/PATH指向JDK25。Pages只承载教程。

从仓库根目录：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d es
bash infra/single-node/wait.sh
bash labs/f10/01-prepare.sh
bash labs/f10/02-modes.sh
bash labs/f10/03-boundaries.sh
```

只用tut-f10-attractions，1主0副本/strict；完整继承F09十六份字段和值。准备依次核对版本9.4.0、创建acknowledged、green且未超时、Bulk16项created且errors=false、refresh零分片失败、count16。curl只判断HTTP错误，200不能代替条级和等待检查；初次索引须不存在，重复创建失败先停止再清理。

全国、不选主题、无半径；name^3/aliases^2/description、best_fields/AND、CNY/open、非负价/20000分预算。九份共同候选，以下均写完整ID：

- relevance：a-sh-exhibit、a-hz-tea、a-hz-guide、a-fz-xihu、a-hz-plain、a-hz-xihu、a-hz-boundary、a-hz-missing-location、a-hz-far。
- price：a-fz-xihu、a-hz-xihu、a-hz-far、a-hz-guide、a-hz-missing-location、a-hz-plain、a-hz-tea、a-sh-exhibit、a-hz-boundary。
- distance：a-hz-guide、a-hz-plain、a-hz-xihu、a-hz-boundary、a-hz-tea、a-hz-far、a-sh-exhibit、a-fz-xihu、a-hz-missing-location。

02先default（无sort、评分降序，同分不承诺ID顺序），再三种模式。显式首键后都按唯一attraction_id keyword升序；sort数组按请求位置解释，不能把默认结果的偶然同分次序当保证。

03依次：price-scores与price同ID/同sort但返回评分；hz-distance加HZ只剩7；budget-price降8000分只剩7（去掉boundary/exhibit）；empty火星200空集；missing-last只圈四ID并显式移除预算，xihu0→guide1000→missing-price→null-price（前缀a-hz-），缺价排序哨兵本次2147483647；missing-zero两份缺价先于免费xihu、再guide，不改_source也不证明免费。主查询range不允许缺价，不能说missing把文档救回。

距离圆心lat30.25/lon120.15，arc/km/asc，不是交通距离或半径过滤；缺坐标仍命中，原始sort为["Infinity","a-hz-missing-location"]，显示待定位而不是0km。价格单位整数分，卡片才除100显示元。相关性模式_score首键会需要评分，即使track_scores=false；价格/距离无评分键时false返回_score:null。

另开终端从仓库根目录：

```bash
cd projects/travel-search/backend
./mvnw -version
./mvnw -B -ntp clean package
java -jar target/travel-search-0.7.0.jar
```

回到第一终端：

```bash
bash labs/f10/04-java.sh
```

POST /api/attractions/sort-search：q/cityCode/maxPriceFen/sortMode/latitude/longitude/trackScores全部必填。cityCode只允许ALL/HZ/FZ/SH，预算整数分0–100000000，模式relevance/price/distance，经纬度有限且范围±90/±180，q非空最长60。固定本课索引（启动前TRAVEL_F10_INDEX可覆盖），默认端点ES_URL=http://127.0.0.1:19200。七组输入与REST逐项对照conditions/esRequest/total/relation/items，保留完整sortValues、分数、hasLocation与distanceKm。正常空集200、非法输入400、缺索引502、连接不可用503。

打开 http://127.0.0.1:18080/f10.html ，切三模式/评分开关/城市/预算后分别点击查询，核对上述次序、分/元/km、原始sort与待定位。失败清空旧卡片。F09计数页保留，本页专门观察排序；课程提供界面，不需前端开发，浏览器→Java→ES。

3案例、23条教学HTTP请求=准备6+模式4+边界6+Java7。点名清理1、启动探活/作者附加断言/浏览器重复另计。脚本连续输出JSON，每份须看完整响应，构建不等于实连通过。

## 点名清理与重做

```bash
bash labs/f10/cleanup.sh
```

只删除tut-f10-attractions，200/404表示清理，不删卷/旧课/业务资源。清理后Java搜索502；再次01–04应16项重新created且上述完整次序一致。结束后关闭自己启动的Java；ES原来停止时用同compose stop es恢复，不执行down -v。

[作者两轮真实记录](../../review/f10/README.md)与[阅读/观察页验收](../../../../docs/framework-review/20261021-f10-sort/README.md)分开保存，作者验收工具不是学习前提。
