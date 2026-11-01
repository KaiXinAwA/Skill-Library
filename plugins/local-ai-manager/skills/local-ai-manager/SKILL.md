---
name: local-ai-manager
description: Manage this machine's local LLM stack (Ollama, Open WebUI, Docker, RTX 5060 Laptop 8GB VRAM, D-drive external SSD). Use when the user asks about local models, Ollama commands, VRAM limits, adding or removing models, connecting other AI tools (Cursor, Cline, Continue, Codex) to the local model, Open WebUI troubleshooting, D-drive / external SSD issues, or deciding whether a task should go to the local qwen model vs the cloud GPT already connected. Do NOT use for cloud-only tasks, web research, or writing code unrelated to the local AI stack. Do NOT attempt to wire Doubao / Doubao Work to the local model as its backend — it is a cloud agent.
---

# Local AI Manager

> 本 Skill 把这台机器上已经核实过的本地 AI 部署知识固化下来，让任何 AI 工具（豆包、Codex、Claude Code、Cursor 等）一上来就懂环境，不用用户每次从头解释。
> 所有事实来自 `D:\AI\Knowledge-Base\06-AI-System\` 下两份部署文档，未核实的推断不要写进来。

## 1. 环境快照（2026-10 核实）

### 硬件
- 笔记本：Lenovo LOQ 15AHP10（83JG00AVMJ）
- CPU：AMD Ryzen 7 250
- GPU：**NVIDIA RTX 5060 Laptop GPU，8GB VRAM（硬约束）**
- 内存：16GB RAM
- 数据盘：Samsung T7 Shield 1TB 外接 SSD，盘符 `D:`
- **外接 SSD 没插好时 Ollama 会找不到模型——任何"模型不见了"的排查，先确认 D: 盘存在。**

### 软件版本
- Ollama：0.40.11，Windows 服务，开机自启
- 模型存储：`D:\AI\Models\Ollama`（**在 D 盘，不在系统盘，也不在 WSL 里**）
- Docker Desktop：管理 open-webui 容器
- Open WebUI：v0.12.4，Docker 容器名 `open-webui`
  - 端口：`127.0.0.1:3000` → 容器内 `8080`
  - 数据卷：`open-webui` → `/app/backend/data`（**这个卷不能删**）
  - 访问地址：http://localhost:3000
  - RAG 嵌入模型：容器内 `sentence-transformers/all-MiniLM-L6-v2`（**这不是 Ollama 模型，不要去 ollama pull**）
- WSL2 + Ubuntu 已装（用户 `richa`），但 Ollama 模型放在 Windows D 盘，不依赖 WSL
- 已接云端：ChatGPT（GPT）

### 已装模型

| 模型 | 用途 | Q4 体积 | 状态 |
|---|---|---|---|
| `qwen3.5:4b` | 通用聊天、中文问答、简单代码解释、看图理解（vision）、RAG 对话 | ~2.5GB | 主力，`100% GPU` |

**预留空位（按需再下，不要一次拉一堆）**：
- 主力升级候选：`qwen3.5:9b`（~5.5GB，8GB VRAM 能整体放下）
- Agent / 工具调用专项：`lfm2.5:8b`（原生 function calling 优化，2026-10 新出）
- 代码专项：`qwen2.5-coder:7b` 或同代 coder 版
- 嵌入：Open WebUI 容器内已配好，**不需要在 Ollama 侧下嵌入模型**

---

## 2. 8GB VRAM 硬约束（推荐新模型前必查）

### 能跑（100% GPU，速度快）
- 4B 及以下 Q4：约 2.5GB，最从容（当前）
- 7–8B Q4：约 4–5GB，能跑但余量小
- 注意 8B 模型开 32K 以上长上下文时，KV cache 会顶爆显存

### 会溢出到内存（速度掉 10–50 倍，不要下）
- 14B Q4 及以上：约 9GB+ 权重，8GB 装不下
- 27B+：完全不要碰

### 速查表（Q4，含 ~1GB 系统开销）

| 模型规模 | 权重 | +4K ctx | +16K ctx | 8GB VRAM 能跑？ |
|---|---|---|---|---|
| 3B | ~1.5GB | +0.005GB | +0.02GB | 很轻松 |
| 4B | ~2.5GB | +0.008GB | +0.03GB | 很轻松（当前） |
| 7–8B | ~4–5GB | +0.01GB | +0.04GB | 能跑，余量小 |
| 14B | ~7.5GB | +0.02GB | +0.07GB | 会溢出，不要下 |
| 27B+ | ~15GB+ | — | — | 完全不要碰 |

### 验证是否真的在 GPU 上
模型跑起来后，另开 PowerShell：
```powershell
ollama ps
```
看 PROCESSOR 列：
- `100% GPU` = 全在显存，正常
- 出现 `XX% CPU` = 显存不够溢出到内存了，换小模型或缩短上下文

---

## 3. 日常命令速查（PowerShell）

```powershell
ollama list                          # 已装模型和体积
ollama ps                            # 当前在 GPU 上跑的模型（重点看 PROCESSOR）
ollama run qwen3.5:4b                # 直接进对话测试
ollama pull qwen3.5:9b               # 下新模型（先过第 2 节的 VRAM 检查）
ollama rm <模型名>                   # 删模型省盘空间
ollama show qwen3.5:4b               # 模型详情（上下文窗口、量化等）
```

Open WebUI / Docker：
```powershell
docker ps                              # open-webui 容器是否在跑
docker logs open-webui --tail 50       # 看 Open WebUI 日志
```

---

## 4. 接入其他 AI 工具

Ollama 提供 **OpenAI 兼容 API**，任何支持自定义 OpenAI endpoint 的工具都能接（Cursor、Cline、Continue、Codex、Chatbox 等）：

| 场景 | Base URL |
|---|---|
| Windows 本机程序（Cursor、Cline、Continue 桌面端） | `http://localhost:11434/v1` |
| Docker 容器内（Open WebUI 等） | `http://host.docker.internal:11434/v1` |
| 同一局域网其他机器 | `http://<这台机器的局域网IP>:11434/v1` |

