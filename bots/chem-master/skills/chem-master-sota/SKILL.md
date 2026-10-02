---
name: chem-master-sota
description: "Use when 化学教学/实验/竞赛任务需要引用最新 SOTA 内容与工具。"
---

# 化学学科域 SOTA 报告（2025–2026）

> 所有 URL 访问日期均为 2026-09-27。未核实处标注"未核"，不编造。

## 1. 计算化学 / 分子模拟教学工具（2025–2026）

### 1.1 Avogadro 2.0.0（开源分子可视化/编辑，教学首选 GUI）
- **版本**：2.0.0 于 2026-04-01 正式发布（GitHub tag）；1.102 为 2025-10-23 的稳定前最终 beta。
- **2.0.0 教学亮点（release notes 原文口径）**：新插件系统可用 `pixi` 一键装 20+ 插件（ML 势函数、AM1-BCC/ABCG2 电荷分配、纳米管/表面晶面、无序冰晶胞）；几何优化提速 ~50%（大分子 UFF 快 5–10 倍）；新增 AutoOpt 分子动力学模式；改进 ORCA 输入生成器（语法高亮）。
- **离线可用性**：✅ 完全离线。Windows `Avogadro2-2.0.0-win64.exe`（115 MB，累计 46562 下载）；macOS（Intel/AS）、Linux AppImage、Flatpak、Microsoft Store 均有；周更 continuous build。
- **硬件需求**：CPU/内存即可，无需 GPU；未核官方最低配置（教学机一般 4 核/8GB 足够，未核）。
- **来源**：
  - https://github.com/OpenChemistry/avogadrolibs/releases/tag/2.0.0 （2026-09-27）
  - https://avogadro.cc/install/versions/v200.html 、https://avogadro.cc/install/versions/v1102.html （2026-09-27）
  - https://pypi.org/project/avogadro/2.0.0/ （2026-09-27）

### 1.2 ORCA 6.0（量子化学，学术免费）
- **版本**：ORCA 6.0 为现行版本；6.0.1 于 2025-06 前后发布（社区 2025-09 修复其 open-shell 输出解析）。
- **教学定位**：ORCA 6.0 官方教程已指定 **Avogadro 2 为标准 GUI 路线**（旧 ORCA 自带 GUI 部分弃用）——"Avogadro + ORCA"是当前教学免费组合。
- **离线可用性**：✅ 完全离线；Windows 可经 Wine 运行（官方教程口径）。
- **硬件需求**：教学级小分子 DFT（≤~30 重原子）4–8 核 + 16GB 即可（未核官方最低值，社区教程经验值）。
- **来源**：
  - https://www.faccts.de/docs/orca/6.0/tutorials/first_steps/GUI.html （2026-09-27）
  - https://github.com/OpenChemistry/avogadrolibs/issues/2039 （2026-09-27，ORCA 6.0.1 时间线）

### 1.3 ASE（Atomic Simulation Environment，开源 Python 库）
- **版本**：现行 3.x 系列（PyPI 持续更新；具体小版本未核，引用前上 PyPI 确认）。
- **教学亮点**：Python API 对接 LDA/嵌入 DFTB/xTB/Gaussian/ORCA；`pip install ase` 可完全离线；适合"代码做分子模拟"课程（配 Jupyter）。
- **硬件需求**：纯 CPU（xTB/嵌入 DFTB 教学：2–4 核、4–8GB）；GPU 仅对特定方法有意义。
- **来源**：https://pypi.org/project/ase/ 、https://wiki.fysik.dtu.dk/ase/ （2026-09-27）

### 1.4 Gaussian 16（商业软件——无"免费教育版"，教学应改推 ORCA+Avogadro）
- **关键结论**：Gaussian Inc. 不提供免费教学版/学生版；大学 HPC 均为商业授权（签 license agreement）。个人教学机请推 ORCA+Avogadro（全免费）；Gaussian 官网可申请限时试用（需逐条核实官网条款）。
- **核数/显存事实（大学 HPC 文档，可核）**：
  - g16 共享内存并行：**仅限单节点内用核**（无 Linda 跨节点）；g16 需 CPU 支持 **AVX**（g09 不要求），AVX2 优化版单独安装；
  - NC State Hazel：`#BSUB -n 12` 单节点 12 核示例；OSC Pitzer 默认 g16c02（CUDA 版需 ECC GPU）；TACC Stampede3/Frontera/Lonestar6 已装 g16。
