---
name: mt5-ea-sota
description: "Use when MQL5 EA 开发、回测工程、成本/tick 真实性任务需要引用最新 SOTA 实践。"
---

# MT5 EA 工程 SOTA（量化域·EA 切片，2026-09 版）

> 职能切片：本文件只覆盖 **EA 开发/回测工程** 职能（quant-trading-sota.md 第 3 节 + 落地项 1）。策略研发看 strategy-rd-sota，风控裁决看 risk-officer-sota。
> 检索日 2026-09-27 · 带来源，引用前复核。策略回测 ≠ 未来收益，改动先回测验收再上模拟，实盘最小影响先报后动。
> 运营操作细节（order_send retcode/休市 10018/GBK 子进程禁 emoji）见技能 mt5-multiagent-trading。

## 1. MQL5 回测引擎 2024-2026 最新实践
**来源**：
- https://nuvora-app.com/knowledge/how-to-improve-metatrader-backtests （访问 2026-09-27）
- https://forex-trading-daily.contentwave.net/article/mt5-strategy-tester-reviewed-updated-june-2026-practical-verdict （2026-06 实测）
- https://mql5.com/en/articles/23980 （MT5 回测报告 Monte Carlo 管线，官方论坛）

**可引用结论**：
1. **Tick 模式铁律**：验证一律 "Every tick based on real ticks"（经纪商真实 tick），必须检查真实 tick 覆盖率（回退到生成 tick 的是混合结果）；2026 现状：供应商直出 MT5 格式 tick 档案（.ticks/.hst + 分时段点差曲线）已成常态。
2. **成本现实化清单**：变动/会话平均点差（禁最低点差）+ 佣金（raw 账户约 0.7 pips/手 RT on EUR/USD）+ swap（含三倍 swap 日）+ 显式滑点 0.5-1 pips/市单。案例：+1.8 pips 纸面 edge 扣完成本只剩 +0.6 pips——三分之二的 edge 是成本假设。
3. **平台 vs 峰值**：参数敏感性看邻域——47 好而 40/55 亏 = 拟合噪声；40-60 都小赚 = 找到行为。优化次数克制（5 参数 20 值 = 320 万次回测必然出偶然冠军）。
4. **OOS 纪律**：保留数据段只验证一次；复调一次即失效（进入 in-sample）。

## 2. EA 开发 2026 最佳实践
1. **MT5 跑参数扫描 + Python 做后处理**（MC/Walk-Forward 主流混合管线；MT5 原生无 MC/WFA 套件）。
2. 回测报告导出 HTML 供 Python 读 PnL 序列（MC 洗牌管线入口，验收规则见 risk-officer-sota）。
3. EA 代码保持确定性逻辑（Python 不套 LLM 铁律适用于 L0 模块同理：EA 侧不引入随机 LLM 决策）。

## 3. 可直接落地
1. 回测/验证全切 **real-tick + 分会话点差 + 显式滑点**，报告必须带真实 tick 覆盖率；报 RR 一律扣执行税。
2. 参数优化后必须输出「邻域敏感性表」（±20% 参数邻域曲线），孤立峰值的配置一律打回。

## 安全与免责
- 本切片是 EA 工程方法论，不构成投资建议；EA 上线前走 strategy-rd 回测验收 + risk-officer 双闸 veto。
