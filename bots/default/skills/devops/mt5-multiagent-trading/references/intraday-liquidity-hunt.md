# Intraday Liquidity-Hunt Layer + Portfolio Governor + Symbol Universe + Self-Evolver

Added 2026-09-25 (李老师 "全部品种都要做 / 日内高低点精准猎杀 / 自我进化" 升级轮). Read before touching the order-placement or risk modules.

## 1. Three-layer order model (replaces single "trend or range" per symbol)
Each symbol can carry up to THREE independent legs with distinct dedup keys `(sym, layer, ptype)` so a big-timeframe BUY_STOP and an intraday BUY_STOP can coexist (user-mandated: "点位不一样就不矛盾"): `trend` (Donchian H4 breakout Stop, 2×ATR SL, RR≥2, chandelier trail), `range` (Bollinger(20,2σ) Limits, anti-whipsaw 2×ATR stat-invalidation SL, breach-and-exit + 48h time stop, L2 early-close DISABLED), `intra` (liquidity-hunt, below). Risk tiers: 主流1% / 中流0.5% / 微流0.25% (crypto `T1_RISK`), range leg = 0.5× base, intra leg = 0.25× base. Strong-trend days (ADX>30) halve the range-leg risk instead of cancelling it (user wants all symbols covered).

## 2. Intraday liquidity-hunt protocol (ICT stop-hunt, learned from web 2026-09-25)
- **Anchors:** PDH/PDL = previous D1 candle high/low (liquidity pools where resting stops cluster); target = pivot midpoint (PDH+PDL)/2.
- **Entry:** SELL_STOP at PDH×1.001 (sweep-of-highs fakeout) / BUY_STOP at PDL×0.999, only when price is within 2.5×ATR of the pool.
- **Sizing/stops:** 0.75×H1-ATR tight SL (H4-ATR fallback 0.25×), RR typically 4-9; risk = layer base × 0.25.
- **Session gating (kill zones, 东八区):** crypto 24/7; FX/intra dept: London h8-10 / NY h13-15; equity dept by exchange timezone — JP {8,9}, EU {15,16}, US {21,22,23}.
- **Not-overnight:** 24h TTL on pending; position exits: 2h-no-progress early out (hypothesis was fakeout-reversal, no move = hypothesis dead), 4h forced exit, 0.5R breakeven.
- **Spread tax gate (equities):** reject the plan if SL distance < 3× current spread — CFD spread eats small-stop intraday edges.
- **Closed-market safety:** `market_fresh(tick)` — tick timestamp frozen >300s = market closed, never post ghost orders (weekend US/JP/EU hours silently skip, by design).
- **Data gotcha:** demo feed has full 500-bar H1/D1 despite tiny default requests; previous-day anchors must come from D1 (H1-UTC-day stitching failed on tz handling). See quirks #11.

## 3. Symbol universe (第14部门 `symbol_universe` → 实盘用 `universe_tiers.py`; 根目录旧版 753行 V2 模块被 15+ 老脚本引用, 勿动)
248 symbols all in the radar, orders only for liquidity tiers: T1 crypto 16 (three layers) · T2 FX major7+cross3+XAU/XAG (two layers + intraday at kill zones) · T3 index 8 + mega-cap 16 stocks (intraday layer only, exchange-timezone kill zones, no overnight) · T4 watch pool 195 (scanned every cycle, promoted on strong signal, never auto-posted). **Rationale to defend if asked:** 248 symbols ≈ 30 independent risk drivers; posting all = governor bleed-triggers every cycle + spread tax on illiquid names. Coverage = radar + tiered ammunition, not 744 pending orders.

## 4. Portfolio governor (第13部门, `portfolio_governor.py`, magic 20260902/20260903/20260904 three-state aggregation)
Shed-only fuses (never adds): position heat >12% NAV → trim largest same-direction position; latent pending heat >20% → cancel weakest-signal pendings; net-direction >8% → trim dominant side; crypto mega-cap cluster (BTC/ETH/SOL/XRP/BNB as ONE driver) >6% or >4 positions → trim; drawdown -10% → half all sizes, -20% → STOP new orders + cancel all pendings; ATR-percentile vol scaling (>80th pct → ×0.75, >95th → ×0.5). Dashboard `governor_dashboard.md`.

