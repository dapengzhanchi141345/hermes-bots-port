---
name: suan-jing-ge-sota
description: "Use when 财会域需要引用最新政策、AI 工具与自动化方案。"
---

# 财会域 SOTA 增强技能（2024-2026）
> 检索日 2026-09-27。政策类内容以当地最新官方文件为准；引用前复核文件号仍有效。
> 注：本文件第一节（LLM 会计场景实证）在生成时未写入，已由总管会话补挖（见「一、补录」）。

# 财会域 SOTA 速查（算经阁 bot 增强素材）

> **政策类内容以当地最新官方文件为准**；以下政策条目附财政部/税务总局文件号与来源 URL（访问日期 2026-09-27）。

## 三、税务：2025–2026 中国增值税/企业所得税重要政策变动

### 3.1 增值税法正式施行（中国税制里程碑）
- **《中华人民共和国增值税法》**：全国人大常委会通过，自 **2026-01-01** 起施行，取代原《增值税暂行条例》体系，实现增值税立法。
- **《中华人民共和国增值税法实施条例》**（**国务院令第826号**，2025-12-19 国务院第75次常务会议通过，2025-12-25 公布，2026-01-01 施行）：
  - 六章五十七条；明确货物/服务/无形资产/不动产定义、一般纳税人认定、进项抵扣规则、税收优惠、征收管理等。
  - 来源: http://beijing.chinatax.gov.cn/bjswj/c104602/202512/0ca0da7237b647d0b87ec22ffc836882.shtml (访问: 2026-09-27)
  - 起草说明（山东税务转载）: https://shandong.chinatax.gov.cn/module/download/downfile.jsp?classid=0&filename=a5d549bcdd0c4a0d8643518478af8856.pdf

### 3.2 增值税优惠政策衔接（财政部 税务总局公告2026年第10号，2026-01-30）
- **小规模纳税人起征点**（2026-01-01 至 2027-12-31）：月销售额10万元 / 季度30万元 / 按次1000元。
- **小规模纳税人减按1%征收率**：除销售/出租不动产、转让土地使用权外，3%征收率减按1%（同上期限）。
- **个人出租住房**：3%减按1.5%（2026-01-01起）。
- **甲供工程建筑服务简易计税**（原财税〔2016〕36号/财税〔2017〕58号）自 2026-01-01 起停止执行。
- **在2025-12-31前制发的国内环节增值税优惠政策同时停止执行**（衔接公告第6条）。
- 来源: https://fgk.chinatax.gov.cn/zcfgk/c102416/c5247434/content.html (访问: 2026-09-27)

### 3.3 非应税交易等增值税明确事项（财政部 税务总局公告2026年第25号，2026-09-01施行）
- 明确《增值税法实施条例》第二十二条"不得抵扣非应税交易"的边界情形；同时废止 财税〔2007〕127号 第一条等。
- 来源: http://beijing.chinatax.gov.cn/bjswj/c104667/202609/127d9c6fedcb46cf8177ad13c6e44c78.shtml (访问: 2026-09-27)

### 3.4 企业所得税（落地前补核）
> 联网被限流，2025-2026 企业所得税优惠未逐项检索；申报前查：《企业所得税法》+ 财政部 税务总局 2025 年度优惠政策公告（小型微利、研发加计比例、设备器具一次性扣除等），文件号以税务总局官网当年公告为准。
- 注：2025-2026 企业所得税端重大政策（研发加计扣除延续、高新技术企业15%优惠税率、小微企业优惠等）需进一步检索确认文件号后补入。当前检索接口 403 未返回结果。

## 一、大模型在会计场景的可靠应用（实证 vs 铛头）

> 定位说明：截至 2026-09，"LLM 直接生成审计底稿/SOX 底稿"在四大所仍属试点/辅助定位，**独立出具底稿无统一实证基准**；对账、勾稽校验类规则任务有较成熟开源实现，属可实证。

### 1.1 SOX 底稿 / 审计工作底稿生成
- **实证**：四大（PwC AI & ML、Deloitte BlueTitan、EY.ai）2025 年公开案例多用于"底稿辅助起草+证据摘要"，非独立出具；KPMG Clara 平台将 LLM 用于工作底稿模板填充与异常标注。
- **铛头**：学术界"LLM 替代审计师判断"类论文（如 arXiv 2024-2025 多篇）尚处于 benchmark 搭建阶段，无 GAAS/ISA 合规认证路径。
- **可核查**：KPMG Clara 官方页 https://kpmg.com/clara (访问: 2026-09-27)；PwC AI 审计应用 https://www.pwc.com/gx/en/services/ai.html

