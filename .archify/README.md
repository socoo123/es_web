# 章节 Archify 图解

第一至第四章的图由 [Archify 3.0.1](https://github.com/tt-a1i/archify/tree/v3.0.1/archify) 正式 CLI 从 JSON 生成。每个目录的 `candidate.json` 是可编辑的图源，HTML 是自包含的静态交互图。章节使用相对路径嵌入，复用 `chapter-diagrams.css/js`；仓库已有 `.nojekyll`，保持 GitHub Pages 零构建和零 CDN。

| 图 | 类型 | 图源目录 |
| --- | --- | --- |
| 倒排索引 | Architecture | `architecture-ch01-index-20261010-113428` |
| 显式分析链 | Workflow v2 | `workflow-ch01-analysis-20261010-113428` |
| 主分片与副本 | Architecture | `architecture-ch01-shards-20261010-113428` |
| 第二章：五大源码区域 | Architecture（静态） | `architecture-ch02-source-map-20261010-143543` |
| 第二章：GET 源码阅读路线 | Architecture（trace） | `architecture-ch02-get-navigation-20261010-162448` |
| 第三章：进程与节点启动时序 | Sequence（trace） | `sequence-ch03-startup-20261010-165543` |
| 第三章：Node 生命周期 | Lifecycle v2（trace） | `lifecycle-ch03-node-lifecycle-20261010-165543` |
| 第四章：Classic 插件隔离与显式扩展 | Architecture（静态） | `architecture-ch04-plugin-isolation-20261010-172141` |
| 第四章：Reindex 启动注册路径 | Workflow v2（trace） | `workflow-ch04-reindex-registration-20261010-172141` |

第一章三图、第二章 GET 导航图、第三章两图与第四章 Reindex 注册图启用 `meta.animation: "trace"`。默认一遍路径动效后回到完整静态图；图内可暂停，章节外层可重播。系统减少动态效果设置优先于播放指令。第二章区域图与第四章隔离图展示静态关系，提供探索与展开入口。点击节点可查看关系与源码证据，展开图解可使用完整查看器和说明卡。

## 再生成

从仓库根目录执行，先安装或下载官方 3.0.1 技能包；技能内部无需 `npm install`。例如倒排图：

```bash
node /path/to/archify/bin/archify.mjs finalize architecture \
  .archify/architecture-ch01-index-20261010-113428/candidate.json \
  .archify/architecture-ch01-index-20261010-113428/inverted-index.html \
  --quality showcase --json
```

分析链使用 `workflow`，分片图使用 `architecture`。修改已有图源后，为新检查指定新的 `--out-dir`，保留旧证据；不要手改生成的 HTML。

第二章两图声明真实 ES 源码证据，必须传 `--repo-root` 指向 Elasticsearch 的干净 Git checkout，固定提交 `2e8528e92361c3399724226deaf2b46f933e925b`；教程仓库不能冒充该源码仓库。具体命令及当前哈希见 [CH02-REVIEW.md](CH02-REVIEW.md)。

## 第一章检查与限制

- 三幅图的 `validate`、`deliver` 和严格 `check` 均通过 9/9 showcase，零错误、零警告。
- Archify 原生 `browser-check` 使用私有 `file://` 快照，本云浏览器管理策略禁止文件 URL，因此该检查报告失败；未修改策略，也未伪造通过。
- 已另外通过允许的 HTTP 路径，用 Chromium 检查三幅图的四种桌面宽度、整页交互、主题同步、暂停后重播、节点探索、390px 页宽及减少动态效果。HTTP 检查和截图不替代上述原生失败结果。
- ES 节点仍受云运行时兼容性问题阻塞，11 个实验的真实 ES 请求没有执行；阅读与图解无需 ES。
- 沿用主站的发布方式：推送到 `main` 触发 Pages。也可从仓库根目录运行 `python3 -m http.server 8000`，打开 `http://localhost:8000/chapters/ch01.html`。

许可证见 `ARCHIFY-LICENSE.txt`；生成 HTML 内嵌的字体保留自己的字体许可。

完整图源与 HTML 哈希、收据位置及视觉审阅范围见 [REVIEW.md](REVIEW.md)。
第二章的验证范围与结果另见 [CH02-REVIEW.md](CH02-REVIEW.md)，第一章记录保持原始交付证据。

第三章的源码、原生门禁、HTTP 浏览器验收与视觉审阅见 [CH03-REVIEW.md](CH03-REVIEW.md)。第三章两图同样需要上述固定 ES 提交和真实 `--repo-root`；用 `sequence` / `lifecycle` 对应其图类型。

第四章的源码校正、生成收据与浏览器审阅见 [CH04-REVIEW.md](CH04-REVIEW.md)。两图需要上述固定 ES 提交和真实 `--repo-root`，分别使用 `architecture` / `workflow`。
