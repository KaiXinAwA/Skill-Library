# 来源与版本记录

本目录原为 git 子仓库，2026-11-13 改成普通目录并入 Skill-Library 主仓库（原因：原 .gitmodules 缺失，成了孤儿子模块，内容只存在本机、进不了备份）。

- 上游仓库：https://github.com/hardikpandya/stop-slop
- 原 commit：8da1f03（2026-03-18，"Add false agency rule: no inanimate objects performing human actions"）
- 许可：MIT（见同目录 LICENSE，Copyright (c) 2025 Hardik Pandya）
- 本地改动：SKILL.md 的 description 末尾追加了中文路由说明（英文散文专用；中文走 doubao-human-signal；学术走 academic-humanizer / anti-defensive-writing）
- 原 .git 备份：D:\Reborn\99-cold\stop-slop-git-backup-20261113\git

## 以后要跟上游更新

不做逐行手工对比。临时拉一份上游下来比对即可：

1. 在临时目录 git clone https://github.com/hardikpandya/stop-slop.git
2. 比对：git diff --no-index <clone目录> <本目录>（或用 VS Code 文件夹对比）
3. 只挑需要的改动搬过来，保留 SKILL.md 里那段中文说明