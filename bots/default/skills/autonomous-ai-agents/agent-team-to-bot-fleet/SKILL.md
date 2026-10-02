---
name: agent-team-to-bot-fleet
description: "Use when 把一批外部专家团/智能体库批量转成 Hermes 专用 bot profile。"
version: 0.1.0
author: li-yanming, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bot-fleet, profiles, workbuddy, expert-teams, model-pool, batch, bot-mode]
    related_skills: [expert-matrix-router, provider-pool-audit, hermes-agent]
---

# 外部专家团 → Hermes 专用 bot 车队

把一批外部 agent/expert 团队（如 workbuddy 39 专家团/178 子代理）批量转成 Hermes profile（= bot，Bot Mode 原生）的**标准工序**。每个 bot 囊括对应专家团全部功能，且**成本可控**。本技能只管「怎么批量落地」；「任务该路由到哪个专家」用 `expert-matrix-router`；模型池本身的探测/审计用 `provider-pool-audit`。

## When to Use
- 「把 XX 专家团/智能体都做成专门的 bot」类需求。
- 要批量创建 N 个 Hermes profile 并继承共享模型池。
- 把第三方 agent md（codebuddy/workbuddy plugin 的 `agents/*.md`）转成 Hermes 惰性技能。
- 「给我建一个 XX 学科的 bot，跟其他教学 bot 对齐」类单 bot 新增需求（无 workbuddy 源，走 11 节单 bot 工序）。

## 设计原则（先定，再动手）
1. **聚类而非 1:1**：功能重叠的团先合并（阅卷官并入对应学科主团、排盘专家并入玄学主团），砍掉闲置+降成本。别 39 团硬做 39 bot。
2. **席位不拆独立进程**：多席团的各成员 persona 收进技能的 `references/` **惰性加载**（单任务只 `skill_view` 1-3 个），不每席起一个 profile。主理人 SOUL 管「路由表+调度规则」。
3. **一个 bot = 一个 profile**：Bot Mode 的 bot 就是 profile。profile 自带专属 SOUL/模型/记忆/技能/头像，桌面 Bots 页自动入册，支持 @互聊/群聊/Routines。
4. **与现有运行时拓扑正交**：已有专职 runtime profile（如金策 chief/risk-officer/strategy-rd）不动；新 bot 只作「功能入口/问答层」，SOUL 写明实盘动作找对应 runtime bot，避免双入口打架。只读方法论文料（SOTA 切片/参考资料）可进 runtime profile，但绝不新增交易入口或写动作。
5. **依赖技能只装实际引用的**：外部技能库（230 个）不全量搬，按各团 `SKILL.md` 正文引用的名字挑装（teaching-visualization、calc-bazi、各 grader 引擎等）。

## Procedure

### 1. 探源（机读全量）
- 找机读元数据（如 workbuddy 的 `05_专家元数据.json`：dir/displayName/teamSize/members/embeddedSkills）+ 活体目录（`agents/*.md`、内嵌 `skill-*/`）。人读手册只在深挖某团时看。
- 统计体量：各团 `du -sh` 去 avatars 后总量；确认 `agents/` 与内嵌 `skills/`/`skill-*` 的落点。

### 2. 写生成器（一个脚本，别手工逐个建）
- 读元数据 json + 活体 `agents/*.md` → 输出每个 bot 目录：
  - `skills/<bot>/SKILL.md`：路由铁律 + 成员 persona 清单（references/）+ 惰性加载用法 + 安全硬规矩。
  - `skills/<bot>/references/<成员md>`：逐团复制 agent md。
  - 内嵌 `skill-*/`：复制到 `skills/<bot>/` 一级目录（**Hermes 只认一级**）。
  - 共享依赖技能：按需 `shutil.copytree` 进 `skills/<共享技能名>`。
- 安全纪律：UTF-8、相对/forward-slash 路径传参、子进程禁 emoji、GBK 环境注意。