- **来源**（均 2026-09-27）：
  - https://hpc.ncsu.edu/Software/Apps.php?app=Gaussian
  - https://www.osc.edu/resources/available_software/software_list/gaussian
  - https://docs.tacc.utexas.edu/software/gaussian
  - https://wiki.gacrc.uga.edu/wiki/GAUSSIAN-Teaching

### 1.5 补充：Jmol/JSmol（3D 分子查看器）
- 离线可用的轻量 3D 查看器（PDB 库/晶体演示），任意低配机可跑；单文件 HTML 课件嵌入"工具结果截图/短视频"为最稳离线方案。
- 来源：https://www.jmol.org/ （2026-09-27 检索；基础功能为常规事实）

## 2. 绿色化学与实验安全教学规范（2025–2026）

### 2.1 美国二氯甲烷（DCM）管制新规 → 教学实验室去毒化
- OSHA DCM 管制四步：2025-05-05 首次监测 → 2025-08-01 暴露限值+皮肤防护 → 2025-10-30 暴露控制计划 → 2025-10 后周期监测。J. Chem. Educ.（ACS）发专评推"DCM-free 实验"：溶剂替代/无溶剂/微量化减量，用重结晶/减压蒸馏替代柱层析。
- **来源**：https://pubs.acs.org/doi/pdf/10.1021/acs.jchemed.5c00106 （2026-09-27）

### 2.2 微量化实验的安全学依据（量化结论可写进教案）
- **CUNY 有机化学 OER 手册**：Kontes 微量化玻璃器皿（25–500 mg 起始物料，溶剂 mL 级）比 macro 减废 90–99%；"10 mL 乙醚泼溅=火灾风险，100 mL=爆炸风险"——事故严重度随规模放大；逐条对应绿色化学 12 原则（#1 预防、#5 更安全溶剂、#12 本质安全）。
- **来源**：https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=1051&context=nc_oers （2026-09-27）

### 2.3 国际趋势（2025 会议级证据）
- **ChemEd2025 微量化专题报告（Myllyviita，2025-07-22）**：四大优势=安全/环境/成本/储存简化；新趋势：微量化+廉价塑料器皿+厨房化学试剂 → 实验可迁移家庭/混合式/远程教学；瓶颈：教材未微量化、教师需再培训。
- **来源**：https://myllyviita.fi/presentations23/ChemEd2025_MicroscaleChemistry_Myllyviita.pdf （2026-09-27）
- **ACS 案例（2025 在线）**：微量化滴定替代铬酸钾指示剂（欧盟限制六价铬；美国 TSCA 90 项评估名单含铬酸盐）——磷酸氢盐+百里酚蓝替代，已教学验证（北欧高中）。
- **来源**：https://pubs.acs.org/doi/pdf/10.1021/acs.jchemed.5c01288 （2026-09-27）

### 2.4 定性分析"去毒"低毒替代清单（2025 综述）
- H₂S 替代（Sidhwani & Chowdhury 系列）；borate 用**姜黄纸**替代甲醇/浓硫酸法；fluoride 用**硫氰酸铁褪色法**；半微量（5 mL 试管/1 mL 样液）替代 20 mL 体系，试剂耗量降 5 倍。
- **来源**：https://doi.org/10.11648/j.mc.20251304.11 （2026-09-27）

### 2.5 美国州级安全规范（K-12 实验室基准）
- 华盛顿州 OSPI《K-12 健康与安全指南》Section K：法定化学卫生/通风/标签标准，明确"绿色化学框架：更安全替代物、微量化减废、降低暴露"；硬件基准：洗眼器/淋浴室 10 秒可达、每周检查，通风橱面风速恒定，易燃品 A2 级灭火器，按相容性分柜，每学期库存审计。
- **来源**：https://content.govdelivery.com/accounts/WAOSPI/bulletins/3f510ba ；https://campusresources.blog/chemistry-labs-high-school-hybrid-guide （均 2026-09-27）

### 2.6 中国侧规范现状（诚实标注）
- 国内"微量化实验/绿色化学"已写入《普通高中化学课程标准》及高考实验题情境，但本轮限流检索未获 2025–2026 专门发文原文；引用国内条款前须核实教育部/省教研 2025 公开文件，不做臆断。

## 3. 高考化学新题型考法 SOTA（2025–2026）

