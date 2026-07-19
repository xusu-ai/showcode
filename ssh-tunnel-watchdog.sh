#!/usr/bin/env bash
# ssh-tunnel-watchdog.sh — 监控 8104 SSH 反向隧道健康状态
# 当检测到隧道断开时，通过 QQ 发送告警
# 在 Hermes cron 中配置为每分钟运行

PORT=8104
API_URL="http://127.0.0.1:$PORT/v1/models"
LOG_FILE="/tmp/ssh-tunnel-watchdog.log"

# 尝试获取模型列表（轻量级健康检查）
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$API_URL" 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
  # 隧道正常，无输出（静默模式）
  exit 0
else
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$TIMESTAMP] ⚠️  8104 SSH 隧道异常，HTTP 状态码: $HTTP_CODE" >> "$LOG_FILE"
  
  # 尝试诊断
  LISTEN=$(ss -tlnp | grep ":$PORT " | head -1)
  if [ -z "$LISTEN" ]; then
    echo "  端口 $PORT 未在监听" >> "$LOG_FILE"
    echo "⚠️  8104 SSH 隧道断开告警：端口 $PORT 未监听，上海 R730 反向隧道已断开"
  else
    echo "  端口在监听但 API 无响应: $LISTEN" >> "$LOG_FILE"
    echo "⚠️  8104 SSH 隧道异常告警：端口在监听但 API 无响应"
  fi
fi
