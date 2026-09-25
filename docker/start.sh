#!/usr/bin/env bash
# 一键启动本地学习用 Elasticsearch 9.4.0(数据落在 docker 卷 es-study-data,可反复重启)
# 用法:bash docker/start.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "❌ 未找到 docker,请先安装 Docker Desktop" >&2
  exit 1
fi

echo "==> 启动 Elasticsearch 9.4.0(首次会拉镜像,约 600MB,耐心等)..."
docker compose up -d

echo "==> 等待节点就绪(首次启动 30-60 秒)..."
for i in $(seq 1 60); do
  if curl -sf http://localhost:9200/ >/dev/null 2>&1; then
    echo ""
    echo "✅ ES 已就绪:"
    curl -s http://localhost:9200/ | head -20
    echo ""
    echo "现在可以打开 console.html 开跑了。"
    exit 0
  fi
  sleep 2
done

echo "❌ 60 次探测后仍未就绪,看日志排查:docker logs es-study" >&2
exit 1
