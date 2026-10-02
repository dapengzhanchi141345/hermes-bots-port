---
name: agent-toolbox-learnings
description: "核验并安装公众号推荐的第三方 agent 工具；已收录 Ekko Studio、agency-agents。"
version: 0.1.0
author: li-yanming, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, multi-agent, tooling, vetting, workbuddy]
---

# Agent 工具箱学习（第三方 AI agent 工具核验 + 安装）

用户（李彦明）关注的「小登登」类公众号常发「一句话部署 N 个 AI 员工」类工具测评，结尾都是「对 Hermes 直接说帮我装 X」。本技能存**已核验的工具条目 + 一套防吹的核验流程**，避免被情绪词带跑、盲装第三方脚本。

## When to Use
- 用户丢来一篇 AI 工具测评（公众号/知乎/小红书），要「学习」或「装一下」。
- 安装/跑第三方 agent 工具前，要先确认它真实、不碰现有 Hermes、落在哪。

Don't use：装 Hermes 官方自带插件/技能（那些不走第三方核验）。

## 核验流程（给任何「公众号推荐的工具」过一遍再装）
1. **验仓库真实性**：`curl -s https://api.github.com/repos/<owner>/<repo>` 读 `stargazers_count`/`forks_count`/`pushed_at`/`archived` —— star 数文章吹的多少，以 API 实读为准；`pushed_at` 看是否活跃；archived=true 别装。
2. **验安装方式**：读 README 的真实命令（`npm` / `pip` / `git clone + install.sh` / 桌面 App）。**先 dry-run**：agency-agents 用 `./scripts/install.sh --tool <x> --dry-run`；npm 先 `npm view <pkg> maintainers homepage version` 看谁发布。
3. **验落点 + 是否碰现有 Hermes**：安装前 `npm config get prefix`、看目标目录结构；安装后立刻 diff「我这套 Hermes 的运行时目录」有没有被改。第三方包落 `node_modules`/独立目录 ≠ 碰我（`{{HERMES_HOME_PARENT}}\AppData\Local\hermes\hermes-agent\venv`）。
4. **验声称的功能范围**：只信「能实际跑起来」的能力；「调 7 个 agent」前提是那几个 agent 真装在本机——先 `which claude codex opencode grok`。
5. **吹的成分标注**：区分「已核实事实」vs「文章说法」，回复里明写哪条没独立验到。

## 已收录工具（已核验）

### ① Ekko Studio（前身 Hermes Studio / Hermes Web UI）
- **仓库**：`EKKOLearnAI/hermes-studio`（GitHub 真）｜npm 包 **`hermes-web-ui` v0.7.23**｜官网 ekko-studio.xyz｜创建 2026-04，活跃。
- **是什么**：本地优先的多 agent 工作台 = 桌面 App + 本地运行时 + Web 控制台。把 **Hermes / Claude Code / Codex / OpenCode / Grok / Pi / DeepSeek Harness 7 套 agent 塞进一个面板**，群聊 `@agent` 路由、可视化工作流、文件浏览、模型/profile 管理、手机连。
- **安装**：`npm install -g hermes-web-ui && hermes-web-ui start`；也支持 Docker。维护者 bigjayz1990。
- **要点**：
  - 它跟「我这套 Hermes Agent」**不是一套**——它借用同名 "Hermes" 把 Hermes 当七把刀之一。装它 = 装独立 npm 包 + 起本地 Web 服务，不动我这套 Python 运行时。
  - 本机 node v22 / npm 10.9 已备，全局前缀 `{{WORKBUDDY}}\国外模型\hermes\node`（当前未装 hermes-web-ui）。
  - 「调 7 个 agent」需那几个 CLI 真装；本机 claude/codex/opencode/grok 均未在 PATH。

### ② agency-agents（虚拟 AI 公司 / 角色库）
- **仓库**：`msitarzewski/agency-agents`（GitHub 真）｜**实读 153,766 star / 24,807 fork**，2026-09-20 活跃，MIT。15 万 star 属实。
- **是什么**：200+「岗位 agent」定义文件，按部门分（engineering/design/marketing/sales/product/pm/testing/security/gis/game-dev/finance/research/healthcare/spatial-computing/specialized/paid-media/support…），每个带人格 + 工作流 + 验收标准。装进现有工具，**不新增运行时**。
- **安装**：`git clone` 后 `./scripts/install.sh --tool hermes`（也支持 claude-code/cursor/codex/gemini-cli/opencode/kimi 等 13 种）；或原生桌面 App（`brew install --cask msitarzewski/agency-agents/agency-agents`）。按部门装：`--division engineering,security`；按 agent 装：`--agent frontend-developer,ui-designer`。
- **坑（README 一致）**：① 别全选（token 烧在「出方案→评审→打回→再出」循环）；② OpenCode 运行时只注册 ~119 个，超出被静默丢（上游 bug）；③ `strategy/` 是策略剧本不是第 17 部门，装不了；④ 定义全英文。建议：先只装 1 个部门，给每个 agent 配模型（理解型喂强的、格式化杂活喂轻的），工作流对齐项目真实边界。
- **「207 个 agent」为文章/README 说法，本部门网络未独立验到确切数；部门数已验到。**

## 两者怎么选（给用户的取舍）
- 要**统一管理多个 agent 运行时**（后厨管理系统）→ Ekko Studio。
- 要**给现有 agent 批量加专职专家角色**（招一批厨师）→ agency-agents。
- 不冲突可叠：先 agency-agents 灌专家人格，再 Ekko Studio 把它们并排调度。

## Verification
- 回复里每条「事实」标注已核实 vs 文章说法。
- 装完任一工具：第三方目录 diff 通过（我这套 Hermes venv 未被改）；目标工具能实际 `start`/`list`。
- 装完 agency-agents：`./scripts/install.sh --tool hermes --dry-run` 先跑通再真装；确认落点是 `.hermes/skills` 而非覆盖现有技能。
