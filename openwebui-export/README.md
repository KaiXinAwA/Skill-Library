# Open WebUI 技能导入包

> 本目录把 `D:\AI\Skill-Library\00-General\` 下的技能整理成 Open WebUI 可识别的格式。
> Open WebUI 版本要求：0.6+（你的实例是 0.12.5，完全支持）。
> 生成日期：2026-10-30

## 目录内容

| 文件 | 技能数 | 内容 |
|---|---|---|
| `A-学术写作.zip` | 9 | 论文写作/去AI味/PaperSpine |
| `B-论文阅读.zip` | 6 | 论文分析/评审/答辩/近30天调研 |
| `C-工程开发.zip` | 43 | 工程全流程/调试/审查/前端/测试 |
| `D-文档办公.zip` | 3 | docx/pptx/pdf 真实文件产出 |
| `E-Prompt工程.zip` | 2 | prompt 优化框架 |
| `F-元工具.zip` | 71 | 67 种设计风格 + 造技能/找技能/记忆/IM 集成 |
| `skills/` | 134 | 同内容扁平目录（供"导入文件夹"方式使用） |

总计：**134 个技能**（全部为标准 SKILL.md + YAML frontmatter 格式）。

## 导入方法（二选一）

### 方式 A：导入 zip（推荐，最快）
1. 打开 `http://localhost:8080` 并登录
2. 左侧边栏 → **工作空间** → **技能**
3. 点 **创建** 按钮旁的小箭头（chevron 菜单）→ **导入**（Import）
4. 选择一个分类 zip，例如 `D:\AI\Skill-Library\OpenWebUI-Export\A-学术写作.zip`
5. 导入预览会列出每个技能的名称/ID/文件，逐个点 **创建**（Create）即可
6. 重复导入其他分类

### 方式 B：导入文件夹
1. 工作空间 → 技能 → chevron → **导入文件夹**（Import folder）
2. 选择 `D:\AI\Skill-Library\OpenWebUI-Export\skills\A-学术写作\` 这样的分类文件夹
3. 预览确认后逐个创建

## 导入后如何使用
- 技能默认 **私有**（仅自己可见）
- 在 **模型配置** 中给模型「添加技能」，或
- 聊天中直接输入 `/skills` 或 `@技能名` 触发
- 模型会通过 `view_skill` / `read_skill_file` 按需读取技能内容，不占满上下文

## 说明
- 技能名称取自各 SKILL.md 的 frontmatter `name` 字段（例如 paperspine5 的技能名是 `paper-spine`）
- 支持文件（scripts/references/assets/agents）已一并打包，导入后完整可用
- 若某个技能导入时报「名称已存在」：说明已在库里，选 **Replace**（替换）或 **Skip**（跳过）
- 若需重新生成此包：运行 `C:\Users\richa\AppData\Local\Temp\build_owui_export.ps1`