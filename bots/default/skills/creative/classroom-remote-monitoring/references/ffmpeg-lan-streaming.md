# Classroom-side LAN camera streaming (Python + ffmpeg, one file)

Run on the classroom Windows PC: USB camera in, LAN stream out. No cloud, no install beyond one `ffmpeg` binary.

## What the streamer does
One Python file (e.g. `camera_server.py`) that:
1. **Finds `ffmpeg`** — check `shutil.which('ffmpeg')`, then fall back to `<script dir>\ffmpeg.exe` and `<script dir>\ffmpeg\bin\ffmpeg.exe`. If missing, print a one-line download pointer (https://www.gyan.dev/ffmpeg/builds/ → ffmpeg-release-essentials.zip, win64 gpl) and stop. A double-click `.bat` wrapper can auto-download + extract on first run.
2. **Lists cameras** — camera device discovery is version-sensitive: ffmpeg 8.x requires `ffmpeg -f dshow -list_devices 1 -i dummy` (without `-i dummy` it prints usage and exits), the device lines become `[in#0 ...] "Name" (video)`, and the command exits non-zero after listing — use `subprocess.run` and ignore the exit code. Keep the ffmpeg ≤7 format (`-list_devices 1`, regex `video device \d+: (.+)`) as a fallback. Default to device 1, allow `python camera_server.py -d "设备名"` to pick. If none found, stop with a message.
3. **Streams HLS over HTTP** — one ffmpeg process, HLS output only (see below).
4. **Serves the result** over HTTP on `0.0.0.0:8000`, prints the LAN URL, and opens a local test page in the browser.

## The stream paths
- **HLS (default, serves iOS phones and any HLS-capable player)**: `ffmpeg -f dshow -i "video=设备名" -c:v libx264 -preset ultrafast -tune zerolatency -g 30 -keyint_min 30 -vf "scale=640:360,fps=15" -an -f hls -hls_time 2 -hls_list_size 5 -hls_flags delete_segments <hlsdir>/playlist.m3u8`
  Serve `<hlsdir>` as the HTTP server root. The phone plays **`http://PC_IP:8000/playlist.m3u8`** (server root, no extra path segment).
- **HTTP-FLV (only if iOS-only phones are confirmed)**: same encode but `-f flv -flvflags no_duration_filesize pipe:1` with stdout as a pipe. If you add it, run it as a **second output of the SAME ffmpeg** (one camera can't be opened by two processes — the second one dies immediately) and drain the pipe in a background thread when idle: a nobody-connected FLV pipe **deadlocks ffmpeg** when the 64KB pipe buffer fills. One ffmpeg with two `-f` blocks, never two ffmpeg processes.
- **RTMP (only if the user has Android-only phones)**: needs a `MediaMTX` relay (single `mediamtx.exe`, listens 1935). Push a third ffmpeg path: `... -f flv rtmp://127.0.0.1:1935/cam`. Phone fills `rtmp://PC_IP:1935/cam`. Don't build this unless required.

## Server specifics that trip people up
- Use `http.server.ThreadingHTTPServer` (not plain `HTTPServer`) so a long-lived streaming client can't block the HLS/static requests.
- `SimpleHTTPRequestHandler` bound with `directory=HLS_DIR` serves the playlist at **`/playlist.m3u8`**, not `/hls/playlist.m3u8`. Build the printed URL from the actual root.
- **Verify the stream locally before phone testing** — `curl -o /dev/null -s http://127.0.0.1:8000/playlist.m3u8` returns 200 with `#EXTM3U` first; this split makes debugging one-shot.
- The LAN IP: open a UDP socket, `connect(('8.8.8.8', 80))`, read back `getsockname()[0]` — don't hardcode it (the user's LAN IP changes per network).
- Low-latency flags: `-tune zerolatency`, `-g 30 -keyint_min 30`, `-hls_time 2`. 640×360 @ 15fps keeps LAN bandwidth trivial — fine for watching discipline, not for quality review.
- `-an` mutes audio; to capture class audio for evidence, swap to `-c:a aac -b:a 64k`.

## Local verification before touching a phone
Ship a `本机试播.html` next to the server: an HLS test page pointing at `http://127.0.0.1:8000/playlist.m3u8` with `hls.js` **inlined from a locally-downloaded copy** (jsdelivr/unpkg often fail inside the 墙内 firewall; a 40-byte response means the download failed, not the lib). Open it on the classroom PC; picture there = the streamer works. No picture = ffmpeg/camera problem, not phone problem. This split makes debugging one-shot.

## Hand-off notes to print for the user
- Phones must be on the **same LAN** as the PC; off-campus / 4G will not reach it (state this honestly).
- PC stays on, camera plugged in, stream window open.
- Firewall: allow inbound on 8000 (and 1935 if RTMP) on first run.
