---
name: expert-matrix-router
description: "按任务类型路由到李老师 39 专家团/178 子代理的正确专家与成员。"
version: 0.1.0
author: li-yanming, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [routing, experts, workbuddy, education, multi-agent]
---

# 专家团路由总控（Expert Matrix Router）

李彦明老师在 WorkBuddy 里建的 39 专家团 / 178 子代理矩阵的**路由索引**。本技能只存「任务→专家」的路由表 + 专家阵容 + 安全硬规矩；每位专家的全量详情（子角色、入口提问、内嵌技能、包体）在导出包里，需要深挖时按路径读。

- **蒸馏源（人读/机读，含全量阵容）**：`{{WORKBUDDY}}\专家团\专家团全量打包_20260920\04_专家团精读手册.md`、`05_专家元数据.json`（机器可读全量）。
- **活体目录（真运行处）**：`{{HERMES_HOME_PARENT}}\.workbuddy\plugins\marketplaces\my-experts\plugins\`（专家）与 `{{HERMES_HOME_PARENT}}\.workbuddy\skills\`（200+ 依赖技能）。
- **同类技能**：`teacher-video-lesson-team`（视频/单文件 HTML 教学系统那条流水线，本技能在媒体创作域交棒给它）。

## When to Use
- 李老师发一个任务，需要判断该唤哪个专家团/子角色。
- 要列出某个领域有哪些专家可用、怎么调。
- 跨领域任务要拆给多个专家团。

Don't use：纯视频/课件/单文件 HTML 教学系统的**制作**（直接走 `teacher-video-lesson-team` 流水线；本技能只在「路由」层交棒）。

## 路由铁律（收到任务第一动作）
1. 先判**任务核心类型**，归属必须唯一明确，第一动作就是判断归谁。
2. 判出归属**立即召唤**，不让用户催；多学科就拆给多个专家团并行。
3. 遍历后无匹配 → 直说「当前无对应专属专家，我直接处理」，不硬套、不猜「可能也适合」。
4. 教学任务再分一刀：**备课/讲解/课件 → 学科主团**；**阅卷/评分/改卷 → 对应阅卷评分官**（两者不混）。

## 路由速查表（任务域 → 专家）
| 任务域 | 召唤 | 目录 |
|---|---|---|
| 生物（教） | @万物生 | `bio-master` |
| 化学（教） | @炼金士 | `chem-master` |
| 语文（教） | @锦心子 | `chinese-master` |
| 英语（教） | @通语者 | `english-master` |
| 地理（教） | @山海客 | `geo-master` |
| 历史（教） | @史鉴君 | `history-master` |
| 道法/政治（教） | @明辨君 | `morality-master` |
| 数学（教） | @数算子 | `math-all-domain` |
| 物理（教） | @格物君 | `physics-omnibus` |
| 信息科技/编程（教） | @码智君 | `it-edu-team` |
| 10 科 **阅卷/评分/改卷** | 对应阅卷官 | `bio/chem/chi/eng/geo/his/mor/math/physics/it -grader` |
| 生物分层（基础/本科/竞赛） | 万物生·基础/进阶/前沿 | `bio-basics / bio-pro / bio-frontier` |
| 八字/风水/占卜/起名/择吉 | @天机阁 | `tianji-ge` |
| 八字精确排盘 | @命理排盘师 | `bazi-calculator` |
| 中医/中西医诊疗 | @岐黄医典 | `qihuang-medical` |
| 会计/报表/税务/审计 | @算经阁 | `suan-jing-ge` |
| 黄金/外汇/量化交易 | @金策宗师团 | `goldstrategy-guild` |
| MT5 EA / MQL5 开发 | @MT5 EA编程专家 | `mt5-ea-expert` |
| 教务/排课/学校管理 | @教务智能体 | `education-admin` |
| 职称晋级填表 | @青云梯 | `teacher-promotion-filling` |
| 课题申报/教科研/论文 | @格物致知科研智库 | `gewu-zhidao` |
| 考研（公共课+14门类） | @研枢考研专家团 | `yan-shu-kaoyan` |
| 教育IP多平台内容/分发 | @教联中枢 | `jiao-lian-zhong-shu` |
| 配色/UI 设计 Token | @色彩设计大师 | `color-design-master` |
| **视频/分镜/剪辑制作** | → 交棒 `teacher-video-lesson-team` | （视频创作团 `video-crew` 亦可作素材源） |
| AI 音乐/词曲/编曲/混音 | @音律工坊 | `music-craft-studio` |
| 棋类博弈/战略推演 | @弈谋阁 | `yimou-pavilion` |
| 电子书转电影 | @电子书转电影 | `ebook-to-movie` |

## 专家团阵容（39，按类别；子角色见手册 §3）
- **学科主团×10**：万物生/炼金士/锦心子/通语者/山海客/史鉴君/明辨君/数算子(9席)/格物君/码智君(8席)。
- **阅卷官×10**：生/化/文/英/地/史/德/数/格/信 各科 grader，各内嵌 `skill-*-grader-workflow`。
- **专项**：万物生·基础/进阶/前沿、色彩设计大师。
- **玄学**：天机阁(10宗师)、命理排盘师。
- **医疗**：岐黄医典(8专家)。
- **财会金融**：算经阁(9)、金策宗师团(9)、MT5 EA。
- **行政教科研**：教务智能体(19部门)、青云梯(7)、格物致知(6)。
- **考研/教育IP**：研枢考研(27席)、教联中枢。
- **媒体**：视频创作团(6)、音律工坊(7)、弈谋阁(5)、电子书转电影。

每个「教学主团」默认含 4 学段导师 + 1 阅卷官；主理人负责诊断水平→推路径→分步讲→出题→跨学科连接。

## 安全硬规矩（v2 升级统一执行，输出前自查）
- **涉 AI 评分**：一律「AI 初评 → 人工终判」，不假装终审。
- **涉政策/考试**：标注「以当地最新官方文件为准」。
- **涉命理/占卜**：标注「仅供文化参考，不作医疗/投资决策依据」。
- **涉交易/量化**：必须带风险提示，**不承诺收益**。
- **涉技术/知识**：每条须带可核查来源与时间，**禁止凭记忆编造**（配 `grounded-citations`）。
- **成本敏感**：优先免费/开源（Agnes API / ACE-Step / 开源 TTS）。

## 交棒与委派
- 跨领域拆多团：用 `delegate_task` 各起一个子代理扮对应专家，传足 context；汇总前**逐条核对上面「安全硬规矩」**。
- 视频/课件/单文件 HTML 教学系统：调用 `teacher-video-lesson-team`（其 7 专家流水线产出脚本/HTML 课件/动画/配音/复盘）；`video-crew`、`music-craft-studio` 作为素材/配乐源。
- 要深挖某专家的成员/入口提问/内嵌技能：读 `04_专家团精读手册.md` §3 对应小节，或 `05_专家元数据.json`（程序化）。

## Verification
- 给一个任务，能指到**唯一**专家（或明确「无匹配，我直接做」）。
- 教学任务能正确区分「主团 vs 阅卷官」。
- 输出若碰政策/命理/交易/评分，已带对应免责与「人工终判」标注。
