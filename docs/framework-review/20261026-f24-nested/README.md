# F24 · 同房型条件、inner_hits与nested排序验收

本课只实施F24和必要F23下一课/读者链接、目录/当前摘要与共享Java工程；F25未开始。[正文](../../../framework/f24.html) · [读者本机入口](../../../projects/travel-search/labs/f24/README.md) · [真实两轮](../../../projects/travel-search/review/f24/README.md)。

[实际运行配置](reasoning.json)：用户最新gpt-6.1-sol/max，父调度报告实际spawn该参数/fork_turns=none；子agent无独立读回API。全部写作、自审、实验、图解、浏览器、实际截图审阅、提交推送和Pages核对由本课作者执行，主agent只调度。未声称主会话compact。

| 类别 | 实际结果与收据 |
| --- | --- |
| 内容与范围 | [作者完整自审](content-review.json)，约4264汉字/七段式/3案例/46教学HTTP/7练习/3陷阱/0播放器。9酒店16报价条目，rooms每元素是房型×单计划×币种×单晚报价，不沿用F23的rates object进行组合筛选。 |
| 官方版本依据 | [四文件](sources.json)与ES官方v9.4.0逐字节一致；NestedQueryBuilder父根返回、SortBuilder独立filter、FieldSortBuilder嵌套上下文、InnerHitsPhase取回路径。在线文档仅为说明，具体行为以固定源与真实9.4.0为准。 |
| 图解生成 | [官方D2生成](../../../framework/diagrams/f24/generation.json)：v0.9.0/dagre/浅4深201，2源4SVG，fmt/validate/全部CLI退出0和当前哈希一致；未手改SVG。与下面阅读/ES验收分开。 |
| 真实ES/Java | [两轮](../../../projects/travel-search/review/f24/README.md)各46教学＋13附加，Java内部5搜索另计；[运行版本/构建/制品](../../../projects/travel-search/review/f24/runtime.json)。object/split各8酒店，单nested3家；无sort.filter错用h02的100元，修复顺序h03/h08/h02=500/500/650元。源码、DSL、源、inner_hits/offset、计数/单位、错误与恢复一致。 |
| HTTP/静态阅读 | [12正文组](http-review.json)、24组F23/目录回归、16组独立图；1920/1440/1024/768/390/320×浅深。最大880px，各块边界差≤1px，无整页横溢；窄代码/表格局部横滚。16锚点/13折叠、16段真实剪贴板、主题/图同步/展开/重载/已读隔离/键盘/file双主题/reduced-motion通过。无JS/HTTP/未解释requestfailed，无业务请求。 |
| 本机真实观察窗 | [40矩阵＋10错误恢复](shell-review.json)，1440/768/390/320×浅深×5输入；同Java PID，浏览器直连ES=0。非法400、源缺失502两类、缺索引502、真实停机503及各恢复；卡片、政策/币种/计划、实际sort与完整DSL/响应一致。完整结果另见[shell raw gzip](shell-review-full.json.gz)。 |
| 实际视觉审阅 | [84PNG](visual-review.json)：80张经14组总览实际查看，4张补拍单开；总计9原图另开。只按记录范围声明，不称所有像素/代码全文逐字审阅。[细节几何](visual-detail.json)确认完整图注和局部横滚；390组合截图曾裁到末行图注，[同宽更高视口补证](visual-followup.json)完整，四张均实际打开。 |
| 探索与修正 | [原始尝试](attempts/README.md)：integer缺值哨兵、term简式与客户端完整value语法、验收init_script覆盖主题。保留失败和真实响应，正式两轮/最终矩阵重新执行；不把探索计最终通过。新课无已发布F24历史勘误。 |
| 清理与保留 | [最终状态](workspace-state.json)：浏览器后两索引全源再次精确核对/open_contexts0，各DELETE/GET404；Java SIGTERM/18081关闭，F24容器/网络移除、19224关闭；所有旧卷/镜像和F24卷保留。旧安全节点ID/StartedAt/PID不变且healthy，记录不含凭据。 |
| 静态/构建门禁 | [checks](checks.json)：站点、图宽、全部片段、JS/Bash/Python语法、固定Bulk、图源与84PNG哈希、两轮计数、完整查询条件一致性、相对链接。工程无测试源，不把No tests to run称测试通过。 |

复现本课阅读验收，使用安装了Playwright/Pillow的Python与本地Chromium：

```bash
python3 docs/framework-review/20261026-f24-nested/generate-diagrams.py
python3 docs/framework-review/20261026-f24-nested/review.py
# shell-review.py需先按读者入口准备ES/Java与本课数据；会进行本课点名故障/恢复
python3 docs/framework-review/20261026-f24-nested/shell-review.py
python3 docs/framework-review/20261026-f24-nested/checks.py
```

实验JSONL不自动覆盖，重新实验使用新的输出目录。作者验收脚本写入本课证据目录，重跑前保存旧收据或在独立工作副本执行，保留原始证据。截图生成不代表已查看，作者按visual-review记录实际打开范围。cleanup-review.py仅在本课结束时点名清理，不删除卷或旧节点。

按用户持续授权提交推送origin/main。提交后运行[publication-check.py](publication-check.py)核对本地/远端精确SHA、该SHA对应Pages built、14份线上产物逐字节、6组双主题窄屏交互、3段实际复制与两SVG弹窗。发布结果写到工作区外，避免证据自身改变所验提交；最终实际结果在交付消息与本机收据，不提前把计划标通过：

```bash
python3 docs/framework-review/20261026-f24-nested/publication-check.py \
  --sha <实际提交SHA> --out /tmp/es-f24-publication.json
```

未测代表性负载/性能/容量、多节点、生产安全、实时供价/CDC、逐晚库存/税费/取消罚金、预订或订单事务；超时与部分分片失败仅有代码防护，未故障注入。本课是固定单晚搜索快照；F04–F06旧未验收项未回填，F25正文与实验未开始。
