# 固定架构与目录

## 1. 两阶段章节映射

报告按一个连续架构规划，跨越两个学期，不是两份互不相关的文件。FYP1 是提案加初步原型与小样本测试，FYP2 是完成系统加完整结果与结论。Handbook 在 8.3.2 定义 FYP1 结构，在 8.4.12 定义 FYP2 结构。

| 章节 | FYP1（提案，Handbook 8.3.2） | FYP2（终稿，Handbook 8.4.12） |
|---|---|---|
| 1 | Introduction | Introduction，沿用并更新 |
| 2 | Literature Review | Literature Review，沿用并更新 |
| 3 | Methodology | Methodology，沿用并更新 |
| 4 | Preliminary Results | Results Analysis |
| 5 | Project Planning | Conclusions and Recommendation |
| 后置部分 | References、Appendices | References、Appendices |

## 2. 逐章固定小节

### Chapter 1 - Introduction

固定小节：1.1 Background、1.2 Problem Statements、1.3 Objectives、1.4 Project Scope、1.5 Report Organisation。

- Background 的论证顺序：调试本身难，到 AI 时代"完成度上升但学习不明"的问题，到新手实证证据，到设计原则，到项目定位。
- Problem Statements 是三个具体、有证据支撑的缺口，不是笼统说法。
- Objectives 按 Design、Develop、Evaluate 排列，并明确 FYP1 交付初步原型与小样本评估，对应里程碑 M8 与 M9。

### Chapter 2 - Literature Review

固定顺序：2.1 Introduction、2.2 Background of Study、2.3 Instructional Frameworks、2.4 Technical Frameworks in Similar Systems、2.5 Proposed Technical Framework for This Project、2.6 Research Gap Synthesis。

- 2.2 分两节：2.2.1 新手调试困难、2.2.2 从代码补全到代码理解。
- 2.3 覆盖四个教学框架：scaffolded guidance 与 Socratic tutoring、teachable agent 与 learning-by-teaching、human-in-the-loop 主动调试、gamification。
- 2.4 逐个评述相似系统与技术框架，每个固定写四段：Framework、How they work、References、Limitations and gaps 与 Relevance to this project。覆盖面为 LLM 智能导师、teachable-agent 框架、编译器集成对话助手、context-aware agent、程序可视化、生成式题目、RAG 知识接地、gamified AI 学习。
- 2.5 给出本项目自己的技术框架，2.6 用对比表收束研究缺口。
- 每个被评述的系统都要写出 limitations 与 gaps，不得只写好处。
- 逻辑链固定为：问题，教学理论，现有技术框架，本项目框架，缺口。

### Chapter 3 - Methodology

依据课堂要求，固定为十节：3.1 Introduction、3.2 Research Design、3.3 Population of the Study、3.4 Sample and Sampling Technique、3.5 Research Instruments、3.6 Data Collection Procedures、3.7 Validity and Reliability、3.8 Data Analysis Techniques、3.9 Ethical Considerations、3.10 Chapter Summary。

- 3.2 内含研究哲学（pragmatism）、混合方法、单组准实验三阶段设计。
- 3.5 内含三个测试表单、四维度评分 rubric、系统与沙箱。
- 评估程序、四维度、混合评分模型在此定义，必须与 `references/evaluation-design.md` 一致。

注：`FYP Template_V5.docx` 的第三章骨架是 Introduction、Chosen Methodology、Stage 1 至 Stage 3、Summary。课堂要求的十节结构更完整且逐项对应 handbook 第 9.1.3 节的内容要求，故以十节为准。此差异已向用户说明并采用十节。

### Chapter 4（FYP1） - Preliminary Results

三部分：未完成的原型、测试流程、初步实验。在报告与原型完成后开始，对齐 M8 Preliminary Implementation 与 M9 Preliminary Results。不得声称产品已完成，不得编造初步结果。

### Chapter 4（FYP2） - Results Analysis

三部分：完成的项目、最终结果、讨论。初步材料被完整系统的全量分析取代。

### Chapter 5（FYP1） - Project Planning

Gantt chart 加文字说明，描述计划与时间线。

### Chapter 5（FYP2） - Conclusions and Recommendation

