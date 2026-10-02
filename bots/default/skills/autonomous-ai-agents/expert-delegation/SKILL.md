---
name: expert-delegation
description: "委派活体专家团执行：delegate_task 扇出回收验收。用于路由已定团时。"
version: 0.1.0
author: li-yanming, Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [delegation, expert-matrix, research, kanban]
---

# 专家团委派执行（路由表 → delegate_task 落地）

`expert-matrix-router`（user-owned，只读）只回答「归哪个专家团」；本技能回答「怎么真正调起来」——把路由结果落到 `delegate_task` 扇出、回收、验收的全流程。适用：教科研（格物致知）、中医（岐黄医典）等任何活体 agent 矩阵任务。

## 铁律
- **路由表匹配到专家 ≠ 调用了专家**。声称「交给 X 团做」而不发 delegate_task，会被用户当场纠正「怎么没调用」。判出归属当轮就扇出，不等用户催。
- **子代理自称完成不算数**：收回结果后自己 read_file 抽查交付文件的关键章节，再向用户汇报；抽查不过关就 steer/重派。
- **后台扇出的失败/完成回报可能晚于实际交付，方向双向都要核实**：(a) `ASYNC DELEGATION TASK FAILED (HTTP 429)` 早期预警常是误报——限速通常打断子代理的收尾/重试阶段，文件本身早已落盘，收讫前自己跑一遍目标模块验证产物存在且可运行，不重派；(b) 子代理也可能**迟交并覆盖**你先手写完成的同名模块（收讫消息晚到），覆盖后接口/类名可能全变，必须重验 import、`__main__` 入口、被其他模块引用的符号名是否还在，缺失的补门面/facade 层，别假设自己写的版本还在。两条共用一个判据：**任何子代理结果（声称成功或失败）落盘后，以「文件在不在+能不能跑+被引用接口是否兼容」三查为准，不以消息状态为准。**
- **429 误报后优先修接线而非重派**：子代理模块落盘后 import 失败（常见：模块在子目录 `multi_agent/<dept>/` 但主程序在仓库根、`sys.path` 没加；或解释器缺该模块依赖），先给接线代码加 `sys.path.insert` + 用**目标环境实际使用的解释器**跑通 import 自检，再判定是否需要重派。重派前跑一遍「被引用符号还在不在」的探针（`hasattr(module, sym)` 逐项），比重新生成便宜。
- **验证 live 循环的改动必须用实盘 watchdog 指定的解释器**，不用 shell 默认 python：本机实盘 `watchdog_loop.ps1` 用 `{{HERMES_HOME_PARENT}}/.workbuddy/binaries/python/envs/ate/Scripts/python.exe`（带 pandas/numpy/MT5），Hermes venv 与 WindowsApps python 都缺依赖会误导判「模块坏了」。改完先 `ast.parse` 全文件语法，再在该解释器下 import + 调一次纯逻辑入口（不连实盘）。
- **给外部实盘主循环插闸门层，坚持「叠加不替换 + 失败开放」**：CIO/风控类决策层插在信号→下单之间（`scan_all` 出提案后、`audit_and_execute` 前），返回 (blocked_set, global_block) 三元组；任何异常 → 全放行绝不断下游 VETO 链；提供 env 开关（`GOLD_CIO=0`）可回退。拦截分级：事件 HALT/风控日亏超限 → global_block 全停；个别品种被否决 → 只剔该品种。