### 3.1 官方评析口径（直接可进课件）
- **来源**：教育部教育考试院《2025 年高考化学全国卷试题评析》（https://gaokao.eol.cn/shiti/hx/202506/t20250608_2673356.shtml ，2026-09-27 访问；转载 https://www.163.com/dy/article/K1HJO1F605268MTU.html ）。
- **三大命题特征**：① 真实情境+素养立意（贴近生活/科技场景，基础性与应用性并重）；② STSE 进题（PLGA 生物材料、电解处理废水/废塑料碱性水解液、蛇纹石资源综合利用/碳中和等中国现代科技成果素材）；③ **工业流程题+资源循环为大题主线**（原料→提纯→合成→尾气/废液处理串联，嵌入绿色化学与可持续发展）。
- **备考打法**：按四素养（宏观辨识与微观探析/变化观念与平衡思想/证据推理与模型认知/科学探究与创新意识）重组复习；工业流程题三段式模板（读图→每步反应原理→绿色追问：原子经济性/三废）；结构测定（核磁/质谱/晶体结构）用真实物质案例（新材料/医药中间体）替代纯记忆晶体。

### 3.2 新高考批次与地区口径
- 2025 年起**第五批新高考改革**：陕西、宁夏、青海等（"四省联考"体系；逐题解析见 bilibili 合集 https://www.bilibili.com/video/BV1pnwZeaEUj/ ，2026-09-27 访问）。各新高考省独立命题，考法以本省考试院 2025–2026 文件为准，不跨省套用；老高考省份理综化学仍用全国卷评析口径。

### 3.3 分题型 SOTA（带地区）
- **工业流程题**：全国卷主线（3.1 特征③）；命题素材从"传统冶金"转向**绿色循环/碳中和场景**（蛇纹石综合利用等），答题必须含"三废处理/原子经济性"追问。地区差异：新高考省（山东/广东/湖南等）独立命题，需按本省卷评析建档。
- **结构测定题**：核磁/质谱数据读取+晶体结构判断；SOTA 趋势为**新材料/医药中间体真实情境**（非纯记忆）；IChO 理论真题（结构推断类）为命题源头参照，官方真题库 https://www.ichosc.org/ （2026-09-27 访问）。
- **实验探究**：控制变量/定量测定题型；微量化与低毒替代进入实验情境（呼应第 2 节 2.1/2.3 趋势）；IChO 57（2025）首次**电子考试**（加密阅读显示器看题，5h 理论+5h 实验）——高考实验题的"数字化情境"趋势同源，命题组素材可借鉴。
- **落地前补核清单（联网 403 未检索项，申报/命题前逐项核官方原文）**：① 2025 全国甲/乙、新高考 I/II 卷逐题命题分析（地区到省）；② 2025 秋学期各省期中考"工业流程题"是否出现真实企业案例；③ 结构测定题是否出现新晶体/衍射数据读图；④ 实验探究"控制变量/定量测定"占比对照 2024 卷。

## 4. 化学竞赛（省级/CChO/IMO）2025–2026 备赛方法

### 4.1 IChO 57（2025，迪拜）赛事事实（可核查）
- 2025-07-05 至 07-14，92 国 354 人；**5h 理论+5h 实验**；40 金/73 银/107 铜。
- **中国队 4 金**：宋子璐（总第 1）、杜贤（第 3）、赵耀希（第 5，**理论单科第 1**）、刘莫涵（第 12，长沙长郡）；导师：北大裴坚/郑洁、中大李乐（观察）、武大刘雨文（观察）。
- **赛制新变化**：本届**首次电子考试**（每人加密阅读软件显示器看题）——备赛后期须加屏幕全真模拟。
- **IChO 58**：2026-07-10 至 07-19，乌兹别克斯坦；参赛费 3000 USD/队。
- **来源**：
  - https://www.chinesechemsoc.org/do/10.5555/a7ee0656-6393-4ef0-b1f6-fec7da62de5a/full/ （CCS 官方，2026-09-27）
  - http://enghunan.gov.cn/hneng/News/Localnews/202507/t20250716_33741259.html （湖南省政府）
  - https://voc-gj.cast.org.cn/index/info?api=GwArticle&id=40646 （电子考试细节）
  - https://www.ichosc.org/ （IChO 58 日期/费用）

### 4.2 CCO/CChO 选拔漏斗与赛制（备赛路线图）
- **时间线**（约 10 个月）：省级初赛（9 月初）→ 全国决赛（10–11 月旋转城市；**2025 年 39 届恢复实验环节，约 610 人**）→ 冬训营（12 月–1 月，约 50 国集）→ IChO 代表队 4 正式+2 替补（3 月公布）。
- **赛制**：理论 4h/100 分，10–13 道大题（禁计算器，给周期表）；实验 4–5h/约 60 分（占总分 40%），滴定/无机定性/有机合成/仪器测定，扣分制。
- **2025 漏斗**：预赛 >17 万人 → 约 2400 一等奖 → 约 600 决赛 → 约 32.2% 金 → 约 50 国集。
- **来源**：https://grokipedia.com/page/chinese_chemistry_olympiad （2026-09-27；数据为聚合口径，引用时用 CCS 官网二次核对届次）

