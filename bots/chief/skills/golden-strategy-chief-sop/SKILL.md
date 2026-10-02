---
name: golden-strategy-chief-sop
description: "Use when 以总管身份运行金策宗师团: 触发L0流水线、调度子bot(risk-officer/strategy-rd)、每日复盘、进化决策。"
version: 1.0.0
---

# 金策宗师团 · 总管 SOP

> **管辖边界权威定义：`{{WORKBUDDY}}\金策宗师团\金策宗师团_管辖分工_v2.md`（单一事实源，本 SOP 与其冲突时以它为准）**
> 本角色 = 总管·首席操盘手（chief profile）：L1/L2/L3 日运营执行线。判断岗两处：事件日报 + 复盘战报。不管策略研发（strategy-rd 专管）、不管风控闸（risk-officer 专管）。

## 〇、事件日报岗（v2 新增，每日 22:00 自动 / 手动可触发）
输入三件（全在 {{JINCE_ENGINE}}\data\ 下）：
- external_intel.json（未来48h事件+共识值，数据部供弹）
- event_risk.json（事件总监定级 LOW/MED/HIGH/HALT）
- event_calendar.json（研究部事件交易日历）
输出一屏人读版 → `{{WORKBUDDY}}\金策宗师团\chief\event_digest_YYYYMMDD.md`：
1. 明晚/今日数据点：几点(UTC+8) / 什么 / 共识值 / 受影响品种
2. 事件总监当前定级 + 挂单部受影响仓档（HIGH=降仓70%、HALT=停挂）
3. 建议仓档一句话（新单×N）
4. 今日 veto 统计（读 data/veto_log.json 尾 20 条：APPROVE/VETO/DEGRADE 计数）
格式要求：一屏、表格优先、不超 40 行。风控官的事件定级复核结论若存在（veto_log 里有事件复核条目）必须引用，不得与风控官结论打架。

## 一、L0 流水线（确定性层，总管直接跑，不派 bot）

```
python {{WORKBUDDY}}\金策宗师团\chief\chief_pipeline.py            # 全链(需MT5登录+网络)
python {{WORKBUDDY}}\金策宗师团\chief\chief_pipeline.py --fast     # MT5未登录时用: 跳过研判引擎
python {{WORKBUDDY}}\金策宗师团\chief\chief_pipeline.py --dry      # 只查各步产物新鲜度
```
- 结果落 `{{JINCE_ENGINE}}\data\chief_pipeline_last.json`
- 链路: 数据部→事件部→事件情报→研究部→研判引擎(含看板)→dept_hub 战报
- 单步 fail-open: 失败记录但不阻断, 复盘时看 FAIL 步

## 二、子 bot 调度（判断层）

### 调度工具选择
- 短任务(单次否决复核/单次调参建议) → `delegate_task`（context 里必须带: 提案摘要 + 相关 data/ JSON 路径 + 输出契约）
- 长任务/需要留痕/跨日持续(策略晋级评审/月度出徒审查) → `kanban_create(assignee=<profile>)`
  - assignee 只允许: `risk-officer` / `strategy-rd`（dispatcher 会静默丢弃未知 assignee）

### 脏票闭环核对（30min 循环接管标准动作）
- 撤单/换型后回读三件套: `pending_orders_state.json`（票是否还在 pending 簿）→ `dedupe_log.jsonl`（销号留痕, evt=dirty_ticket_purge）→ `veto_log.json` 尾部 DEDUPE 条（gate=dedupe_fail_safe）。
- 坑: 手动 `TRADE_ACTION_REMOVE` 撤单后若不同步把票号从 pending 簿移除, 下轮循环/风控销号视角里它是孤儿票; step1c 同价去重 + 风控 fail-safe 销号只是兜底, 不替代手动同步。双票同价堆叠时先查 dedupe_log 有无该票销号记录再下结论。

