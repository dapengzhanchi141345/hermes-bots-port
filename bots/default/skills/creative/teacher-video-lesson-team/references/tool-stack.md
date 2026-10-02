# 工具栈速查（按环节）

## 录屏/录课
| 场景 | 首选 | 备注 |
| 纯 PPT 讲解零成本 | PowerPoint 自带录屏 / WPS 录屏 | 无复杂编辑需求时 |
| 长课稳定（4h+） | Bandicam | 免费版有水印 |
| 录剪一体精品微课 | 蒙以 CourseMaker | 多通道（课件/人像/语音独立对象），绿幕抠像 |
| 新手高频录课 | 数据蛙录屏 | 自动生成分享链接 |
| 屏幕讲解+轻剪辑 | Camtasia / 万兴喵影 | 喵影有语音转字幕、降噪 |
| 开源 | OBS | 需手动配编码；教师向教程参考 Joe Milne「OBS for Teachers」 |
| 浏览器零安装 | Clipchamp | Win/365 |

## 剪辑/成片
- 轻：剪映（字幕、模板、一键成片）、万兴喵影。
- 转写剪辑：Descript（删一句文字=删一段视频，口误一键清）——对「对着镜头讲」的课最省时间。
- 白板动画课：VideoScribe（手写讲解风）。

## 课件制作
- PPTX：`powerpoint` 技能（python-pptx）。
- 单文件 HTML 教学系统：`templates/interactive-course.html` 模板（本技能自带，可交互、可测验、零依赖）。
- 网页课件/视觉：`claude-design`、`popular-web-designs`；信息图/知识导图：`baoyu-infographic`、`architecture-diagram`。
- Canva：模板化课程片头/封面，免费额度 30 秒剪辑。

## 动画/演示
- 数学/物理/算法：`manim-video`（3Blue1Brown 风格）。
- 交互式拖拽/模拟：`p5js`（沙盒演示、生成式演示）。
- 化学结构/几何：`desmos` 类网页截取或 Manim 画。

## AI 视频生成（2026 模型版图 · 教学 B-roll/情境画面）
> ⚠️ **Sora 2 已日落**（2026-04-26 网页版关停、API 2026-09-24 停服）——新项目不用 Sora，迁移下表。价格按厂商变动，下单前查当期报价。

| 场景 | 首选 | 说明 |
|---|---|---|
| 默认旗舰（带对白/旁白） | Google **Veo 3.1** | 原生音频（对白+环境音一次渲染）、逼真度最强；Vertex AI / Google AI Studio |
| 长片段 + 低成本 | 快手 **Kling 3.0** | 原生 4K、Pro 档最长 2 分钟、单价最低；无原生音频，需另配音 |
| 已有素材精修/剪辑流 | **Runway Gen-4.5** | 时间线编辑+运动笔刷+换背景重打光，成片工作流最完整 |
| 二次元/风格化概念演示 | 即梦 **Seedance** | 动漫风，便宜 |

教学铁律：
1. **先脚本+分镜再开模型**——按次计费，模糊需求 = 3× 重生成成本（对应本技能第 3 步脚本产出）。
2. **一次生成多年复用**：按 单元/年级/学习目标 打标签归档进课程库；高频概念（光合作用/历史场景重现/病毒复制）最值得做。
3. **理科公式/数值画面一律 Manim，不用 AI 生成**（AI 有公式幻觉，Manim 可精确且可验证）。
4. 生成画面**给学生看前必须 `grounded-citations` 事实核查**。

## 字幕管线（Whisper + ffmpeg，免费开源，替代平台自动字幕）
平台自动字幕按整片对齐 → 随时间漂移；本地 Whisper 逐词时间戳才稳。
```bash
# 1) 抽 16k 单声道音轨（比直接喂 mp4 快且小）
ffmpeg -i input.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le audio.wav -y
# 2) 转写 SRT：锁语言 + 术语表（解专名误识别）
whisper audio.wav --language zh --model small --output_format srt \
  --initial_prompt "术语：判别式 抛物线 李彦明"
# 3) 软字幕（播放器可开关，平台上传用）
ffmpeg -i input.mp4 -i audio.srt -c copy -c:s mov_text output_cc.mp4
# 4) 硬字幕（烧录，投屏/微信场景；字号 16 起）
ffmpeg -i input.mp4 -vf "subtitles=audio.srt:force_style='FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'" -c:a copy output_sub.mp4
```
- 有显卡优先 faster-whisper（同精度 4× 速）；方言/多口音换 large 模型。
- 保留 .srt 交付（人工校对后重烧）；双语字幕行 1 原文、行 2 中文，别丢原文。

## 配音
- 免费：`text_to_speech`（edge 档，中文教学口播可用，机械感明显换下家）。
- 高级：openai / elevenlabs 档（`text_to_speech provider=openai`，需 API key；elevenlabs 有 teacher/instructor 音色库）。
- 教师自录：OBS/课程软件直接录，最自然。
- 音乐：`songwriting-and-ai-music`（Suno：「60 秒轻钢琴 lo-fi 教学背景 60bpm」类提示词）；版权安全备选 YouTube Audio Library、Pixabay Music。
- 质检：`songsee`（频谱/响度检查）。

## 平台与互动（国内）
- 雨课堂：PPT 内推题、弹幕、签到、前中后三闭环数据报表（清华+学堂在线；会员制直播）。
- 学习通：题库、签到、讨论区。
- 学堂在线：慕课资源直接插 PPT。
- 国外：Moodle/Canvas LMS 挂载、Panopto 规模化讲座捕捉。

## 复盘
- `video_analyze`：自己课例的结构/节奏报告。
- `youtube-content`：转写对标名师课例学结构。
- `grounded-citations`：知识点来源核验。
- 发布数据：B 站/视频号/YouTube Studio 的留存曲线（对照 retention.md 指标）。
