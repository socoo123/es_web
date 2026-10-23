# F15 探索与修正

本目录保留失败与探索，最终通过状态在上级记录，不以成功记录覆盖失败原因。

1. `token-probe.json`、`brand-probe.json`、`boundary-probe.json`：9.4.0真实IK本地重启前后样本探索。最初尝试“云栖里程”边界，smart仍保留里程，不能当新增误入；最终选择实测会把“湾流”切成“星澜湾/流”的样本。最终词典仅云栖里/星澜湾两条，后续两轮按该配置重新运行，未把探索词条混入成品。首次探索也试过星澜湾区/云栖里程，完整结果保留。
2. `before-conflict-status-*`：首次附加验收错误预期重复create型_reindex返回200；实际409与version_conflicts/failures真实保留。改为预期409，说明中补目标已存在冲突。没有更改生产DSL或吞掉冲突以求通过。
3. `before-restart-readiness-*`：重启后Java诊断出现503；下一次同进程手工请求200。起初没有足够证据确定具体传输原因，未将其归因为已确认的连接池故障；验收增加只读连接就绪检查，实际503仍按503记录，不算成功。
4. `before-recovery-readiness-*`：下一轮GET /与_nodes/plugins已200，但cluster_uuid为_na_，全局_analyze实际503，错误为`state not recovered / initialized`。原wait只探活根端点太早。本课wait改为等待隔离集群恢复、yellow/green且1节点、timed_out=false；修正后从清理开始完整两轮，各158次客户端请求通过。
5. `http-before-runtime-records.json`：12组正文、24组必要回归、16组独立图及交互已执行，最终静态链接检查因真实第二轮记录尚未生成而失败。未创建假的成功实测文件；真实两轮结束后重跑链接终检并检查哈希未变，复用已通过的阅读矩阵。最终状态见http-review.json与finalize-http.py。
6. 作者两次临时命令工作目录错误（首次build重定向/末轮构建前哈希读取）导致FileNotFound，已在正确目录执行。最终clean package成功，API源码哈希与两轮一致；观察窗初始提示从继承的“故宫”改为本课词项提示后使用最终jar实测。未把未捕获的旧jar指纹补造为已记录。

这不是读者步骤。最终教程只保留可复现的本课路径；不改检查器绕过失败，不把未执行项目标为通过。

7. 最终文字自审把“在看结果前写进判断文件”精确为“正式对照前”：样本经过词边界探索后才定稿，人工意图在正式两轮前固定，不冒充从未看过探索输出的盲评。修改仅此一句；最终HTTP/复制/图与表格检查重新执行。最终表格附加脚本首次命名覆盖了http模块，在启动服务前报AttributeError；原错误保留，改名后通过。

8. 首次staged diff检查发现Docker构建日志的CR进度与行尾空格。原文及SHA256以plugin-image-raw.json逐字保存；展示日志仅转为逐行并去行尾空白，更新运行收据哈希后重新检查，未改生成SVG或真实响应。
