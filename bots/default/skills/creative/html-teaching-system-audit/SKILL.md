---
name: html-teaching-system-audit
description: "Upgrade/QA single-file HTML courseware + WeChat miniprogram source delivery."
version: 1.0.0
author: Agnes
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [education, courseware, single-file-html, audit, accessibility, offline, pyodide]
---

# 单文件 HTML 教学系统 · 全面升级/体检

Class: 对一套大型单文件交互式 HTML 课件（内联全部 JS/CSS，file:// 双击即用）做缺陷修复 + 质量升级（知识点讲解、自学利用率、版面设计、无障碍、打印）。重复 id 与「面板永远显示不出来」类功能 bug、JS 完整性、离线内嵌引擎（Pyodide/WASM）取舍、a11y / 打印 / 字号基线、批量注入事故纪律是本技能的核心。

## 固定工作流（按顺序执行，每步有闸门）

0. **先学既有样板再动手（本用户铁律，第一闸门）** — 动手重做任何课件/教案/学案/练习前，先把该用户已有的**旗舰样板**（如 七/八年级 合订本 docx、workbuddy 终版 HTML）逐段读透并固化为「标准」，**先汇报学会的栏目结构，获用户点头再开工**。用户已多次因「未先学样板就开做」而判活全废。样板 docx 用 `python-docx` 逐段 dump 全量文本再读（段落常 2000-5000 行，先 grep 结构骨架再精读），HTML 用正则抽 h2/h3 标题 + 每课正文块 + `function` 名清单。汇报要落到「具体栏目名+顺序」，不是泛泛而谈。
1. **盘点与备份** — 列出目录内全部 `.html`（排除备份目录）；在**同目录**建 `备份_<标签>_<YYYYMMDD>/` 复制全部原件。后续任何事故都从备份恢复，不信任中间状态。
2. **静态审计** — 跑 `scripts/audit-html.js <dir>`（重复 id / JS 语法 / aria / 外链 / 大 base64 blob / 打印样式 / 小字号，全量扫描）+ `scripts/verify-all.js <dir>`（双闸门复核）。**不允许抽样目检替代扫描**——大文件里重复 id 藏在模板字符串与静态区交界处，肉眼会漏。
3. **缺陷分类闸门** — 把每个重复 id 判为「真 bug / 互斥模板分支（运行时只渲染一个，误报）/ 动态注入区与静态区同名（真 bug）」三类，逐条写判定理由。判定法：静态 `getElementById` 绑定与 JS 模板字符串生成的同名节点并存 → 真 bug；同一模板字符串内两个 `if/else` 分支各一个 → 误报。
4. **逐点修复 + 全量验证** — 每个修复立即过两道闸门：(a) 全部 `<script>` 块 JS 语法解析（Node `new Function`）；(b) 重复 id 复扫。闸门不过就回滚该点。
5. **批量增强走「恢复→重放」纪律** — 给多文件注入公共模块（a11y、打印样式、快捷键）时，**绝不写会向 DOM 插入带 id 节点的 JS 批量补丁**；只做纯加法文本替换（aria-* 属性、`<style>` 内 CSS 块、button 的 title/aria-label）。一旦批量注入出事：从备份恢复全部原件，只重放已逐点验证过的单点修复，再做增量增强。事故后残留标记（如注入器的版本 marker `__*PATCHED`、注入的 `a11y-*` id）必须全量 grep 清零。

## 无头验证 + schema 归一化（build 前必做）

