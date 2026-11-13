---
name: fyp-report-workflow
description: 用于 UTS BCS FYP 报告（D:\Reborn\01-study\fyp1）的写作与维护：Chapter 1 至 5 撰写与修订、Reference 引文核验与书目、markdown 转 docx 与核查、目录架构与交接文档、导师与 SV 沟通材料。用户提到 FYP、chapter、introduction、literature review、methodology、preliminary results、project planning、reference 核查、TRF、handbook，或要接手续写该报告时使用。动笔前必须先读知识库与 handbook 并确认架构。
---

# FYP 报告工作流

目的只有一个：任何接手的 AI 都从同一基点出发，写出结构一致、口径一致、每条论断可回到原文的报告。

## 加载预算

- 本 skill 只服务 `D:\Reborn\01-study\fyp1`。别的项目不读它的 references，也不套用它的流程。
- 进门顺序：`D:\Reborn\01-study\fyp1\AGENTS.md` → `Overview\FYP_AI_Sync_and_Master_Architecture.md` → 本章现行权威文件。
- references 按需读，一次只读用得上的那一份，不预读全套：

| 要解决的问题 | 读哪份 |
|---|---|
| 章节结构与小节编号 | `references/architecture.md` |
| 具体怎么写、句式与格式 | `references/writing-rules.md` |
| 引文怎么核、失效模式 | `references/citation-verification.md` |
| 资料在哪、哪份文件回答哪类问题 | `references/kb-map.md` |
| 四维度、三测试、评分口径 | `references/evaluation-design.md` |
| `_Skills` 里有什么 | `references/bundled-skills.md` |

- `_Skills` 下的 word、pdf、sheet 等随附 skill 不预读，真正要用某个格式时才读。

## 四道门禁：任一未通过，不许动笔

**门禁 1 先读资料。** `D:\Reborn\03-knowledge\reference\fyp-writing-guide`、`D:\Reborn\01-study\University`、`Administration\Handbook_Template_Forms`（handbook 与 `FYP Template_V5.docx`）、`Overview` 总架构、本章现行文件。读摘要或凭记忆不算读完，读不到先解决读取问题。

**门禁 2 先确认。** 给用户一段确认，写清四件事：改哪章哪节；用哪个固定结构；改哪些文件、不动哪些；哪些决定资料没覆盖、必须由用户拍板。确认后才动笔。

**门禁 3 框架锁定。** 小节编号固定，见 `references/architecture.md`。要增删先回查 handbook（FYP1 8.3.2，FYP2 8.4.12）；handbook 支持就做并记录；不支持或资料冲突，先说清两种后果再取得同意。

**门禁 4 引文先定位，后使用。** 带引用的句子，动笔前必须在 `Reference` 下该 PDF 找到承载原句，记下文件名、页码或章节、原句、边界。四项缺一不许进正文。catalogue 与 deep analysis 只用于导航；摘要只够确认主题。定位不到只有三种处理：改写到原句范围、降级为不带该文献、删掉该句。记录写进本次中文说明。

## 八步流程

1. 读入口上下文：AGENTS.md、总架构、本章权威文件与相关资料。
2. 确认范围，有未覆盖的决定就停下问。
3. 改动前把现行版本移入 `_Archive` 对应子目录。
4. 在章节文件夹内写 `.md`，保留固定小节。
5. 每个事实先落到 PDF 原句，再写；支持不到就改写或删。
6. md 转 docx，回读核对。
7. 交付并说明保存位置；结构或口径有变，同步总架构文档。
8. 清理确认：问用户本轮临时 `.py`、`.txt`、中间稿要不要删，只删自己产生的。

## 写作硬规则

细则是 `references/writing-rules.md`，动笔前读。不可协商项：

- 第三人称，不出现 I、we、you；不用缩写形式。
- APA 文内引用与参考文献表；TNR 12 pt、1.5 倍行距。
- 不用 em dash（U+2014）与 AI 腔调符号。
- 不防御性示弱，不写"遗憾的是""效果有限"；论断不宽于证据。
- 每条引用指得到 PDF 的具体位置，指不到的改或删。
- 数字十以下写单词；表题注在上、图题注在下，按章编号。
- 篇幅底线：FYP1 至少 30 页，FYP2 至少 50 页。