### 1.2 对账自动化（bank rec / 往来对账）
- **实证**：`reconcile.py` 类开源脚本（pandas 金额匹配 + 容差）+ OCR 发票识别（PaddleOCR / Google DocAI）已在银行对账场景生产落地；KNIME 银行对账模板免费可下载。
- **LLM 参与**：用 LLM 做"模糊交易分类"（差旅报销/费用归集）有公开 demo，但准确率无统一基准。

### 1.3 报表勾稽校验（balance sheet / P&L 交叉）
- **实证**：`great_expectations`（数据质量断言）+ `pandas` 列关系断言 + 开源 `financial-data-validator` 类项目，规则可机验，可审计。
- **XBRL 层面**：SEC EDGAR 官方校验器（US-GAAP）成熟；国内 A 股 XBRL 校验无公开 SOTA 库。

## 二、Python 财务自动化 SOTA 工具栈（2024–2026）
（基于 2026-09-27 检索；以下为生态事实 + 可核查来源，工具名/版本稳定可核。）

### 2.1 连 ERP 取数层
- pandas + pyodbc：连 SQL Server/SAP(HANA 经 ODBC)/Oracle 的事实标准；pyodbc 4.x 自 2024 起持续维护（pypi: pyodbc）。
- 替代方案: pandas.read_sql 配 SQLAlchemy 2.0（2024 年起 SQLAlchemy 2.0 成为默认 API，`from sqlalchemy import create_engine`）。
- 定位: 稳定生产级，非实验。

### 2.2 财务 RAG（LlamaIndex）
- LlamaIndex: 财务文档 RAG 主流框架，`VectorStoreIndex` + 结构化文档（PDF 财报、审计底稿）；2025 年 LlamaIndex 推出 "Agents" 与 LLM Router，财务场景常配合 LlamaParse（PDF 解析）。
- 典型模式: LlamaIndex + pgvector/Chroma + GPT-4o/Claude → 对"某科目审计调整"做语义检索 + 原文引用。
- 定位: 生产可用（多家四大所/咨询公司 2025 年公开案例），但"财务专用 RAG 准确率"无统一公开基准，引用时需标注。
- 参考: LlamaIndex 官方 docs (docs.llamaindex.ai)；财务案例可查 LlamaIndex 博客 "Financial Document RAG" 系列。

### 2.3 XBRL 解析库
- 官方标准工具: **XBRL 实例/链接基线解析** 用 Python `lxml` + `xmlschema`；
- 社区库: **`python-xbrl`**（SEC EDGAR 官方 API 客户端，`python-xbrl-tools`）、SEC 官方 **EDGAR API**（`data.sec.gov/api/xbrl/...`，免费，无需 key，2024 起支持 JSON）；
- 中国 XBRL：财政部《企业会计准则》2024 起要求 A 股年报报送 XBRL，解析可用 `pyxb`(已停更) 或 `lxml` 手写映射；开源项目 **`xbrl-taxonomy`**（SEC taxonomy 下载 + 可视化）。
- 定位: EDGAR API 成熟；国内 XBRL 工具链较薄（铛头居多）。

### 2.4 报表勾稽校验
- 开源: **`financial-reporting-validation`** 类项目多为一行脚本（`assert bs['资产']==liability+equity`）；
- 生产级: SAP BPC / Oracle EPM 自带校验；Python 侧推荐 `pandas` 列关系断言 + `great_expectations`（数据质量断言库）做"自动化勾稽规则引擎"。
- 定位: 无单一 SOTA 库，组合使用；属"可实证"（规则可机验）。

## 四、审计抽样与数据分析（ACL/IDEA 替代）

### 4.1 KNIME Analytics Platform —— 最接近 ACL/IDEA 的免费替代
- 官方对比页: KNIME vs. ACL
  URL: https://www.knime.com/knime-vs-acl (访问: 2026-09-27)
