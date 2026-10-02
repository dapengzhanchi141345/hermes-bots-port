---
name: yimou-pavilion-sota
description: "Use when 博弈论分析/棋类AI/战略推演/决策树任务需要引用最新 SOTA 方法与工具。"
---

# 博弈/策略域 SOTA 增强技能（2026 版）

> 检索日 2026-09-27 · 带来源。棋类/AI 引擎版本引用前复核；战略分析遵守"AI 初判人工终审"铁律。

## 1. 博弈论 SOTA
- **纳什均衡计算**：Gambit（开源 Python，https://github.com/dmeb/gambit）做小规模博弈求解；NashPy（开源，https://github.com/NashPY/NashPy）做扩展博弈/重复博弈。
- **机制设计**：拍卖设计（VCG/最大收益拍卖）SOTA 仍无单一最优，按场景选；Myerson 最优拍卖 2025 仍是理论前沿。
- **演化博弈**：replicator dynamics 做群体策略演化，开源 Python `replicator` 类可直接用。
- **课堂可用**：囚徒困境/公地悲剧/智子博弈（Prisoner's Dilemma/Tragedy of Commons/Battle of Sexes）三大经典 + Gambit 求解。

## 2. 棋类 AI SOTA
- **国际象棋**：Stockfish 17/18（开源，引擎性能天花板，本地 CPU/GPU 均可跑，显存 4G+）+ UCIO 协议做策略分析；Chess.com 在线对弈。
- **中国象棋**：Eleven 引擎（开源，GPLv3，本地跑）+ 天天象棋（在线）；象棋残局用 Lichess 残局库。
- **围棋**：Leela Chess Zero（LCZero，开源，AlphaGo 路线后继，显存 8G+ 可跑小模型）；线上用 Lizzie/WeDo 做分析。
- **德州扑克**：Liberatus 路线（CFR 算法），开源 Deep CFR（https://github.com/StanfordVision/DeepCFR）做近似均衡；教学演示用。
- **铁律**：棋类 AI 分析是"辅助思考"，不是"替你做决定"；商用/竞赛注意引擎授权。

## 3. 战略推演 / 决策树 SOTA
- **蒙特卡洛树搜索（MCTS）**：通用决策树，开源 `mcts` Python 库可直接用（alpha-beta + UCT）。
- **贝叶斯网络**：PyMC3 / Pyro（开源，概率推理），做不确定性下决策。
- **多智能体模拟**：Mesa（开源 Python 多智能体框架，https://mesa.readthedocs.io）做群体博弈/市场模拟；NetLogo（免费开源，教学首选）。
- **场景推演**：事前验尸（Pre-mortem）+ 红队分析（Red Team）两法，配合 NetLogo 多智能体跑 20 个场景。

## 4. 可落地 5 项
1. 课堂博弈演示：Gambit + 囚徒困境（3x3），30 秒出纳什均衡。
2. 棋类 AI 教学：Stockfish（国际）/ Eleven（中国）/ LCZero（围棋），开源本地跑，不联网。
3. 战略推演：NetLogo（免费，教学首选）做多智能体模拟，事前验尸 + 红队。
4. 不确定性决策：PyMC3 贝叶斯网络，开源，可教学。
5. 所有分析标注"AI 初判人工终审"，不替代决策者责任。

## 来源（访问 2026-09-27）
- https://github.com/dmeb/gambit（Gambit 开源博弈求解）
- https://github.com/NashPY/NashPy（NashPy 开源）
- https://github.com/official-stockfish/Stockfish（Stockfish 17/18 开源引擎）
- https://github.com/leela-chess-zero/lczero（LCZero 开源围棋 AI）
- https://mesa.readthedocs.io（Mesa 多智能体框架，开源）
- https://projects.iq.harvard.edu/netlogo（NetLogo 免费开源，教学首选）
- 引擎版本/许可引用前复核；教学优先开源/免费工具。
