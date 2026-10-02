---
name: cn-client-pitch-deck
description: Use when making 李彦明 Chinese PPT pitch decks (客户汇报/产品介绍).
version: 1.0.0
author: Hermes
tags: [pptx, chinese, pitch-deck, client, cjk]
metadata:
  hermes:
    category: productivity
    related_skills: [powerpoint]
---

# Chinese Client-Facing Pitch Decks

Build a client-facing product/pitch deck for this user's AI-bot systems in Chinese: 16:9, dark + gold house palette, name-only attribution, plain-language lines, per-slide speaker notes, honest data framing. Deliverable goes to `{{WORKBUDDY}}\内容中心\交付\` (standing rule: all content lives under 内容中心).

## House spec (always on)

- **Name-only attribution**: presenter name (e.g. 李彦明) on cover, footer, closing slide. NO company / affiliation / org name anywhere in deck body or footer. If an architecture diagram has a top "user" node, label it `客户 / 决策者`, not the presenter's name.
- **Plain language (大白话)**: audience may not read code — pair every technical term or English abbreviation with a one-line plain wording. A jargon stack must land as a sentence a non-coder can follow.
- **Speaker notes on every content slide**: written as the live talk track (sentences to say, not bullets). Tell the user to present in 演示者视图.
- **Honesty framing**: simulation / backtest / demo data carries a visible disclaimer (历史 ≠ 未来, 模拟 ≠ 实盘, 大动作先报后动).
- **Required arc**: 亮点 (one page each) → 与市面系统对比表 → 前沿科技对标 (backed by real evidence, not buzzwords) → 全行业扩展 (methodology + a per-industry blueprint table) → 数据 + 下一步建议 (3-option close: 打样 / 复制 / 陪跑).
- **Frontier slides need numbers**: named benchmark / paper / competition with dated, concrete results (e.g. a live-trading contest's win/loss figures). Do a web research pass before writing them; an unbacked claim is a weak slide.
- **Full-industry extension is a standing selling point**: the user repeatedly wants "能延伸到全行业" — always include a methodology page (copy the skeleton) AND a per-industry role-mapping table (who schedules / executes / vetoes / researches / which external event triggers a pullback).

## Workflow (multi-pass, not one-shot)

The user expects repeated build → read-back → leak-scan → refine passes; a single delivery pass is a miss.

1. Gather source material (state cards, 分工 docs, READMEs) + do the frontier research before writing slides.
2. Author ONE build script (python-pptx; toolkit in `references/cjk-python-pptx-toolkit.md`) as the single source of truth — custom cards/geometry/tables beat the JSON-spec `pptx_create.py` script for CJK multi-card decks.
3. Build → `pptx_read.py OUT.pptx --outline > outline.json` → verify slide count, texts, tables, notes.
4. **Leak scan**: join every text + table cell into one string; search for forbidden tokens (org names, credentials, internal absolute paths) and confirm required ones (presenter name appears only as name, disclaimer present, user node labeled 客户/决策者).
5. Refine in the build script, rebuild. Never hand-edit the .pptx.
6. Deliver to 内容中心/交付 with a short report: what changed, what's verified, slide count + arc, plus the presenter-view tip.

## Pitfalls

- **East-Asian font fallback**: `run.font.name` sets only the Latin typeface; Chinese renders via the East-Asian (`a:ea`) typeface and silently falls back to a default CJK font — the usual cause of a deck that "looks cheap" on the client's screen. Set `a:ea` on every run (helper in the toolkit).
- **Read-back table shape**: in `pptx_read.py --outline` JSON, `tables` are nested `[[cell,...],...]` lists, not `{rows: ...}` objects. Iterate `for row in tb:` — `tb["rows"]` raises `TypeError`.
- **Windows/MSYS text capture**: the outline CLI prints non-ASCII JSON; redirect to a file and `open(path, encoding="utf-8")`. Piping through `head` or a `subprocess` harness mangles/truncates it; loading the skill script via `exec_module` is fragile. Run the CLI directly in the terminal.
- **Frontier claims without numbers**: a cutting-edge slide that names a trend with no dated benchmark / result is a buzzword slide. Back it.

## Verification

1. Slide count matches the arc; every content slide has a note.
2. Leak scan clean: zero org / credential / internal-path tokens; presenter name only as name; disclaimer present.
3. If LibreOffice is available, render slides to PNG and review with vision_analyze; otherwise the outline is the check.
