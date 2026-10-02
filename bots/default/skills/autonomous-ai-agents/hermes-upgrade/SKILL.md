---
name: hermes-upgrade
description: "Upgrade Hermes Agent here; Windows pip lock-recovery loop."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, upgrade, windows, pip, uv, file-lock]
    related_skills: [hermes-agent, hermes-agent-skill-authoring]
---

# Hermes 升级/更新

把本机 Hermes Agent 升到最新版。覆盖两种安装方式（pip / git），以及 Windows 上因运行中进程占用旧 .pyd 导致 uv 卸载失败的恢复循环。

## 何时用

- 用户说"升级到最新版本 / update Hermes"。
- `hermes update --check` 报告有新版可用。

## 步骤

1. **摸清安装方式**（不装任何东西，纯探测）：
   - `hermes --version` — 输出含版本、Install directory、Install method（`pip` 或项目目录）。
   - `which hermes` — 拿到 venv 里 `hermes` 的真实路径，从它推出 `venv/Scripts/python.exe`。
   - `hermes update --check` — 最便宜的检查，不安装。
2. **按安装方式分路**：
   - 提示 `Run 'uv pip install --upgrade hermes-agent'`（pip 安装）→ 第 3 步。
   - git checkout（安装目录有 `.git`）→ 直接 `hermes update --yes`；Windows 上检测到其他 hermes.exe 运行中会拒绝，可加 `--force`。
3. **pip 升级**：
   ```bash
   uv pip install --upgrade hermes-agent --python <venv>/Scripts/python.exe
   ```
   必须显式 `--python` 指向 Hermes 自己的 venv，否则装到别的解释器里等于没升。
4. **Windows 文件锁恢复循环**（见下节，Windows 下大概率要跑）。
5. **验证**：`hermes --version` 显示新版本且 Install method 不变；`<venv python> -c "import hermes_cli, hermes_constants"` 无报错。两步都过才算完成。
6. **收尾**：正在跑的 Hermes 进程还是旧代码。告知用户要**完全关闭 Hermes 桌面应用再重开**才生效（关窗口≠退出）；可选 `hermes doctor` 体检。用大白话汇报结果，不堆英文术语。

## Windows 文件锁恢复循环

机制：正在运行的 Hermes 桌面/gateway/node 进程持有旧版二进制扩展（jiter、_cffi_backend、cryptography _rust.pyd、watchfiles _rust_notify、mypyc、charset_normalizer 等 .pyd）的打开句柄，uv 卸载旧包时报 `failed to remove file ... 拒绝访问 (os error 5)`，每失败一次换下一个被锁文件——所以别一次报错就停手。

恢复手法（比杀进程安全得多）：

- 被锁文件用 **rename** 挪开即可：`python -c "import os; os.rename(p, p+'.orphan')"`。Windows 允许 rename 正被占用的文件，不影响运行中进程。
- 每轮从 uv 报错里 grep 出 `failed to remove file <路径>`，挪开该文件，重跑安装，循环到 exit 0。整条循环约 12 行 bash，现场拼即可；上限设 15 轮，超限停下人工看。
- 顺手清理 site-packages 里 `~` 开头的 uv 失败残留目录、以及缺 `RECORD` 的旧 dist-info（会留 "incomplete environment" 警告，不影响运行）。
- **坑：半新半旧环境**。uv 中途失败后旧包已卸一半，`import hermes_cli` 可能仍能过（残留文件够导入）——不要据此宣布没事，必须循环装完 + 第 5 步双验证。
- **坑：别杀 Hermes.exe 解锁**。执行升级的 agent 本身就是 Hermes 进程，杀进程会把自己连坐断掉。rename 法全程不需要动任何进程。

## 验证判据

- [ ] `hermes --version` 版本号前进、Install method 未变（pip 还是 pip）。
- [ ] venv python 能 import hermes_cli / hermes_constants。
- [ ] 已告知用户"完全退出桌面应用再重开"生效步骤。