通用配置：
- API Key：随便填（Ollama 不校验），比如 `ollama`
- Model 名：填已 `ollama pull` 的名字，如 `qwen3.5:4b`

### 已验证的接入
- **Open WebUI（Docker 容器）**：已通
- **Codex（ChatGPT 桌面应用）**：`ollama launch codex-app --model qwen3.5:4b` 启动，基本通；但"每次请求是否都走本地"和"完全断网时是否可用"还没严格验证

### 不要尝试的接入
- **不要把豆包 / Doubao Work 接成 Ollama 后端**——豆包是云端 agent，后端是字节模型，不能换成本地模型。方向是反的：豆包可以帮你管理本地 Skill 库、分析仓库、审核模型，而不是被本地模型替换。

---

## 5. 本地 vs 云端分工

| 任务类型 | 用哪个 | 原因 |
|---|---|---|
| 日常中文问答、简单解释 | 本地 qwen3.5:4b | 免费、离线、隐私 |
| RAG 知识库问答 | 本地 qwen + Open WebUI | 资料不出本机 |
| 看图理解（截图、UI 草图） | 本地 qwen3.5:4b（带 vision） | 已支持 |
| 简单代码解释、单文件 bug | 本地 qwen | 够用 |
| **复杂 agent 任务**（自动改多文件代码、跑测试、长链工具调用） | **云端 GPT** | 4B 原生 function calling 不稳，社区需专门微调版才能真正调用工具 |
| 大型架构决策、深度推理 | 云端 GPT | 4B 推理能力有限 |
| 需要最新模型能力的任务 | 云端 | 本地模型有知识截止日期 |

**原则**：不要硬逼 4B 干它不擅长的 agent 活。本地模型做离线、隐私、RAG 辅助；复杂 agent 交给已经接好的 GPT。

