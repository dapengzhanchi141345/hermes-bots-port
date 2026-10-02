---
name: strategy-rd-sota
description: "Use when 策略研发、信号实证、ML 因子挖掘、回测验收（L5）需要引用最新 SOTA 方法论。"
---

# 策略研发 SOTA（量化域·L5 研发切片，2026-09 版）

> 职能切片：本文件覆盖 **L5 研发** 职能（quant-trading-sota.md 第 1/2/4 节 + 落地项 2/3/4/5）。EA 工程看 mt5-ea-sota，风控裁决看 risk-officer-sota。
> 检索日 2026-09-27 · 带来源，引用前复核。策略回测 ≠ 未来收益；统计对比必须同分母；高胜率 ≠ 正期望。

## 1. SMC/ICT 流动性猎杀 + 订单流实证（哪些有边、哪些是噪音）
**来源**：
- https://fxnx.com/en/blog/smart-money-concepts-work-backtest-evidence （1,000 笔机械化回测审计）
- https://www.alphaexcapital.com/smart-money-concepts/ （证据分级）
- https://www.buildalpha.com/backtest-ict-and-smc/ （ATR 归一化防重绘）

**可引用结论**：
1. **裸 Order Block 是负期望**：无 FVG 伴随的独立 OB 回弹失败率 56.9%（OB 需紧邻位移+FVG 才有预测价值）——与李老师「裸反转/FVG 只做否决门」铁律互相印证。
2. **FVG 有统计边**：EUR/USD 15m 上 64.8% 的 48h 内会被部分回补；流动性扫荡后顺势跟随 58.2%。
3. **Killzones 过滤是最大单一提升项**：未过滤胜率 41.2% → 限定伦敦 07:00-10:00 GMT / 纽约 12:00-15:00 GMT + 4H 结构偏向后 58.4%；窗口外期望 -0.22R/笔，窗口内 +0.64R/笔。
4. **执行税吃掉纸面 RR**：3-pip 止损 + 0.8 点差 + 0.4 滑点 = 实际风险 +40%，理论 1:5 RR 退化为有效 1:2.8。
5. **ATR 归一化防重绘铁律**：所有尺寸阈值用 ATR 倍数（如 gap > 0.35×ATR14），禁写死点数。
6. **证据级别**：无 peer-reviewed 研究证明 ICT 图案可靠；网上 80-90% fill-rate 是无源传说，禁止引用。结论只能来自自己的机械回测。

## 2. 机器学习 Alpha 挖掘 SOTA（防泄漏 Walk-Forward 协议）
**来源**：
- arXiv:2603.09219 《AlgoXpert Alpha Research Framework: A Rigorous IS–WFA–OOS Protocol》
- arXiv:2605.23959 《When Alpha Disappears: A One-Switch Benchmark for Decision-Time Leakage》（东京大学/HKUST-GZ）
- Kaufman & Rosset, 《Leakage in Data Mining》 ACM TKDD；AAAI 2025 AlphaForge

**可引用结论**：
1. **IS→WFA→OOS 三段协议**：IS 找参数平台区（Sharpe ≥ 最优 90%）而非单点最优；WFA 滚动窗口 + purge gap（stateful 策略必须重置状态）；OOS 锁参数不许再调。
2. **两大隐形泄漏源**：NORM_GLOBAL（特征归一化用全样本统计量）与 EXEC_OPEN（t 时刻决策按 t 开盘价成交）；诊断法 one-switch 对照（每次只切一个协议约定，测泄漏增益）。
3. **稳健性四件套**（回测后必跑）：Vs Random、Noise Test、Monte Carlo Permutation Test、Walk-Forward。
4. **过度自由度警示**：一个 FVG 规则 7 个旋钮——「找到盈利配置」在纯噪声里也大概率发生。降自由度：核心参数 2-3 个、粗步长。

## 3. 黄金/加密货币 regime detection SOTA
**来源**：
- Giudici & Abu Hashish 2020, QRE 《A HMM to Detect Regime Changes in Cryptoasset Markets》
- arXiv:2011.03741 + ScienceDirect S0275531921001756（4 状态 NHHM 最优）
- https://github.com/hidden-regime/hidden-regime （开源 Python HMM regime 管线，MIT）

**可引用结论**：
1. **HMM regime 检测**：币圈惯用 4 状态 = bear / bull×2 / calm；高波动状态罕见但短促。
2. **开源落地**：`hidden-regime`（Python 3.10+，MIT）内置时间隔离 V&V 回测、regime 画像、regime-based 仓位管线——可进 L0 确定性层（确定性模块保持 Python 不套 LLM）。
3. **外部因子**：VIX + 美债收益率是对加密收益唯一稳健的外部预测变量——宏观日报只盯这两项，避免 12 因子全上的过拟合。

## 4. L5 验收职责（策略上线前必过）
1. 新策略验收加 **MC 洗牌管线**（读 MT5 HTML 报告 → Python 洗牌 1000 次 → bust rate/MDD 分布），仓位建议按坏端定，验收记录交 risk-officer 双闸 veto。
2. WFA 用 **purge gap + 参数平台区**（Sharpe≥最优90% 取中位），OOS 锁参数单次验证。
3. 金/币线加 **hidden-regime 4 状态 HMM**（Python 确定性层，30min L3 循环里每 4h 刷新 regime 标签），regime 切 bear/高波动 → 联动风控降档仓位+收紧日亏熔断。
4. SMC 类信号统一 **ATR 归一化尺寸阈值 + Killzones 会话过滤**，裸 OB 继续只作否决门；统计引用必须同分母（窗口内 vs 窗口外分开报）。

## 安全与免责
- 本切片是研发方法论，不构成投资建议；任何参数改动先回测验收再上模拟，实盘最小影响方案（先报后动）。