- 要点: KNIME Analytics Platform 免费 + 开源扩展；可连 ERP/SAP/财务系统 300+ 数据源；
  嵌入 Python/R/SQL/ML 节点；替代 ACLScript；支持 LLM/Agentic AI 审计工作流；
  可审计性：版本化、审批流、LLM 使用治理。
- 定位: 生产级免费替代，**实证充分**（全球数千家企业使用，ACL 官方生态亦含 KNIME 集成）。

### 4.2 Caseware IDEA —— 市场领导者（商业）+ 内置 AI
- 官方 brochure: Caseware IDEA "Expanding the Audit Analytics Landscape"
  URL: http://insights.caseware.com/hubfs/IDEA%20brochure_Final.pdf?hsLang=en (访问: 2026-09-27)
- 要点: IDEA 已推出 **AiDA**（AI-powered digital assistant）；支持 Benford、Gap Detection、
  高级模糊去重、风险化抽样；IDEA Lab 允许用 Python + ML 开发高级插件；
  连接 50+ 会计软件（QuickBooks/Sage/Xero）；ODBC 接 PowerBI/Tableau。
- 定位: 商业工具 SOTA（非开源，但为行业基准）。

### 4.3 Python 原生审计数据分析（开源 SOTA 组合）
- 推荐栈（2024–2026 实证）: `pandas` + `great_expectations`（规则断言） + `dabl`（自动 EDA） + `arviz`/`scikit-learn`（Benford、异常检测） + `pyodbc`（连 ERP）。
- 定位: 组合生产级，无单一包；可复现、可审计（全部开源 + 版本锁定）。

### 4.4 ACL 现状
- ACL 现为 **Diligent** 旗下（原 HighBond），产品线含 ACL Analytics + ACL Robotics（RPA + 持续监测）。
- 来源: KNIME 官方对比页（同上）。

## 一（补录·总管挖掘，访问 2026-09-27）税务与会计政策 SOTA（带文件号）
> 政策类内容以当地最新官方文件为准；引用前复核文件号与有效期。
1. **增值税法正式施行（2026-01-01 起）**：《中华人民共和国增值税法》2024-12-25 全国人大常委会通过，2026-01-01 施行；配套《增值税法实施条例》+ 财政部 税务总局公告2026年第10号（优惠政策衔接）。
   - 小规模纳税人起征点：月 10 万 / 季 30 万 / 按次 1000 元（2026-01-01~2027-12-31，10号公告）。
   - 3% 征收率减按 1%、自产农产品免税、学历教育免税、技术转让/开发/咨询/服务免税延续至 2027-12-31；**停止执行**：劳务派遣、动漫、生物制品、甲供建筑等简易计税。
   - 个人住房：财政部 税务总局公告2025年第17号——满 2 年免、不满 2 年按 3% 全额征，2026-01-01 起施行。
   - 行业调整：2025年第10号（风电即征即退50% 至 2027-12-31）、第11号（黄金税收政策）；加计抵减（集成电路/工业母机 15%、先进制造 5%）有效至 2027-12-31。
   - 来源：https://www.mof.gov.cn/jrttts/202602/t20260203_3983175.htm （财政部 税务总局公告2026年第10号原文）；https://kpmg.com/cn/zh/insights/2026/02/china-tax-alert-03.html （毕马威衔接解读）
2. **企业所得税**：引用最新口径时必带文件号（如 财税〔2019〕13号研发加计 100%、小型微利税政策逐年延续公告）；AI 筹划只做测算，申报以主管税务机关核定为准。
3. **AI 会计场景实证边界**（回答子代理漏掉的第一节）：大模型做对账/底稿/勾稽校验的公开实证集中在「人机协同+人工终判」；纯自动申报/无审计复核属噱头。审计底稿生成可靠路径：LLM 草拟 + 审计软件（ACL 替代品）数据透视 + 签字会计师复核。

## 来源
- https://www.mof.gov.cn/jrttts/202602/t20260203_3983175.htm （10号公告原文，访问 2026-09-27）
- https://fgk.chinatax.gov.cn/zcfgk/c102416/c5243708/content.html （2025年第10号 风电/核电 即征即退，访问 2026-09-27）
- https://www.waizi.org.cn/tax/272580.html （2025年第17号 个人住房，访问 2026-09-27）
- https://kpmg.com/cn/zh/insights/2026/02/china-tax-alert-03.html （衔接解读，访问 2026-09-27）
