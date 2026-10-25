# F18 · 探索与修正

[probe.jsonl](probe.jsonl)保存固定语料的初探请求和解释树；正式两轮前已固定资料与相对次序预期，不冒充盲评。prepare/contexts/unrelated.jsonl是正式脚本编写期的实测；正式结果见工程review/f18。

[build-explain-api.log](build-explain-api.log)：最初误用了客户端ExplainResponse不存在的exists()；用9.4.8实际javap核对后，改为核对index/id及完整explanation，正常matched=false保留。缺资源由ES拒绝分支处理。未关闭客户端必填校验。

[java-explanation-precision.jsonl](java-explanation-precision.jsonl)：初次验收误将客户端double再序列化的解释值与REST float短小数逐位比较；卡片/结构/描述仍完整逐项核对，数值采用2e-6相对、1e-7绝对容忍。该误差远小于所教的次序差，不把误差解释为业务权重。

本轮编写脚本另遇到Python3.11对f-string表达式反斜杠限制和工作目录错误，修正生成脚本/路径后重跑；未修改站点检查器、伪造响应或跳过真实验收。若后续浏览器发现问题，记录原失败及修正。

HTTP首轮完成12组/24必要回归/16独立图/16复制后，收据链接检查引用了作者替换时误写的f19目录且部分最终收据尚未生成；修正路径、补齐真实收据后重新运行。原失败见[http-missing-receipt.json](http-missing-receipt.json)。

视觉复核发现matched=false仍可带正分文本子句，增加明示说明；最终jar重新构建，真实两轮与73次观察窗重新通过，额外4次面板/表格观察。补充前记录见before-explain-note-shell-review.json与before-explain-note-visual-detail.json；不是伪造或丢弃失败。

末次HTTP浏览器矩阵已完成后，链接收尾早于repository-checks.json写入；见[原收据](http-final-receipt-order.json)。保留已完成矩阵并在真实仓库收据写入后重新检查全部静态链接，不把先后顺序错误称为浏览器通过。D2与源码检查脚本的相对仓库根修正后实际重跑，图源/产物哈希不变。

提交前git空白检查识别到Maven原始日志的行尾空格；可读log仅去行尾水平空白，原始错误日志字节保留于[build-explain-api.log.gz](build-explain-api.log.gz)，成功日志和依赖树原始gzip及解压哈希见工程runtime.json。
