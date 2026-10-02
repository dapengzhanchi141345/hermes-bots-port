# Camera-side HLS/FLV push recipe (when the camera host can't run JS)

Use when the camera lives on a device that can't open a browser (headless box, locked-down 一体机) but you can run one shell command there. The viewer stays a plain browser (this skill's HTML, minus the WebRTC pair; the video tag's `src` is the HLS/FLV URL instead).

## One-process, one-reader rule (the deadlock you must avoid)
- **Never start two `ffmpeg` processes on the same camera** to produce HLS + FLV. Most UVC cameras allow a single reader; the second opens, fails, and the first is torn down. Verified symptom: the primary HLS stream dies ~1s after start with "推流进程退出 (摄像头被占用?)".
- Correct: ONE `ffmpeg`, camera read once, two outputs:
  ```
  ffmpeg -f dshow -i "video=<dev>" -an \
    -c:v libx264 -preset ultrafast -tune zerolatency -g 30 -keyint_min 30 \
    -vf "scale=640:360,fps=15" \
    -f hls -hls_time 2 -hls_list_size 5 -hls_flags delete_segments out/playlist.m3u8 \
    -f flv -flvflags no_duration_filesize pipe:1
  ```
- BUT: a `pipe:1` FLV output **deadlocks the encoder when nobody reads the pipe** (OS pipe buffer ~64KB fills, ffmpeg stalls → HLS stops updating → black screen on the viewer). If you keep the FLV pipe, you MUST have a reader always draining it (e.g. the HTTP server pipes `proc.stdout` to each `/live.flv` client). For a pure-HLS deployment, **drop the FLV output entirely** — simpler and no deadlock.
- Serve HLS over a tiny HTTP server rooted at `out/` so the playlist and `.ts` segments resolve relative to the playlist URL. Phone plays `http://<lan-ip>:<port>/playlist.m3u8`.

## Camera device enumeration (ffmpeg 8.x)
`ffmpeg -f dshow -list_devices 1` only works on old ffmpeg. On **8.x**:
```
ffmpeg -hide_banner -f dshow -list_devices 1 -i dummy
```
- It prints each device as `[in#0 ...] "<Name>" (video)` and **exits non-zero** (the `dummy` input can't open). So use `subprocess.run`, merge `stdout+stderr`, and regex `^\[in#0.*?\] "([^"]+)" \(video\)`; also keep the old `video device N:` pattern as fallback for <8. Do **not** use `check_output` (raises on the non-zero exit → empty list).

## Protocol limits (pick the viewer path accordingly)
- iOS web players / HLS players: **HLS `.m3u8`** over http. Fine for ~1–3s latency discipline monitoring.
- Android WeChat miniprogram `live-player`: **RTMP only** (official limit). Needs a MediaMTX (or ffmpeg) RTMP relay: push `-f flv rtmp://127.0.0.1:1935/cam`, viewer dials `rtmp://<lan-ip>:1935/cam`.
- Web `<video>` for FLV needs `flv.js` (browser) — heavier; prefer HLS for the web viewer.
- Latency: HLS with `-hls_time 2` is ~2–3s. For sub-second on the same machine use RTMP+relay or WebRTC (main skill). Discipline monitoring tolerates 2–3s; if not, switch to the WebRTC path.

## Verification that actually proves it
Run one process, wait ~5s, then: `ls out/*.ts` (segments being written), `cat out/playlist.m3u8` (EXTINF lines present), and a browser/phone hitting the `.m3u8`. Segments written ≠ playable end-to-end; confirm picture on the real viewer device.