### 3. 批量建 profile（CLI，不手写目录骨架）
```bash
export HERMES_HOME="<你的hermes根>"
for b in <24个bot名>; do
  hermes profile create "$b" --no-skills --description "<中文一句话>" >/dev/null 2>&1
done
hermes profile list   # 复核全在册
```
- `--no-skills` 避免灌 6.9M 默认技能进每个 bot（只装需要的）；`--description` 给 kanban 分解器路由用。
- 交互确认坑：`hermes profile create/delete` 默认要交互确认；脚本批量用 `--no-skills`/`--yes` 等 flag 或确保非交互。误触的测试 profile 用 `hermes profile delete <name> -y` 清。

### 4. 配模型池（每个 profile 的 config.yaml + .env）
- 每个 bot 复制一份「共享模型池」config：单 key 主池 + 双 key 轮询池 + `fallback_providers` 兜底（与既有 chief 同构）。**key 值从一个已知好的 source config 用正则 `grab(pool)` 提取后写入模板**——绝不把完整 key echo 进输出/日志/聊天。
- 主池 provider 用独立名（`agnes-<bot>`）指向共享端点 + `key_env`，`.env` 补该变量（从 default `.env` 取值）。
- **池名隔离 vs key 复用**：每 bot 池名独立（不串到既有 chief 池），但 `base_url`/`key_env` 可共享；`fallback_providers` 只挂文本模型。
- 落地细节与坑：见 `references/model-pool-per-profile.md`。

### 5. Bot Mode 标记（进桌面 Bots 花名册）
- 每个 bot 的 `profile.yaml` 追加：
  ```yaml
  ui_meta:
    hermes-bots: {}
  ```
  空块即可标记「Bot-Mode-managed 安装」，桌面 Bots 页自动收录。缺它 bot 不进册。

### 6. 冒烟验收（真跑，非纸面）
- 挑 1 个带内嵌引擎的 bot + 1 个学科 bot，各 `hermes -p <bot> chat -q "入口提问"`，确认：①自动加载成员 persona ②内嵌技能/引擎可用 ③安全免责自动带上（命理→「仅文化参考」、教学→「以当地官方为准」）。
- `hermes profile list` 全在册、模型池继承、`ui_meta` 标记齐全。
- **验证通过才算交付**，不要把「文件写进去了」说成「生效了」。

## 派单调度全车队 (kanban = 真正的跨 bot 通道, 实跑验证)
fleet 建成后用户会问"总调度 Hermes 能不能调度所有 bot"——能, 但只有一条通道真能跨 profile 派活: **kanban 派单**。`delegate_task` 生的是**当前 profile 的临时克隆子代理**(继承调用方 key/工具/提示词, 干完销毁), 它**叫不动**任何命名专家 bot——这两条常被混为一谈, 用户也会据此质疑"它说能调度全部专家团是吹的"。分清: 要跨 bot = kanban; 要临时并行算数/研究 = delegate_task。

### 派单 (Hermes 自己派, 或用户让 Hermes 代派)
1. 核对 assignee: `hermes kanban assignees` 列全部在册 profile (调度器视角), 名字必须与 `profiles/` 目录实况**精确一致**, 调度器静默丢弃未知名, 不报错。
2. 建卡: `hermes kanban create "任务标题" --assignee <profile> --body "给 worker 的完整自足说明(它看不到主会话)"`。**坑: 标题是位置参数, 不是 `--title`**——`hermes kanban create --title X` 直接报 `unrecognized arguments: --title`; 先 `hermes kanban create --help` 核字段。`--body` 写全背景+验收标准, worker 只读 body 不读主会话。
3. 调度器拉起: 网关内 kanban dispatcher (`kanban.dispatch_in_gateway: true`, 60s tick, Windows 计划任务常驻) 认领 ready 卡 → spawn `<profile>` worker 进程 → 干完落卡。
4. 收结果: `hermes kanban show <task_id>` 看 `status`/`Latest summary`/`Events`/`Runs`。done + summary 有实质内容才算交付, 不凭"建卡成功"。
5. 冒烟验证整链 (每次改 fleet 后做一次): 派一张单 token 量的轻卡给某个专家 bot (`--body "一句话回答 X, 不要用工具"`), 等 ~70s (一个 tick) 后 show, 确认 ~40s 级 claimed→spawned→completed。