- **无头 DOM 桩（不装 Chromium 的函数级闸门）**：用 `new Function(scriptBlock)` 把全部 `<script>` 块载入 + stub `document`（含 `addEventListener(){}`、`querySelectorAll` 返回可 forEach 的空数组、`querySelector` 按选择器分情况返回）/`window`/`localStorage`，再依次调用 `showLesson / submitEx / revealAll / resetEx / goHome / renderStats / renderBkt / renderWrong / renderBadges / exportData`，验证主路径不抛错、学情键写入 localStorage。`init()` IIFE 缺 `addEventListener` stub 会抛错——桩里必须提供。
- **正则字面量双重转义**：build 脚本用模板字符串生成 HTML，JS 正则 `\n` 被字符串转义吃掉 → `new Function` 报 `Invalid regular expression: missing /`。规则：生成 HTML 后**必须先跑 `new Function(每个 script 块)` 语法检查，再跑无头桩**；发现错误先定位哪行，不能目检。
- **练习题 schema 归一化（数据源层，build 前）**：判断题 `options=None` → 补 `['对','错']`；排序题 options 保留 A-D 索引字符串；简答/挑战题 `options` 字段一律删除。归一化在 Python merge 完 `ai_content.json` 后、build 前跑；**不要**在 build 脚本里做 `ex.options || []` 防御兜底——会把 schema 不统一掩盖到运行时崩溃。
6. **质量基线** — 对每个文件扫 aria 属性数、`@media print` 有无、5-9px 装饰字号分布，作为升级前后对照表（写进升级报告）。
7. **升级报告** — 落到课件同目录 `升级报告.md`：缺陷清单（现象/影响/修复）、保留不动项（误报理由）、验证结果、遗留可选项（等用户拍板，不擅自做）。
## 数据源 schema 归一化（子代理产出 → 前端渲染前的必做闸门）

子代理（delegate_task）批量补造/深化练习题时，落盘的 JSON 字段**不保证与既有 schema 一致**，合并进数据源后、build 前必须跑一次归一化，否则前端渲染全错。三类高频坑（实测）：
- **判断题 `answer` 是文本 "A"/"B" 而非 int 索引**：前端 `String.fromCharCode(65+ex.answer)` 拿到字母会渲染成乱码。归一化：判断题 `options=['正确','错误']`，把 answer 的 "正确"/"A"→0、"错误"/"B"→1；单选题同理把 "C"→2。写个 `for e in lessons: if type==判断/单选: e["answer"]=to_index(e["answer"], e["options"])`。
- **简答题答案藏进 `explain`、`answer` 留空**：子代理有时把参考答案写在 `explain` 字段。合并时若 `type in(简答,挑战) and answer=="" and explain!=""` → 把 explain 内容回填进 `answer`（或约定前端读 explain）。
- **`kp`（知识点）缺失**：子代理补造的新题常没有 `kp` 字段，前端 BKT/知识追踪按 kp 聚合会全丢。归一化时 `e["kp"]=e.get("kp") or f"第{lid}课·题{i+1}"` 兜底。
归一化在 Python 层做完、写回数据源后再喂 build 脚本；**不在 build 脚本里做 `ex.options||[]` 防御**（会把 schema 不统一掩盖到运行时）。

## 数据升级 ≠ 静态题卡升级（build 脚本必须重跑）

单文件 HTML 教学系统里，练习题卡片是**构建期静态预渲染**进 HTML 的（`ex-card` 由 build_html.js 模板字符串生成），JS 里的 `const LESSONS` 数据与静态题卡**两套并存**。只升级数据源/JS 数据不重跑 build → 题卡数不变（旧题量）、新模块容器插了但数据没喂。铁律：**改了数据源/题型/题量，必须重跑 `node build_html.js` 重新生成 HTML**，再注入新模块，最后 `node --check` 全量校验。验证信号：`grep -c 'class="ex-card"'` 要等于总题量（如 300），不是旧值 120。

## 正则字面量跨行陷阱（build 生成 HTML 时）

build 脚本（Node 模板字符串或 Python f-string）生成含 JS 正则的 HTML 时，正则字面量里的 `\n`（如 `s.replace(/\n/g,' ')`）会被字符串转义吃掉 → 写进 HTML 后变成**真实换行**跨在正则中间，`node --check`/`new Function` 报 `Invalid regular expression: missing /`。修复：确保正则 `\n` 在最终 HTML 里是字面两字符（`\\n` 或保持 `\n` 不被二次转义）。生成后先 `node --check` 全 script 块再跑无头桩，报错定位到哪行就改哪行，别目检。

## 课堂检测版（交卷后出分） — 练习版「即时判分+解析常驻」与检测版「作答期全隐藏、交卷统一判分出成绩单」并存

