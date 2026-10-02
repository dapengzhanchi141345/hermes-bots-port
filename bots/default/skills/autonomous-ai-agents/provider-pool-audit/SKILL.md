---
name: provider-pool-audit
description: "审计 Hermes 多 provider 池配置：逐池探测 key 可用性、额度、fallback 链路完整性。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [providers, config, audit, custom-endpoints, fallback]
    related_skills: [hermes-agent]
---

# Provider Pool Audit

审计自定义 OpenAI-compatible provider 池（config.yaml `providers:` 多池 + `fallback_providers` 链）时的标准动作序列。本环境（`{{WORKBUDDY}}/国外模型/hermes`）已把 agnes 系 4 把 key 拆成 A/B/C/D 四池，每池独立 key + 独立端点，poolcfg 备份链命名 `config.yaml.backup-poolcfg-*`。

## Procedure

1. **定位配置源**：`config.yaml` 顶层 `providers:` 段是活的 provider 定义（每池带 `api_key`/`key_env`/`base_url`/`models`），`fallback_providers:` 段是故障接管链（list of `{provider, model}`，按序尝试）。`.env` 里的 `*_API_KEY` 是 provider 的 `key_env` 指向的实际凭证，config 内 `api_key:` 是快照——两者都查。
2. **逐池探测，不打印密钥**：每池一条 `curl -m 15 -X POST <base_url>/chat/completions`（`Authorization: Bearer $key`，`max_tokens: 8`）验证文本模型；图像模型池（model id 含 image）改打 `/v1/images/generations`，视频模型池注意端点可能是 `/v1/videos` 类——端点错了会返回 `invalid_request` 且提示正确路径，这是正常端点报错不是 key 错。key 从 `.env` 用 `grep '^VAR=' .env | cut -d= -f2` 提取，shell 变量里传递，全程不在输出/日志里 echo 出完整 key。批量探测写 bash 函数 `probe() { label/envname/base/model; }` 复用，不要写四段重复 curl。探测结果三类：正常返回（含 `choices`）/ 额度耗尽（`insufficient_user_quota` + 余额数字，属充值问题非配置问题）/ 429 限速（免费档撞墙，属限额问题非配置问题）。额度/限速是服务商侧状态，修配置解决不了，直接报告给用户。
3. **验证 fallback 链路完整性**：`fallback_providers` 每条目 `{provider, model}`——provider 名必须在 `providers:` 段存在，model 必须在该 provider 的 `models:` 清单里（`discover_models: false` 时 model 名是白名单硬匹配，拼错/漏配就整条链断裂）。文本池失败接管用同模型名的文本池。**`fallback_providers` 是文本/聊天对话的容灾链，只允许文本模型条目**——往里面挂 image/video 生成模型是语义错误（对话补位时 Hermes 会拿视频模型当文本模型调，产生无效请求或 400）。媒体生成（图像/视频）的失败路由不归它管，走各自的 media/video provider 机制（如 video_gen provider 插件）。检查方法：解析 `fallback_providers` 每条目，grep 对应 provider 的 `models:` 块确认 model 在列且为文本模型。
4. **改 config.yaml 前必备份 + 改后必验证**：备份命名 `config.yaml.backup-<tag>-YYYYMMDD_HHMMSS`（与既有备份链一致，如 `-poolcfg-`、`-3keys-`、`-bidir-fb-`），tag 写改动主题。改完全文件过一遍 `python -c "import yaml; yaml.safe_load(open('config.yaml',encoding='utf-8'))"` 确认 YAML 合法（`models:` 下 512000 这种大数字 key 值、中文注释、多行 fallback 列表都是易写坏点）。**新加的 fallback 条目要 gateway 重启才生效**——当前运行中的进程读的是旧配置，改完文件不等于改完运行时，要告知用户何时生效，不要把「文件改了」说成「已生效」。

## Account-level RPM bucket discovery (critical, 2026-09-30)

**Before assuming N dedicated keys = N independent RPM buckets, probe them CONCURRENTLY.**

The user's 12 'dedicated' Agnes keys across 25 profiles turned out to be only 3 independent accounts (3 underlying quota buckets) replicated as different keys. Same-account keys 429 simultaneously — rotating between them inside a fallback chain gives zero relief during a storm.

