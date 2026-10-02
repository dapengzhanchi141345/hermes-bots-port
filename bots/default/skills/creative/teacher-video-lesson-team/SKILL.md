---
name: teacher-video-lesson-team
description: "教师视频备课 7 专家流水线：定题、脚本、单文件 HTML 教学系统、配音、复盘。"
version: 0.2.0
author: teacher-user, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [education, teaching, video, lesson, courseware, experts]
---

# 教师视频备课专家团

7 个专职虚拟专家按流水线协作，完成一节教学视频课的全流程：定题→教学设计→脚本→课件（单文件 HTML 教学系统）→动画→配音→合成→复盘。方法论见 `references/teaching-design.md` 与 `references/retention.md`，工具选型见 `references/tool-stack.md`，可运行的课件模板在 `templates/interactive-course.html`，模板校验脚本 `references/tests/run-template-check.mjs`。

## When to Use
- 用户是教师，要做教学视频 / 网课 / 微课 / 翻转课堂视频
- 要单文件 HTML 教学系统（互动课件、随堂测验、知识演示动画）
- 要教学视频的脚本、配音、配乐或复盘

Don't use: 一般商业视频、短视频、非教学场景。

## 专家团角色
1. **教研定题专家** — 知识点定稿、学习目标（ABCD 四要素）、前测；产出「定题书」。
2. **教学设计专家** — 脚本结构、分段、互动点位置、认知负荷检查；产出教学设计方案。依据 `references/teaching-design.md`。
3. **脚本与留存专家** — 旁白稿，带时间码、分段、模式打断点；产出 `.md` 脚本。依据 `references/retention.md`。
4. **课件专家** — 按 `templates/interactive-course.html` 生成单文件 HTML 教学系统（键盘导航、测验判分、演示动画全内置，零外部依赖）。
5. **动画专家** — 理科演示：`manim-video` 技能；交互式演示：`p5js`；图表信息图：`baoyu-infographic`。
6. **配音配乐专家** — 旁白：`text_to_speech`（edge 免费 / 有 API key 用 openai·elevenlabs）；音乐：`songwriting-and-ai-music`；音频质检：`songsee`。
7. **复盘专家** — `video_analyze` 看留存曲线；`grounded-citations` 校验知识点；`youtube-content` 转写对标课例；`weekly-review-planning` 规划下一节。

## 流水线（每步结束即有可检查产出）
1. **定题立项** — 定题书：学科/学段、知识点、可观测目标≥1、时长、前测题。✅ 目标可写成「学完后能……」。
2. **教学设计** — 结构方案：开场钩子 + 分段表（≤3 分钟/段，段落=一个概念）+ 互动点清单。✅ 每段≤3 分钟。
3. **脚本** — 旁白稿带时间码；开场前 15 秒钩子+承诺；≥每 90 秒一个模式打断。✅ 通读无长句。
4. **课件/HTML 教学系统** — 填 `templates/interactive-course.html`：标题、学习目标、≥3 页幻灯片（断言-证据式）、≥1 道自测题、≥1 段演示动画。✅ 单文件、双击即开、可投屏。
5. **动画/画面** — 按需；每段动画 ≤30 秒。理科公式/数值优先 Manim（精确可控、可验证）；情境画面/B-roll 可用 AI 生成（选型见 tool-stack「AI 视频生成」节，Sora 已日落）。✅ 本地跑通渲染。
6. **配音配乐** — 脚本→TTS 逐段生成 mp3。✅ 能播放、语速自然。
7. **合成发布** — 按 tool-stack 选录剪方案；字幕走 Whisper+ffmpeg 管线（见 tool-stack「字幕管线」，逐词时间戳），教学视频优先硬字幕。
8. **复盘** — 看曲线（前 15 秒流失>20% → 重写开场），`grounded-citations` 过一遍知识点。✅ 留存曲线截图 + 问题清单。

