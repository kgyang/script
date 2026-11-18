#!/usr/bin/env bash
# ollama-serve.sh - 按需启停本机 Ollama 服务
#
#   ollama-serve.sh            启动（已在跑则直接报告状态）
#   ollama-serve.sh stop       停止
#   ollama-serve.sh restart    重启
#   ollama-serve.sh status     看状态（版本 / 进程 / 已加载模型）
#   ollama-serve.sh log        跟踪日志
#   ollama-serve.sh install    装成 launchd 登录自启（LaunchAgent）
#   ollama-serve.sh uninstall  移除登录自启
#
# 自启只在登录后生效（LaunchAgent，非系统级 LaunchDaemon）；装了自启后
# start/stop/restart 会自动走 launchctl，避免和 launchd 抢端口。
#
# 参数都可用同名环境变量覆盖，例如: OLLAMA_KEEP_ALIVE=30m ollama-serve.sh

set -u

OLLAMA_BIN="${OLLAMA_BIN:-/Applications/Ollama.app/Contents/Resources/ollama}"
HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
API="http://${HOST}/api/version"
LOG="${OLLAMA_LOG:-$HOME/Library/Logs/ollama-serve.log}"

# launchd 登录自启（LaunchAgent）：label 与 plist 路径
AGENT_LABEL="local.ollama-serve"
AGENT_PLIST="$HOME/Library/LaunchAgents/${AGENT_LABEL}.plist"
CURRENT_UID="$(id -u)"

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

# 自启是否已装好并处于加载状态
agent_loaded() { launchctl print "gui/${CURRENT_UID}/${AGENT_LABEL}" >/dev/null 2>&1; }

# 等 curl 里的 /api/version 起来，最多 ~20s
wait_up() {
  for _ in $(seq 1 40); do
    sleep 0.5
    is_up && return 0
  done
  return 1
}

# 生成 LaunchAgent：launchd 负责拉起并在退出后不再重试（KeepAlive false），
# 所以 `ollama-serve.sh stop` 不会被立刻重启；进程以 run 模式前台 exec，
# 环境变量仍由本脚本统一提供，plist 里不重复写。
write_agent_plist() {
  local self
  self="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  mkdir -p "$(dirname "$AGENT_PLIST")"
  cat >"$AGENT_PLIST" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>__LABEL__</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>exec "__SCRIPT__" run</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>__HOME__</string>
    <key>PATH</key>
    <string>/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>WorkingDirectory</key>
  <string>__HOME__</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <false/>
  <key>StandardOutPath</key>
  <string>__LOG__</string>
  <key>StandardErrorPath</key>
  <string>__LOG__</string>
</dict>
</plist>
PLIST
  sed -i '' -e "s|__LABEL__|${AGENT_LABEL}|g" \
    -e "s|__SCRIPT__|${self}|g" \
    -e "s|__HOME__|${HOME}|g" \
    -e "s|__LOG__|${LOG}|g" "$AGENT_PLIST"
}

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
    if agent_loaded; then
      echo "正在通过 launchd 启动 ..."
      launchctl kickstart "gui/${CURRENT_UID}/${AGENT_LABEL}" 2>/dev/null || true
    else
      echo "正在启动 ..."
      nohup "$OLLAMA_BIN" serve >>"$LOG" 2>&1 &
      disown 2>/dev/null || true
    fi
    if wait_up; then
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
    if agent_loaded; then
      launchctl kill SIGTERM "gui/${CURRENT_UID}/${AGENT_LABEL}" 2>/dev/null
      for _ in $(seq 1 20); do
        sleep 0.5
        is_up || break
      done
    else
      pid=$(pid_of)
      if [ -n "$pid" ]; then
        kill "$pid" 2>/dev/null
        for _ in $(seq 1 20); do
          sleep 0.5
          is_up || break
        done
      fi
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
  install)
    if [ ! -x "$OLLAMA_BIN" ]; then
      echo "找不到可执行文件: $OLLAMA_BIN" >&2
      exit 1
    fi
    # 先把手动起的进程停掉，否则 launchd 启动时会撞端口
    if is_up && ! agent_loaded; then
      "$0" stop >/dev/null 2>&1 || true
    fi
    mkdir -p "$(dirname "$LOG")"
    write_agent_plist
    launchctl bootout "gui/${CURRENT_UID}/${AGENT_LABEL}" >/dev/null 2>&1 || true
    if ! launchctl bootstrap "gui/${CURRENT_UID}" "$AGENT_PLIST" 2>/dev/null; then
      echo "launchctl bootstrap 失败，检查 $AGENT_PLIST" >&2
      exit 1
    fi
    if wait_up; then
      echo "已安装登录自启: $AGENT_PLIST"
      show_status
    else
      echo "已写入 ${AGENT_PLIST}，但服务没起来，最近日志：" >&2
      tail -15 "$LOG" >&2
      exit 1
    fi
    ;;
  uninstall)
    if agent_loaded; then
      launchctl bootout "gui/${CURRENT_UID}/${AGENT_LABEL}" >/dev/null 2>&1 || true
    fi
    rm -f "$AGENT_PLIST"
    echo "已移除登录自启（${AGENT_LABEL}），服务已停止。"
    ;;
  run)
    # launchd 专用：前台 exec，环境变量由本脚本统一导出
    exec "$OLLAMA_BIN" serve
    ;;
  status)
    show_status || exit 1
    ;;
  log)
    [ -f "$LOG" ] || { echo "还没有日志: $LOG"; exit 1; }
    tail -n 50 -f "$LOG"
    ;;
  -h|--help)
    cat <<'EOF'
按需启停本机 Ollama 服务（Apple Silicon 上走 MLX 后端），启动时自动带上合适的显存/网络参数。
Usage: ollama-serve.sh [start|stop|restart|status|log|install|uninstall]

start     start the service; if already running, just report status (default)
stop      stop the service
restart   restart the service
status    show version, pid, endpoints and loaded models
log       tail -f the log (~/Library/Logs/ollama-serve.log)
install   install a launchd LaunchAgent so the service starts at login
uninstall remove the LaunchAgent (stops the service)

Parameters set on startup (all overridable by env var of the same name):
OLLAMA_MAX_TRANSFER_STREAMS=32  pull concurrency; default 4 gives only ~300KB/s on throttled links
OLLAMA_MAX_LOADED_MODELS=1      on 32GB, 27B(19GB)+9B(8GB) overflows the 25GB GPU budget
OLLAMA_FLASH_ATTENTION=1        Metal flash attention
OLLAMA_KV_CACHE_TYPE=q8_0       8bit KV cache, halves long-context memory
OLLAMA_KEEP_ALIVE=10m           unload the model after 10m idle

Example:
ollama-serve.sh                      start
OLLAMA_KEEP_ALIVE=1h ollama-serve.sh  start with overridden keep-alive
EOF
    exit 0
    ;;
  *)
    echo "Usage: $(basename "$0") [start|stop|restart|status|log|install|uninstall]" >&2
    exit 2
    ;;
esac
