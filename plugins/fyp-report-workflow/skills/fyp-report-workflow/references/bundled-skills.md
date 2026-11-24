# 随附 skill 清单

需要的 skill 已复制到 `D:\Reborn\01-study\fyp1\_Skills`，目的是让接手的 AI 即使换到没有装这些 skill 的环境，也能从项目文件夹里就地读取并使用。

优先规则：当前环境已装同名 skill 时用已装版本；路径失效、或换了机器读不到时，改用 `_Skills` 内的副本。行为一致，副本只是快照。

规模：12 个目录 / 9.25 MB。2026-11-15 核对：8 份 `SKILL.md` 与运行时逐字节相同（doubao-academic-polish、doubao-academic-researcher、doubao-journal-format、doubao-reference-audit、fyp-report-workflow、pdf、sheet、word）；另外 4 份在运行时未安装（academic-humanizer、anti-defensive-writing、anti-defensive-writing-en、pptx），只能读 `_Skills` 里的快照。

## 清单

| 目录 | 用途 | 什么时候读 |
|---|---|---|
| `fyp-report-workflow` | 本工作流自身。含 SKILL.md、五份 reference、`scripts/md2docx.py`（md 转 docx）与 `scripts/check_report.py`（结构与文风核查） | 任何 FYP 任务开始前。本文件的上一级目录就是它 |
| `doubao-academic-polish` | 论文正文写作总入口：整章起草、续写、扩写、补写、结构性修订，以及忠实润色与中译英（内部走 paper-write-zh / paper-write-en / paper-shape） | 要动正文内容——起草整章、改小节顺序、成段重写时 |
| `anti-defensive-writing` | 中文学术写作的反防御性原则与自查清单 | 写中文学术段落前 |
| `anti-defensive-writing-en` | 上者的英文版 | 报告正文为英文，起草时以这份为准更贴合语感 |
| `academic-humanizer` | 英文学术语气的去 AI 味：清理高频 AI 词与可预测句式，只改语气不新增研究内容 | 英文正文定稿前过一遍 |
| `doubao-academic-researcher` | 研究方向调研：系统检索、证据分级、主题聚类、争议与空白识别，产出结论先行、引用可追溯的综述 | 写 Ch2 literature review、找选题依据、摸某个机制的研究现状时 |
| `doubao-reference-audit` | 参考文献审计：真实性、题录准确性、文内与文后对应、正文主张是否被被引文献支持，出审计报告 | 每次新增或改动引用后，交付前 |
| `doubao-journal-format` | 把论文 Word 套用 `.docx` 模板或校格式规则（字体、行距、题注、标题层级） | 按 `Administration\Handbook_Template_Forms` 里的 `FYP Template_V5.docx` 出终稿时 |
| `word` | Office Word 的读取、新建、修改，图片转 Word，样式与页眉页脚处理 | 生成或修改 docx；需要样式、题注、目录时 |
| `pdf` | PDF 读取、创建、编辑、转换、内容提取、页面处理、扫描件解析 | 读 handbook、教学 deck、参考文献 PDF 时 |
| `sheet` | 表格读写、分析与可视化 | 读写 `Administration\Gantt_Chart\FYP1_Gantt_Chart_Version5.xlsx`，或任何 xlsx 与 csv |
| `pptx` | 本地 `.pptx` / `.potx` 的读写与生成 | 做答辩 deck、进度汇报幻灯片时；飞书在线幻灯片不归它，用平台 `ppt` |

## 分工与边界（为什么不会互相抢）

写作四件各管一层，先有内容再谈语气，最后才排版：

1. `doubao-academic-polish` 管**内容与结构**——写什么、按什么顺序写。
2. `anti-defensive-writing` / `-en` 管**叙事姿态**——不要写"本文旨在""综上所述"这类防御性套话。
3. `academic-humanizer` 管**定稿语气**——英文读起来不像 AI 写的，但不承诺绕过 AI 检测率。
4. `doubao-journal-format` 管**版式**——已定稿的 docx 套模板；`word` 管文档本身的结构操作（样式、页眉页脚、题注、图片）。转换脚本已出 TNR 12 pt、1.5 倍行距的正文与标题；模板级自动编号、目录、题注与统一页边距留到定稿套模板，不在转换环节声称整本终稿版式完成。

