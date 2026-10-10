# 第一章 · Archify 试读

三幅图由 [Archify 3.0.1](https://github.com/tt-a1i/archify/tree/v3.0.1/archify) 的正式 CLI 从 JSON 生成。每个目录的 `candidate.json` 是可编辑的图源，HTML 是自包含的静态交互图。`chapters/ch01.html` 使用相对路径嵌入 HTML；仓库已有 `.nojekyll`，保持 GitHub Pages 零构建和零 CDN。

| 图 | 类型 | 图源目录 |
| --- | --- | --- |
| 倒排索引 | Architecture | `architecture-ch01-index-20261010-113428` |
| 显式分析链 | Workflow v2 | `workflow-ch01-analysis-20261010-113428` |
| 主分片与副本 | Architecture | `architecture-ch01-shards-20261010-113428` |

图源启用了 `meta.animation: "trace"`。默认一遍路径动效后回到完整静态图；图内可暂停，章节外层可重播。系统减少动态效果设置优先于播放指令。点击节点可查看关系，展开图解可使用完整查看器和说明卡。

## 再生成

从仓库根目录执行，先安装或下载官方 3.0.1 技能包；技能内部无需 `npm install`。例如倒排图：

```bash
node /path/to/archify/bin/archify.mjs finalize architecture \
  .archify/architecture-ch01-index-20261010-113428/candidate.json \
  .archify/architecture-ch01-index-20261010-113428/inverted-index.html \
  --quality showcase --json
```

分析链使用 `workflow`，分片图使用 `architecture`。修改已有图源后，为新检查指定新的 `--out-dir`，保留旧证据；不要手改生成的 HTML。

## 检查与限制

- 三幅图的 `validate`、`deliver` 和严格 `check` 均通过 9/9 showcase，零错误、零警告。
- Archify 原生 `browser-check` 使用私有 `file://` 快照，本云浏览器管理策略禁止文件 URL，因此该检查报告失败；未修改策略，也未伪造通过。
- 已另外通过允许的 HTTP 路径，用 Chromium 检查三幅图的四种桌面宽度、整页交互、主题同步、暂停后重播、节点探索、390px 页宽及减少动态效果。HTTP 检查和截图不替代上述原生失败结果。
- ES 节点仍受云运行时兼容性问题阻塞，11 个实验的真实 ES 请求没有执行；阅读与图解无需 ES。
- 沿用主站的发布方式：推送到 `main` 触发 Pages。也可从仓库根目录运行 `python3 -m http.server 8000`，打开 `http://localhost:8000/chapters/ch01.html`。

许可证见 `ARCHIFY-LICENSE.txt`；生成 HTML 内嵌的字体保留自己的字体许可。

完整图源与 HTML 哈希、收据位置及视觉审阅范围见 [REVIEW.md](REVIEW.md)。
