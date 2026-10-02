---
name: risk-officer-sota
description: "Use when 风控双闸 veto、仓位管理、蒙特卡洛压力测试、熔断定级（L4）需要引用最新 SOTA 方法。"
---

# 风控 SOTA（量化域·L4 风控切片，2026-09 版）

> 职能切片：本文件覆盖 **L4 风控** 职能（quant-trading-sota.md 第 4 节仓位管理 + 第 3 节 MC 压力测试 + 落地项 2/4 的风控侧）。
> EA 工程看 mt5-ea-sota，策略研发看 strategy-rd-sota。风控官不听总管、不听研发，只按本文件 + veto_log 留痕裁决。
> 检索日 2026-09-27 · 带来源，引用前复核。风控裁决以李老师实盘纪律为最高优先级。

## 1. 风控铁律基线（不可被 SOTA 推翻）
- 品种日≤3单计数闸 / 日亏10%熔断 / 连亏3笔24h冷却 —— 这三条是制度，任何策略研发结果都不得突破。
- SOTA 方法论只用于「在制度内更稳」，不用于「放大风险换收益」。
- 双闸 veto 留痕：每个否决/放行写 data/veto_log.json（时间/依据/数据引用）。

## 2. 仓位管理 / 风险平价 SOTA
**来源**：
- 逆波动率仓位（target vol / realized vol）是 regime 切换下最稳健的一层（Giudici & Abu Hashish 2020 QRE；arXiv:2011.03741，见 strategy-rd-sota 第 3 节同源）。
- https://github.com/hidden-regime/hidden-regime （MIT，内置 regime-based 仓位管线，访问 2026-09-27）

**可引用结论**：
1. **波动率 scaling**：逆波动率仓位 = 目标波动 / 已实现波动，按品种分别设 target vol；与日亏熔断叠加使用（波动率高的品种自动降仓）。
2. **regime 联动降档**：hidden-regime 4 状态 HMM 切到 bear/高波动状态 → 自动降档仓位 + 收紧日亏熔断阈值（具体档位由风控官定，研发不得自定）。
3. **坏端定仓**：仓位必须按 MC 洗牌后坏端（p95 drawdown）定，不按单条曲线峰值定。

## 3. Monte Carlo 压力测试（风控裁决口径）
**来源**：
- https://mql5.com/en/articles/23980 （MT5 回测报告 Monte Carlo 管线，官方论坛）
- quant-trading-sota.md 第 3 节案例：单条曲线 MDD 284$ vs 洗牌后 578$

**风控裁决规则**：
1. 读 MT5 HTML 回测报告 → 抽取已成交 PnL → Python 洗牌生成数千条净值曲线 → 输出 bust rate / profit rate / max drawdown 分布。
2. **裁决阈值（风控官制定）**：bust rate > 5% 或 p95 MDD > 账户 20% → veto；p95 MDD 在 10-20% 之间 → 放行但仓位降一档 + 24h 复评。
3. 洗牌必须用「逐笔 PnL 重排」而非整条曲线重采样（保留交易间依赖结构）。
4. 每个放行策略的 MC 报告存档，risk-officer 每月抽检一次。

## 4. 事件定级 / 熔断联动（风控视角）
1. regime 切 bear/高波动 → 自动降档仓位 + 收紧日亏熔断（研发提联动参数，风控官否决权）。
2. 外部因子监控：VIX + 美债收益率（对加密收益唯一稳健外部预测变量，见 strategy-rd-sota），异常波动日风控官可临时加严计数闸。
3. 所有风控动作写 veto_log.json；第 12/13 复核（开单双闸）按本文件阈值执行。

## 安全与免责
- 风控 SOTA 不承诺收益，只降低爆仓概率；任何降档/加严动作以李老师实盘纪律为最高优先级，留痕可审计。