## 视频铁律（每片必做，最高标准）
1. **水印**：每片右下角必须带「李彦明 <PHONE>」。Manim 场景在 `Base.setup` 里 `self.add` 半透明 Text（约 40% 透明、z_index 最高）；剪辑层再用 `ffmpeg drawtext` 补一层双保险。换分辨率不丢。
2. **底色（传统文化片基准·定稿 C 玄金红）**：玄色近黑 `#0d0b10` / 宣纸白 `#f4efe2` / 亮金 `#e0b341` / 强调绿（锐化版）`#5fa87f` / 朱砂（陷阱/错误）`#b23a2e`。高对比、金字「发光」，纪录片质感，区别于市面奥数蓝绿科技风。备选护眼版 A 暖墨黑 `#17120b`（HTML 课件/长时间观看用）；金字可加轻描边更锐。
3. **字幕优先已知文案**：若旁白是自家 TTS 生成，直接用「已知文案 + 各段实测时长」等比铺时间轴生成 SRT（见 `gen_srt_known.py` 思路），比 ASR 准还省模型下载；只有录真人自录稿才走 faster-whisper 转写。faster-whisper 模型缓存损坏会报 `model.bin incomplete`——先删 `~/.cache/huggingface/hub/models--Systran--faster-whisper-*` 再重下。
4. **烧录**：逐段 `tpad=stop_mode=clone` 末帧定帧补齐到配音时长 + 0.5s，concat 拼接后用 `ffmpeg -vf subtitles=x.srt:force_style='FontSize=15,...'` 一步硬字幕出片。中文路径易 `Illegal byte sequence`，把 srt/list 复制到 build 目录用 ASCII 名再烧。
5. **抽帧终验**：成片必须 `ffmpeg -ss N -vframes 1` 抽帧 + `vision_analyze` 核「硬字幕在 / 水印在 / 中文无豆腐块 / 底色对」四项，缺一不交付。

## 质量门槛
- 脚本：段落≤3 分钟；开场 15 秒内完成钩子+承诺；禁止「同学们好欢迎收看」式片头。
- 课件：一页一个概念，元素≤6，字号≥24pt；断言-证据（标题即结论）；语音讲解优于满屏文字（modality）。
- HTML：零外链/零 fetch/零 CDN，纯离线可跑；测验有即时反馈。
- 配音：每段≤30 秒一个音频文件；edge 免费档「机械感」明显时降级为教师自录或换 openai/elevenlabs。
- 动画：理科公式/数值优先 Manim（可验证），情境画面才用 AI 生成（Sora 已停服，2026 默认 Veo 3.1/Kling 3.0/Runway Gen-4.5，见 tool-stack）；交互拖拽类优先 p5js；不确定先出 ASCII 草图确认再写代码。
- 字幕：本地 Whisper 逐词时间戳（锁 `--language zh`，专名/术语喂 `--initial_prompt`）；硬字幕字号 16 起；有显卡优先 faster-whisper。

## Pitfalls
- 段落>3 分钟 → 认知疲劳，必须拆。
- 满屏文字 + 语音念同样文字 = 冗余效应，留白改图。
- HTML 课件引了外部资源（CDN 字体/脚本/图片链接）→ 违反单文件可用原则，改为内联。
- 片头>5 秒 → 留存杀手，直接砍。
- 互动点（测验/举手/暂停思考）必须提前设计在脚本里，不能录完再想。
- 知识点未经 `grounded-citations` 校验 → 可能出错，尤其理科公式/数值。
- AI 生成的教学画面直接给学生看 → 有事实幻觉（画面漂亮≠知识正确），必须先 `grounded-citations` 核查；公式/数值画面绝不用 AI 生成（用 Manim）。
- 字幕用平台自动字幕 → 整片对齐会随时间漂移；逐词时间戳必须本地 Whisper。

## Verification
- HTML 课件：双击浏览器能跑；`node references/tests/run-template-check.mjs <course.html>` 校验通过（单文件、无外链、必需函数齐全、标签闭合）。
- 视频：`video_analyze` 出结构报告；前 15 秒留存达标。
- 交付清单：定题书 / 设计方案 / 脚本.md / course.html / 动画 mp4 / 配音 mp3 / 合成 mp4 / 复盘报告，逐项勾。