---

## 6. 排查顺序（按优先级，不要跳步）

### Open WebUI 页面打不开（ERR_CONNECTION_REFUSED）
1. Docker Desktop 是否已启动？（容器的 `--restart unless-stopped` 在 Docker Engine 没跑时不生效）
2. `docker ps` 看 `open-webui` 容器状态
3. 端口 3000 是否被占
4. 刷新 http://localhost:3000
5. **不要**第一时间删容器或数据卷

### Open WebUI 能打开但没有模型
1. Ollama 是否在跑（系统托盘有没有 Ollama 图标）
2. `ollama list` 看模型是否还在
3. **D: 盘（外接 SSD）是否已连接？** 模型文件在 D 盘上
4. Open WebUI 容器内的 Ollama 连接地址是否正确

### 模型加载慢 / 回答慢
1. `ollama ps` 看是不是 `100% GPU`——如果在 CPU 上跑就是显存不够
2. 是不是同时开了别的占显存的程序（游戏、其他 AI 工具）
3. 上下文是不是开太长
4. 模型刚下载或刚重启后首次加载慢是正常的，预热后会快

### D 盘满了
1. `ollama list` 看各模型体积
2. 不常用的模型用 `ollama rm <名字>` 正规删
3. **不要**删 Docker 卷 `open-webui`——里面是聊天记录、账号、知识库索引
4. **不要**直接删 `D:\AI\Models\Ollama` 下的文件——用 `ollama rm` 正规删，否则 Ollama 状态会不一致

---

## 7. 安全红线（agent 看到这些要主动拦）

1. **`open-webui` Docker 卷不能删**——聊天记录、用户、知识库向量索引都在里面，删了不可恢复。删容器 ≠ 删卷，但 `docker volume rm open-webui` 是致命操作。
2. **`WEBUI_SECRET_KEY` 不能贴进公开文档、GitHub、聊天截图**——历史上曾经明文贴过；重建容器时要生成新的随机值并妥善保存。
3. **外接 SSD 没连时不要重新 `ollama pull` 模型**——会重复下载到系统盘或报错。先确认 D: 盘存在。
4. **不要在 Docker 容器跑着的时候直接复制 `webui.db` 当备份**——SQLite WAL 模式下要一致性备份（停容器后再复制，或用 `.backup` 命令）。
5. **不要一次 `ollama pull` 一堆模型**——按实际短板逐个加，每个都先过第 2 节的 VRAM 检查。
6. **不要把本地模型接到豆包 / Doubao Work 当后端**——方向错了。
7. **不要把 Open WebUI 绑定到 `0.0.0.0:3000` 暴露到公网**——当前是 `127.0.0.1:3000`，保持这个绑定。

---

## 8. 关键路径速查

| 用途 | 路径 / 地址 |
|---|---|
| Ollama 模型文件 | `D:\AI\Models\Ollama` |
| Open WebUI 聊天界面 | http://localhost:3000 |
| Ollama API（本机） | `http://localhost:11434` |
| Ollama API（OpenAI 兼容） | `http://localhost:11434/v1` |
| Skill 中央仓库 | `D:\AI\Skill-Library` |
| 知识库原始资料 | `D:\AI\Knowledge-Base` |
| AI 系统部署文档 | `D:\AI\Knowledge-Base\06-AI-System` |
| Open WebUI 容器数据 | Docker 卷 `open-webui` → `/app/backend/data` |

---

## 9. 更新日志

- **2026-10-28**：初始版本。基于 `D:\AI\Knowledge-Base\06-AI-System\` 下两份部署文档创建。已装模型仅 `qwen3.5:4b`。参考了 gschoep/build-with-local-llm-ollama 的 config/VRAM 估算结构和 IsmaelMartinez/delegate-local 的红线写法，但没有抄代码模板（本场景是个人运维，不是用 Ollama 写应用）。