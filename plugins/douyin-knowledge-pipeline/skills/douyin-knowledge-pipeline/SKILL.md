---
name: douyin-knowledge-pipeline
description: 抖音视频知识自动入库流水线。用户提供抖音分享链接（v.douyin.com 短链、完整链接或分享文本），自动完成 下载视频→本地 SenseVoice 提取口播逐字稿→本地 qwen 整理成结构化知识卡片→推入 Open WebUI「个人综合知识库」做 RAG。无需登录抖音账号、无需 API key、全程本地。也用于把逐字稿/笔记批量整理成知识卡片入库。用户说"处理这条抖音/把这个视频整理进知识库/提取视频内容存起来"时使用。
---

# 抖音知识入库流水线 (Douyin Knowledge Pipeline)

把抖音口播视频自动变成 Open WebUI 可检索的知识卡片。单链接 5~10 分钟，无需账号。

## 触发场景

- 用户发来抖音分享链接或分享文本，要求"提取/整理/存进知识库"
- 用户提供多条链接（文本文件、Excel、聊天里多条）要求批量处理
- 用户已有逐字稿/笔记文本，要求整理成知识卡片入库

## 依赖（已在本机装好）

| 组件 | 位置/说明 |
|---|---|
| likebeans/douyin_text_extraction | `D:\AI\douyin_text_extraction`（uv 项目，SenseVoiceSmall 本地转写） |
| uv | WinGet 安装，完整路径见 `references/dependencies.md` |
| ffmpeg | WinGet 安装，bin 目录见 `references/dependencies.md` |
| Ollama | `http://localhost:11434`，默认 `qwen3.5:4b`；指定的模型不存在时脚本自动回落到已安装的对话模型 |
| Open WebUI | `http://localhost:8080`，API key 在 `D:\Reborn\skill\Skill-Library\OpenWebUI-Sync\.env` |
| 知识库 | 双写：「抖音知识卡片」ID=`d580d64e-1d2d-40cf-9dc5-7900bd85c76c` + 「个人综合知识库」ID=`1c84643c-02d3-452e-9336-1718b10acafd` |

## 执行流程

用 `scripts/douyin_pipeline.py` 一条命令完成全流程：

```powershell
python "D:\Reborn\skill\Skill-Library\02-Custom\douyin-knowledge-pipeline\scripts\douyin_pipeline.py" "<链接>" "qwen3.5:4b"
```

- 批量（每行一条链接的文本文件）：
  ```powershell
  python "...\scripts\douyin_pipeline.py" --file "D:\path\links.txt" "qwen3.5:4b"
  ```
- 模型可选 `qwen3.5:4b`（快，默认）或 `qwen3.5:9b`（更准、慢）；传了不存在的模型名不会失败，会自动回落。

脚本输出：每条视频的 标题 / 判定语种 / 逐字稿字数 / 知识卡片路径（`D:\AI\douyin_text_extraction\output\*_knowledge.md`）/ 知识库入库 file_id。

## 关键规则

1. **不要登录抖音账号**——方案无需登录；用户手动把收藏链接整理成文本/Excel 发来即可。
2. **整理一律走本地 qwen**，不调 DeepSeek 等云端 API。
3. 知识卡片规范（YAML frontmatter + 七个章节）由脚本内置 prompt 保证，并由 `build_card()` 强制清洗：剥掉模型爱加的整篇代码块包裹（三个反引号或 ```markdown）、重写合法 YAML（tags 强制为列表、weight 夹到 1-5）、date/valid_from 覆写为当天。这样卡片在 WebUI 里才会正常渲染，不会显示成一大段代码块、YAML 裸露。
4. 入库走 Open WebUI 两步 API：上传文件 → 关联知识库。脚本用 requests 标准 multipart（**不要用 urllib 手拼 multipart，会超时**），且幂等：同名文件已在库则直接复用，重复处理同一链接不会产生重复文件。
5. RAG 引用验证：对话时以 `files: [{id: "<知识库ID>", type: "collection", status: "processed"}]` 传参（`knowledge` 参数不生效）。
6. Open WebUI 工具调用：裸 API 请求（无 chat_id/id/stream）**不会执行工具**。WebUI 界面聊天天然走对路径；API 直调需用 `params.function_calling: "legacy"` + `tool_ids`（Path B），或完整 chat 流程（Path A）。

## 验证方法

处理完成后，向「个人综合知识库」提问测试 RAG：用 Open WebUI 任意模型对话并确认响应含 sources/citations 引用。

## 参考

- 依赖清单与排障：`references/dependencies.md`
- 工具（Open WebUI Tools）版本：`douyin_pipeline_tool` 已注册，预设模型 `douyin-kb-local` / `douyin-kb-cloud` 已挂载该工具，用户在 WebUI 直接发链接给这两个模型即可触发。

7. **多语言支持**：ASR 用 SenseVoice 多语模型（中/英/日/韩/粤），`language` 由环境变量 `SENSEVOICE_LANGUAGE` 控制，默认 `auto` 自动识别；云端 DashScope 路径本身带 `language_hints=["zh","en"]`。无论原文是中文还是英文，卡片正文一律输出简体中文；英文原文的「原文摘录」保留原句并附中文直译，frontmatter 带 `source_language`。
8. **入库 400 排查**：若关联知识库返回 `Collection expecting embedding with dimension of 384, got 1024`，说明该库的向量集合还是旧的 384 维（all-MiniLM），而当前嵌入已换成 bge-m3（1024 维），需调 `POST /api/v1/knowledge/reindex` 重索引；重索引后同名上传即可恢复正常入库。
