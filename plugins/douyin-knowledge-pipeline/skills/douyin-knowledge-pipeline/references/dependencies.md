# 依赖清单与排障 (douyin-knowledge-pipeline)

## 已安装组件（无需重装）

### 1. likebeans/douyin_text_extraction
- 位置: `D:\AI\douyin_text_extraction`
- 来源: https://github.com/likebeans/douyin_text_extraction (MIT)
- 作用: 解析抖音链接 + 下载 + 本地 SenseVoice 转写
- .env 关键值: ASR_PROVIDER=local / LOCAL_ASR_ENGINE=sensevoice / FLASK_PORT=5000 / OUTPUT_DIR=./output / MAX_VIDEO_DURATION=600
- 首次安装: git clone + uv sync --extra local-chinese（92 包含 sherpa-onnx）

### 2. uv (Python 包管理器)
- 完整路径: C:\Users\richa\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe
- 说明: WinGet 安装 (astral-sh.uv)；当前 shell PATH 未刷新时要使用完整路径

### 3. ffmpeg
- bin 目录: C:\Users\richa\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin
- 说明: WinGet 安装 (Gyan.FFmpeg)；脚本运行时自动把它拼进 PATH

### 4. Ollama (本地大模型)
- 服务: http://localhost:11434
- 模型: qwen3.5:4b (默认整理模型)、qwen3:8b (更准更慢)
- 调用: POST /api/chat {"model": "...", "messages": [...], "stream": false}

### 5. Open WebUI
- 服务: http://localhost:8080 (v0.12.5)
- API key: 存于 D:\AI\Skill-Library\OpenWebUI-Sync\.env 的 OPENWEBUI_API_KEY=（脚本自动读取，不硬编码）
- 知识库: 「个人综合知识库」ID=1c84643c-02d3-452e-9336-1718b10acafd

## 知识库 API 调用（脚本已封装，这里留档）

1. 上传: POST /api/v1/files/ (multipart, file=<markdown>) → file_id
2. 关联: POST /api/v1/knowledge/{kbId}/file/add body={"file_id": "..."}
3. 确认: GET /api/v1/knowledge/{kbId}/files

## 常见排障

- "uv 不是内部或外部命令" → 用完整路径（见上）
- ffmpeg 找不到 → 脚本已自动加 PATH；手动跑 CLI 时需 $env:Path 拼接
- 转写太慢/超时 → 视频超过 MAX_VIDEO_DURATION=600 秒会拒绝，可调 .env
- 抖音改版导致解析失败 → 更新 likebeans 仓库 (git pull)；该工具是社区维护，平台策略变化可能临时失效
- 知识库未入库 → 检查 OpenWebUI-Sync\.env 的 key 是否有效（Admin→账户→Generate API Key）

## Open WebUI 侧配套（已配置）

- 工具: douyin_pipeline_tool（id=douyin_pipeline_tool）已注册，调用本脚本
- 预设模型: douyin-kb-local (base=qwen3.5:4b) / douyin-kb-cloud (base=qwen/qwen3.8-27b)，均已挂载该工具
- 用户在 WebUI 直接发抖音链接给这两个模型 → 模型自动调工具 → 入库