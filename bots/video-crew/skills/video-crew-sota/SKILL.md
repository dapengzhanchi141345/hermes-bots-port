---
name: video-crew-sota
description: "Use when 视频/分镜/剪辑/AI视频制作任务需要引用最新 SOTA 模型、工具与成本口径。"
---

# 视频创作 SOTA 增强技能（2026 版）

> 检索日 2026-09-27 · 带来源，引用前复核仍有效。成本敏感：开源/自托管优先；成品遵守李老师视频铁律（右下角白色40%水印「李彦明 <PHONE>」全程静态，在 Manim Base.setup 里 add，勿在剪辑层烧）。

## 2026 关键格局（先记住这几条，选型直接看）
1. **Sora 2 已下线，别建在它上面**：OpenAI 于 2026-03-24 宣布退出，sora.com 应用 2026-04-26 关停，API 2026-09-24 日落。老工作流一律迁到 Veo / Kling / Runway / Seedance。（多源一致：josenobile / imagineclip / techsy / bigbangindex）
2. **原生音频 = 前沿基线**：Veo 3.1、Kling 3.0、MiniMax H3、LTX-2.5 同一次前向就出同步音（对白/音效/环境声），唇形对齐。有人口说话的片子，音频支持优先于 0.5 档分辨率。
3. **4K 已成入门，战场转向长时长时间一致性**：Kling 3.0(4K 60fps 16bit HDR)、LTX-2.3(4K 带原生音频)、Runway Gen-4.5(4K) 都在 4K。
4. **开源中心重镇已转移**：一年前是 Wan 2.1 LoRA，现在是 **MiniMax H3**（33B 原生立体声、到 2K、4-15s、ComfyUI 官方工作流+LoRA/步蒸馏生态，社区可商用）；开源可跑组合 = **Wan 2.2 / HunyuanVideo 1.5 / LTX-2.3 / Mochi 1 / CogVideoX**。

## 选型决策树（按场景，直接抄）
| 场景 | 首选 | 理由 |
|---|---|---|
| 全能/要音质要 4K | Google **Veo 3.1** | 原生音频+4K+prompt 遵守最强；Standard $0.40/s、Fast $0.10/s、Lite $0.05/s |
| 性价比/多镜头叙事 | **Kling 3.0** | ~$0.08-0.13/s，llm-stats 榜首，多镜头音轨连续，发丝/液体/织物好 |
| 图生视频 I2V | **Seedance 2.0** | I2V 盲测第一(1,219 Elo)，8+ 语言唇动，广告口播强 |
| 纯本地免费无限跑 | **Wan 2.2 / LTX-2.3 / Hunyuan 1.5 + ComfyUI** | 只花电费；Wan 2.2(Apache2.0)写实人脸最佳，24GB 可量化到 8-16GB |
| 零预算商用 | 自托管 | 唯一诚实答案；Kling 免费档标注不可商用 |
| 口播/数字人 | HeyGen / Synthesia | 不是生成模型，是分身合成 |

## 开源本地栈（李老师有 GPU 时）
- 模型全在 HuggingFace 可下，全部 ComfyUI 一等公民节点。
- 单卡显存口径：LTX-Video 最快(实时 5s 768x512)；Wan 2.5 24GB 离载可跑 1080p、48GB 稳；Hunyuan 全精度 60GB、FP8+离载 24GB；Mochi 1 动效好；CogVideoX 最易微调/训 LoRA。
- 集成路径：闭源 API 走 Runway SDK / google-genai / openai SDK（都是提交 job→轮询→下载）；开源自托管走 ComfyUI（REST API 可无头跑管线）。

## 成本口径（预算用）
- 前沿带音频单镜：4 次生成出 1 可用镜 ≈ $3-13；Fast/开权重单镜 <$1。
- 本地盈亏平衡：约 500-2000 条视频后自托管赢（取决于 GPU 与闭源价）。
- 教学/低成本迭代首选开权重；旗舰交付用 Veo/Lite 档控成本。

## 分镜→出片标准流程（bot 可复用）
1. 写分镜脚本（每镜：景别/运镜/首帧/对白/时长）→ 2. 关键镜用图生视频锁首帧（保角色/品牌一致）→ 3. 生成→按音频是否原生决定要不要后期 TTS/混音 → 4. Premiere/DaVinci 剪 + 烧李老师铁律水印（Manim 层，勿剪辑层）→ 5. 成本记录（每镜几次生成）。

## 来源（访问 2026-09-27）
- https://creativeainews.com/articles/ai-video-generation-complete-landscape-2026
- https://ocdevel.com/mlg/mla-26 （2026 ML Podcast：Sora 退场、Veo/Gemini Omni、开权重中心 H3）
- https://josenobile.co/guides/video-generation （Sora 2 迁移源、开源五模型、ComfyUI 管线）
- https://techsy.io/en/blog/best-ai-video-models （11 模型 arena 排行 + VRAM 表）
- https://bigbangindex.com/blog/best-ai-video-generators-2026 （Sora 关停 + 免费三档辨析）
- https://imagic-ai.com/blog/ai-video-generator-comparison-2026
- https://github.com/JeremyGDM/imagineclip-ai-video （模型/工具清单）

> 免责：本技能为技术选型参考，不承诺任何商业收益；模型版本与价格变动快，出片前复核官方定价。