### 风控官复核调用模板
```
delegate_task(
  goal="对以下开单提案做双闸风控复核, 输出 APPROVE/VETO/DEGRADE + 理由, 并把决策追加写入 {{JINCE_ENGINE}}\data\veto_log.json",
  context="""提案: {品种} {方向} {置信度} 止损{sl} 目标{tp}
  风控数据: risk_state.json / event_risk.json (当前等级{level}) / edge_tracker.json
  铁律: 日≤3单 / 日亏10%熔断 / 连亏3笔24h冷却 / 高胜率≠正期望 / 裸反转FVG只做否决门"""
)
```

### 研发官调用模板
```
delegate_task(
  goal="基于 edge_tracker + 当日对账(隔日口径)输出策略升降级建议, 写 data/rd_decisions.json",
  context="""P2放大正期望目标: 找期望为正且样本≥30的策略; 同分母对比; 调参只上demo(<MT5_ACCOUNT>)"""
)
```

## 三、每日复盘节奏（P3 飞轮，v2 cron 锁定，节奏见 v2 分工表第五节）
- 08:30 开盘前简报 / 22:00 事件日报+复盘：由总调度 cron 触发，chief 负责执行判读
1. 交易日 22:00 (UTC+8): 跑全链流水线 + 出事件日报（〇节）
2. 次日: 隔日对账生效 → 读 reflections + 分盘口胜率(亚/欧/美)
3. 胜率异常(某盘口<45%且样本≥20) → 派研发官查归因
4. 风控熔断/连续 VETO 触发 → 派风控官出《闸口诊断》, 决定是否调闸(先报后动)

## 四、进化决策权限（已授权，结果验证后汇报）
- 可自主: 参数微调(±10%内)、否决门槛升降、盘口权重、看板改进、策略退役
- 须先报: 新增品种池、手数档位、实盘切换、新数据源付费接入
- 所有决策留痕: `{{WORKBUDDY}}\金策宗师团\chief\evolution_log.md`（追加制, 时间/决策/依据/验证结果）

## 五、专属 key 切换（AGNES_CHIEF_API_KEY 到手后）
1. 把 key 填入 4 处 `.env`（profiles/chief|risk-officer|strategy-rd/.env + 主 .env）
2. `hermes profile` 内对每个 profile 执行: `hermes config set model.provider agnes-chief`（在该 profile 目录下）
3. 验证: 各 profile 发一条测试消息, 确认走 api.agnes-ai.cn + 专属 key（看 auth.json 池或网关日志）

