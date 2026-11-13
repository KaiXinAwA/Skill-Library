# 随附 skill 清单

需要的 skill 已复制到 `D:\Reborn\01-study\fyp1\_Skills`，目的是让接手的 AI 即使换到没有装这些 skill 的环境，也能从项目文件夹里就地读取并使用。

优先规则：当前环境已装同名 skill 时用已装版本；路径失效、或换了机器读不到时，改用 `_Skills` 内的副本。行为一致，副本只是快照。

## 清单

| 目录 | 用途 | 什么时候读 |
|---|---|---|
| `fyp-report-workflow` | 本工作流自身。含 SKILL.md、五份 reference、`scripts/md2docx.py`（md 转 docx）与 `scripts/check_report.py`（结构与文风核查） | 任何 FYP 任务开始前。本文件的上一级目录就是它 |
| `word` | Office Word 的读取、新建、修改，图片转 Word，排版与样式处理 | 生成或修改 docx；需要样式、页眉页脚、题注、目录时 |
| `pdf` | PDF 读取、创建、编辑、转换、内容提取、页面处理、扫描件解析 | 读 handbook、教学 deck、参考文献 PDF 时 |
| `sheet` | 表格读写、分析与可视化 | 读写 `Administration\Gantt_Chart\FYP1_Gantt_Chart_Version5.xlsx`，或任何 xlsx 与 csv |
| `anti-defensive-writing` | 中文学术写作的反防御性原则与自查清单 | 起草或修改任何正文段落前 |
| `anti-defensive-writing-en` | 上者的英文版 | 报告正文为英文，起草时以这份为准更贴合语感 |

## 使用方式

1. 先读目标 skill 的 `SKILL.md` 全文，再按其指引调用。只凭记忆或只凭目录名推断用法不算读过。
2. `fyp-report-workflow` 是主流程，其余是被它调用的能力。主流程的三道门禁优先，能力 skill 不能成为跳过门禁的理由。
3. 需要把 markdown 转 docx 时，优先用 `fyp-report-workflow\scripts\md2docx.py`，它已做成命令行版本：

```
python "D:\Reborn\01-study\fyp1\_Skills\fyp-report-workflow\scripts\md2docx.py" <源 md> <目标 docx>
```

4. 需要终稿版式（Times New Roman 12 pt、1.5 倍行距、题注规范）时读 `word`，不要用转换脚本的工作稿冒充终稿。

## 没有随附的 skill

`verifier-hub` 只出现在平台的 skill 注册列表中，磁盘上没有对应目录，无法复制进本文件夹，因此不在清单内。

它原本提供的能力是交付前对 docx、xlsx、pdf、pptx 做确定性校验。本项目只需要其中与报告有关的部分，已由 `scripts/check_report.py` 覆盖：固定小节、em dash、缩写、第一第二人称、段落与表格计数。xlsx、pdf、pptx 深度校验本项目用不到，需要时再单独处理。

## 维护

- 副本是某一时点的快照。上游 skill 更新后，重新复制一次覆盖即可：

```
Copy-Item -LiteralPath "<上游 skill 目录>" -Destination "D:\Reborn\01-study\fyp1\_Skills\<名称>" -Recurse -Force
```

- 新增依赖 skill 时，复制进 `_Skills` 并同时更新本表，不要只在对话里说明。
- `_Skills` 只放 skill，不放项目产物。产物仍归各自章节文件夹。
