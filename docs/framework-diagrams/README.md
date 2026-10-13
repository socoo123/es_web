# 框架篇规划图

这是一幅规划总览，以两个视图分别解释业务请求和日志驱动的搜索投影。两处数据库与 Elasticsearch 表示同一套系统的角色，并非两套独立数据；PostgreSQL/MySQL 使用独立实验 profile。箭头表示请求或数据流，省略认证、精确报价实现、消息重试与索引重建。课程和真实链路尚未实现。

## 图源与再生成

- [D2 图源](travel-system.d2)
- [浅色 SVG](travel-system-light.svg) / [深色 SVG](travel-system-dark.svg)
- [HTTP 检查脚本](review.py) / [检查与当前 SHA-256](review.json)

使用官方 [D2 v0.9.0](https://github.com/d2lang/d2/releases/tag/v0.9.0)，布局为 TALA。生成工具不参与站点阅读；SVG 为本地预生成资产，图源修改后通过 CLI 重新生成，未手改 SVG。

从仓库根目录执行，`d2` 为已安装的 v0.9.0 CLI：

```bash
d2 fmt --check docs/framework-diagrams/travel-system.d2
d2 validate docs/framework-diagrams/travel-system.d2
d2 --layout=tala --theme=4 --pad=24 --timeout=30 docs/framework-diagrams/travel-system.d2 docs/framework-diagrams/travel-system-light.svg
d2 --layout=tala --theme=201 --pad=24 --timeout=30 docs/framework-diagrams/travel-system.d2 docs/framework-diagrams/travel-system-dark.svg
python docs/framework-diagrams/review.py
```

本轮使用官方 `d2-v0.9.0-macos-arm64.tar.gz`，下载包 SHA-256：`eaf6c0c143e56dd9fa97bfb6df25ea9c1ebce40245f056a0768cf1a6c15d3064`，已与 GitHub release asset 的 digest 核对。CLI 临时放在仓库外，未提交可执行文件。Python 检查需 Playwright 与 Chromium；这是作者验收工具的依赖。

SVG 包含 D2 默认 Source Sans Pro 的字体子集；保留 [SIL OFL 1.1 许可](SOURCE-SANS-LICENSE.txt)，许可文本取自 [Adobe 官方固定提交](https://github.com/adobe-fonts/source-sans/blob/87b37a2daaed80fcb8e8ccb0085c4d72ddade12e/LICENSE.md)。中文使用浏览器可用的字形回退，本轮 Chromium 下已实际查看中文标签。

## 2026-10-13 实际验证

- D2 格式与语法检查、两份 SVG 生成通过；最终图源与产物哈希见 review.json。
- 独立 SVG 以 HTTP 加载：1440px 浅/深主题均通过，文字边界在 viewBox 内。
- 验证夹具复用 `style.css` / `chapter-diagrams.css`：1440、1024、390、320px × 双主题共 8 组，桌面列宽 880px，整页无横向溢出，图片成功加载，展开链接可打开对应 SVG。
- 窄屏夹具使用 720px 图像最小宽度和局部横向滚动，保留展开入口；实际审阅了 390px 的浅/深截图。该夹具用于检验图像呈现方案，不是已发布的 F 章节。
- 实际查看了全部 6 张截图：独立浅/深图、1440px 夹具浅/深图、390px 夹具浅/深图。最终箭头与标签无重叠，中文可读，手机裁切限于可滚动图容器。
- 初稿平面网格存在交叉标签，拆为两个视图；ELK 在网格内的方向使图过高，改用支持容器方向的 TALA，再生成并复核。夹具最初只加载全站样式时列宽为 896px，接入源码篇共用布局后为 880px。

本轮只验收规划图与呈现夹具。F 章节中的站点主题开关同步、代码块、实验播放器和进度导航尚待页面接入；前后端构建、业务 API、真实 ES/CDC 案例未执行。未使用 Archify，因此无 Archify 原生门禁项目。
