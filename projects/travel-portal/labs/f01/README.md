# F01 实验：路由、请求契约与健康 API

这是旧门户草稿的实验步骤，与现行 F01 导学不同。`verify.py` 含旧教程的 DOM 断言，不能直接验证当前 `framework/f01.html`；原始结果和截图保留在 [历史验收记录](../../review/f01/README.md)，本次保存未重新执行浏览器或 Java 健康实验。

先按 [项目说明](../../README.md) 启动；不要先启动 ES。本课的三类结果分别为前端条件对象、页面地址/校验反馈、真实 Java 响应。

| 案例 | 固定输入与步骤 | 断言 / 失败对照 | 恢复 |
| --- | --- | --- | --- |
| f01-c01 | 首页 → 寻找景点 → 西湖 / 杭州 / 200 元 → 生成请求 | cityCode=330100、maxPriceCent=20000、page=1；200.05 元→20005 分；北京→110100；0 合法，负数表单拒绝 | 返回首页，重新输入固定样本 |
| f01-c02 | 首页 → 安排住宿 → 2027-05-01 / 2027-05-03 / 2 人 / 1 间 → 房型页 | 2 晚；URL 保存全部参数；刷新不丢条件；修改条件保留选择；同日离店不跳转；直接 URL 的非法日期/小数人数/缺参显示错误 | 返回酒店页重新选择 |
| f01-c03 | Java 启动 → 检查连接；停止 Java → 再检查；重启 Java → 重试 | 实际 JSON 为 UP/travel-portal/F01；失败显示重试按钮；恢复后显示 Java 已连接 | 停止/启动自己开的 Java 进程 |

房型页没有真实酒店、价格或库存，景点页没有 ES 命中；案例只验收 F01 所交付的旅程阶段。完整业务流程随后续课继续验收。

## 可执行验收

`verify.py` 检查 8080/5173 空闲后启动自己管理的 Java 与 Vite，重复执行两轮案例、停止重启 Java、检查直连和代理响应；最后仅关闭它自己启动的进程。应先停止手动启动的本课服务，不会自动占用或终止未知进程。

```bash
# 仓库根；先完成 npm ci / npm run build、./mvnw -B package
python3 -m venv /tmp/es-f01-review-env
/tmp/es-f01-review-env/bin/pip install playwright==1.63.0
/tmp/es-f01-review-env/bin/python -m playwright install chromium
/tmp/es-f01-review-env/bin/python projects/travel-portal/labs/f01/verify.py
```

浏览器同时以 HTTP 的 `/es_web/` 前缀检查教程、预览、浅深主题与 1920/1440/1024/768/390/320px 阅读布局、代码复制、展开图解、已读进度和减少动态效果。当前脚本使用 Unix 进程组来控制其子进程，作者环境为 macOS；Windows 可按表手工完成案例或在 WSL 使用脚本。

结果写入 [review/f01](../../review/f01/)。截图生成后仍须实际查看；脚本把视觉状态写成 pending。重跑会更新 JSON 与截图，实际视觉审阅必须重新记录。ES、数据库、CDC、真实搜索、报价与预订不在本课范围。