**Detection method:** fire 2-3 different keys at the same endpoint in parallel (e.g. `concurrent.futures.ThreadPoolExecutor` + `urllib.request` or `curl`). If keys X and Y both 429 in the same second, they share the same account bucket. If X is 200 while Y is 429, they are independent buckets. Report the actual number of independent accounts, not the number of keys.

**Implication for fallback pool design:**
- Adding 3 'idle' same-account keys to a hot profile's `fallback_providers` list is a **false safety net** — during a 429 storm the whole account is throttled, so the fallback targets are also 429. The chain exhausts without relief.
- True diversification requires keys from **different accounts or different providers** (e.g. a DeepSeek/OpenRouter key as the 4th layer). Until the user supplies one, state explicitly in the report: 'these N keys share M accounts; rotating within an account does not lift the RPM ceiling.'
- The fallback chain is still useful for **failover on 401/403 (auth) and connection errors**, just not for 429 (rate-limit) on the same account.

## YAML indentation pitfall when appending to `fallback_providers`

When a Python script appends new `- provider: …` entries to an existing `fallback_providers:` list in a profile's `config.yaml`, the new entries must carry the **same 2-space indent** as the existing list items (`  - provider: x`). A script that string-concatenates without preserving the leading spaces produces top-level `- provider:` entries, which are valid YAML syntax at the document root but **invalid inside the nested mapping** — `yaml.safe_load` fails on the first line after the break. Verify with `yaml.safe_load` immediately after writing; on failure, diff against the backup and fix the indent before restoring. One typo'd profile can cascade: if the broken file is loaded by the gateway at next profile rotation, the profile gets no provider and the next request 403s with 'no provider configured' rather than the expected 429-fallback.

## Pitfalls

- **Restore-from-backup 在 shell 里可能静默 no-op:** 用 `ts=$(ls -t backup_* | head -1 | sed ...)` 拼出备份名再 `cp "$backup" live` 时, 若 sed 因路径/中文/通配没命中, `$ts` 为空 → `cp` 目标变成不存在的 `config.yaml.backup-` (空后缀), stat 报错但脚本常没 `set -e`, 看起来"跑完了"实际 live 文件根本没被还原、仍处于写坏状态。**恢复前必做两步验证:** ① `echo "$ts"` 非空, ② `test -f "$backup"` 真存在, 再 cp; cp 后再 `yaml.safe_load` 回读 live 确认已恢复 (别假设 cp 成功 = 文件合法)。

- **多 profile 网关(multiplex gateway)下每个 routed profile 的回合只解析自己 profile 的 `.env`, 不继承顶层 `HERMES_HOME/.env`**(env_loader multiplex guard: 路由到 profile 时跳过进程级 dotenv, 凭证走 profile 域解析)。所以 profile config.yaml 里 fallback_providers / provider 段引用的共享池 `key_env`(如 AGNES_FLASH_API_KEY)若不写进**该 profile 自己的** `.env`, 整条 fallback 链在该 profile 下失效(只能靠 config 内 api_key 快照硬撑, 换共享 key 即断)。审计多 profile 环境时逐 profile 跑「config 引用的每个 key_env 都在该 profile .env 里」检查; 修复 = 把顶层共享池 key 追加进每个 profile 的 `.env`(先备份, 全程不打印密钥全文, 专属 key 的 profile 不动)。另: 业务侧 Python(如 ate venv)缺 yaml 模块 — 读 Hermes 的 profile/config 一律用 Hermes 自带 venv 解释器(`AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`), 别拿业务 Python 跑 `import yaml` 脚本。

