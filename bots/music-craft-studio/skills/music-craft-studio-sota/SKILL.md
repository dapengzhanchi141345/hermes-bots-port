---
name: music-craft-studio-sota
description: "Use when 作曲/编曲/混音/音色设计任务需要引用最新 SOTA 工具、模型与技法。"
---

# 音乐制作域 SOTA 增强技能（2026 版）

> 检索日 2026-09-27 · 带来源。工具版本/价格引用前复核；教学演示遵守李老师护眼配色（C 玄金红/护眼备选已写入 teacher-video-lesson-team）。

## 1. AI 音乐生成 2026 SOTA
- **Suno 4/5**（商业）：prompt→完整歌曲（含人声/伴奏），当前最强一站式；人声情感表达 2025-2026 代际提升明显；商用需订阅（Pro 档）并遵守平台版权政策。
- **Udio**（商业）：与 Suno 并列头部，音质/编排细节更偏制作师；同样订阅制。
- **开源/自托管**：
  - **ACE-Step / Step-Audio**（阶跃）：开源音乐生成，10s 内片段强，本地可跑（显存 8G+）。
  - **YuE**（腾讯开源）：开源完整歌曲生成（含中文词谱对齐），显存 12G+。
  - **AudioCraft（MegaBART/MusicGen）**（Meta 开源）：非人声配乐强，本地 CPU/GPU 均可，CC 许可友好。
  - **Stable Audio 2.0**（Stability 开源）：音效/短配乐/室内声学，适合教学演示与影视配乐。
- **红线**：AI 生成音乐商用前核版权（训练数据争议未决）；教学演示优先开源（AudioCraft/Stable Audio，许可干净）。

## 2. 编曲/和声 SOTA
- **和声进行库**：Jazz II-V-I、Cinematic 四和弦（Pachelbel/50s progression）、Trap 小调 1-6-3-4；用 ChordProgressions 数据库（开源）查经典曲目进行。
- **配器 SOTA**：
  - **GarageBand**（苹果免费）：教育首选，自带鼓组/合成器/和弦生成，0 门槛。
  - **Band-in-a-Box**（Melodyne 系，商业）：自动伴奏，输入和弦即出 band，教学演示神器。
  - **Logic Pro / Studio One**（商业，Studio One 有免费版）：完整 DAW，插件生态最强。
  - **Cakewalk by BandLab**（免费 DAW）：Windows 端最强免费完整 DAW，MIDI 编辑+混音+母带，公开课首选。
  - **Ardour / LMMS**（开源）：LMMS 类 FL Studio，免费；Ardour 类 ProTools，开源录混。
- **和声辅助**：Chord（开源 Python 库）做和弦识别/转换；MIR 库（Music Information Retrieval，开源）做旋律/和声分析。

## 3. 混音/母带 SOTA
- **母带 AI**：Landr/CloudBounce（商业订阅，在线母带，教学演示够用）；iZotope Ozone 12（商业，含 AI 母带建议，制作师级）。
- **开源混音**：LMMS/Cakewalk 内建 limiter+EQ；**JUCE**（开源框架）自建插件；**LADSPA/VST3 开源插件**（TDRs 全套免费、XLN Addictive Drums 免费版）。
- **母带铁律**：教学演示用 -14 LUFS（流媒体），CD 级 -9 LUFS；先响度再做响度，别过度压缩。

## 4. 音色设计 2026
- **合成器 SOTA**：Vital（免费，形态/颗粒合成，教学首选）、Serum（商业，Wavetable 标杆）、Plogue Chips（免费，8-bit 复古）。
- **采样 SOTA**：Splice（订阅，采样+Loop+预设，在线协作）、Decent Sampler（免费高品质采样库，商用可）。
- **AI 音色**：Vocodex（开源，语音→合成）、Amphion（开源，歌声合成 TTS，教学演示）。

## 5. 可落地 5 项（教学场景）
1. 公开课演示：Cakewalk（免费 DAW）+ Vital（免费合成器）+ 自带鼓组，全免费可复现。
2. 编曲教学：Band-in-a-Box 输入和弦出伴奏（30 秒出 band），配合 ChordProgressions 库讲进行。
3. 混音母带：用 -14 LUFS 流媒体标准演示，iZotope Ozone 免费版听 AI 母带建议。
4. 音色设计：Vital 免费 + Decent Sampler 免费采样，0 预算做出教学 demo。
5. AI 生成对比：Suno（商用）vs ACE-Step/YuE（开源本地）做"AI 作曲"教学对比，强调版权红线。

## 来源（访问 2026-09-27）
- https://suno.com / https://udio.com（商用 AI 音乐生成，订阅制）
- https://github.com/stepfun-ai/ACE-Step / https://github.com/Tencent/YuE（开源音乐生成，本地可跑）
- https://github.com/meta/audiocraft / https://stability.ai（AudioCraft/Stable Audio 开源，CC 许可）
- https://www.bandlab.com/cakewalk（Cakewalk 免费 DAW，Windows）
- https://vital-instruments.com（Vital 免费合成器）
- https://decent-sampler.com（免费高品质采样库，商用可）
- 工具版本/价格引用前复核；教学演示优先开源/免费工具。
