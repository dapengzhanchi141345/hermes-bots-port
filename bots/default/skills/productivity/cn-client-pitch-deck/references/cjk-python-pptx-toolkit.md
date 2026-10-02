# CJK python-pptx deck toolkit

For custom CJK multi-card decks the JSON-spec `pptx_create.py` can't express. Keep one build script as the source of truth; run it after every content edit.

## Base setup

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)  # 16:9
BLANK = prs.slide_layouts[6]   # blank; index varies per template — confirm via outline's layouts_available
```

Dark + gold house palette: BG `0E1420`, card `1A2334` / `222E44`, gold `D4AF37`, accent blue `4FC3F7`, body text `E8E6E1`, muted `9AA5B8`, warning red `E05B4B`, good green `5FBF7A`.

## East-Asian font helper (call on EVERY run)

`run.font.name = "微软雅黑"` writes only the Latin typeface; PowerPoint renders CJK via `a:ea` and falls back to a default font without it.

```python
def _set_font(run, name="微软雅黑"):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', name)
```

## Card + text helpers (cover ~90% of visual needs)

- Card: `MSO_SHAPE.ROUNDED_RECTANGLE`, `fill.solid()`, `line.fill.background()`, `shadow.inherit = False`; content goes in the shape's `text_frame` as multiple paragraphs. A single `add_card(slide, x, y, w, h, lines=[(text, size_pt, color, bold, space_after), ...])` helper covers most layouts.
- Connectors: `MSO_SHAPE.RIGHT_ARROW` / `DOWN_ARROW` with solid fill between cards.
- Text: `add_textbox` with `tf.word_wrap = True`, zero margins, one paragraph per line, `p.line_spacing` for CJK comfort.
- Tables: `slide.shapes.add_table(...)` then style every cell (`fill.solid()`, `vertical_anchor = MSO_ANCHOR.MIDDLE`, margins) — default table styling is ugly on dark backgrounds. Header row: dark-gold fill `8A6D1F` + dark text; body rows alternate card fills.
- Footer / page number: plain textboxes per slide (placeholder copying is unreliable on blank layouts).

## Speaker notes in the build script

`slide.notes_slide.notes_text_frame.text = "..."` — author notes while building (per-slide, as a talk track the user will say live), not by post-processing the file with `--set-notes`.

## Verification without LibreOffice

1. `pptx_read.py OUT.pptx --outline > outline.json` (run the CLI directly in the terminal, redirect to file); inspect with `json.load(open(..., encoding="utf-8"))`.
2. Tables in that JSON are nested `[[cell, ...], ...]` lists — iterate rows, do NOT index a `rows` key.
3. Leak scan: join all texts + table cells into one string; grep for forbidden tokens (org names, credentials, absolute internal paths) and confirm required ones (presenter name only as name, disclaimer, user node labeled 客户/决策者).
4. Rebuild after every edit; never hand-edit the .pptx.

## Windows/MSYS gotchas

- MSYS path conversion is disabled for native tools: pass `C:/...` forward-slash paths to python; inside the Python source use forward slashes (MSYS-style `/c/...` breaks `os.path` into `C:/...`).
- Non-ASCII JSON through pipes/`head`/`subprocess` capture gets mangled or truncated — redirect to a file and read it.
- `exec_module` on the skill scripts is fragile (module-level code can swallow stdout); prefer plain CLI invocation.