### 路由表 (活→派给谁) 单一事实源
落 `{{WORKBUDDY}}\内容中心\知识库\Hermes_bot派单路由表.md` (内容中心铁律目录): 一张 `任务类型 → assignee` 对照 + 派单铁律 (专属 key 消耗/429、任务制非持续对话、金策 3 岗内部边界仍归 `金策宗师团_管辖分工_v2.md`)。改路由先改这张表, 别在聊天里即兴路由。SOTA 升级/新增坐席导致 bot 能力面变化时, 同步扩充该 bot 路由行的任务类型词 (如「中医太极养生(八段锦进课堂/九体体质档案)」)。

### 边界 (提前说清, 免得用户踩坑以为是 bug)
- **派单消耗目标 bot 的专属 key**; 专家 bot 里分组共用 key 的组, 免费池 RPM 撞顶时它派出去的活会 429 (诊断法见 `mt5-multiagent-trading` 的 429 节, 通用)。
- **kanban 派单是任务制**: 一卡一活、干完回传, 不是持续对话。要追问就群里 @ 或再派后续卡。
- **专家 bot 不由 Hermes 命令链管辖** (只有金策 3 岗是被总调度派单的下级); 专家 bot 经 kanban 是"借调干活", 干完即回传, 汇报人还是 Hermes。别把"经 kanban 能借调"讲成"专家 bot 归 Hermes 管"。

## 11. 单 bot 新增（无 workbuddy 源，手工建）

用户说「建一个 XX 学科的 bot，跟现有的对齐」且该学科不在 workbuddy 39 团包里时，不走生成器，直接复制同域 bot 做基线、手工补内容。

### 11a. 找基线 bot
同学段/学科域选一个已建好的 bot 做模板（K-12 教学学科→`physics-master`；工具类→`tianji-ge`；量化→`chief`）。读它的：
- `SOUL.md`（复制模板结构，改标题/说明/安全规矩）
- `profile.yaml`（改 `description`、`display_name`；`ui_meta.hermes-bots: {}` 必须保留）
- `config.yaml` + `.env`（同组共用 key，见 11b）
- `skills/<bot>/SKILL.md` + `references/` 结构（persona 数量/命名格式照搬）

### 11b. 复制模型池 + 专属 key（同组共用，不新配）

同一功能组（见花名册 9 组 key 分配表）共享一把 key。步骤：
```python
# 从同组已有 bot（如 geo-master）复制 .env，改专属变量名
cp profiles/geo-master/.env profiles/pe-master/.env
sed -i 's/AGNES_KEY_GEO_MASTER/AGNES_KEY_PE_MASTER/' profiles/pe-master/.env
# 复制 config.yaml，把池名从 agnes-geo-master 改成 agnes-pe-master
sed 's/agnes-geo-master/agnes-pe-master/' profiles/geo-master/config.yaml > profiles/pe-master/config.yaml
```
池名（`agnes-<bot>`）每个 bot 独立；`key_env` 变量名改为本 bot 专属名；`.env` 里 4 把共享池 key（FLASH/REASON/MEDIA/MAIN）直接复用同组 bot 的值。