### 逐角色独立 `.com` 兜底层配置 (每人各配一把, 不共享, 2026-09-30)
**"每人各配一把" = 1:1 角色隔离, 不是共享池。** 4 个角色(总调度 default / chief / risk-officer / strategy-rd)各给一把独立的 `.com` 端点 key, 配到**各自角色 profile 的 `.env` + `config.yaml` 命名 provider 块 + fallback 链尾位**:
- 每 profile 的 `.env` 加一条专属变量(如 `AGNES_KEY_DCOM`/`AGNES_KEY_CHIEF_COM`/`AGNES_KEY_RISK_COM`/`AGNES_KEY_RD_COM`), 值=该角色那把 `.com` key 全文。
- 每 profile 的 `config.yaml` `providers:` 段加一个命名 provider 块 `agnes-com-{角色}`(base_url=`https://apihub.agnes-ai.com/v1`, key_env 指向本角色变量, models 列 3.0-flash 等文本模型)。
- 每 profile 的 `fallback_providers` 链**尾位**追加该命名块(主池 `.cn` → 共享 `.com` 池 `agnes-main` → 本角色专属 `.com` key), 作最后独立兜底。
**1:1 的理由(写死):** 4 把 key 正好 4 角色, 各锁各的保住**独立 RPM 桶** — 正是上轮"12 把 key 其实 3 个账号共享桶一起 429"的教训反着做。若 4 把 key 其实同属少数账号, 1:1 隔离也是唯一能避免"再变回共享桶"的配法。`.com` key 与 `.cn` 主池**不互认、禁混池**, 只在主池+共享池全 429 时才切到本角色专属那把。
**配完必验(不信"配好了"自报):** ① 逐角色 grep `.env` 的 key_env 值尾 4 位, 与该角色 key 本体尾 4 位逐字节对上(防脚本拼 expect 字典截断错位造成假 MISMATCH); ② 逐 profile 用 Hermes venv `yaml.safe_load` 读 `config.yaml`, 断言命名块在 `providers:` 里 + `key_env` 指向对 + `fallback_providers` 尾位是该命名块 + YAML 全合法; ③ gateway restart 让新 provider 生效, 再 `hermes -p <角色> chat -q "..." --max-turns 1` 冒烟一条(主池 200 正常时 `.com` 兜底层不会真触发, 不报错即配通)。
**YAML 插入踩坑(写坏过一次):** 往嵌套 `providers:` 段 / `fallback_providers:` 列表插新块时, 模糊匹配(找 `key_env` 行后插块)易插错缩进或插到 `video_gen` 等无关段 → `yaml.safe_load` 报错。**姿势: 先备份(`config.yaml.backup-<tag>`), 读真实段落精确文本再插, 插完立即 `yaml.safe_load` 验证, 失败 diff 备份定位坏行修缩进, 不留下"fallback 引用了不存在的 provider 名"的坏引用。**
- **改 Hermes 的 config.yaml 走不了 patch/write_file 工具**：安全敏感文件被拒（'Refusing to write to Hermes config file'）。一律用 `hermes config set KEY VALUE` CLI 改（含 `video_gen.provider`、`video_gen.model`、`plugins.enabled`、`fallback_providers` 等），改后 grep 回读验证。**注意 `hermes config set` 对列表值**：单字符串参数会被存成标量（如 `plugins.enabled: video_gen/agnes`），而发现逻辑要求 YAML 列表——列表值要传 JSON 字符串 `'["a/b"]'`，改完必须回读确认是 list 不是 str。

- **bash 多变量拆 `label:env:base:model` 这类用 `:` 分隔的字符串**，其中 base_url 本身含 `:`（`https:`），`${var%%:*}` / `${var#*:}` 解析会切碎 URL——探测函数参数必须逐个位置传参（`probe "$1" "$2" "$3" "$4"`），别在 shell 里做多层字符串切片解析 URL。本会话第一次批量探测就踩了这个坑，输出全是空，重写才通过。
- **config 内 `api_key:` 快照与 `.env` 实际值可能不一致**：改 key 时通常 `.env` 先改、config 内快照滞后（或反过来），两边都要 grep 确认同一把 key。本次审计发现两边一致（4 把），但规则是要查两边，别只看一处。
- **`insufficient_user_quota` 和 429 都是「服务商侧状态」，不要写进 fallback 链路修**：额度归零、免费档限速是充值/限额问题，改 config 救不了。报告给用户时明确区分：配置可修（fallback 断裂、model 白名单漏配）vs 充值/限额需用户操作（B 池 ¥0、D 池 429）。
- **gateway 进程不热加载 config.yaml 的 fallback 段**：改完 `fallback_providers` 后当前会话仍在用启动时读入的旧链。验证新链是否生效要么重启 gateway 要么看下一轮请求的 errors.log 是否走了新 provider。不要假设「文件写进去了 = 运行时就生效」。
- **日志里查 fallback 是否真接管过**：grep `logs/errors.log*` 找 `rate limit on custom and all fallbacks exhausted` / `connection error on ... and all fallbacks exhausted` 这类 WARNING——它们说明 fallback 链已经走完没接住（链断/全池 429），是配置问题的硬证据；找不到这类行只说明没触发到全链失败，不代表配置对。