## 目录与文件

根目录 `D:\Reborn\01-study\fyp1`；文件夹用平实英文名，不加数字前缀。不设 Revised 式目录，每章一个文件夹，现行文件直接放里面；被取代的版本进 `_Archive`，不删。每章固定四件套，命名以章文件夹名为前缀：

| 文件 | 读者 | 职责 |
|---|---|---|
| `Chapter_X_Name.md` | AI | 唯一事实来源，改动先改它 |
| `Chapter_X_Name.docx` | 用户与导师 | 由 md 生成的阅读稿 |
| `Chapter_X_Name_中文翻译.docx` | 用户 | 正文逐段中文翻译，只译不解释 |
| `Chapter_X_Name_中文说明.docx` | 用户 | 中英对照逐段理由，见「中文说明」一节 |

章内专题（评估卷、rubric、隐藏用例、附录材料）在章内单独建子文件夹，同一套四份，前缀换成专题名。评估材料以 `Chapter_3_Methodology\Evaluation\` 为唯一源，`Communication\` 只留邮件与对外 overview。同一批内容不再单开翻译 md 或核验 docx。目录表与权威文件位置见 `references/architecture.md`。

## md 转 docx

```
python scripts/md2docx.py <源 md 绝对路径> <目标 docx 绝对路径>
```

中文文档加 `--cjk`，字体切微软雅黑并写 eastAsia，否则落到回退字体。输出是 Calibri 11 工作稿，不是终稿版式，别在转换环节声称排版已完成。

## 交付前验证

退出码 0 不算证据。

```
python scripts/check_report.py <章 md> --docx <章 docx>
```

它阻断固定小节缺失、em dash、缩写与人称，并报告标题数、表数、段落数；退出码 1 即不合格，改到通过。脚本覆盖不到的仍需回读核对：

- 表题注在上、图题注在下，正文提及每个表与图。
- 引用指到 PDF 具体位置，方向与强度与正文一致；只靠 catalogue 或摘要的算未验证。
- 书目与正文一一对应，无孤立条目。
- 数字与合计逐项复算。
- docx 打开后标题层级、表格、分页视觉完好。

## 中文说明：每次交付必带

没有它，任务不算完成。命名 `<章文件名>_中文说明.docx`，与章节 md 同目录，保留 `.md` 源；生成用 `md2docx.py --cjk`。写给作者本人，平实中文，讲判断与取舍，不复述正文。第 2 项用中英对照写：英文段紧跟中文段，逐段说明这一段承担什么作用、为什么这么写、挂哪条引用，骨架照 `Chapter_1_Introduction\Chapter_1_Writing_Rationale_Bilingual.docx`。必备六项：

1. 改了哪几处，每处写改前原句、改后新句、为什么改。
2. 这章写了什么，逐节说明为什么这样组织。
3. 关键取舍与理由，覆盖结构、方法、评分、样本。
4. 与前后章的接口：从哪承接，向哪交付。
5. 口径来源：数字与规则指明权威文件；引用类论断附核验表（正文句、PDF 与页码、原句、边界）。
6. 尚未落定的事与下一步建议。

涉及题量、时长、评分、章节结构的改动，必须写明改前、改后与已同步文件清单。正文改了，这份说明同批更新。

## 随附 skill

脱离本机 skill 目录也能工作：所需 skill 已复制到 `D:\Reborn\01-study\fyp1\_Skills`，清单与用途见 `references/bundled-skills.md`。已装同名版本优先用已装的，路径失效再用副本。

## 全局记忆

`AGENTS.md` 是入口记忆：目录地图、已拍板规则、环境实测、常犯的错、未决事项。长期规则写它，控制在 200 行内；一次性决策与过程写 `AGENTS_LOG.md`；同类问题出现两次以上才升级成规则。

## 交接

结束前保证三件事一致：目录结构、各章权威文件、总架构文档。结构变了就改文档，不要只留在对话里。