### 11c. 手工建 skills/
- `skills/<bot>/SKILL.md`：frontmatter + 路由铁律 + 成员 persona 清单（references/）+ 惰性加载用法 + 安全硬规矩（对照 physics-master 模板）。
- `skills/<bot>/references/<persona>.md`：每个成员 1 个 md，结构：定位 / 专长 / 交付物规范 / 硬规矩。K-12 教学主团标准 8 席（主理人 + 各功能切片 + 阅卷官）；有全名录/弹药库性质的内容单独一个 references 文件（如 `pe-traditional-sports-catalog.md`），不塞进 persona。
- `skills/<bot>-sota/SKILL.md`：web_search 拿真实 URL + 访问日期 → 写 3-5 条可核查条目 + 安全红线 + 落地升级项清单；检索被拦时标注「联网被拦，落地前核当年官方原文」，不编造 URL。
- `skills/teaching-visualization/`：K-12 教学 bot 必须装；它不在共享 skills/ 根目录，从已有教学 bot（如 physics-master）的 `skills/teaching-visualization/` 直接 `shutil.copytree`。
- 用户要「一项不能落下/全量清单」（如中国传统体育全部项目）时：清单独立成一个 references 文件（不进 persona，避免上下文膨胀），文件开头写「补充追加不删存量」，主 SKILL.md 路由铁律加一条「涉该类任务先读清单定位条目再配 persona」；清单条目去重（同类异名合并，如「高跷/踩高跷」）——冒烟时 bot 会自己报出重复项，交付前修净。
- 头像：PIL 生成 512×512，`ImageDraw` 画字符+副标题，`C:/Windows/Fonts/msyh.ttc` 字体，保存 `assets/avatar.png`。

### 11d. 路由表 + 花名册同步（必须同时改，漏一个就断）
- `{{WORKBUDDY}}\内容中心\知识库\Hermes_bot派单路由表.md`：在对应学科行后面加新 bot 行。
- `{{WORKBUDDY}}\内容中心\交付\<月份>_专家团Bot化\02_专家Bot花名册.md`：① 学科主团表加行；② 9 组 key 分配表把新 bot 归入对应组；③ 如有 SOTA 技能，加 SOTA 行。

### 11e. 冒烟
`hermes -p <bot> chat -q "<本学科问题>"`，确认：persona 自动加载、SOTA 技能被引用、安全免责带上、回答不是 fallback 出的（检查无 AGNES_KEY 缺失报错）。

### 11f. 跨域理论坐席（用户要求把 A 域理论深度融入 B 域 bot 时，如「中医养生×太极/心理学×课堂进体育 bot」）
- **找既有理论深库，不复制内容**：用户内容中心常已有沉淀的理论文档（如 `{{WORKBUDDY}}\内容中心\知识库\中医太极深度融合_理论内核.md`）。新 persona 文件头加一行「理论深库指针」指向它（注明行数/章节供定位），persona 本体只写**课堂/任务落地切片**；讲标书级理论时让 bot 先读深库文档，单任务只读 1-3 节。整块复制会让两个文档漂移。
- **文化层/证据层双红线**（中医类、命理类理论进教学 bot 通用）：阴阳/五行/经络/气血等传统概念只作「文化溯源引注」，不断言生物机制；机制表述一律用现代可测变量（HRV/姿态角/呼吸节律/功能系统互养互制），每式动作配「白话翻译」。诊断类措辞红线：体质/分型只说「偏颇倾向+建议方向」，异常体征转介校医/就医；教学用功法只教官方推广版/团体标准版，不传非规范流派。
- **跨界 bot 边界写进 persona 尾**：本域只管自己场景（体育 bot 只管运动/课堂），内容线/科普线归哪个 bot 明写一句（如「中医科普内容线归岐黄医典 bot，互引不复制」），呼应设计原则 1「按职能拆片不整块塞」。
- **升级全套同步点**（新增坐席或 SOTA 升级后漏一个就断）：主技能路由铁律加一条触发规则 → 成员 persona 清单加行 → SOUL 域描述+安全规矩 → profile.yaml description → 派单路由表对应行扩充 → 花名册席位数字 → 验收报告追加 PASS 行。最后跑一轮针对新坐席的冒烟（问一个必须引用新 SOTA 分片/新 persona 才能答好的题，确认逐条带源）。
- **同类席位合并纪律**：新坐席与原席位功能相邻（如「运动心理」与「教育心理学×心理健康」）时，新 persona 头明写边界分工句（本席位管课堂学习/发展/促进，该席位管竞赛情境调控），路由铁律里两者触发词各归各位，避免 bot 读错人。同一域连续加多个理论席位（心理/中医/视力…）时不另起新域，进同一 SOTA 技能的同一章追加子节，验收报告按「域·子主题」加行。
- **政策+机制+行为三层进 persona**：卫生/健康类深化（近视防控、脊柱侧弯等）按「政策锚点（带文号/发布日期/来源 URL）→ 机制一句话（为什么有效，如自然光-多巴胺、远眺-调节放松）→ 行为清单（可进教案的口诀，如 20-20-20/一尺一拳一寸）」三层写，教案交付时 bot 能一次带全三层。教师边界红线固定写：记录+反馈+转诊，不诊断。