教师用户标准诉求：练习版给学生自学（随时可看答案），**检测版**用于课堂测效果（交卷前看不到任何答案/解析，交卷后出分+成绩单）。做法 = 从练习版**派生**新文件（追加在练习文件后边，练习版原样保留），注入检测补丁：
- 每作业目录生成 `<同名>_课堂检测系统.html`；标题/顶部提示条（琥珀色"作答期隐藏答案"）替换。
- 作答期：MutationObserver 移除 `.hint-btn` 里「先看答案/查看参考方向/展开解析」按钮 + 隐藏 `.analysis`；只拦截 `hint-btn` 点击（原生即时判分不拦截）。
- 交卷：右下角浮层「已答 X/N + 交卷出分」；未完成二次确认（未答 0 分）；`gradeAll()` 遍历题库判分（客观题精确、主观题按「解题思路要点」命中比例给分）；`LOCK.submitted` 防重交；交卷后锁定输入（选项 pointer-events:none / 输入框 disabled）+ 逐题 ✅/❌ 得分角标 + 正确选项绿框/错选红框 + 解锁全部解析 + 成绩单弹窗（百分制/等级/用时/各题型得分率）+「重新检测」一键重置。
- **注入方式铁律**：检测补丁必须是**独立 `<script id="AGNES_XQ">` 块**插在 `</body>` 前，绝不追加进原系统已有的 `<script>` 块——原块里的模板字符串常含 `</script>` 字样，浏览器会把补丁在第一个 `</script>` 处截断，导致补丁整段不执行、答案照旧显示（v2 事故根因）。同理，生成 HTML 内的 JS 字符串里任何字面 `</script>` 都必须拆写（如 `'</'+'script>'`）。
- 交卷 POST 学情收集器 `:8001/quiz`（报告上报老师看板）；成绩单另存 localStorage（key 含 hostname，多课件互不干扰）。
- 交卷后必须「出答案」：逐题加蓝底「参考答案：…/正确答案：X」提示条 + 解锁全部 `.analysis` 解析 + 选项绿/红框 + 解锁填空/简答输入框供订正。只判分不展示正确答案会被用户判「订正时没答案」= bug。
- **主观题判分用关键词命中法（不用「解题思路要点」精确匹配）**：旧法把 `al.解题思路` 按 ①②③/分号切出完整要点串再 `indexOf` 全串匹配 → 学生答得再对也 0 分（全答对只给 31% 的实测事故）。改法：把 `q.ans` 拆成语义段、每段抽 2-6 汉字核心词 + 短段(≤12字)整段做关键词集合（上限 12 个），学生答案小写包含几个关键词就给几档分（命中 1 个=40%，每多 1 个 +20%，>=半数命中=满分）。新法全答对 ≈ 93%（剩余差异是答案格式极特殊的题，属正常）。判分契约仍按练习版真实 `q.type/q.ans/q.al` schema 写；主观题自动给分只是**参考**，教师人工复核为准——报告里明说。
- 验证判分：写 node 桩脚本 `require` 导出的 `test_data.json`，构造「全答对」的 `userAnswers`（按题型从 `q.ans` 回填正确值）跑 `gradeAll`，核对百分制应在 90%+；若全答对应 ≈100% 却只有 30-50%，就是要点匹配过严，换关键词法。
- **作答镜像（刷新/崩溃不丢作答，交卷不出 0 分假象）**：练习版原生 `userAnswers` 只存内存（`saveProgress` 只落盘 progress 状态），学生误触 F5 / 浏览器崩溃重启后作答全丢，交卷按空作答判 0 分——「明明答对却 0 分」的第二根因（第一根因是判分过严）。检测补丁必须自维护一份作答镜像：`AK = RKEY + '_ANS'`，每 2s + `pagehide`/`beforeunload` 时把 `app.userAnswers` 快照存 localStorage，启动时 `mirrorRestore()` 回填缺失作答并 `render()`，「重新检测/换下一课」清空 `AK`。无镜像的检测版只要刷新过就交卷 0 分，用户必判 bug。
- **分发器考试泄题防护（EXAM_MODE）**：做课堂检测时，学生机 `http://IP:8000` 的文件列表里会**同时列出带答案的「练习版/融合版」和备份目录**——学生点旁边链接就查到答案。检测场景必须把分发器 `EXAM_MODE=True`：`list_directory()` 只留含「课堂检测」且不含「练习/融合版/备份/报告」的行，`send_head()` 对非检测文件与「备份」目录回 404。平时自学保持 `False`。更优做法：**用 marker 文件动态切换**（如目录里 `考试模式.txt` 内容为 1 即考试模式），分发器每次请求都读 marker——`一键启动_检测.bat` 写 1、`结束检测模式.bat` 写 0，**无需改代码、无需重启服务**，教师课后一键恢复。
- **多年级/多变体共源时 localStorage key 必须按变体命名空间**：同一套系统的七年级/八年级检测版都在同一老师 IP:8000 源下运行，若成绩单/计时/作答镜像 key 只用 `hostname` 做后缀（`XQREPORT_+hostname`），先考的年级数据会泄漏进后开的年级页面（症状：打开八年级弹七年级成绩单）。规则：key 必须带变体前缀（如 `XQREPORT_g7_` / `XQREPORT_g8_`），hostname 只用于区分学生机、不用于区分课程变体。

