# Agnes vendor specifics

## Topology (verify current state before relying on it — keys can be reissued)
| pool (config `providers.`) | endpoint | .env var | role |
|---|---|---|---|
| agnes-flash | api.agnes-ai.cn/v1 | AGNES_FLASH_API_KEY | primary text (credential pool = FLASH + MEDIA keys, auto-rotate) |
| agnes-reason | api.agnes-ai.cn/v1 | AGNES_REASON_API_KEY | heavy inference; historically ¥0 quota — keep OUT of rotation pools until recharged |
| agnes-media | api.agnes-ai.cn/v1 | AGNES_MEDIA_API_KEY | image/video key; ALSO rotated in the agnes-flash credential pool |
| agnes-main | apihub.agnes-ai.com/v1 | AGNES_MAIN_API_KEY + manual pool keys | .com rotation pool — 7 credentials: #1 legacy config key + six manually added .com keys (labels `com-`+first-4-of-key), auto-rotate on 429/503 — verify count with `hermes auth list agnes-main` |
| (legacy) | .com | AGNES_API_KEY | same key as AGNES_MAIN_API_KEY (check by fingerprint); is credential #1 of the agnes-main pool |

- `.cn` and `.com` keys do NOT authenticate across endpoints (401). Never mix them in one pool.
- `.com` free tier has a low text RPM per key (vendor cut it 50% recently); pool rotation multiplies effective RPM by credential count. If rate limits are account-level (same-account keys share quota), rotation spreads RPM but NOT total quota — watch event digests for sustained 429s across the whole pool; that is the signal to stop adding same-account keys.

## Docs
- Index: `https://wiki.agnes-ai.cn/llms.txt` (Mintlify; every page is also at `<page>.md` — curl-friendly, no JS). International mirror: agnes-ai.com.
- Per-model API reference pages: `agnes-video-v20.md`, `agnes-video-25.md`, `agnes-video-25-flash.md`, `agnes-image-*.md`.

## Video model parameter contracts (never share params across models)
Common: `POST /v1/videos` create → poll `GET {base}/agnesapi?video_id=<id>[&model_name=<model>]` (model_name REQUIRED for keyframe/reference modes). Terminal status: `completed`/`failed`.

| | agnes-video-v2.0 (RETIRED — vendor deprecated it; the agnes plugin auto-routes to 2.5-flash) | agnes-video-2.5 | agnes-video-2.5-flash |
|---|---|---|---|
| duration | `num_frames` (≤441, 8n+1) + `frame_rate` (1–60) | `seconds` string "4"–"12" | same as 2.5 |
| size | `width`/`height` px (auto-standardized to 480/720/1080p presets) | `size` tier "720P"/"1080P"/"1K"/"2K" + `aspect_ratio` | ONLY "720P" — any other value → HTTP 400 |
| mode | `image` (t2v/i2v), `extra_body{image:[…], mode:"keyframes"}` | `mode` REQUIRED: text / keyframe / reference | same as 2.5 |
| reference media | none | images ≤8, audios ≤3, videos ≤1 (2–12 s, 24–60 fps) | images ≤5, audios ≤3, NO videos (400) |
| forbidden fields | — | `width`/`height`/`fps`/`num_frames`/`quality`/`video_url`/`input_reference` → 400 | same as 2.5 |
| result URL | `metadata.url` | top-level `url` | top-level `url` |

Price notes at probe time: 2.5 = ¥0.15/s (720P) up to ¥0.35/s (2K); 2.5-flash was promo ¥0/s. Probe, don't assume.

## Plugin
- Lives at `$HERMES_HOME/plugins/video_gen/agnes/` (`plugin.yaml` kind: backend + `__init__.py`). Two payload builders: `build_v20_payload` (legacy fields) and `build_25_payload` (2.5-series fields); Flash branch enforces 720P, truncates images to 5, clamps seconds to 4–12.
- Gated by `plugins.enabled` (YAML LIST, see SKILL.md) + `video_gen.provider: agnes`, `video_gen.model: agnes-video-2.5-flash`.
- Verify: fresh python process → `hermes_cli.plugins._ensure_plugins_discovered(force=True)` → `agent.video_gen_registry.get_active_provider().name == 'agnes'`.
