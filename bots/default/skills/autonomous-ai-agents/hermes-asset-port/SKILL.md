---
name: hermes-asset-port
description: "Use when 打包 Hermes bot/专家资产给另一台 Hermes 学习或迁移。"
version: 0.1.0
author: li-yanming, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [profiles, packaging, sanitize, port, expert-teams]
    related_skills: [agent-team-to-bot-fleet, mt5-multiagent-trading]
---

# 打包 Hermes 专家资产给另一台 Hermes 学习

用户说「把 XX bot 的数据打包，加上 YY，我要让另一个 Hermes 学习」时走本工序。产出 = 一个目录 + 同名 zip，按资产块分子目录，附 README 教对方接机。

## 范围界定（先查清再动手）
- 用 `search_files target=files pattern=*关键词*` 扫全 workbuddy 找资产根；用户点名的资产可能有散落的共享工作区（如金策宗师团在 `{{WORKBUDDY}}\金策宗师团\`，profile 在 `{{WORKBUDDY}}\国外模型\hermes\profiles\`）。
- 每块资产先 `ls` + `du -sh` 摸底体量，把「用户点名的内容线」与「同目录混排的其他内容」分开——成品目录常混多线稿件（如山海拾珍里考研英语 + 岐黄医典），按内容筛选而非整目录拷。

## 每个 profile 拷什么（不是整目录）
profile 目录 30+ 项里只有这些有学习价值，其余全是不透明噪声：
- **拷**：`SOUL.md`、`profile.yaml`、`config.yaml`（脱敏后）、`memories/*.md`（不含 .lock）、自定义技能目录（`golden-strategy-*`、`calc-bazi`、`*-sota` 等——看 `skills/` 一级目录，bundled 类目目录如 apple/creative/github 不拷）、`cron/jobs.json`。
- **不拷**：`.env`（真密钥）、`state.db*`、`projects.db`、`sessions/`、`cache/`、`backups/`、`logs/`、`auth.lock`、`*.etag`、`audio_cache`、`image_cache`、`sandboxes/`、`pending/`、`runtime/`、bundled 技能类目。
- 共享技能单列一块（如 `devops/` 整个类目 + 根级数据 json），不复制进每个 profile。

## 脱敏与密钥安全
1. **先认指纹再决定脱敏深度**：本机 config.yaml 的 `api_key` 常被写成指纹形式（`sk-xxx...yyyy`，源文件即如此），脱敏正则置空后 grep 仍会命中指纹——**指纹不算泄漏，真 key 才要拦**。
2. 脱敏：对每个 profile 的 config.yaml 跑 `re.sub(r"(?m)^(\s*api_key:\s*)'.*?'", r"\1''", txt)` 再写进包；`.env` 直接不拷。
3. **外发前双向扫描**：
   - 真 key 拦截：`grep -rnE "sk-[A-Za-z0-9-]{20,}" <包>` 须零命中（指纹带 `...` 会自然排除）。
   - 反向核查：确认包内 config.yaml 的 api_key 全为 `''` 或既有指纹，别只正向扫就收工。
4. **排除运维脚本**：资产根下 `_` 前缀脚本（`_dist_keys.py`/`_keymap.py`/`_probe_keys.py` 这类 key 分发/探测工具）是内网运维件，不进外发包；README 注明哪些路径不在包内（如交易引擎 `{{JINCE_ENGINE}}`）、对方需自行配 key。

## 内容筛选坑
- **二进制文件不进 `grep -rl` 结果**：按关键词筛内容线的成品时，`grep -rl` 只报 md/html 文本命中，PNG 封面等二进制全漏。补救：按命名规律用 glob 补拷（`cp */*关键词*封面*.png`），再清掉混入的其他线文件。
- 多行 Python 脚本走 `write_file` 落盘再跑，不走 heredoc（Windows 中文路径 + 嵌套引号断行坑）。

## 交付
- 包结构：`<名>_学习包/` 下按 `01_资产A/`、`02_资产B/` 分子目录 + `README_学习包说明.md`（列目录内容、接新机步骤、脱敏说明、包外依赖路径）。
- `python3 shutil.make_archive` 出同名 zip 放在包同级；zip 用 `MEDIA:` 绝对路径发给用户，包大小在报告里写明。
- 对方接机三件事：拷 profile 目录（或不建 profile 直接读技能学习）、config.yaml 空 key 位填对方 key + .env 配 key_env 变量、补包外引擎/数据路径。

## Verification
- 包内 `grep -rnE "sk-[A-Za-z0-9-]{20,}"` 零命中且 config.yaml api_key 全 `''`/指纹；README 存在且含接机步骤；`du -sh` 总量符合预期（profile 级学习包通常 <10M，超了多半误拷了 bundled 技能或缓存）；成品块里混入的其他内容线文件已清零。