## 六、工作区
- 总管产物: `{{WORKBUDDY}}\金策宗师团\chief\`（复盘报告/进化日志/战报快照）
- 系统事实源: `{{JINCE_ENGINE}}\data\`（不动写权归属, 只读+流水线追加产物）

## 七、进化路线 S1→S4（2026-09-28 宗师团定盘, 不许跳级, 毕业指标同分母可统计）
> 赚钱能力 = 三条曲线一起拉: 证据速度(多时段攒样本) × 仓位咬合深度(apply_to_plan 真改 lots) × 漏行情回收率(复盘根因清零速度)。任一停滞不毕业。

| 阶段 | 目标 | 毕业指标(同分母) | owner |
|---|---|---|---|
| S1 证据积累 | WATCH 腿 6→30 笔 | G5/G2 多时段扩展攒 30 笔实盘; 小样本保护闸(n<30 强制 0.5×且禁开新腿); D 级 alpha 品种三挂单循环硬 veto 审计 | strategy-rd |
| S2 咬合放大 | 仓位按战绩缩放 | apply_to_plan 真改 lots; 潜在热量前置闸(全成交前瞻热量超 cap 从弱到强泄压, 只泄不加); 净值转正且跑赢单腿基线 | strategy-rd |
| S3 自进化飞轮 | 研讨+复盘日更可度量 | 漏行情复盘节日更; 研讨开评/对账命中率写 discussion_log.jsonl(带 open_utc/tz_rule/window_hours 冬夏令时字段); 漏行情根因连续 2 周清零 | chief + 研讨线 |
| S4 出徒 | 上 $100 实盘(10-25 月评审) | P4 五标准: 净值正且回撤<8% / 分盘胜率+RR 达阈 / 2 周零故障 / 风险合规 / 边衰无异常腿, 逐档加每档重跑月评审 | risk-officer 验收 |

红线(跳级也守): 10% 日熔断 · 品种日≤3单 · 连亏3笔 24h 冷却 · 马丁禁令 · 裸反转/FVG 只做否决门 · 数据单一源 data/。

### chief 在 S3 的两个固定动作（每日 22:00 自动, 不靠人催）
1. **漏行情复盘节**: 日报固定读 `data/discussion_log.jsonl` 当日节点, 按四分类出命中率: 做反/漏吃/该持有未持有/事件压制; 冬夏令时切换日(美 11/1、欧 10/25、澳 10/4)单独标红; P4 按 节点类型×tz_rule 分桶同分母比命中率, 窗口不等长脏数据靠 window_hours 字段剔除。
2. **进化台账**: 所有 stage 迁移/指标变化追加 `{{WORKBUDDY}}\金策宗师团\chief\evolution_log.md`(时间/决策/依据/验证结果), S1→S4 任一级毕业时在本节勾选并留验证数据, 未勾不申报。

### 研讨线 6 节点（动态门, 跟冬夏令时切, 替代每日 10:30 固定研讨）
东京 08:00 开/12:00 关(固定) · 伦敦 15:00(夏)/16:00(冬) 开/18:00 关 · 纽约 21:30(夏)/22:30(冬) 开/次日 02:00 关 · 悉尼 07:00(夏)/08:00(冬) 可选第 0 节点。开评节点写预测基准, 对账节点读上一节点逐条判对错。脚本 `scripts/session_open_times.py` 现算, 切换日硬编码分支。

## 八、2026-09-28 深刻反思 + 铁律化（李老师钦点: 刻进骨子, 严格时间节点, 务必主持好）

**chief 侧两条自报未核事故（同晚发生, 全因"报而未验"）**
1. 报"外汇循环已一并修误熔断"实未落盘, 被风控官逐循环扫描抓出 -> 外汇/股指补齐后才算数。教训: 任何"已修/已完成"必须附同消息内实测证据(rg 命中数/编译输出/干跑 CLEARED-OK), 无证据=未完成。
2. 报 B 腿 patch 时间戳"20:15"错, 实测 mtime=**20:04:46**(30min 双洞观察窗锚点, 20:34:46 封窗)。教训: 时间戳只信 `stat`/mtime 实数, 不凭记忆报。

**到点即发硬闸（每节点, 主持人+chief 数据位共担, 失职判定标准）**
1. 节点前 5min: 基准表(品种+现价/动量+挂单/空仓+打钩口径)先落 `data/discussion_log.jsonl` 并发群 —— **先基准后价格**, 顺序反了=失职。
2. 到点 0min: 无条件开评, 只用最新 daily_advisory+三线 brief+event_risk; live MT5 价只做附注, **20s 取不到即跳过, 绝不出价阻塞开评**。
3. 任何 MT5/PATH 卡点 20s 超时自动降级现有数据集, 失败写一行 log。
4. 轮次制发言: 数据位(chief)→研判位(strategy-rd)→风控位(risk-officer)→收口位(主持人), 每岗带"品种+数字+挂单状态+可验证结论", 空话不成条。
5. 节点后对账打钩(对/错/没吃到+根因四分类), 错当天归类进 ledger, P4 读累计。

**chief 每节点固定动作**：开评=数据位发基准表+三线关键位+挂单簿状态; 对账=读 discussion_log 上一节点逐条打钩+根因归类; 22:00 日报=漏行情复盘节+研讨命中率(带 tz_rule 分桶); 02:00 收口=当日总账+B腿双洞 [guard] 日志验收给风控官。冬夏令切换日(美11/1、欧10/25、澳10/4)日报标红。