### 4.3 备赛方法（可操作清单）
1. **理论**：IChO 考纲主线（热力学/动力学/配位/有机机理/谱学），历届 CCO+IChO 真题限时训练；每题拆子步+量纲核对（热力学单位陷阱、谱学误读为高频失分点——《大学化学》CCO 真题分析栏目 https://ccspublishing.org.cn/article/doi/10.3866/PKU.DXHX2016100121 ，2026-09-27）。
2. **实验**：决赛/冬训已恢复实验（约 40% 权重），练滴定精度/未知物鉴别/仪器操作/扣分制实验报告。
3. **信息题（2025-2026 趋势）**：新文献阅读+推断计算题权重上升——每日 1 篇文献精读 SOP，练"读论文抓关键数据"。
4. **分阶段**：基础 3 月 → 题型专项 3 月 → 真题冲刺 2 月；每周限时套题+错题按"计算/推断/实验"三类归因。
5. **电子化适应**（新赛制）：备赛末期至少 3 次屏幕全真模拟（5h 理论+5h 实验）。
6. **起点与资源**：多数强者 15 岁左右系统起步；历届 CCO 真题（1990s 起公开汇编）+《冲刺金牌：高中化学奥林匹克教程》（孙希莉等）+ 竞赛 MOOC/论坛模拟卷；竞赛日程以当年中国化学会/教育部通知为准。

### 4.4 AI 相关（教学引用，非备赛刚需）
- arXiv 2511.16205《ChemLabs on ChemO》：以 IChO 2025 题构造多模态基准 ChemO；AER（画分子→SMILES 生成改写）+SVE（结构化视觉描述）；Gemini-2.5 Pro 多智能体 93.6/100（估算超金牌线）；结论：视觉感知是 MLLM 主要瓶颈。
- **来源**：https://arxiv.org/pdf/2511.16205 （2026-09-27）

## 可直接落地的 5 个升级项
1. 炼金士·高考席加"2025 官方评析三大特征+STSE 答题模板"复习卡（第 3.1）。
2. 工业流程题三段式（读图→反应→绿色追问）做成单文件 HTML 刷题系统（file:// 离线）。
3. 结构测定/分子模拟课堂用 Avogadro 2.0.0+Jmol 离线演示包（截图+短视频嵌入，无网可用，第 1 节）。
4. 竞赛组加"文献信息题"每日 1 篇精读 SOP + 电子考试模拟（第 4 节）。
5. 实验安全课嵌入第 2 节微量化量化依据（减废 90–99%、事故随规模放大）与低毒替代清单（姜黄纸/硫氰酸铁）。

## 来源汇总（访问 2026-09-27）
- 高考：https://gaokao.eol.cn/shiti/hx/202506/t20250608_2673356.shtml ；https://www.163.com/dy/article/K1HJO1F605268MTU.html ；https://www.bilibili.com/video/BV1pnwZeaEUj/
- 工具：https://github.com/OpenChemistry/avogadrolibs/releases/tag/2.0.0 ；https://avogadro.cc/install/versions/v200.html ；https://www.faccts.de/docs/orca/6.0/tutorials/first_steps/GUI.html ；https://pypi.org/project/ase/ ；https://hpc.ncsu.edu/Software/Apps.php?app=Gaussian ；https://www.osc.edu/resources/available_software/software_list/gaussian
- 绿色化学/安全：https://pubs.acs.org/doi/pdf/10.1021/acs.jchemed.5c00106 ；https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=1051&context=nc_oers ；https://myllyviita.fi/presentations23/ChemEd2025_MicroscaleChemistry_Myllyviita.pdf ；https://doi.org/10.11648/j.mc.20251304.11 ；https://content.govdelivery.com/accounts/WAOSPI/bulletins/3f510ba
- 竞赛：https://www.chinesechemsoc.org/do/10.5555/a7ee0656-6393-4ef0-b1f6-fec7da62de5a/full/ ；https://www.ichosc.org/ ；https://arxiv.org/pdf/2511.16205 ；https://ccspublishing.org.cn/article/doi/10.3866/PKU.DXHX2016100121
