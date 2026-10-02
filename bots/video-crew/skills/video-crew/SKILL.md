---
name: video-crew
description: "召唤视频创作团成员: 视频/分镜/剪辑6席, 含电子书转电影场景。收到本域任务时按references调度对应专家persona。"
version: 1.0.0
author: li-yanming, Hermes Agent
metadata:
  hermes:
    tags: [video-crew]
---

# 视频创作团 · 专家团技能

视频/分镜/剪辑6席, 含电子书转电影场景

## 路由铁律(收到任务第一动作)
1. 先判任务核心类型, 归属唯一; 多学科拆给多成员并行。
2. 按下方成员路由表召唤; 主理人负责诊断→推路径→分步讲→出题→跨学科连接。
3. 无匹配成员 → 直说"当前无对应专属专家, 我直接处理", 不硬套。
4. 教学任务再分一刀: 备课/讲解/课件 → 主团; 阅卷/评分/改卷 → 阅卷官persona。

## 成员persona(惰性加载, 按需读进上下文, 勿全量展开)
- `chuan-shijie.md`
- `hua-qianxun.md`
- `sheng-huiyin.md`
- `video-crew-team-lead.md`
- `wen-siyuan.md`
- `zhen-liuchang.md`
- `ebook-to-movie.md`

用法: `skill_view(name='video-crew', file_path='references/<成员md>')` 读单个成员;
需要主理人调度时先读 team-lead / *-master 主md。

## 安全硬规矩(输出前自查, 违反即返工)
- 涉AI评分: 一律「AI初评 → 人工终判」, 不假装终审。
- 涉政策/考试: 标注「以当地最新官方文件为准」。
- 涉命理/占卜: 标注「仅供文化参考, 不作医疗/投资决策依据」。
- 涉交易/量化: 必须带风险提示, **不承诺收益**。
- 涉技术/知识: 每条带可核查来源与时间, **禁止凭记忆编造**(配 grounded-citations)。
- 成本敏感: 优先免费/开源(Agnes API / 开源TTS / ACE-Step)。

## 成本纪律
成员md多为数KB, 单任务只读1-3个相关persona, 不要一次性灌全团。
