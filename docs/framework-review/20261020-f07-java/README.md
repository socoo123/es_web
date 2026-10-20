# F07 · 教程阅读、图解与本机展示壳

2026-10-20，仅F07及必要的F06下一课、目录/摘要。当前入口无法设置/确认实际xhigh；作者自审，无独立代理。

- [F07正文](../../../framework/f07.html)、[完整工程](../../../projects/travel-search/backend/README.md)、[本机手工实验](../../../projects/travel-search/labs/f07/README.md)
- [ES/Java两轮真实验收](../../../projects/travel-search/review/f07/README.md)：构建、三组REST/Java、八种非法输入、502/503与同进程恢复通过。
- [官方D2图源生成](../../../framework/diagrams/f07/generation.json)：v0.9.0/dagre/主题4、201，两源四SVG，fmt/validate/生成与SHA256；无Archify/机制播放器，其门禁不适用。
- [HTTP教程阅读](http-review.json)：最终结果与截图逐张状态以该文件为准。
- [真实本机展示壳](shell-review.json)：独立记录浏览器→Java→ES，不用Pages阅读替代业务调用。
- [内容自审](content-review.json)、[仓库检查](repository-checks.json)记录实际结果及限制。

作者复现（需要Playwright/Chromium，业务验收还需JDK25与已构建jar）：

```bash
python3 docs/framework-review/20261020-f07-java/review.py
python3 projects/travel-search/review/f07/shell-review.py
node tools/check.mjs
```

真实运行与结构、图生成、HTTP阅读分别记录。截图生成不代表已审阅，逐张状态和哈希保存于JSON。未运行分片部分失败/执行超时、多节点、插件、TLS/权限、数据库/Kafka/CDC与性能测量。

## 实际通过与截图范围

HTTP课页1920/1440/1024/768/390/320×浅深12组，F06/目录24组回归，独立图16组。每组17锚点/10折叠、14段真实复制、主题/图/展开同步、已读与前课旧键隔离/导航、file双主题与reduced motion通过；列最大880px，边界差≤1px，无整页横溢。JS/HTTP/请求失败/业务请求均0。

26张教程PNG实际查看20张：四组桌面/手机浅深开头、两幅图桌面/手机浅深、320px图、REST桌面浅色/Java手机深色代码、手机展开练习与四张独立图；其余6仅生成。长代码局部滚动保留完整内容，不以截图右侧未入视口断言代码缺失。

真实展示壳12组尺寸/主题，200元、80元、空集、1km、还原逐次真实调用；另做ES真实停止、503清空旧卡片与同进程恢复。浏览器直接访问ES为0。7张完整PNG保留：4张全图查看，另外3张只查看顶部1500px的可读裁切；4张全图中另2张也裁切放大核对。长JSON下方未逐字视觉审阅，已通过DOM与实际API的解析一致性核对。逐张状态/哈希见shell-review.json，不把裁切审阅冒称整图精读。

作者主题验收首次通过add_init_script在每次重载强行写回初始主题，导致持久化断言失败；修正为首次初始化后完整重跑，原失败记录见[工具尝试](attempts/shell-theme-initializer.json)。不是产品的主题缺陷。
