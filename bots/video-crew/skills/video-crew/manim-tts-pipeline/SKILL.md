---
name: manim-tts-pipeline
description: "做 Manim 教学动画视频的免费管线。TTS 对齐、0.21 API 避坑、水印烧入。"
version: 1.0.0
---

# Manim 数学动画视频管线（v0.21 · Windows · 免费栈）

适用：教学/科普数学动画、公式动态演示、课堂视频。铁律：李老师水印「李彦明 <PHONE>」白色 40% 透明度右下角，**全程静态，只在 Manim 层烧入（Base.setup 里 `self.add`），绝不放 ffmpeg 剪辑层**。

## 流程（按序执行）

1. **装环境**（一次）：`pip install manim edge-tts` + ffmpeg（WinGet Gyan.FFmpeg）。Manim 渲染要 LaTeX：Windows 装 TeX Live 或 MiKTeX；缺公式字体只挂 MathTex 场景，纯几何场景能先跑。
2. **先写 TTS，再写动画**（关键顺序）：
   - 每段旁白存独立 txt：`edge-tts --voice zh-CN-XiaoxiaoNeural --text s1.txt --write-media s1.mp3`（或 python edge_tts.Communicate）。免费中文 TTS。
   - 测真实时长：`ffprobe -v error -show_entries format=duration -of csv=p=0 s1.mp3` 循环全段，**记下每段秒数**。
3. **写 Scene 时逐段对齐**：每 Scene 末尾 `self.wait(max(0, TTS秒数 - 该段动画已耗时))`。动画 run_time 之和 + 尾部 wait = TTS 秒数 ±0.3s，否则音画不同步。
4. **逐场景渲染**（别一次渲全片）：`manim -qh --disable_caching main.py S1 S2 S3` 分批，出错快定位；`--disable_caching` 防 Windows 中文路径缓存损坏。背景色 0.21 用 `self.camera.background_color = ...` 每场景设，或 CLI 传参。
5. **ffmpeg 合片**：concat demuxer 拼视频（先同规格转码 1080p30 yuv420p），`-i 各段mp3` 对齐时间轴合音轨，`-c:v libx264 -c:a aac`。
6. **交付**到内容中心对应目录，附「每段动画 vs TTS 时长表 + 总时长」。

## Manim 0.21 API 避坑表（实测全部踩过）

| 坑 | 规则 | 原因 |
|---|---|---|
| `CONFIG` 未定义 | 0.21 无全局 CONFIG；背景色用 CLI 参数或 Base.setup 里设 | 旧版教程的 `CONFIG.background_color` 在 0.21 报 NameError |
| `Rectangle(w,h)` / `RoundedRectangle(w,h)` 位置传参 | 全改关键字：`Rectangle(width=..., height=...)` | 0.21 构造签名收紧，位置传参报 multiple values |
| `Polygon([x,y], ...)` list 点 | 每点包 `np.array([x, y])` | 裸 list 触发 `broadcast (1,2) into (1,3)` |
| `Line(a,b,c,d)` 多位置参 | Line 只收两端点 + kwargs；竖线写 `Line(p1, p2)` | 多余位置参被当 start 第二维 |
| `MathTex(..., color=X)` | 改 `.set_color(X)` 链式 | MathTex 构造不收 color 关键字 |
| `Line(..., color=X)` | VMobject 构造色统一 `stroke_color=`；`set_color(x, opacity=)` 报 unexpected kwarg | 0.21 颜色 kwarg 名字分裂 |
| `CENTER` 常量 | 不存在；`align_to(m, CENTER)` 也炸，删掉或用 ORIGIN 向量算 | ManimGL/旧 API 残留 |
| `Circle(radius, color=X)` / `Ellipse(..., color=X)` | 形状构造用 `stroke_color=`；`Circle(radius, stroke_color=X, fill_color=X, fill_opacity=)` | 同上 |

**通用修法**：报 `TypeError: __init__` → 先怀疑颜色/尺寸 kwarg 名；报 `broadcast (1,2)` → 先怀疑点没包 `np.array`。

## 水印 & 出片铁律（本域专属）
- 水印在 `Base.setup`：`wm = Text("李彦明 <PHONE>", font_size=22, color=WHITE).to_corner(DR, buff=0.25); wm.set_opacity(0.4); self.add(wm)`，所有 Scene 继承 Base。
- 1080p 渲染 `-qh`（默认 60fps）或加 `--fps 30`；课堂横屏 16:9 默认比例。
- 成本：edge-tts 免费、manim/ffmpeg 本地零成本；唯一付费点 = 真人克隆音色才上付费 TTS，教学片不用。

## 交付自查
- [ ] 每段动画秒数 ≈ TTS 秒数（±0.3s），音画对齐表附交付说明
- [ ] 水印只在 Manim 层烧入，ffmpeg 层无水印滤镜
- [ ] 全部 Scene 渲染成功无黑帧（抽 3 帧目检）
- [ ] 存到 `{{WORKBUDDY}}\内容中心\课程\{主题}\`：成品 mp4 + manim 脚本 + 时长表
