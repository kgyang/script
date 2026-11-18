# mac 环境笔记

本机：MacBook Pro / Apple M6（12 核 GPU）/ 32GB 统一内存 / macOS 27。
记录几个踩过的坑，避免重复排查。

## Ollama

装的是 `/Applications/Ollama.app`（v0.40.16），CLI 在 bundle 内：
`/Applications/Ollama.app/Contents/Resources/ollama`（PATH 已在 `mac/zshrc` 中配置）。
启停用 `mac/ollama-serve.sh`，日志在 `~/Library/Logs/ollama-serve.log`。
登录自启用 `mac/ollama-serve.sh install` 装（LaunchAgent `local.ollama-serve`，
plist 在 `~/Library/LaunchAgents/`）。macOS 没有 systemd：登录自启是 LaunchAgent，
系统级（开机、未登录也跑）才是 LaunchDaemon，这里只要前者。`KeepAlive` 故意为
false——否则 `ollama-serve.sh stop` 刚杀掉就被 launchd 拉起来；代价是不做崩溃重启。
装好后 start/stop/restart 自动走 `launchctl`。脚本挪位置后要重跑一次 install。

Apple Silicon 上 Ollama 自动选 **MLX 后端**（不是 llama.cpp），Metal 可用显存 25GB。

已拉模型与实测（400 token 生成，中位数）：

| 模型 | 磁盘 | 生成速度 | 显存 @8K / 32K |
|---|---|---|---|
| qwen3.5:9b | 7.6GB | 38.1 tok/s | 8.1GB / ~10GB |
| qwen3.8:27b | 18GB | 21.9 tok/s | 19GB / 22GB |

### 坑 1：拉模型只有 300KB/s

Ollama 默认 4 条传输流，在限速网络上跑不满。`OLLAMA_MAX_TRANSFER_STREAMS=32`
把 18GB 的模型从「6 小时」缩短到「25 分钟」。

### 坑 2：同时驻留两个模型会互相拖慢

32GB 机器 GPU 额度约 25GB。27B(19GB) + 9B(8GB) = 27GB 超额度后，系统压缩换页，
27B 从 21.9 掉到 13.4 tok/s。用 `OLLAMA_MAX_LOADED_MODELS=1` 限制只驻留一个。

### 坑 3：Ollama 的 MLX 权重不能直接给 mlx-lm 用

Ollama 把 MLX 模型拆成 **1199 个单张量 safetensors**（每个 blob 一个），
量化用 NVIDIA ModelOpt 的 NVFP4 布局（`weight` U32 打包 + `weight.scale` U8 +
`weight.global_scale` F32，config.json 里是 compressed-tensors 的 `config_groups`）。

mlx-lm 要的是「HF 目录 + 扁平 `quantization` 配置 + `scales` 命名」，两者不兼容，
需要写转换脚本才能互通。另外 mlx-lm 0.32.2 要求 **Python ≥3.11**，本机只有 3.9.6。

结论：日常就用 Ollama（已经在跑 MLX），mlx-lm 只在需要微调/LoRA 或拿 logits 时才值得折腾。

## Git / GitHub 访问

### 坑 4：所有 git 操作 404

`~/.gitconfig` 里曾有：

```ini
[url "https://gh-proxy.com/https://github.com/"]
    insteadOf = https://github.com/
```

但 **gh-proxy 不支持 git 智能协议**——拿公开仓库验证，`git/git` 和 `kgyang/script`
都返回 404（它只适合下 release / raw 文件）。这条规则会让所有 GitHub 的
clone/fetch/push 失败。

以前没暴露是因为 URL 里嵌了 token（`https://ghp_xxx@github.com/...` 不匹配
`https://github.com/` 前缀，从未被改写）。

### 坑 5：强制 HTTP/1.1 会被 reset

GitHub 直连必须走 HTTP/2。`http.version=HTTP/1.1` 会长时间挂起后
`Recv failure: Connection reset by peer`；默认 HTTP/2 正常。

### 现在的配置

- remote 用干净地址：`https://github.com/kgyang/script.git`（URL 里不再有 token）
- 凭据存 macOS 钥匙串：`git config --global credential.helper osxkeychain`
- 删除了那条 gh-proxy 规则，备份在 `~/.gitconfig.bak.20261118-215506`

## genreadme

`common/genreadme` 会扫描各子目录的**可执行文件**，执行 `-h` 并把输出写进
`README.md`（整篇覆盖）。两个注意点：

1. 它在脚本里写的是 `python ./$f -h`，而 macOS 只有 `python3`。
   直接跑会**丢掉所有 .py 条目**（实测会少 5 段）。重新生成前先备份 README。
2. 因此手写的说明不要放 README.md，会被下次生成覆盖 —— 就是本文件存在的原因。
