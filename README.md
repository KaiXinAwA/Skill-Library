# Skill Library — 个人 AI 技能市场

> 个人收集/整理的 Agent Skills 市场仓库，供 **ChatGPT 桌面版（Codex 插件市场）** 与 **Open WebUI** 同步使用。
> 内容由本地 `D:\Reborn\skill\Skill-Library` 维护并自动推送。

## 仓库结构

```
Skill-Library/
├── .agents/plugins/marketplace.json   # 市场清单（24 个插件）
├── agents/plugins/marketplace.json    # 同内容副本（双保险）
├── plugins/                           # 24 个 Codex 插件（.codex-plugin + skills + LICENSE）
│   ├── anti-defensive-writing/
│   ├── paper-skill/
│   ├── paperspine5/
│   ├── agent-skills/
│   ├── ...（共 24 个）
└── openwebui-export/                  # Open WebUI 导入包（6 个分类 zip + 说明）
    ├── A-学术写作.zip  (9 技能)
    ├── B-论文阅读.zip  (6 技能)
    ├── C-工程开发.zip  (43 技能)
    ├── D-文档办公.zip  (3 技能)
    ├── E-Prompt工程.zip (2 技能)
    ├── F-元工具.zip    (71 技能)
    └── README.md
```

## 接入方法

### ChatGPT 桌面版（自动同步）
1. 插件页 → **添加插件市场**
2. 来源填本仓库地址：`https://github.com/KaiXinAwA/Skill-Library`
3. **Git 引用留空**，**稀疏路径留空**
4. 加载后出现「Skill Library」市场，逐个安装即可

> 本地更新后 push 到本仓库 → ChatGPT 重新加载/刷新市场即同步。

### Open WebUI（半自动）
1. 工作空间 → 技能 → chevron → **从 URL 导入**
2. 贴分类 zip 的直链，例如：
   `https://raw.githubusercontent.com/KaiXinAwA/Skill-Library/main/openwebui-export/A-学术写作.zip`
3. 预览后逐个创建

> 或直接在仓库页面下载 `openwebui-export/*.zip` 再「导入」上传。

## 更新流程
1. 在本地 `D:\Reborn\skill\Skill-Library\GPT-Export` 整理好市场与技能
2. `git add . && git commit -m "..." && git push`
3. 各端按上述方式刷新

## License
各插件技能遵循其来源仓库的 LICENSE；本仓库组织文件（README/marketplace.json）MIT。