## 响应延迟排查（用户报「bot/群聊反应慢」时先走这条）

瓶颈常不在模型本身，而在 DNS 抖动、限流重试、上下文膨胀、工具多轮往返叠在一起。**先诊断再开方**：
1. **读 profile 日志定瓶颈**：`profiles/<name>/logs/agent.log` 里每行 `API call #N: ... in=<N> out=<N> latency=<S>s cache=<X>/<Y> (<Z>%)` 是量化锚点——`cache%` 高（>90%）说明前缀缓存已在生效，慢就是 context 体积本身；`latency` 远超 token 量该有的值（如 65k in 只花 18s 是正常，55s 就异常）+ `cache%` 正常 = 传输层（DNS/TCP）在拖。`logs/errors.log` 里 `getaddrinfo failed` / `APIConnectionError` = DNS 解析挂；`429 免费用户限速` = 免费池 RPM 撞顶（见上方 429 节，降 `delegation.max_concurrent_children` / 停 `orchestrator_enabled` 止血）。
2. **DNS 兜底（本机已知痛点）**：github.com 已有 `resolve-dns.bat`（aliyun DoH）方案；agnes 端点（api.agnes-ai.cn / apihub.agnes-ai.com）偶发 `getaddrinfo failed` 是同类问题——先确认 2-3 轮重试能否恢复（curl 验活多轮），再决定是否把 agnes 域名加进 `nameResolution.provider` 的 DoH 列表，别一把认定"网络坏了"。
3. **提速方案排序（按性价比）**：DNS 兜底 + 限流错峰（消 50s 级挂起，最大一笔）→ 上下文瘦身（`context_length` 降到位、更早触发压缩、系统提示/skills 索引用两级分类索引替代全量列表）→ 动态工具加载（群聊场景 60+ 工具裁到 10-15 个高频，其余走 `tool_search` 按需拉，省 1000-3000 tokens/请求且选工具更准）→ 简单问题走小模型路由（寒暄/简单确认走 2.0/2.5-flash，复杂研判才 3.0-flash）→ 高频重复问法加语义缓存（命中时 ~20s → <1s，工程量大放最后）。
4. **provider 前缀缓存是自动的**：OpenAI-compatible 端点对重复前缀自动复用 KV cache，把静态内容（system prompt/工具 schema）排前、动态内容排后即可最大化命中——改任何 prompt 组装顺序前先量一次 `cache%`，改后再量一次，别凭感觉说"变快了"。

## 官方文档取参数（媒体/视频模型配置类任务）

- Agnes 文档站是 Mintlify/Next.js SPA，curl 页面只能拿到导航壳；**模型参数细节在 wiki 子站的 `.md` 端点**：`https://wiki.agnes-ai.cn/llms.txt` 给完整页面索引，每页可取 `https://wiki.agnes-ai.cn/zh-Hans/docs/<page>.md`（干净 markdown）。国际站镜像同理（agnes-ai.com / wiki.agnes-ai.com）。配置多模型参数差异类任务先抓 llms.txt 定位专用文档页，再逐页取 .md，不要只抓 overview。
- **同厂商多个模型 API 参数可能完全不通用**（如 agnes-video-v2.0 用 `num_frames`/`width`/`extra_body.mode`，agnes-video-2.5 系列用 OpenAI-Videos 的 `mode`/`seconds`/`size` 档位且 400 拒收旧字段；Flash 版又限 `size=720P`/参考图≤5/不支持视频参考）：写 provider/工具配置时**每个模型独立组参，互不复用字段**；先用真实 key 对每个模型端点发最小请求实测（`/v1/videos` 建任务 + 轮询端点），拿到参数校验通过/失败的实际响应再定配置，文档+实测双确认。
