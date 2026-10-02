---
name: webrtc-remote-view
description: "远程看另一台设备的摄像头/屏幕（零服务器、离线单文件HTML）。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [webrtc, p2p, remote-view, camera, screen-share, live-stream, offline-html, hls, flv, rtcdatachannel]
    related_skills: [claude-design, spike]
---

# WebRTC Remote View (zero-server, offline single-file)

Let a phone/laptop see a **camera or screen** on another device with **no server, no cloud account, no install** — all logic + libs inlined into two self-contained HTML files you copy onto each device. This is the class behind "手机远程监控教室里的一体机摄像头", "让我从手机看这台电脑的屏幕", etc.

## Step 0 — Pin down the REAL endpoints BEFORE choosing an architecture (highest-cost mistake)
Confirm, in one shot, which **device + OS + browser** holds the camera, and which browser the viewer uses. Build for THAT. A camera on an Android 一体机/Android box cannot be reached from a Windows miniprogram; a viewer inside **WeChat's in-app browser has no `getUserMedia`/WebRTC** — it needs an external browser (Chrome/Safari/Edge). Getting this wrong means shipping the whole wrong stack. If the user is non-technical and won't answer, default to the browser the camera physically runs in and say so.

## Architecture (default)
- **Two single-file HTML pages** (viewer + camera side). Inline `qrcode-generator`, `jsQR`, and (for cross-net) `PeerJS` into the file so each works fully **offline** via `file://` or a LAN share — never rely on a public CDN at runtime (behind the GFW / in a school LAN a `cdn.jsdelivr.net` script tag silently 404s and the page is dead). Download the UMD bundles locally and paste their text in.
- **Same LAN, no internet needed:** WebRTC P2P direct. Pair two ways:
  - **QR pairing:** camera side shows a QR of its `localDescription` (offer); viewer's phone camera (jsQR) scans it, builds the `answer` QR; hold the phone screen in front of the room camera → camera side (jsQR on its own video) reads it. Fallback: copy the base64 offer string and paste it.
  - **Room-code (cross-net):** camera side registers a 4-digit PeerJS id; viewer dials the id from 4G/anywhere. Requires internet on BOTH sides.
- **Latency ~0.3s**, one-way (viewer watches; a small `RTCPeerConnection` datachannel carries text commands back, e.g. "全班安静" full-screen alert + beep on the camera side).

## Core build procedure
1. `getUserMedia({video, audio:false})` on the camera side; `addTrack` the **camera tracks onto the RTCPeerConnection BEFORE `createOffer`** — forgetting this is the #1 cause of "connected but black screen" (an empty SCTP/DTLS channel, no media).
2. Camera side creates + `setLocalDescription(offer)`, encodes the SDP `base64` into the QR / room-code path.
3. Viewer side `new RTCPeerConnection` with a `recvonly` video transceiver, `setRemoteDescription(offer)` → `createAnswer` → `setLocalDescription` → send the answer back (QR/paste for LAN, datachannel for room-code).
4. `ontrack` on the viewer → attach `stream` to `<video>`. `onconnectionstatechange === 'connected'` flips status to 监控中.
5. Commands back: a named `DataChannel('ctrl')` created by the camera side (or via the PeerJS conn), JSON `{t:'alert', text}` → camera side renders a full-screen red alert + `OscillatorNode` beep.

