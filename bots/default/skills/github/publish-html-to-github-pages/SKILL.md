---
name: publish-html-to-github-pages
description: Use when 把本地 HTML 文件发布成可分享的 GitHub Pages 公网链接。
---

# 发布本地单文件 HTML 到 GitHub Pages(可分享链接)

Class of task: turn a local self-contained HTML artifact (dashboard, report, single-file teaching page) into a public URL the user can forward to anyone, and keep it live by auto-syncing the source into a public repo. On this host the user is on Windows/MSYS (git-bash), and the target audience opens the link in a browser with no login.

## User preferences (李彦明, standing)
- **Self-contained single file is the deliverable** — the artifact must work from `file://` and have **no CDN externals** (offline-capable is the norm here). A GitHub Pages host serves it fine as-is.
- **Never publish more than the one artifact.** The public repo gets ONLY the shareable HTML (as `index.html`). Anything that could carry live data, strategy logic, P&L, MT5 passwords, or API keys stays out of the public repo — even when the source and the sensitive material sit in the same directory tree. Build the publish repo from a **separate scratch dir**, not by git-init'ing the source directory.
- **The link stays current, not a frozen snapshot.** A Pages URL only updates when you push. If the source is regenerated on a schedule, wire a sync step into that schedule so the shared link tracks the latest content; report that the link is "real-time (up to one refresh cycle stale)" not "a fixed snapshot."
- **Report the shareable URL plainly** — one screen: the URL, that it needs no login, what it shows, and how to take it down later (make repo private / delete Pages). 大白话, not a process replay.

## Procedure
1. **Security pre-check on the artifact BEFORE publishing.** Grep the file for secrets/identifiers that must not hit a public URL: CDN/external `src=`/`href=`, `sk-`/`Bearer`/`api_key`/`password=` strings, and account IDs. If clean (no externals, no secrets, no account IDs), proceed. If a secret is embedded, fix the source to strip it — do NOT scrub-and-publish (the source still has it and the next sync re-leaks it).
2. **Build an isolated public repo** in a scratch dir (`mkdir + git init`), copy ONLY the artifact in as `index.html`, commit. Do not `git init` the source tree.
3. **Create the public repo + push + enable Pages** (commands below). Expect the github.com network to flake on this host — wrap the push in a retry loop and verify the remote actually has the commit (see gotcha #4).
4. **Verify the public URL live** with a real HTTP fetch: expect `200` + a body byte-count matching the source + the expected `<title>`. A 200 with an empty/short body = network flake, retry; don't declare success on the Pages `status: built` alone.
5. **Wire auto-sync** (only if the source is regenerated on a schedule): hook a small idempotent sync step into that schedule. Use `templates/sync_pages.py` as the starter — it is failure-safe (records the last-SUCCESS mtime; only re-pushes when the source is newer; re-pushes on network failure instead of swallowing the pending update). For a schedule that is itself a Python pipeline, add a `subprocess.run([sys.executable, SYNC, "--quiet"], timeout=240)` step at the END that is **best-effort** (try/except, never affects the pipeline's return code) — the trading/main chain must keep running even if a push flakes.
6. **Report** the URL + "no login, shows X, takes up to one refresh cycle to update, to remove: <one command>".

## Commands (gh first; this host has `gh` authenticated as `dapengzhanchi141345`)
```bash
# 1) scratch repo with only the artifact
cd {{USER_HOME}} && rm -rf <name> && mkdir <name> && cd <name>
cp "E:/path/to/artifact.html" index.html
git init -q && git add index.html && git commit -m "publish"
git branch -M main          # git init here defaults to master; Pages+push expect main

# 2) create public repo + push (retry: github.com flakes on this host)
gh repo create <owner>/<name> --public --source . --remote origin --push
for i in 1 2 3 4 5; do
  git push -u origin main >/dev/null 2>&1
  git ls-remote origin main >/dev/null 2>&1 && break; sleep 8
done

# 3) enable Pages (source must be an OBJECT, not a string, or 422)
PAYLOAD="$LOCALAPPDATA/Temp/pages_payload.json"
printf '%s' '{"build_type":"legacy","source":{"branch":"main","path":"/"}}' > "$PAYLOAD"
gh api -X POST repos/<owner>/<name>/pages --input "$PAYLOAD"
# 4) poll until built (takes ~1-2 min)
for i in 1 2 3 4; do sleep 30
grep -aoE '"status":"[^"]*"' <(gh api repos/<owner>/<name>/pages) | tail -1
done

# 5) verify live (a real browser-like fetch, not just the Pages status)
python -c "import urllib.request as u; r=u.urlopen('https://<owner>.github.io/<name>/', timeout=40); b=r.read(); print(r.status, len(b))"
# share link: https://<owner>.github.io/<name>/
```

## Windows / MSYS gotchas (this host — these are NOT in the bundled github skills)
1. **Native `gh`/`git` cannot read `/tmp`** — MSYS's `/tmp` is a virtual path; write `gh api --input` payload files to `$LOCALAPPDATA/Temp/...` (a real `C:\Users\<user>\AppData\Local\Temp\...`) instead, or gh fails with `The system cannot find the file specified.`
2. **`git init` defaults the branch to `master`**, so `git push origin main` / Pages `branch:main` fail with `src refspec main does not match any`. Always `git branch -M main` first.
3. **A green-looking "push succeeded" echo is not proof.** This host flaps github.com (DNS via aliyun DoH, occasional 443 reset). A loop that echoes success on `git push` exit can lie. Authoritative check = `git ls-remote origin main` returns a commit hash.
4. **Pages `source` is a JSON object.** Passing the source as a quoted string (`-f source='{...}'`) → `422 Invalid property /source ... is not of type object`. Use `--input file.json` (see step 3).
5. **Network flake = retry with backoff, not a new failure.** Re-run the push/poll a few times with sleeps; a 200/`built` on a later attempt is the expected pattern. Don't write down "github is broken here" — the retry clears it.

## Pitfalls
- Publishing the source directory (or a repo that also holds engine/data/credentials) instead of an isolated single-file repo = leaking live data to a public URL. The isolation in step 2 is the safeguard; re-check `git status` shows only `index.html` before the first push.
- Forgetting auto-sync → the shared link silently freezes at the publish-time snapshot while the source keeps regenerating. Hook the sync into the SAME schedule that regenerates the source.
- A sync step that records "synced" on FAILURE: if you stamp success before the push actually lands, the next run sees no mtime change and skips forever, so a flaky-push window permanently strands the update. Only stamp on a verified successful push; on failure keep the old stamp so the next run re-pushes.
- **Static footer / injected marker gets clobbered by the regenerator.** If the artifact is regenerated on a schedule, a footer/signature you add by editing the output `.html` directly disappears on the next cycle. Inject the marker into the GENERATOR (the script that writes the HTML), then re-run the generator and push manually once — never rely on a one-off edit to the output file.

## References
- `templates/sync_pages.py` — known-good idempotent + failure-safe source→Pages sync step; copy, edit SRC/REPO paths, drop into the source's regeneration schedule.