## 5. Self-evolver (第16部门, `meta_evolver.py`) — closes the P&L feedback loop
- Collects settled trades from all 3 state machines; buckets by layer (trend/range/intra/swing); rolling-30 stats: win rate, expectancy per R, SQN.
- **Edge-decay detection (learned 2026-09-25: "strategy decay is the most expensive silent accident"):** sample<10 → ×1.0 (no small-sample overfitting); rolling expectancy<0 → ×0.75~0.5 tier down (diagnose, don't stop yet); SQN≥2 with n≥20 → ×1.25 max (half-Kelly discipline, capped, never all-in).
- Weak symbol: 7-day ≥3 trades & win rate<40% → that symbol ×0.5.
- Effective diversification EP = 1/Σw² (inverse Herfindahl over open risk shares) — "24 orders ≠ 24 diversified bets".
- **Coupling (the 2026-09-25 "deepen the connections" upgrade):** `apply_to_plan(plan)` multiplies layer-scale × symbol-scale × governor-drawdown-scale into `plan['risk_pct']` and returns a block reason on governor STOP. Called inside every placement entry wrapped in fail-open try/except (evolver/governor files missing or stale → scale 1.0, never block the order flow). If a module only writes a dashboard nobody reads, the coupling is fake — verify lots actually scale.

## 6. Regime hysteresis deadband (fixes the R1 cancel-repost livelock)
ADX hovering 24-27 made every 30-min cycle flip trending↔ranging and cancel-repost (user saw "many symbols have no orders" — they were in the cancel gap). Fix: trend→range requires ADX<22, range→trend requires ADX>28; 22-28 = deadband, keep current regime. Intra layer exempt from R1 (only R2 D1-flip + R3 small drift 1.5×ATR + R5 24h).

## 7. Auto cycle order (auto_run_cycle.py)
reconcile-orphans → CIO (steward→chart→intel→events→research→trading→risk→pending) → crypto_pending → equity_pending → governor → meta_evolver → training log (equity_curve.csv + daily report). Windows task `JinCeAutoCycle` every 30 min; `JinCeMonthlyReview` 10-25 → monthly_review.py 5-criteria check for $100 real-account switch. Read `data/auto_cycle.log`, not the sub-agent's claim.

## 8. edge_tracker universe narrowing ("赚不到钱" 根因诊断, 2026-09-30)
当 edge_tracker 里 **n≥30 且 pf≥1 的品种数 = 0** (大样本正期望为零), "赚不到钱" 的根因是**品种宇宙宽度失血**: 248 品种全开 → 每个只攒个位数样本 → 全被 0.5× 小样本闸压死 → 无人攒到 30 笔验证 → 仓位永死 0.5× + 125 个负期望品种持续失血。**修法:**
1. 收窄开单宇宙到 T1/T2 正期望苗头 (T4 watch 池保留雷达+打分但**永不自动开单**);
2. 堵 9 个大样本失血品种 — `is_symbol_allowed` 已自动拦, **验证方式是直接调 `edge_tracker.is_symbol_allowed(sym)` 看返回值**, 不是只读 veto_log 有没有 D_HARD_VETO 条目 (留痕≠门控生效);
3. 集中最强正期望腿 (intra 杀单 exp_R 2.89/胜率 80%/wf3 全正) 提速攒样本: 同腿跨伦敦+纽约 kill zone × 多币并行, 单笔风险不变, 总热量组合总督封顶;
4. demo 练手账号可放宽 P2 放大 (多品种并行/1.0× 基准/不逐步请示), 同分母铁律 + 只放大已验证正期望 不破。
**诊断脚本** (三问定根因, 不先改参数):
```python
et = json.load(open('data/edge_tracker.json',encoding='utf-8'))['symbols']
n30_pos = {s:v for s,v in et.items() if v.get('n',0)>=30 and v.get('pf',0)>=1}
n30_neg = {s:v for s,v in et.items() if v.get('n',0)>=30 and v.get('pf',0)<1}
# 大样本正期望=0 且 全负期望>100 → 宇宙宽度失血, 收窄+堵漏+集中提速
```