## 局域网分发与学情看板（微机室必做项） — 老师机两个纯标准库 Python 服务：8000 端口分发课件目录（学生机浏览器直接访问），8001 端口学情收集（`学情数据.json` 落盘 + 自动生成的深色看板页，5 秒轮询，在线判断/排序/CSV 导出）。课件 HTML 在 `</body>` 前注入协议守护的 localStorage 上报探针（file:// 静默跳过，离线能力零影响）。细节与脚本模板见 `references/局域网分发与学情看板.md`；两个服务脚本直接放课件同目录，双击即用。

## 性能 / 体验 / 落档补充（大题量检测版常用）

- **MutationObserver 去抖**：检测版作答期用 `MutationObserver` 监听新渲染的 `.q-card` 以隐藏答案/解析。题目多（几百题）时 `render()` 一次新增几百节点，observer 逐 addedNode 触发 `hideAnswers` 会逐节点全量 `querySelectorAll` 造成卡顿。做法：observer 回调里套 `setTimeout(...,120)` 去抖（已有 timer 就直接 return），把一批新增合并成一次隐藏。规则：子树 observer 回调必须去抖，别每 addedNode 各跑一次全树查询。
- **一键启动 .bat**：微课室要同时拉 8000 分发 / 8001 学情 / 8002 看班三个服务时，写一个 `一键启动.bat`（`chcp 65001` + `start "标签" python 各服务.py` 依次开三个独立窗口，顶部 echo 打印各端口 + 学生端/老师看板 URL + 「课堂检测时把 分发.py 的 EXAM_MODE 改 True」提示）。学生只输一个 IP 三个服务都在；下课关任一窗口不影响其他两个。放课件同目录，双击即用。
- **一键启动 .bat 自动提权（防火墙放行一次到位）**：微机室需要放行 8000/8001/8002 入站时，`一键启动.bat` 头部加自提权段：`net session >nul 2>&1` 失败则 `powershell Start-Process -FilePath "%~f0" -ArgumentList "%~dp0" -Verb RunAs` 后 `exit`——双击非管理员也能自动弹 UAC，用户只点一次「是」，之后 `netsh advfirewall firewall add rule ... dir=in ... tcp port=8000,8001,8002` 持久生效（规则入注册表，换 IP 也不用重放）。
- **检测成绩单打印存档**：交卷后成绩条加「🖨 打印」按钮（`window.print()`）+ 注入 `<style id="XQ-PRINT">` 的 `@media print` 块：默认 `body *{visibility:hidden}`，只放行成绩条 `.q-card` 及后代，白底黑字、`.q-card{page-break-inside:avoid}`、隐藏 `.q-card` 高亮外的挂件与 dock。教师可打印成绩单 + 每题解析存档或发家长。注意：出分报告/成绩条等展示层一律 `createElement` + 节点拼接（不嵌双引号 style 字符串），打印样式里引号嵌套同样要避。

## 判断规则（可泛化）

