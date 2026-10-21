# F12 作者尝试与修正

- 初次check发生在verify.py与sources.json尚未落盘时，两个链接不存在。保留[原输出](initial-check-missing-evidence.log)；补齐真实文件后check通过。
- 初次观察窗验收用inner_text读取关闭的details内JSON，得到空串，作者脚本JSON解析失败；此前GET/搜索实际200、卡片正确。保留[原记录](shell-hidden-observer.json)，改用text_content比较隐藏JSON后完整重跑12组/86次真实API通过；未修改应用绕过断言。
- 视觉总览发现初始viewport截图未完整拍到409提示和卡片。原图/记录保留；用visual-detail.py额外13次真实浏览器API补9张区域/开头截图，全部逐张查看。
- 合成总览第一次误用没有Pillow的浏览器venv；改用本机已安装Pillow12.0.0的Python生成，未安装或改动依赖。