---

## SOTA 全网增强波次（每个 bot 按功能域升级到最新方法论）
fleet 建成后的二期工序：给每域产一份 SOTA 技能，装进对应 bot，验收后收口。

### 7. 挖 SOTA（按功能域分片）
- 每域一份 `sota/<域>-sota.md`：frontmatter（name 与技能名一致）+ 每域 3–5 个可核查来源（URL+访问日期）+ 该域安全红线（交易不承诺收益/中医非医疗建议/政策以当地当年文件为准/玄学仅文化参考等）+ 可落地升级项清单。
- 检索失败（429/WAF/后端故障）时按公开权威框架 + 官方入口锚点写，显式标注「联网被拦，落地前核当年官方原文」——**绝不编造 URL/文件号**。
- **多通道检索下逐条判定**：同一批分片常出现一个检索后端故障、另一个成功（并行多后端场景）。只收录成功通道返回的条目（带 URL）；失败通道对应主题写一条「检索通道受限未核源，引用前核当年原文」占位句（可标注该主题在成功通道有旁证则附旁证链接），绝不把未检索内容写成确定条目。
- **技能追加章后重排编号**：往已带交叉引用的 SOTA 技能里插新 `## N.` 章时，后续旧章号整体后移（如 `## 3.`→`## 4.`、`## 4.`→`## 5.`），子节号同步改（`### 3.1`→`### 4.1`），并全文扫一遍正文里「对照 §X」类交叉引用改到新号——插章只插正文不重排是最常见的自我埋雷，bot 引用旧号会指到别的章节。

### 8. 幂等安装 + 追踪（脚本，不手工逐个装）
- 安装器脚本模式：`域 -> (bot 列表, 技能名)` 映射表；内容哈希比对跳过已最新；复制进 `profiles/<bot>/skills/<技能名>/SKILL.md`；SOUL.md 追加 `skill_view(name='<技能名>')` 指针（已存在不重复）。任何源文件重写后重跑即全量重同步。
- 追踪器脚本模式：域完成判据 = 源文件在 + frontmatter 规范 + 所有目标 bot 技能装好 + SOUL 指针在；输出 pending 清单供下一批发车。

### 9. 验收（冒烟，不是「文件写进去了」）
- 抽 2–3 个 bot `hermes -p <bot> chat -q`，确认 bot 自动 skill_view 加载 SOTA 技能、作答带来源与红线；全量收口跑一遍 24 bot 冒烟脚本出 PASS/FAIL 清单归档进花名册。
- **冒烟脚本的判定必须只认「最终答案」，不能对原始日志尾巴匹配**：从输出里取最后一个 `⚕ Hermes` 答案框正文（先去 ANSI 色码，剔 Query 问句/Initializing/┊ 过程行）。对原始日志匹配会把问句文本算进判定——问句自带期望关键词（如 "VERVE"、"PhET"）导致假 PASS，摘要栏也抓到过程日志而非答案，清单不可归档。