- **重复 id 的 `getElementById` 只命中首个节点**——这是「面板永远显示不出来」类缺陷的根源。修复时 HTML 节点与 JS 里的 `getElementById` 引用必须**同批改名**，改一半 = 功能静默坏掉且审计查不出（id 已不重复）。
- **批量脚本改多文件 = 每个文件都必须过闸门**；「在 A 文件验证过就跳过 B 文件」禁止。事故后无法定位是哪个文件哪段注入。
- **巨型内嵌引擎（如 Pyodide base64 WASM 占 19MB 文件的 15.8MB）：保留不拆**——它是 file:// 离线真跑的唯一载体（Worker 异步加载不阻塞主线程）。优化只做体验侧：引擎状态标签加启动耗时显示、loading 阶段加「约 N 秒、不阻塞学习」类 toast，把等待变成可感知进度。不追求体积。
- **字号下限 9px**：5-8px 装饰文字统一 +1px（投屏教室可读性），9px 及以上不动（保护 3D 拓扑标签、星点等装饰布局）。改前先扫分布（`scripts/audit-html.js` 的 tinyFonts 字段）。
- **打印样式缺失 = 注入 `@media print` 块**（隐藏顶栏/侧栏/挂件、白底黑字、A4 页边距）；已有打印样式的不重复注入（按 `@media print` 存在性判定）。
- **a11y 只做属性级纯加法**：`<summary>` 补 `aria-expanded`、无文本按钮补 `aria-label`/title。不新造任何带 id 的 DOM 节点。
- **内容体系不动**：BKT 知识追踪、间隔复习日历、目标-任务-证据表、提示词规范、单元大情境等教学内容是课件的底座，升级默认只碰功能 bug / 版面 / 可访问性，**不重写教学内容**。
- **融合版/主文件并存**：同一套系统若有「主文件 + 练习融合版」，每个 bug 修复必须**同步到两版**（融合版常漏修），并在报告里标注二选一建议（参赛用功能最全的一版），不擅自删版。

## 工具命令

- 备份 + 全量统计：`python scripts/backup-and-scan.py <dir>`（同目录建 `备份_升级前_<YYYYMMDD>/`，输出各文件 id/aria/字号统计）
- 审计：`node scripts/audit-html.js <dir>`
- 双闸门验证：`node scripts/verify-all.js <dir>`（语法 + 重复 id；误报在报告里标注理由）
- 注入事故后残留清理：全文件 grep 注入器 marker，确认清零。

## 配套 PDF（出书级合订本/导学单/练习）

做本用户的出书级教学 PDF（reportlab + Windows 中文字体）时，缺字形清洗、版式量化（配色/字号/结构铁律）、彩色思维导图绘制、页眉课题名动态映射、数据驱动全册生成的规范见 `references/reportlab-中文缺字形与出书级版式.md`——生成前必读母版量化值，生成后必扫空字节（豆腐块=0）与 7 项导图视觉项。

## 微信小程序源码（小橙看班类）

李老师要「可发布给真学生用」的微信小程序（班级管理/考勤/通知/课表）时，按 `references/微信小程序源码交付规约.md` 走：本地存储版先行（`utils/store.js` 唯一数据入口，云开发可无缝替换）→ 功能增强套路 → 四件套自检（JSON 解析 + node --check + pages 对账 + wx:for 有 key）→ README 含已知边界。本次小橙看班 Pro 36 文件即按此验收，零语法错误。

## 用户偏好（本用户）

