#!/usr/bin/env bash
# 每个步骤自动回到工程根目录，避免 @文件 的相对路径失效。
F01_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$F01_PROJECT_ROOT"
# 固定隔离端口。教程脚本不接入读者已有的 9200 节点。
export ES_URL=http://127.0.0.1:19200