阅读与引用三件分工：

1. `doubao-academic-researcher` 管**摸方向、出综述**——还没锁定具体文献，要看这个领域在说什么。
2. `doubao-reference-audit` 管**逐条核验**——已有文献清单或已写好引文，要查真假与是否支持主张。
3. `pdf` 管**读原文**——拿到 PDF 之后的抽取与定位。

## 刻意没有随附的 skill

| 没装 | 原因 |
|---|---|
| `paper-spine`（2.0 MB） | 端到端"研究→写→审→交付"论文流水线，与 `doubao-academic-polish` + `doubao-academic-researcher` 职责重叠；本项目要的是报告，不是一个可投稿的 paper 工程 |
| `doubao-human-signal`（172 KB） | 中文去 AI 味。本报告正文为英文，英文这一层由 `academic-humanizer` 覆盖 |
| `paper-lookup` / `literature-review` / `citation-management` | 数据库检索与引文管理，功能已被 `doubao-academic-researcher`（检索+溯源）与 `doubao-reference-audit`（核验）覆盖，且依赖外部 API |
| `paper-review-assistant` | 审稿人视角与目标期刊匹配，面向投稿，不面向学位报告 |
| `docx` / `word-document-processing` | 与 `word` 在 OOXML 与本地 Word 处理上重叠，且体量更大 |
| `ppt`（飞书在线幻灯片） | 需要飞书账号与联网，本项目答辩 deck 用本地 `pptx` 即可 |
| `doubao-coding-*` 系列 | 平台自带，且与报告交付无关；换到没装这些的环境时由平台侧提供，不复制进项目 |

## 使用方式

1. 先读目标 skill 的 `SKILL.md` 全文，再按其指引调用。只凭记忆或只凭目录名推断用法不算读过。
2. `fyp-report-workflow` 是主流程，其余是被它调用的能力。主流程的三道门禁优先，能力 skill 不能成为跳过门禁的理由。
3. 需要把 markdown 转 docx 时，优先用 `fyp-report-workflow\scripts\md2docx.py`，它已做成命令行版本：

```
python "D:\Reborn\01-study\fyp1\_Skills\fyp-report-workflow\scripts\md2docx.py" <源 md> <目标 docx>
```

4. 定稿套模板（自动编号、目录、题注、页边距）时读 `word` 与 `doubao-journal-format`；转换脚本只负责正文 TNR 12 pt、1.5 倍行距，不冒充整本终稿。

## 没有随附的 skill

`verifier-hub` 只出现在平台的 skill 注册列表中，磁盘上没有对应目录，无法复制进本文件夹，因此不在清单内。

它原本提供的能力是交付前对 docx、xlsx、pdf、pptx 做确定性校验。本项目只需要其中与报告有关的部分，已由 `scripts/check_report.py` 覆盖：固定小节、em dash、缩写、第一第二人称、引文↔书目对应、同章小节交叉引用、docx 残留 markdown 标记、段落与表格计数；孤立书目、段数/词数差量、缩写首用为警告级。xlsx、pdf、pptx 深度校验本项目用不到，需要时再单独处理。

## 维护

- 副本是某一时点的快照。上游 skill 更新后，重新复制一次覆盖即可：

```
Copy-Item -LiteralPath "<上游 skill 目录>" -Destination "D:\Reborn\01-study\fyp1\_Skills\<名称>" -Recurse -Force
```

- 新增依赖 skill 时，复制进 `_Skills` 并同时更新本表，不要只在对话里说明。
- `_Skills` 只放 skill，不放项目产物。产物仍归各自章节文件夹。
- 与 `D:\Reborn\skill\Skill-Library` 的关系：库里是正本与三端导出，`_Skills` 是项目内快照。改库里的正本后，这里按需重新覆盖；反之亦然。