- **先学样板再开工（第一铁律）**：做任何课件/教案/学案/练习/HTML 前，必须先读透用户已有的旗舰样板（docx 合订本 / workbuddy 终版 HTML），把栏目结构与顺序固化为「标准」，**先向用户汇报学会了哪些栏目、再获点头才动手**。用户反感「没学会就做、做出来的比他现有作品差」——质量下限是用户既有的旗舰作品，不是通用模板。做完要能讲清「对齐了样板的哪几段、叠了什么新东西」。
- 授权自主决策时仍要**全量验证后再报**：报告里区分「已修 / 保留不动（含理由）/ 待拍板」，遗留项列清楚让用户选。
- 产物归档进 `{{WORKBUDDY}}\内容中心\` 体系：升级报告落在课件同目录。
- 中文报告、中文 UI 文案；投屏场景字号/对比度要过教室投影仪。
- 微机室上课场景标配**局域网分发 + 实时学情看板**：学生机浏览器输老师机 IP 即用（零拷贝零安装），老师机一个深色看板页 5 秒刷新（在线状态/打开的系统/进度/星数/最后活跃时间/CSV 导出）。两个 .py 脚本放课件同目录，双击即用。用户偏好**单文件双端口融合版**（一个 `上课.py` 同时起 8000 分发 + 8001 学情收集，共用一次 UDP 探测的本机 IP，双线程 ThreadingHTTPServer，下课关一个窗口全停；仍保留两个独立脚本作兑底），见 `references/局域网分发与学情看板.md`。多服务并存时，用户要**一个 .bat 一键拉起全部服务**（见「性能/体验/落档补充」节的一键启动 .bat），不要手动逐个开窗口。
- 要「小橙看班」类**教师实时管理**（全屏/定向通知、学生回复、一键考勤、考试时钟全局同步、在线监控、检测成绩聚合）时，做成 8002 端口的独立 `看班中心.py` 服务（老师控制台 + 学生端两页，纯标准库），见 `references/看班中心实时管理.md`。

## Pitfalls

- 改 `getElementById` 引用却不改 HTML 节点（或反之）→ 功能静默失效。规则：改名必须 HTML+JS 同批。
- 批量注入脚本一次改 N 个文件再统一验证 → 出事时无法定位。规则：批量 = 每文件单独过闸门；事故 = 备份恢复 + 只重放已验证单点。
- 看到 15MB+ base64 就想拆引擎瘦身 → 拆掉就失去 file:// 离线能力。规则：先判「它是功能的唯一载体还是可外置资源」，唯一载体保留。
- 检测版注入「交卷才出分」补丁时，原生 submit-btn 仍会即时判分+存 status → 答案照样提前暴露。规则：拦截 `hint-btn` 全部点击（不看/参考/展开）+ 隐藏 `.analysis` 才是真「作答期无答案」；submit-btn 保留原生行为不动（拦截它要重写整条判分链，得不偿失）。
- 检测版判分引擎不先读练习版真实数据结构就写 → 字段名/题型判分规则全错。规则：先 grep 练习版 `renderQCard/gradeOne/q.type/q.ans/q.al` 把 schema 摸清，判分逻辑按真实字段写，写完用「构造假 userAnswers→gradeAll→核对分」桩测试。
- 检测补丁塞进原系统已有 `<script>` 块 → 模板字符串里的 `</script>` 字样让浏览器提前截断脚本，补丁静默不执行（症状：grep 得到补丁全部函数都在文件里，但页面上答案照显示、浮层不出现——grep 存在 ≠ 运行，必须真实打开页面或无头验证 DOM 结果）。规则：注入永远开独立 `<script id="AGNES_XQ">` 块；验证必须看运行态（浏览器查 `.analysis` 的 display、`.hint-btn` 是否被移除），静态 grep 只算第一道闸门。
- 生成 JS 里拼接 HTML 字符串含 `style="..."` 嵌套引号 → `new Function` 报 Invalid token。规则：出分报告等展示层一律 `createElement` + 设 `style.cssText` 拼接节点，不在单引号字符串里嵌双引号 style。
- 9px 字号继续往上提 → 装饰布局崩。规则：上调上限 9px。
- 升级报告只写「做了什么」不写「哪些没做及为什么」→ 用户无法验收边界。规则：三栏对照（已修/保留/待拍板）。
- 判断题 options=None / 排序题 options 格式不统一 → build 时 `ex.options.map` 崩溃。规则：归一化在数据源层做，build 脚本不做防御性兜底（防御性 `|| []` 会把 schema 不统一的问题掩盖到运行时）。
- 子代理补造的新题数据 schema 不齐（判断题 answer 文本化 / 简答答案藏 explain / kp 缺失）→ 前端 BKT/选项渲染全错。规则：合并进数据源后、build 前跑一次「答案索引归一化 + kp 兜底」（见「数据源 schema 归一化」节），不假设子代理产出与既有 schema 一致。
- 只升级数据源不重跑 build_html.js → 静态题卡数不变、新模块没数据。规则：改数据必重跑 build 再注入，`grep -c 'class="ex-card"'` 校验 == 总题量。
- 没先读用户既有旗舰样板就开做 → 用户判活全废、要求返工重做。规则：动手前先 dump 并逐段读透样板 docx/HTML、把栏目结构固化为「标准」、先汇报学会的内容再开工（见固定工作流第 0 步）。
- 无头桩里 `new Function` 执行含 `document.addEventListener` 的 script 块 → 桩里必须提供 `addEventListener(){}` stub，否则 `init()` IIFE 抛错。
- 跨端口 XHR 目标写成相对 URL（`S=m[0]+":8001"` 无协议）→ 浏览器按当前 8000 页面解析，心跳/交卷全部 POST 到 8000 分发器（501），学情 8001 一条数据都收不到；症状是「手动 curl 8001 正常、看板却全空」，且 **8000 访问日志里会有 `POST /IP:8001/beat` 501 行**可直接确认。规则：跨端口 XHR 目标一律完整绝对地址 `location.protocol+"//"+host+":8001"`；8001 无数据时先翻 8000 访问日志找 501 再动手。
- 服务「重启」后端口仍时有时无 → Windows 上 `allow_reuse_address` 的 ThreadingHTTPServer 允许多进程同时 bind 同一端口，旧进程未杀干净时新旧共存、请求随机分发。规则：重启前先 `netstat -ano | findstr :PORT` 列出全部 PID 逐一 taskkill，确认 LISTENING 只剩 1 个 PID 再启动，然后才声明服务就绪。
- 多线程收集服务（ThreadingTCPServer 每连接一线程）的 load/save 无锁 → 学生并发上报时各线程读旧 json 各自写回，后写覆盖先写，记录随机丢失（症状：学情数据.json 时全时缺、看板记录时有时无）。规则：模块级 `threading.Lock`，写路径用 `update(fn)` 在锁内原子完成 load→改→save，读路径也持锁；并发 30 条 `/beat` 全 200 且记录数对得上才算验证通过（见 `references/局域网分发与学情看板.md` 并发写原子性节）。
- 服务 HTML 页面引用独立 `.js`（`<script src="teacher.js">`）但服务端 do_GET 没写静态文件路由 → JS 全 404，打开页面后**整个界面没反应**且无报错（服务端日志的 404 不显眼，极易误判为前端 bug 去翻 HTML）。规则：「HTML + 独立 .js」形态的服务，do_GET 必须含 `.js/.css` 静态路由（按 `os.path.basename` 读 ROOT 下文件）；交付后 GET 每个 .js 端点实测 200 才算验证通过（见 `references/看班中心实时管理.md` 静态路由坑）。
- 分发器 `send_head` 按原始 `self.path` 判断中文文件名（浏览器实发百分号编码 URL）→ 部分编码路径 0 字节/404（症状：点课程卡片里面没内容）。规则：先 `urllib.parse.unquote(self.path)` 再判断，卡片 `href` 也 `quote(文件名)`；验证用编码 URL 实测字节数（0 字节=路径处理 bug）（见 `references/局域网分发与学情看板.md` URL 解码节）。
- 防火墙放行只靠本机 `127.0.0.1` 自测验证 → 回环不走 Windows 防火墙，自测通过 ≠ 学生机可达。规则：验证学生机链路用真实局域网 IP（学生机 curl/ping）或 `netsh advfirewall firewall show rule name=all dir=in` 确认 8000/8001/8002 入站规则存在；本机自测只能证明服务本身活着。
- build 脚本 `path.dirname(path.dirname(__dirname))` 取「上一级目录」，但 `__dirname` 已是 build/ 下 → 多了一层 dirname，ENOENT。规则：单文件数据源在项目根、build 脚本在 build/ 子目录时，用 `path.dirname(path.resolve(__dirname))`（只 dirname 一次）。
- 检测版没做作答镜像 → 学生刷新/F5/浏览器崩溃后 `userAnswers` 全丢，交卷按空判 0 分，用户判「答对的还是 0 分」。规则：检测补丁自维护 localStorage 作答快照（每 2s + pagehide 存、启动回填、重置清），判分前优先取镜像（见 检测版 节）。
- 分发器考试模式没屏蔽答案版 → 学生从文件列表点进「练习版/融合版」直接看到答案，检测失效。规则：检测场景分发器 `EXAM_MODE=True`，列表与 `send_head` 双处只放行「课堂检测」文件、对练习/融合版/备份目录回 404（见 检测版 节）。
- 可移植性扫描把题库 IP 判成「写死 IP 不可移植」→ 误报。用 `\d+\.\d+\.\d+\.\d+` 扫 HTML 会命中 IP 地址知识点的**题目文本**（如故意非法的 `256.1.1.1`、例题 `192.168.1.10`），这些在 `DATA` 题库区不是代码逻辑。规则：报「写死 IP」前先确认命中的是题库文本还是 JS 上报逻辑；上报目标只要是**从 `location.hostname` 动态算出**的（`hostname.match(/^\d+(\.\d+)+$/)` 再拼 `:8001`），换任何机房/任意 IP 都能直接用，判「可移植」。但动态算出的目标**必须带协议拼成完整绝对地址**（`location.protocol+"//"+m[0]+":8001"`）——只写 `m[0]+":8001"` 不带协议是相对 URL，被浏览器拼到当前 8000 页面路径下、全量打错端口（见下条 Pitfall）。