### 10. 合并/退役重复 bot（用户说「保留一边就行」时）
两 bot 功能/SOTA 重叠要并成一个（保留更完整一侧、删另一侧，**别两边都留**）时：
1. **先备份**：`cp -r <旧bot目录> <交付目录>/backup_<旧bot>_<HHMM>`，误删可回滚。
2. **搬技能**：`cp -r <旧bot>/skills/<主技能> <旧bot>/skills/<SOTA切片>… <新bot>/skills/`，把旧 bot 的功能技能与 SOTA 切片全部并入存活侧。
3. **改 SOUL**：存活侧 SOUL 追加被并入域的「弹药库」指针 + 一行合并说明 + 交叉引用（「风控口径看 risk-officer-sota」式），不复制内容；职能切片仍按第 7/11 条各归各岗。
4. **同步所有映射**：`install_sota.py` MAP、`drive_waves.py`、花名册、验收报告里凡引用旧 bot 的条目全改成新 bot（旧行标注「已并入 X」留痕）。
5. **删旧 profile**：`hermes profile delete <旧bot> -y`（**必须带 -y**；不带会停在「Type 'name' to confirm / Cancelled」实际没删）。
6. **key 归并**：查存活侧 `config.yaml` 的 `key_env`，被并入 bot 的专用 key 直接并入存活侧那把 key，别留孤儿 key 槽。
7. **验证**：确认存活侧 skills/ 三类技能齐全，`hermes -p <新bot> chat -q` 问一个旧 bot 域的问题，确认按本域口径答、不串岗。

