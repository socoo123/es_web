#!/usr/bin/env bash
# start-secure.sh — 启动第 29 课的「开安全」ES 节点(9201,elastic / elastic-password)
# 用法:bash docker/start-secure.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 启动 es-study-secure(9.4.0,security on,http://localhost:9201)…"
docker compose -f docker-compose-secure.yml up -d

echo "==> 等待节点就绪(首次启动约 30-60 秒)…"
for i in $(seq 1 60); do
  code=$(curl -s -o /dev/null -w "%{http_code}" -u elastic:elastic-password http://localhost:9201/ 2>/dev/null || true)
  if [ "$code" = "200" ]; then
    echo "✅ 安全节点已就绪:curl -u elastic:elastic-password http://localhost:9201/"
    echo "   不带凭据试试:curl -i http://localhost:9201/  → 401 + WWW-Authenticate"
    exit 0
  fi
  sleep 2
done
echo "❌ 60 次探测未就绪。看日志:docker logs es-study-secure"
exit 1