## 流程（以课题/论文类为例，最常用）
1. 读活体 agent 定义：`{{HERMES_HOME_PARENT}}\.workbuddy\plugins\marketplaces\my-experts\plugins\<目录>\agents\*.md`——角色、质量门禁、快照格式都在这里，prompt 里引用规范不必全文抄。
2. delegate_task 扇出（可多团并行）。每个 task 的 context 必给三样：① 已有材料路径 + 「先读后写，不得推翻已有框架只补强」；② 关键证据清单（逐条带来源+年份）；③ 安全硬规矩（政策「以当地最新官方文件为准」、中医文化科普口径、AI 初评人工终判）。
3. 交付物路径在 prompt 里给死（李老师体系内固定落 `{{WORKBUDDY}}\内容中心\交付\<项目>\`，知识库沉淀落 `知识库\`）。
4. 回收后抽查 + 补子代理做不了/漏了的：最典型是 **GB/T 7714 文献 [待核] 条目**——子代理会留坑，收回后自己 web_search/web_extract 逐条补 DOI/PMID/链接，补不全的保留 [待核] 并列人工核对清单，**不得编造作者卷期**。

## 用户工作流形态（跨会话验证的稳定模式）
- **「可实行方案」= 三层闭环，缺一即被追问**：① 决策/呈现层（HTML 建议书或申报书，定调与论证）② 工具包层（评价量表/评分细则/判级线/红线动作，可独立执行）③ 表单层（知情同意书/转介单/评分记录卡/校准表，可直接打印签字）。用户说「形成一整套可实行的方案」时，按三层交付；只做第一层会被追问「量表呢/表单呢」。安全红线（识别+转介、不做诊断/处方）在三层各自复述一遍。
- **「深度优化升级」六维清单**：语言（公文/学术语体分层）、策略（加项不换项、边界原则如「三不」）、理论支撑、政策支撑（逐条核验官方文件与先例）、方法路径（可操作时间轴+负责方）、版式（玄金红 HTML + WCAG 对比度门禁）。收到「全面/深度优化」时按此清单自查，不遗漏维度。
- **色彩校验是定稿门禁**：李老师点名「调用色彩师做到最给力」时，先读活体 `color-design-master` agent 定义，再用 execute_code 算 WCAG 相对亮度对比度逐项过 4.5:1；不过就调亮交付色（如朱砂 #b23a2e→#d9705e、玉青 #5fa87f→#74c49b），再 patch 回 HTML 的 :root 变量。视频烧录层保留原色板，HTML 呈报层用升亮版。

## 大规模联网挖掘批次（delegate_task 扇出 SOTA/研究报告）
- **免费档共享池禁高并发**：子代理模型走共享免费 key 时，10 并发会在 40 秒内被 429 全灭。发车前 `hermes config set delegation.max_concurrent_children 2`，主会话亲自挖与子代理批次交替发车、错峰。
- **子任务提示词必须带限流规避模板**：「搜索只用顶层 web_search、≤6 次；每搜 1–2 次立即 write_file 分段追加目标文件（别攒到最后——攒到最后崩 429 时全文丢失）；遇 429 等 30 秒重试；禁止在 execute_code 里 import web_search/web_extract；最终文件带 frontmatter + 各节 + 非空自检再结束」。缺此模板的子代理几乎必死且不落盘。
- **429 崩 = 半截文件而非无文件**：批次收讫后对全部交付文件 grep 占位符（`待检索|待补|待补充`）；命中的节主会话亲自补齐，补不上的按公开权威框架 + 官方入口锚点写并标注「联网被拦，落地前核当年官方原文」——绝不编造 URL/文件号。
- **晚到回执先核文件再定夺**（铁律「不以消息状态为准」的延伸）：特别注意 status=failed 但子代理 JSON 里 ok:true + path 的回执——文件其实写成功了，同步装 bot 即可，不重派；只有 ok:false/无 path 才需重做。
- **sibling 中途重写同名文件后必重同步**：子代理合并时可能吸收或覆盖主会话已补的段落；任何重写后用安装器重同步所有目标 bot 副本并比对源（Python 读内容比对，不用 md5sum/cmp——CRLF 行尾差异会造成假警报）。
- **后台批量冒烟**：`terminal(background=true)` 起全量冒烟脚本 + process_manage poll；Python stdout 重定向到文件是块缓冲，日志长时间为空属正常，以 process 状态为准，别判「没在跑」。

## 跨团联用坑
中医×运动（太极/功法/体质辨识）类课题 = 岐黄医典 + 格物致知双团共管。两团会共改同一份理论层文件——prompt 里写明「patch 追加，不重写全文」；收回后抽查两个文件无互相覆盖。中医概念必须双层标注：文化阐释层（不得作机制断言）vs 现代证据层（HRV/姿态/平衡等可测变量）——这是李老师课题体系的写作红线，两团 prompt 都要带。

## 多部门智能体交易/量化系统（CIO 中枢 + 下属部门）

适用于 GoldstrategyEngine 这类「1 个 CIO 中枢 + N 个下属部门（数据管家/事件总监/研究部/交易部/风控部/盘感/操盘手）」的多智能体实盘系统：
- **新增数据源/外部 API 时坚持「失败开放 + 降级缓存」**：ForexFactory 限流 429、BLS 反爬 403、Yahoo 网络不通都是常态。任何 fetch 必须 try/except 后落本地缓存（`data/_review_mt5.json` / `external_intel.json`），主循环绝不因某源挂了而断；降级时数据可能混入脏值（`impact='Holiday'` 字符串混进数字字段），`int()` 转字段前必须 try/except 容错，否则限流降级读缓存时会 ValueError 崩掉 CIO 主链。
- **账户切换要全链同步**：风控部/操盘手/事件总监里硬编码的 `equity`（如 410/465）是账户净值的兜底值，切新 demo 账户（如 410→1000）时这些常量要全改，否则风控仍按旧净值算预算（日亏 3% 会错到 $12 vs $30）。改完用 `risk_officer` + `top_trader` 各跑一次确认预算数值已更新。
- **MT5 新账号先连探针再改预算**：用户给新 demo 账号（账号+密码+服务器）时，先写独立探针脚本（密码内嵌不外泄）连 `mt5.login + account_info + positions_get`，验证账户净值/持仓/成交后，再把风控/操盘手的 equity 硬编码切到新值。`trade_mode` 字段可辨 demo(1) vs real(0)。
- **盘感/策略路由按品种加权**：`market_intuition.py` 回测出的「盘感 WR」（如 XAUUSD/EURTRY >60%）和「盘感差品种」（<40% 负 edge）要作为缩放因子进 `top_trader`（盘感强×1.0/盘感弱×0.3），不是只做展示。小账户（<$500）下单手数 `round(x,2)` 易归零，要 `max(0.01, ...)` 保底 0.01 手。
- **数据管家（第7部门）定位**：专职对接外部数据源（ForexFactory/FOMC 官方/本地缓存），每轮 CIO 决策前 `run_steward()` 供弹；CIO 主流程顺序：数据管家→事件情报→事件总监→研究→交易→风控→放行。数据源优先级：官方 JSON 端点（FOMC）> 第三方日历（ForexFactory，有限流）> 本地缓存兜底。
