# Hermes Bots Port — 李彦明 bots 全量资产包（技能 + 工作流记忆 + 定时任务）

把本机 27 个 bot（1 个总调度 default + 26 个 profile）的全部**可学习资产**打包，
让另一台 Hermes 一键学会并安装。已脱敏：无任何 API key、手机号、微信账号、MT5 账户号。

## 目录结构

```
bots/
  default/            总调度 bot（装进 hermes home 根目录）
  chief/              金策·总管·首席操盘手
  risk-officer/       金策·风控官
  strategy-rd/        金策·策略研发
  it-edu/             码智君·信息科技
  bio-master/ … 22 个学科/职能专家 bot
  manifest.json       全部 bot 清单 + 描述
```

每个 bot 目录含（缺项说明没有对应资产）：
- `SOUL.md` / `profile.yaml` — 人设与 profile 元数据（群聊历史已剥掉，只留群名）
- `config.yaml` — 脱敏配置（api_key 全空，保留结构）
- `.env.template` — 环境变量清单（变量名全保留，值占位 `<FILL_ME>`）
- `memories/` — 深度工作流记忆（MEMORY.md / USER.md）
- `skills/` — 该 bot 的自定义技能（含 SOTA、工作流、脚本；官方 bundled 技能不打，目标 Hermes 自带）
- `cron/jobs.json` — 定时任务定义（金策 30min 循环、日更流水线等）

## 一键安装（路径自适应）

```bash
python install_bots.py [bots目录路径]
```

安装器自动：
1. **识别目标 hermes home**：环境变量 `HERMES_HOME` > 脚本向上找 > 常见位置，任何安装位置都认得出。
2. **路径占位符替换**：包内所有绝对路径已抽象成 `{{WORKBUDDY}}` / `{{HERMES_HOME_PARENT}}` / `{{JINCE_ENGINE}}`，
   安装时替换成目标机实际路径。三个占位符的落点可在 `paths.json`（与 install_bots.py 同目录，可选）里定制：
   ```json
   {"WORKBUDDY": "E:/workbuddy", "JINCE_ENGINE": "E:/GoldstrategyEngine"}
   ```
   不写 paths.json 就全默认（挂在 hermes home 下）。
3. **安全合并**：已有文件不覆盖（SOUL/profile/config/.env 缺才补），memories/skills 只补缺，
   cron/jobs.json 按 prompt 去重并集合并。跑多少次都不会破坏目标机现有数据。
4. 装完报告每个 bot 落了哪些新文件。

## 装完后必做（目标机自己的 key）

进各 bot 目录的 `.env`，把 `<FILL_ME>` 填成自己的 key（AGNES_* 系列等）。
config.yaml 里 `api_key: ''` 的空位同理。金策 3 个子 bot 各有专属 4 把 key 的槽位，按需填。

## 路径占位符说明

| 占位符 | 默认落点（目标机） | 含义 |
|---|---|---|
| `{{WORKBUDDY}}` | `<hermes home>/workbuddy` | 工作资料根（内容中心、金策宗师团、公众号） |
| `{{HERMES_HOME_PARENT}}` | hermes home 的上级目录 | 本机工具目录（.workbuddy/binaries 等） |
| `{{JINCE_ENGINE}}` | `<hermes home>/GoldstrategyEngine` | 金策交易引擎（需另装，MT5 终端+auto_run_cycle.py） |

金策交易引擎本身不在包里（含实盘逻辑与账户），需要的话让 strategy-rd bot 帮你重建或单独提供。

## 已脱敏清单（验收标准）

- 真 API key / sk- 长 token：0 命中
- 手机号（15684394135 及 sota 示例号）：全部 `<PHONE>`
- 微信 iLink 账号 / user_id：`<WEIXIN_ACCOUNT_ID>` / `<WEIXIN_USER_ID>`
- MT5 账户号 60137964：`<MT5_ACCOUNT>`
- 绝对路径：全部占位符化，无 `E:\workbuddy` 等残留
- 群聊历史日志：profile.yaml 里 `hermes-bots-groups` 段已剥除
