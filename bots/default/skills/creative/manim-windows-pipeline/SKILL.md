---
name: manim-windows-pipeline
description: "Use when 在 Windows 批量渲染 Manim 教学视频。0.21/中文路径/TTS/字幕管线坑。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
---

# Manim 教学视频 Windows 批量出片管线

Class: multi-episode Manim teaching videos on a Windows host with Chinese delivery paths — setup, render, TTS, SRT, stitch, burn, verify. For the pedagogy/script/coursware side of a lesson, use `teacher-video-lesson-team`; this skill is the Windows production half.

## Pipeline order
1. **Setup** (once per machine): `uv venv venvs/manim --python 3.11` then `uv pip install --python venvs/manim/Scripts/python.exe manim pango`. No LaTeX needed if all text goes through `Text` (Pango) instead of `MathTex` — check CJK fonts exist in `C:\Windows\Fonts` first.
2. **Shared base module** for series: one `kbase.py` holding palette constants, a `Base(Scene)` with `camera.background_color` + a global watermark `Text` added in `setup()` (so every episode inherits it), and shared mobject helpers. Each episode file imports it — no per-episode palette/watermark code.
3. **Per-episode scene file + JSON**: scene file with static `Scene` subclasses; a JSON `{"name":..., "segs":[{"vid": <exact scene class name>, "text": <narration>}]}`. `vid` MUST be the full class name — Manim outputs `E1_Hook.mp4`, not `E1.mp4`; a short name silently breaks the pipeline's file lookup. Before TTS, hand-compute every number in both the scene labels and the narration (quotients, coefficients, roots, magic-square sums) — hard subtitles make arithmetic errors invisible, students hear them anyway; if a number is wrong, fix the scene AND the narration together so they stay in sync.
4. **Render**: `-ql` (480p) all scenes first to shake out API errors; then `-qm` (720p30) final. Render scenes **one command at a time** instead of batching five in one `manim render A B C D E` — the encoder fails intermittently (ExternalError mid-batch) and per-scene runs localize the broken scene without re-rendering survivors.
5. **Assemble** (one pipeline script per episode JSON): per segment — TTS mp3 → duration probe → `tpad=stop_mode=clone` pad video to audio +0.5s → concat → burn SRT → final mp4.
6. **Verify**: `ffmpeg -ss N -vframes 1` stills at 2–3 timestamps, vision-check four items: hard subtitles present, watermark present, CJK not tofu, background color correct. No delivery without this.

## Manim 0.21 API breakages (tested on 0.21.0)
- `align()` removed → `align_to()` or coordinate `set_x/set_y`. Same for `VGroup.align()`.
- `DrawLine` removed → `Create(line)`.
- `Polygon`/`Line` vertices must be **3D** — a 2D list like `[0,0]` or `[x-0.25,0]` dies with `ValueError: could not broadcast input array from shape (1,2) into shape (1,3)`. Pass 3D: `ORIGIN, RIGHT*3, UP*4` for Polygon, `[x,0,0]` for Line endpoints / shifts. A 2D coordinate that happened to work on an older manim will crash the first 720p render.
- `Mobject.__init__` takes **no custom kwargs** — `VGroup(frame, beam, digit=5)` raises `TypeError: ... unexpected keyword argument 'digit'`. Build the group plainly, then assign: `g = VGroup(frame, beam); g.num = digit`.
- A **zero-length arrow** `Arrow(pt, pt)` renders as a tofu box (missing-glyph glyph), not an arrow — don't build arrows from a mobject's own center to itself. For a word→word chain, join with `Text("→")` separators in a single `arrange(RIGHT)` row instead.
- Scene classes must be **static** in the module: dynamic registration (`globals()[name] = SceneSubclass` in a factory) is blocked by Manim's module importer (`module_ops` errors at render). For parameterized variants (e.g. 5 color palettes on one scene), write 5 explicit classes or 5 files.
- These surface as `AttributeError: ... has no attribute 'align'` on the first 720p render even though `-ql` passed layout checks — run a full `-ql` pass over ALL scenes before committing to 720p.

## Windows + Chinese paths: the ASCII-workspace rule
ffprobe/ffmpeg on this host fail on Chinese path segments (`Illegal byte sequence` from MSYS layers, exit codes like 2880417800 from native ffmpeg). Therefore:
- Run TTS, concat, and subtitle-burn entirely inside a pure-ASCII temp workdir (e.g. `{{HERMES_HOME_PARENT}}\AppData\Local\Temp\epXX_work\`), with ASCII filenames (`subs.srt`, `raw.mp4`, `list.txt`).
- Burn subtitles with `cwd=<build dir>` and **relative** srt name (`subtitles=subs.srt:...`) — an absolute Chinese path in the filtergraph fails.
- Probe durations with **ffprobe**, never `ffmpeg -show_entries` (ffmpeg doesn't have that syntax; the call dies with a huge exit code that looks like a path bug but isn't).
- Deliver via Python `shutil.copy2` into the Chinese target dir — shutil handles Chinese fine; only the ffmpeg/ffprobe binaries don't.
- Mixed-slash paths (`C:/...\sub.mp4`) also break native ffmpeg — normalize to forward slashes before handing to ffmpeg/ffprobe.

## edge-tts CLI pitfalls
- Transient network failures (exit 1, "No audio received") are common; the step is idempotent because already-generated per-segment mp3s are skipped on re-run — just re-invoke the pipeline, don't re-author.
- Invoke via global Python (`python -m edge_tts`), not the Manim venv (which lacks the package).
- **Do not pass `--rate` with `%`**: `-4%` either gets cmd env-var expansion (`%%` errors) or argparse misparses it; omit rate entirely (default pace is fine for teaching) unless a plain value works.
- Chinese output paths fail: write input txt + output mp3 to an ASCII tempdir, then `shutil.move` to the real location.
- Chinese text files must be written UTF-8 explicitly.

## Narration-synced SRT without ASR
When narration is generated TTS from known scripts, skip Whisper entirely: take each segment's measured mp3 duration, lay the exact narration text over it proportional to character length (split at CJK punctuation, ≤16 chars/cue). Result is 100% accurate subtitles with no model download; faster-whisper is only for human-recorded audio, and a corrupt model cache shows as `model.bin incomplete` — delete `~/.cache/huggingface/hub/models--Systran--faster-whisper-*` and re-download.

## Pitfalls recap (each cost real time)
- Math errors in scene labels / narration (wrong coefficient, quotient, or root) → rework after TTS; verify all numbers by hand before generating audio, keep scene and narration in sync.
- Mass-batching 15+ episodes then finding a systematic error → re-render everything; render + pipeline the 2nd episode, vision-verify it, only then batch the rest.
- edge-tts network flake mid-batch → re-run the pipeline (idempotent); don't treat exit 1 as fatal.
- Batched `manim render A B C` with an intermittent encoder failure → re-rendering everything; render per-scene.
- `vid` in JSON as short name → pipeline can't find `E1.mp4` (actual file `E1_Hook.mp4`); use full class names.
- Chinese absolute paths in ffmpeg filtergraphs / ffprobe args → use ASCII workdir + relative names + shutil delivery.
- `ffmpeg` used as duration probe → ffprobe.
- Factory-registered Manim scenes → static classes only.
- `-qm` rendered before `-ql` passed all scenes → fix the batch cheaply at 480p first.