Future work、limitations、research gap，素材来自 `Chapter_5_Project_Planning\Limitations_Draft.md`。

## 3. 阶段承接规则

Chapter 1 至 3 在 FYP1 写成，进入 FYP2 时更新而非重写。只有 Chapter 4 与 5 在两阶段之间更换角色。任何要求重构章节的指令，先对照上表与 handbook 指定小节核验；handbook 不支持时按门禁 2 当作问题交给用户。

## 4. 目录表

根目录 `D:\Project\FYP`。

| 文件夹 | 用途 | 权威内容 |
|---|---|---|
| `Chapter_1_Introduction` | 第一章 | `Chapter_1_Introduction.md` 与 `.docx` |
| `Chapter_2_Literature_Review` | 第二章 | `Chapter_2_Literature_Review.md` 与 `.docx` |
| `Chapter_3_Methodology` | 方法与评估设计 | `Chapter_3_Methodology.md` / `.docx` / `_中文说明.md` / `.docx`；`Evaluation\`（评估卷、rubric、隐藏用例的唯一源） |
| `Chapter_4_Preliminary_Results` | FYP1 初步结果 | 待原型与初步测试完成后写入 |
| `Chapter_5_Project_Planning` | 计划与 FYP2 素材 | `Limitations_Draft.md` |
| `Reference` | 全部文献与文献文档 | 25 个 PDF；`_PDF_Text\`（同名纯文本，供 grep 原句）；Catalogue；`Reference_Deep_Analysis.md` 与 `.docx`；离题文献在 `_Archive\Excluded_References` |
| `Administration` | 官方文件 | `Handbook_Template_Forms`、`TRF`、`Gantt_Chart` |
| `Communication` | 邮件、会议、给 lecturer 的材料 | `Emails`、`Meeting_Preparation`、`Lecturer_Proposals` |
| `Overview` | 跨章与交接文档 | 总架构文档；`Chapters_1_3_Review_Notes_中文说明`（含 Ch1、Ch2 逐段理由附录）；`Document_Cleanup_2026-11-08_中文说明` |
| `Review_Comments` | 导师审阅记录 | `FYP_Version_D_SV_Comments_Reviews_and_Responses_Master_Record.docx`、`SV Review-1/2/3.docx` |
| `_Archive` | 被取代的材料，不删除 | `Old_Chapter_Versions`、`Superseded_Comm_2026-11-08`、`Superseded_Chapter3_Planning_2026-11-08`、`Excluded_References`、`PreReview_2026-11-08`、`TRF`、`Gantt_Chart`、`About_Files`、`Version_D_Records`、`Backups` |
| `_Skills` | 随附 skill 的离线副本 | 见 `bundled-skills.md` |

### 具体位置

- 最新 TRF：`Administration\TRF\BCS24090023_RICHARD WONG KIAN CHEN_TRF Version 2.pdf`。
- 最新 Gantt：`Administration\Gantt_Chart\FYP1_Gantt_Chart_Version5.xlsx`。
- handbook、模板、里程碑表、技术规范：`Administration\Handbook_Template_Forms`。
- 文献目录：`Reference\FYP_Final_Reference_and_Guidance_Catalogue.docx`。
- 文献逐篇拆解：`Reference\Reference_Deep_Analysis.md` 与 `.docx`。
- 评分权威口径：`Chapter_3_Methodology.md` 第 3.5 节；评估卷与 rubric 的源文件在 `Chapter_3_Methodology\Evaluation\`。
- 每章四件套的命名与职责见 `SKILL.md`「目录与文件」一节。
- 文献文档损坏时的回退：`_Archive\Backups`。

## 5. 归档纪律

章节文件被取代时，先把旧版移入 `_Archive` 对应子目录，再替换权威文件。任何情况下都不得让旧版只剩一份被覆盖的副本，也不得为了腾空间删除归档材料。

## 6. 驱动时程的里程碑

以 Milestones Verification Form 为准。FYP1 相关节点为 Week 9 的 M8 Preliminary Implementation、Week 11 的 M9 Preliminary Results、Week 12 的 M10 Document Submission。原型与初步测试属于 FYP1 工作，不推迟到 FYP2。