## Standing pitfalls (why each is stated)
- **PeerJS `DataConnection` has NO `onmessage`/`onclose` properties — the events are `.on('data')` and `.on('close')`.** Writing `conn.onmessage = fn` silently does nothing: the answer / alert JSON from the other side never lands, so the room-code pairing deadlocks both ways and the symptom is exactly "点了没反应 / 没画面" with both sides showing connected-but-idle. After inlining PeerJS, grep the inline lib for the real event names (`emit("data"` in 1.5.x) before wiring handlers — do not trust the W3C `RTCPeerConnection` API name. Mirror the same on the viewer side that sends the answer.
- **Re-send the SDP offer a few times after the room-code channel opens, not once.** The viewer's `conn.on('data')` handler may attach a beat after the camera side's first offer is already on the wire, so a single send gets missed. Offer a small loop: on channel `open`, send the offer, then re-send every ~1.5s up to ~5 rounds; make the viewer's answer handler idempotent (a new offer with `signalingState==='stable'` reuses the RTCPeerConnection, re-answers, doesn't crash). This is what makes the room-code path actually converge.
- **`addTrack` before `createOffer`, always.** An offer with no local tracks is a dead pipe: the two peers handshake to "connected" but nothing renders → user sees a black box. THE most common "连上了但黑屏".
- **Never run two `ffmpeg` (or two camera readers) on the same physical camera simultaneously** to make HLS+FLV. Most UVC cameras allow one reader; the second process fails silently and the "primary" stream dies mid-run. If you must serve two formats, one process with **two outputs** (`-f hls` + `-f flv pipe:1`) — but a FLV `-f flv` to `pipe:1` **deadlocks the encoder when nobody is reading the pipe** (OS pipe buffer fills). Only keep a FLV pipe if a reader is always attached; for a pure-HLS setup drop the FLV pipe entirely. See `references/ffmpeg-camera.md`.
- **ffmpeg ≥8.x changed `-list_devices` output.** Old: `video device N: Name` lines. New (8.x): you must pass `-list_devices 1 -i dummy` and the device prints as `[in#0 ...] "Name" (video)`, and the command exits non-zero (the `dummy` input can't open) — use `subprocess.run` + merge `stdout+stderr` and regex **both** formats; do NOT use `check_output` (it raises on the non-zero exit and you get an empty list). Full recipe in `references/ffmpeg-camera.md`.
- **Surface every async connect with staged status + timeout + an explicit switch-to-other-method line.** A `connect()` that fires `new Peer(...)` and waits with no UI is "点了没反应" to a non-technical user. Write staged text under the button (①连中继… ②已找到… 出画面), add a `setTimeout` (~15s) that prints a red "没连上 → 改用另一条路" fallback, and map each PeerJS `error.type` to a specific next step (`unavailable-id`→room-code wrong/offline, `peer-unavailable`→other side not up, else→relay/无外网 → use QR/LAN). Same for the QR path: show "正在扫…对准别晃" → "✅已识别" the moment jsQR hits.
- **WeChat in-app browser ≠ a real browser.** If the viewer opened the HTML from a WeChat link, `getUserMedia`/`RTCPeerConnection` are absent → nothing works. Detect via `navigator.userAgent` containing `MicroMessenger` plus `window.isSecureContext`/`navigator.mediaDevices` presence, and print a red banner telling them to "用浏览器打开". Do this at page load on BOTH files.
- **`file://` + non-secure context:** `getUserMedia` needs a secure origin; `file://` counts as secure in most desktop Chrome/Edge but NOT in some mobile WebViews — test on the actual device, and note the "地址栏点允许" step (camera permission must be granted manually the first time).
- **Keep it one feature, end-to-end.** This user wants the fastest minimal path: live view + one-tap snapshot (canvas→dataURL, keep last 50) + one remote-alert button. Do NOT bolt on a multi-module miniprogram scaffold, tab bars, attendance, or class-management — the correction "先别搞太复杂/主要功能是监控纪律" means ship the camera loop only. Extras go in a later iteration the user asks for.

## Delivery shape (this user)
- Two self-contained `.html` files (each a few hundred KB with libs inlined) + one short 使用说明.md.
- End with a **10-second self-check table**: row = the step, columns = 正常表现 / 不正常怎么办, so a non-technical user can report back exactly which cell failed. That table is how you get the next debug round to be precise instead of "还是不行".
- Store files under the user's content root (`{{WORKBUDDY}}\内容中心\…`), not the model/comparison folder.

## Cross-net vs LAN decision
| Situation | Path |
|---|---|
| Viewer on same LAN/Wi-Fi as camera device | QR pairing (no internet needed, most robust) |
| Viewer on 4G/different network | Room-code via PeerJS (both sides need internet; GFW/ISP may block the relay — fallback is LAN QR) |
| No JS allowed on camera device (e.g. a headless box) | `references/ffmpeg-camera.md` — push HLS/FLV from the camera side to a static server, viewer plays in a normal browser |

## Verify on real hardware before calling it done
The pairing flow MUST be confirmed end-to-end on the actual camera device + actual viewer browser (画面出来 + 抓拍 + 大屏提示). "It compiles / node --check passes / segments are written" is NOT done. If you couldn't get live picture on the real device, say so plainly and hand the user the self-check table — do not claim success.
