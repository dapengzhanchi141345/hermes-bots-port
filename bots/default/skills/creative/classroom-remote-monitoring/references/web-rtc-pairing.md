# WebRTC two-page pairing (camera on an Android all-in-one)

Use when the classroom camera is the all-in-one's built-in camera: WeChat mini programs can't reach it, and no PC ffmpeg can either. The all-in-one runs a Chrome-based browser; two offline single-file HTML pages pair via WebRTC P2P. ~0.3s latency, zero install, zero server.

## The two pages
- **All-in-one page** (`一体机端.html`): `getUserMedia` camera → preview; generates an SDP **offer** and renders it as a QR (`qrcode-generator`); a `jsQR` loop over the local camera frames (~800ms) auto-detects the phone's answer QR held 10–30cm in front of the lens; also accepts a pasted answer string. `ondatachannel` handler receives control JSON. A fixed full-screen red overlay (`position:fixed; z-index`) shows big-text alerts (120px) + a short WebAudio beep when the phone sends one.
- **Phone page** (`手机端.html`): `addTransceiver('video', {direction:'recvonly'})` + receiver `ontrack` → `<video>`; creates the offer, renders it as QR, and creates its own data channel named `cam` for sending alerts; one-tap snapshot = draw current video frame to canvas → `toDataURL('image/jpeg', .85)` → keep last ~50 in memory with timestamp; alert UI = preset select (安静/收手机/坐姿端正/停笔…) + free text (cap ~8 chars for the big screen).

## Pairing protocol
- SDP is passed as a string, not a signaling server: encode with `btoa` guarded by `decodeURIComponent(escape(...))` for non-UTF8 bytes, or `encodeURIComponent` — either, as long as both sides match. Prefix the payload (`XKCAM1.` offer / `XKCAM2.` answer) so the camera-side `jsQR` loop ignores QRs that aren't this tool.
- Offer on the camera side, answer on the phone side (camera owns the offer because it also owns the video track + `ondatachannel`).

## Offline single-file requirement (this user's iron rule)
- Inline the libs: `qrcode-generator` (~56KB) and `jsQR` (~257KB) directly into each HTML — no CDN script tags. In the 墙内 (China) environment jsdelivr/unpkg often fail or are blocked, so a CDN `<script>` makes the delivered file silently dead. Verify the downloaded lib's byte size before inlining (40 bytes = not-found page, not the lib).
- Keep templates with `/*QR_LIB*/` / `/*JSQR_LIB*/` placeholders and a small script that splices the lib files in; after generating, extract each inline script block and `node --check` it before shipping.

## WebRTC networking notes
- **Cross-net room-code path needs PeerJS inlined.** PeerJS's `DataConnection` exposes no `onmessage`/`onclose` properties — data events are `conn.on('data', fn)` and `conn.on('close', fn)`. Wiring `conn.onmessage = fn` is a silent no-op: the phone's SDP answer (and any reverse alert) never reaches the all-in-one, the room-code handshake deadlocks, and the symptom is exactly "点了没反应". Grep the inlined lib for its real event names (`emit("data"`) before wiring handlers. Keep the LAN QR path as the always-working fallback.
- **Offer the room-code SDP a few times after the channel opens** (viewer's data handler may attach late): re-send the offer every ~1.5s up to ~5 rounds and make the viewer's answer handler idempotent (a repeat offer with `signalingState==='stable'` re-answers on the same RTCPeerConnection, doesn't throw).
- Same LAN: works with STUN alone (`stun:stun.l.google.com:19302`) — but that STUN is Google, and the all-in-one may be behind a firewall that blocks it; if STUN fails, try a bare config (no iceServers) first since LAN WebRTC can complete via host candidates alone.
- If the all-in-one can't reach the LAN, the stable fallback is phone hot-spot: phone creates a hotspot, all-in-one joins it.
- `getUserMedia` only works in a secure context: `file://` is treated as secure by Chrome-family browsers on Windows/Android — opening the HTML directly from USB storage or the all-in-one's local storage works. If the browser refuses, the first run still needs the camera permission prompt granted manually (address-bar camera icon → allow).

## Reverse alerts (the feature that beats the original 小橙看班)
- Phone → all-in-one full-screen big text is a DataChannel message (`{t:'alert', text}`), rendered on the all-in-one's fixed overlay with a WebAudio beep. It only works if the all-in-one has a speaker and hasn't been muted — state this limitation to the user.
- The phone side can also record an SVG "evidence card" of the alert moment into its snapshot list.

## Pitfalls (with why)
- **Camera-side jsQR scan loop without an `offerPending`/success stop** — it keeps scanning after pairing and can re-trigger with a stale QR; stop the interval the moment an answer is applied.
- **`receiver.receiver.ontrack` vs `pc.ontrack`** — `pc.ontrack` fires for all directions; bind on the specific recvonly transceiver's receiver so your `<video>` only gets the remote track.
- **Snapshotting before first frame** — `video.videoWidth` is 0 until a frame lands; fall back to 640×360 and gate the button on the track's `ontrack` fired.
