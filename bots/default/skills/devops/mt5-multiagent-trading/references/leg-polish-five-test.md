# Leg-polish 5-test gate (无损打磨五验)

The user's iron law: 每一个技能务必打磨到没有瑕疵才能用. Every construct/leg/parameter change must pass the 5 tests before it may touch the live path. Unverified ⇒ stopped (flag off / neutral), not merely observed-soft.

## Deliverable schema
`data/leg_<name>_polish.json`:
- `pnl归因`: closed-deal P&L for this layer, bucketed by loss cause (e.g. 目标太近RR<1.5负期望 / 止损打掉 / 贴脸成交 / 无SLTP). Keys: `ts, range_closed_n, buckets:{name:{n,pnl,pnl_set}}, total_pnl, note`. Source: state json `filled/history` + `mt5.history_deals_get` (magic filter); MT5 deals primary, state orphans secondary.
- `ab_grid`: each cell `{key:"k/period/target/slmult", avg_expR, wr, n}` — every cell (current + candidates) re-scored on the SAME full event set (same-denominator rule).
- `五验`: `品类稳健_ge4_6:{passed,total,pass}`, `甜蜜点_no_sign_flip:{pass,sign_flip_found,adjacent_cells_checked}`, `walk_forward_3_segments:{passed_segments,total,pass}`, `delta_abs_significant:{delta_abs, z, p_two_sided, significant_at_0_05, pass}`, `best_expR_positive:{best_expR, pass}`, plus `n_pass`/`all_5_pass`.
- `同分母结论`: `{cur_key, best_key, cur_expR, best_expR, delta_abs, delta_rel_pct, z, p_two_sided, n_events, per_symbol_deltas}`.
- 裁决: `接` only when all 5 pass AND same-denominator Δ is significant; else `维持现参数` (or observation mode, below).

## Procedure
1. P&L attribution: bucket closed orders of the layer by loss cause; report n + pnl per bucket. This step alone often finds the real disease (e.g. 重估撤单 ≫ 挂单 ⇒ cancel-repost churn, not a parameter problem).
2. A/B grid: full-history replay (~2600 bars × T1 symbols) of the leg's entry events; score every cell on the identical event set; per-cell win rate / expected R / max drawdown.
3. Five checks per the schema. z-test recipe: two-proportion on the shared denominator, `se = sqrt(pp(1-pp)(1/n1 + 1/n2))`, `p = 2*(1-Φ(z))` with `Φ` via `0.5*(1+erf(z/√2))`.
4. Same-denominator conclusion: judge by ABSOLUTE Δ exp_R + p, not by relative % (relative % on small denominators is a known liar — see the Eq-Pool incident in the SKILL.md same-denominator rule).
5. Decision:
   - 5/5 + p<0.05 + best_expR>0 ⇒ wire the params into the live module, set the verify flag True.
   - All-negative grid (best_expR < 0 on every cell) ⇒ OBSERVATION MODE: flip the leg's candidate-generation flag off (e.g. `RANGE_LEG_VERIFIED=False`) so no new orders are posted; existing pendings/positions keep flowing through `manage_positions` (fail-open, never naked). Re-test next regime cycle before re-enabling.
6. Record the verdict in `docs/playbook_master.md` + sync to GitHub (`sync_to_github.py`).

## Running it via subagents (and the fallback)
- Dispatch step-wise: each step must write its partial JSON to disk immediately (落盘) so a mid-run crash loses nothing; final output ≤300 words, JSON only.
- A 429 rate-limit death makes the agent's partial "verdict" text untrustworthy (it may have printed 5/5-接 before dying without writing the file). Verify the JSON on disk first; salvage intermediate scripts from the transcript; if 2+ tasks die at 429, abandon subagents and run the verification directly in the main process — its own API quota is not affected by the subagent cap.
- A range/high-low forecaster that cannot beat its 50% baseline (p≈1.0) is NOT a win-rate edge: wire it structural-only (SL outside the predicted band, state-machine leg routing) behind a verify-off flag. Never claim edge.
