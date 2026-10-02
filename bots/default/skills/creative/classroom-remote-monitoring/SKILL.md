---
name: classroom-remote-monitoring
description: 看班/看课远程监控：先定位摄像头在哪台设备（安卓一体机→WebRTC 双页；Windows 电脑→ffmpeg 推流进微信小程序），再给手机侧看画面+一键抓拍。建教师教室监控工具时用。
---

# Classroom remote monitoring (看班 / 看课)

Build a tool where a teacher watches a classroom camera from their phone and grabs a still as discipline evidence. **Step 1 is always: locate the physical device the camera is on** — a classroom all-in-one machine (一体机, Android OS) can't run the WeChat mini program's `live-player`, and a Windows PC's USB camera can't be reached from an Android all-in-one. The wrong assumption here ships an architecture the user can't test. If the camera is on an Android all-in-one, use the WebRTC two-page pair (recipe: `references/web-rtc-pairing.md`); only use the ffmpeg + mini program path when the camera is on a Windows PC the user controls.

## Rule 0 — match scope to the user's stated CORE use case FIRST
This user (李老师) wants the minimum that does the job; he has cut a large speculative build back to a single screen more than once. Before fanning out into a multi-module app, identify the one concrete job the user named and build that end-to-end; treat every other module as opt-in follow-up. Concretely: restate the single core job back, confirm, build only that, and list the rest as *proposed* next steps rather than *built* pages. Building 9 modules when the need is "watch the classroom" wastes the whole pass — he will delete 80%.

## Rule 0.5 — locate the camera's physical host BEFORE choosing an architecture
Ask where the camera physically is (Windows PC vs Android all-in-one vs phone) and what the phone side may look like (WeChat mini program vs plain browser). The all-in-one's camera is an Android `getUserMedia` device: WeChat `live-player` cannot consume it, and an ffmpeg on a separate PC cannot see it. If the all-in-one can open a Chrome-based browser, two single-file HTML pages with WebRTC P2P is the whole solution. Don't ship the mini program architecture before confirming the camera's host — it is the most expensive wrong turn in this task class.

## The two ends (choose by camera host)
- **Camera on a Windows PC** → PC runs one `ffmpeg` binary turning the USB camera into a LAN stream; phone side is a single WeChat mini program page with a `live-player`, a "fill stream URL" affordance, and one **one-tap snapshot** button that stores stills as evidence. No cloud. Full recipe: `references/ffmpeg-lan-streaming.md`.
- **Camera on an Android all-in-one** → two offline single-file HTML pages: all-in-one page opens `getUserMedia` camera + QR pairing + full-screen big-text alerts; phone page shows the remote video + one-tap snapshot + sends full-screen alert text back to the all-in-one big screen. WebRTC P2P, no server. Full recipe: `references/web-rtc-pairing.md`.

## live-player protocol decision table (the non-obvious part)
WeChat's `live-player` accepts different stream protocols depending on OS — you cannot use one URL for all phones:

| Phone | `live-player` accepts | What to fill in |
|---|---|---|
| iOS WeChat | HLS (`.m3u8`) **and** HTTP-FLV | `http://PC_IP:8000/playlist.m3u8` (or `/live.flv` for lower latency) |
| Android WeChat | **RTMP only** | `rtmp://PC_IP:1935/cam` — requires a MediaMTX relay (see reference) |

So the streamer must expose HLS + FLV (both free, built into the Python server) and, only if Android is the target, add RTMP. Don't build the RTMP path unless the user actually has Android-only phones.

## Snapshot-as-evidence step
- `wx.createLivePlayerContext('playerId').snapshot({ success: res => res.tempFilePath })` → save `{id, time, tempPath}` to local storage, cap the list (e.g. 60). `tempFilePath` is enough for a local-only version; only upload to cloud in a later pass.
- Gate the button on "player ready" so it can't fire on a black frame.

## Standing preferences for this user's deliverables
- Theme: 玄金红 (玄黑 #0d0b10 bg / 宣纸白 #f4efe2 text / 亮金 #e0b341 accent / 朱砂 #b23a2e alert / 绿 #5fa87f ok). Apply unless told otherwise.
- Deliver as a WeChat mini program he can import into 微信开发者工具 with a test AppID, and pair it with a double-click classroom script. State honestly that it is LAN-only (4G / off-campus won't reach it) and that stills are local until a cloud pass is added.

## Pitfalls (with why)
- **Assuming one stream URL works on all phones** — Android WeChat's `live-player` only decodes RTMP; an HLS URL silently shows black there. Match the URL to the OS before shipping.
- **Hardcoding a `SimpleHTTPRequestHandler` subdirectory prefix** — when you serve HLS files with `directory=HLS_DIR`, the playlist is at `/playlist.m3u8` (server root), NOT `/hls/playlist.m3u8`. Print the URL actually bound.
- **Blocking the HTTP server on a long-lived FLV stream with the default `HTTPServer`** — a stuck FLV client freezes every other request; use `ThreadingHTTPServer`.
- **Forgetting the firewall** — first run needs inbound on the stream port (8000, and 1935 if RTMP); Windows prompts on first run, "allow" it, or phones can't connect even on the right LAN.
- **Running two `ffmpeg` processes against one camera for "HLS + FLV"** — the second process fails to open the device and kills the pipeline; if a second output is ever needed, use one ffmpeg with two `-f` outputs. Also: an HTTP-flv endpoint reading an ffmpeg stdout pipe deadlocks ffmpeg when nobody is connected — drain the pipe in a background thread or drop the endpoint.
- **ffmpeg 8.x camera device discovery** — `ffmpeg -f dshow -list_devices 1` now requires a trailing `-i dummy` (or it prints usage and exits), output moves to `[in#0] "Name" (video)` lines, and the command exits non-zero after listing; use `subprocess.run` and ignore the exit code. Keep the old-format regex as fallback for ffmpeg ≤7.
- **Assuming the camera is on a PC because that's where the tooling runs** — see Rule 0.5; confirm the physical host with the user before writing any streaming code.

## Pointers
- `references/ffmpeg-lan-streaming.md` — the complete classroom-side recipe: one-file streamer, auto-download ffmpeg, HLS streaming, Android RTMP via MediaMTX, local test page, device selection, low-latency flags.
- `references/web-rtc-pairing.md` — two-offline-single-file-HTML recipe for Android all-in-one cameras: WebRTC P2P pairing via QR (camera side scans the phone's QR with `jsQR`), phone-side one-tap snapshot, reverse full-screen big-text alerts to the all-in-one display, STUN notes for LAN-only setups.
