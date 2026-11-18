#!/usr/bin/env bash
# ollama-serve.sh - 按需启停本机 Ollama 服务
#
#   ollama-serve.sh            启动（已在跑则直接报告状态）
#   ollama-serve.sh stop       停止
#   ollama-serve.sh restart    重启
#   ollama-serve.sh status     看状态（版本 / 进程 / 已加载模型）
#   ollama-serve.sh log        跟踪日志
#
# 参数都可用同名环境变量覆盖，例如: OLLAMA_KEEP_ALIVE=30m ollama-serve.sh

set -u

OLLAMA_BIN="${OLLAMA_BIN:-/Applications/Ollama.app/Contents/Resources/ollama}"
HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
API="http://${HOST}/api/version"
LOG="${OLLAMA_LOG:-$HOME/Library/Logs/ollama-serve.log}"

export OLLAMA_HOST="$HOST"
# 拉模型并发流：默认 4 条在限速网络下只有 300KB/s，调到 32 能跑满带宽
export OLLAMA_MAX_TRANSFER_STREAMS="${OLLAMA_MAX_TRANSFER_STREAMS:-32}"
# Metal flash attention + KV cache 8bit，长上下文省一半显存
export OLLAMA_FLASH_ATTENTION="${OLLAMA_FLASH_ATTENTION:-1}"
export OLLAMA_KV_CACHE_TYPE="${OLLAMA_KV_CACHE_TYPE:-q8_0}"
# 32GB 机器上 27B(19GB)+9B(8GB) 会超出 25GB 显存额度，限制只驻留一个
export OLLAMA_MAX_LOADED_MODELS="${OLLAMA_MAX_LOADED_MODELS:-1}"
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-10m}"

is_up() { curl -s -m 2 "$API" >/dev/null 2>&1; }

pid_of() { pgrep -f "${OLLAMA_BIN} serve" 2>/dev/null | head -1; }

show_status() {
  if is_up; then
    local ver pid
    ver=$(curl -s -m 2 "$API" | sed -n 's/.*"version":"\([^"]*\)".*/\1/p')
    pid=$(pid_of)
    echo "状态   : 运行中 (v${ver:-?}${pid:+, pid $pid})"
    echo "地址   : http://${HOST}   (OpenAI 兼容: http://${HOST}/v1)"
    echo "日志   : $LOG"
    echo "已加载 :"
    "$OLLAMA_BIN" ps 2>/dev/null | sed 's/^/         /' | tail -n +1
  else
    echo "状态   : 未运行"
    return 1
  fi
}

case "${1:-start}" in
  start)
    if is_up; then
      echo "服务已在运行，无需重复启动。"
      show_status
      exit 0
    fi
    if [ ! -x "$OLLAMA_BIN" ]; then
      echo "找不到可执行文件: $OLLAMA_BIN" >&2
      exit 1
    fi
    mkdir -p "$(dirname "$LOG")"
    echo "正在启动 ..."
    nohup "$OLLAMA_BIN" serve >>"$LOG" 2>&1 &
    disown 2>/dev/null || true
    for _ in $(seq 1 40); do
      sleep 0.5
      is_up && break
    done
    if is_up; then
      show_status
    else
      echo "启动失败，最近日志：" >&2
      tail -15 "$LOG" >&2
      exit 1
    fi
    ;;
  stop)
    if ! is_up; then
      echo "服务未在运行。"
      exit 0
    fi
    pid=$(pid_of)
    if [ -n "$pid" ]; then
      kill "$pid" 2>/dev/null
      for _ in $(seq 1 20); do
        sleep 0.5
        is_up || break
      done
    fi
    if is_up; then
      echo "未能停止，请手动检查: pgrep -fl ollama" >&2
      exit 1
    fi
    echo "已停止。"
    ;;
  restart)
    "$0" stop
    sleep 1
    "$0" start
    ;;
  status)
    show_status || exit 1
    ;;
  log)
    [ -f "$LOG" ] || { echo "还没有日志: $LOG"; exit 1; }
    tail -n 50 -f "$LOG"
    ;;
  *)
    echo "用法: $(basename "$0") [start|stop|restart|status|log]" >&2
    exit 2
    ;;
esac