## Pitfalls
- **一域跨多职能时按职能拆片，别整块塞多 bot**：如量化域拆 EA 工程/L5 研发/L4 风控三片各归各 profile，完整总源保留在 sota/ 供查全貌；各片 SOUL 指针写交叉引用（「EA 口径看 X，风控口径看 Y」）不复制内容。整块塞多 bot 会让研发岗背风控口径、边界糊掉，用户会当场纠正「按功能分下去」。
- **bot 真名以 `profiles/` 目录实况为准**：手写报告/映射表里的 bot 名容易写错（本会话曾把 it-edu 写成 code-master、color-design 写成 secai-dashi）；安装后跑一遍实况扫描核对，报告与花名册同步勘误。
- **内嵌 `skill-*` 必须落一级 `skills/<skillname>/`**：Hermes 只扫 profile 下 `skills/` 一级目录；复制进主技能 `skills/<bot>/` 内部就「Hermes 看不到」。生成器写完后跑一遍「找 `skills/<bot>/skill-*` 上移到 `skills/skill-*`」的修复，再复核。
- **同一 skill 目录名冲突**：多团共享的 `skill-x` 已存在同级时跳过不覆盖（`os.path.exists(dst)` 判断），避免后团覆盖前团。
- **别把 key 打进模板/输出**：模型池 key 用 `grep` 从 source config 提取、走变量写文件；输出层 `print` 只报「池名/模型名」，不报 key 值。
- **`hermes profile create` 会建默认 6.9M 技能**：加 `--no-skills` 再手工装需要的，否则 24 bot × 6.9M 爆盘。
- **桌面 Bots 建群成员数有硬上限，不可 config 改**：`apps/desktop/src/plugins/hermes-bots/group-chat.ts` 的 `GROUP_CHAT_MAX_MEMBERS`（当前 =6，建群弹窗文案 `Pick 2–6 bots` 写死）。上限 6 含发起人本人，故实际最多再拉 5 个 bot 进群——用户报「只能加 5 个 bot」是这个 6 人上限减 1，不是配错。调大需直接改该常量并重新 build 桌面端，且多 bot 同群会放大同组共用 key 的并发 429；建议先用默认 6 人版（关键 bot 成群、其余私聊）。回答「为什么建群只能加 N 个」时：`grep -rE 'GROUP_CHAT_MAX_MEMBERS' apps/desktop/src/plugins/hermes-bots/` 取实况值再答。**改常量的实际生效路径见 class-level 技能 `patching-hermes-desktop-build`**（打包态 app 从 `win-unpacked/resources/app.asar.unpacked/dist/` 加载 renderer，不是 `dist/`；build 后要覆盖 unpacked 的 index + 同名 index.html 再重启才生效）。
- **合并 bot 时映射改一半会残留**：installer/roster/验收报告多份都引用旧 bot 名，只删 profile 不改映射，下轮 `install_sota` 会往已删 profile 报「bot 不存在」。删 profile 前先 `grep -rn <旧bot名> <交付目录>` 列出全部引用点一次改净。
- **`hermes kanban create` 标题是位置参数, 不是 flag**: `hermes kanban create "标题" --assignee X --body "..."`; 写成 `--title X` 报 `unrecognized arguments: --title` (CLI 语法会变, 先 `--help` 核对)。assignee 未知名被调度器静默丢弃不报错, 派单前先 `hermes kanban assignees` 核名。
- **delegate_task ≠ 跨 bot 派单**: `delegate_task` 生的是调用方 profile 的临时克隆子代理 (继承其 key/工具/系统提示, 用完销毁), 只能并行干算数/研究, **叫不动任何命名专家 bot**。跨 profile 派活唯一真通道 = kanban (`hermes kanban create --assignee <profile>` / 工具 `kanban_create`)。用户问"总调度能不能调度全部 bot"时: 能, 经 kanban; 但专家 bot 是借调非管辖 (汇报仍归总调度), 金策 3 岗才是命令链下级。
- **主瓦片名易让用户数错 bot**: 用户"只看到 3 个金策 bot 没看到 4 个"时, 真相是 4 角色 = 1 主瓦片(default, 无 display_name → Bots 面板显示名 "Hermes") + 3 金策子瓦片; 数"带金策前缀的"永远 3。改/改回显示名: 根 `{{WORKBUDDY}}/国外模型/hermes/profile.yaml` 加/删 `display_name: <名>` 字段即可 (删掉即回默认 "Hermes"), Bots 面板重开生效, 不影响对话/key。
- **`hermes profile delete` 不带 -y 不删**：默认交互停在确认提示后 Cancelled，profile 原样还在；脚本/批量一律带 `-y`。
- **交互确认挡脚本**：create/delete 默认交互；批量走 flag，误触测试 profile 记得 `-y` 清。
- **路径带中文/空格**（`{{WORKBUDDY}}\国外模型\hermes`）：Python 里用原生 `E:/...` forward-slash 绝对路径；bash 传给原生工具（find/cat/ls）时用引号包整路径，别裸拼（本会话裸拼 `profile.yaml` 被 shell 黏成 `...profiles/tianji-ge/profile.yaml` 无引号报错，实际是路径拼接缺分隔）。
- **多行 Python 别走 heredoc（Windows bash）**：`python - <<'EOF'` 内脚本只要带引号嵌套或 `E:\...` 反斜杠 Windows 路径，heredoc 传递中会断行报 `unterminated string literal`（且失败得靠试错定位）。凡 >10 行的同步/归档脚本直接 `write_file` 写 `<交付目录>/xxx.py` 再 `python xxx.py` 跑——脚本本身还是可归档工件，一石二鸟；本会话 4 连摔后全改此法。
- **聚类判错成本高**：合并前读各团 members/职责确认功能真的可并（阅卷≠教学、排盘≠泛玄学），宁可多留一个 bot 也别把不兼容功能塞进一个 SOUL。
- **冒烟自动判定的两个假警报（写脚本时一次性规避）**：① 假 PASS——关键词匹配作用在全量日志含问句文本上（见步骤 9），必须限定最终答案框；② 假 FAIL——答案字数下限（如 20 字）会把「短但全对」的答案判死（「看半球,定纬度」9 字是对的）。设计：非空且关键词命中=PASS，非空但未命中=PASS*（人工复核留档），别自动 FAIL；个别 bot 429/TIMEOUT 只单独重试一次再定 FAIL，勿把一次限流判成死。清单定稿前逐行人工扫一遍 FAIL，区分「脚本过严误判」与真故障，改判后归档。

## Verification
- 生成器跑完：`hermes profile list` 全在册；抽查 2 bot 冒烟通过（persona 加载 + 免责带上）；`ui_meta.hermes-bots` 全写；无 key 泄漏进日志。
- 分组共用 key：每个 bot 的 `config.yaml` 主池 `key_env` 变量名在 `.env` 已含 `sk-`（全量 grep 核对 M/M 过）；抽 2 个不同组 bot 实测出答案（非 fallback）。
- 交付物落内容中心铁律目录（`{{WORKBUDDY}}\内容中心\交付\<月份_主题>\`）：方案 md + 花名册 md + 可复用生成器脚本。
