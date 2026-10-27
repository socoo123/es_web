# F27 · 酒店与房型的分层排序

[正文](../../../../framework/f27.html) · [完整DSL与输入](../../search/f27) · [固定表](../../data/f27/stay-table.json) · [真实验收](../../review/f27/README.md)

8家酒店根文档、19条nested报价摘要。默认“西湖”命中6家/14条报价，逐晚合格10条/5家。酒店按相关性、品质或距固定点的距离排序；房型在各酒店内部按总价或“含早→可退→总价”排序。默认早餐/可退为软偏好；两个require标记独立进入同条报价的硬过滤。

从仓库根目录，只启动本课资源：

~~~bash
cd projects/travel-search
docker compose -f infra/f27/compose.yaml up -d
bash infra/f27/wait.sh
export ES_URL=http://127.0.0.1:19227
export APP_URL=http://127.0.0.1:18081
export F27_OUT=/tmp/f27-reader-round1
bash labs/f27/01-prepare.sh
bash labs/f27/02-hotels.sh
~~~

另一终端从仓库根目录，先将JAVA_HOME/PATH配置为JDK25：

~~~bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19227 APP_PORT=18081 java -jar target/travel-search-0.7.0.jar
~~~

回到第一个终端，Java已启动，浏览器访问本机 http://127.0.0.1:18081/f27.html：

~~~bash
bash labs/f27/03-rooms.sh
bash labs/f27/04-boundary.sh
curl --fail-with-body -sS -X POST "$APP_URL/api/hotel-ranking/inspect" \
  -H 'Content-Type: application/json' --data-binary @search/f27/relevance-preferred-input.json
~~~

酒店最终次序：

| 模式 | 完整核对后酒店ID |
| --- | --- |
| relevance | h01、h02、h05、h06、h04 |
| quality | h04、h02、h01、h05、h06 |
| distance | h04、h01、h02、h05、h06 |
| quality + top2 | 仅h04；h03被拒绝，不补位，局部结果 |

仅改变房型模式，酒店次序保持；h01的total为a01/a02/a03/a04，preferred为a03/a04/a02/a01。默认最低60000分、偏好所选80000分，分别标注。必须含早可退后，h01只有a03/a04；默认关键词合格酒店变为h01/h02/h05/h04，合格报价5条。

固定日期[2026-11-01,03)、Asia/Shanghai、一间两成人、CNY整数分。逐晚时效对比固定参考时刻2026-10-27 08:00上海时间，允许0–300秒，未来拒绝；不跟随电脑时间。a05缺价、c01库存旧、c02缺晚、c03售罄。固定快照合格不等于实时可订，不含税费、换汇或订单锁库存。

独立需求先在正文中自行判断，再执行：运河、必须含早且可退、品质酒店排序、偏好房型排序、完整范围。答案见正文折叠区；脚本也核对这一组新样本。

主流程3案例/27HTTP（13+6+8），Java内部另7次ES搜索。脚本完整比较Java DSL与REST固定JSON、实际REST重放的ID/source/score/sort/total/inner_hits；只归一化typed响应省略的null评分字段。附加错误51HTTP与清理2HTTP另列；额外手工curl不计入27条。

~~~bash
python3 labs/f27/lab.py errors --out /tmp/f27-reader-errors
bash labs/f27/cleanup.sh --out /tmp/f27-reader-between
export F27_OUT=/tmp/f27-reader-round2
bash labs/f27/01-prepare.sh
bash labs/f27/02-hotels.sh
bash labs/f27/03-rooms.sh
bash labs/f27/04-boundary.sh
~~~

附加验收会改写本课根投影、注入点名测试酒店，核对快照错配与107家命中仅返回100家的502；只操作tut-f27-hotels。为恢复固定相关性语料，错误后点名清理、重建并重新导入，不只还原_source。固定实验期间不要并发写入。完整候选上限100家/每家匹配报价20条，分别检查截断；组内超过20条的防护未单独注入，非任意规模遍历方案。

收据目录必须新建，不覆盖旧记录。结束时关闭自己启动的Java，清理点名索引，保留卷：

~~~bash
bash labs/f27/cleanup.sh --out /tmp/f27-reader-final
docker compose -f infra/f27/compose.yaml stop es
~~~

如需移除自己启动的本课容器/网络，用同一compose文件的down，不加-v。教学节点只绑定回环、无认证；安全连接在F35。浏览器经Java访问ES，Pages教程不连接本机服务。稳定键不等于跨更新视图稳定，本课未实现酒店分页。
