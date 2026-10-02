---
name: colored-docx-to-pdf
description: "White-bg colored Word→PDF via python-docx + Word COM."
version: 1.0.0
---

# 彩色 Word → PDF 文档交付（Windows）

Class: 生成带配色、表格、标题、协作署名的 Word 文档，并自动转 PDF，全部 Windows + Python 完成，无需用户手开 Word。本技能是本用户「按最高标准出结果、版式色彩精美、必须白底、署名让给协作人」诉求的可靠路径。

核心链路：`python-docx` 生成 `.docx` → Word COM（`comtypes`）自动转 `.pdf`。装依赖：`python -m pip install python-docx comtypes pypdf`。

## 何时用

- 用户要「色彩精美」「版式美化」「PDF 呈报版」的 Word/建议书/报告/量表/表单。
- 需要白底学术配色（深色底/玄墨底被明确否掉：用户说「这样的底色不行，要 Word 转 PDF 才行」）。
- 成果要「让给协作人」/联合署名（提出人放次要位）。
- 纯 HTML→PDF（Edge 无头）深色版用户不接受；要白底 + 可编辑 .docx 双件时走本技能。

## 固定工作流（按顺序，每步有闸门）

0. **判底**：受众是屏幕交互（课件/看板）→ 可用深色「玄金红」板；受众是纸质/会议/呈报领导 → **必须白底**（本用户否决过深色呈报 PDF）。
1. **定白底三色体系并验对比度**（写码前做，别凭感觉）：用相对亮度公式算每对「文字/背景」`(L1+0.05)/(L2+0.05)`，正文需 ≥4.5:1、大字/表头白字需 ≥3:1，不过就调。复用值见文末「配色铁律」（已验全过 4.5:1）。
2. **加协作署名表（文首）**：一张表，行=提出人/协作人/协作单位/成果归属/日期；「成果归属」写明「本成果归协作团队共同所有，署名顺序以联合署名为准」；提出人（李彦明）放次要位。人名以用户当次点名为准，勿沿用旧名单。
3. **python-docx 生成 .docx**：
   - 字体：正文宋体 10.5pt、标题黑体加粗、引文/表格 9–9.5pt；`run._element.get_or_add_rPr()` 设 `w:rFonts w:eastAsia`（中文不糊）。
   - 表格：`style='Table Grid'`；表头格 `OxmlElement('w:shd')` 设 `w:fill` 金底 `D8B45A` + 白字加粗黑体；首列常加粗上色（金/玉青）。
   - 竖条标题：`w:pBdr/w:left`（金 `8a6210`，sz 18）；引文/警示块用单格表 + `shd`（玉青浅 `DCEFE4` / 朱砂浅 `F3DEDA`）+ 对应边框色。
   - 页面：`sections[0].top/bottom_margin=Cm(2.0)`、`left/right=Cm(2.2)`。
   - **陷阱**：`OxmlElement.set(qn('w:color'), ...)` 只收 **hex 字符串**，传 `RGBColor` 即 `TypeError: Argument must be bytes or unicode, got 'RGBColor'`。所有 `w:color`/`w:fill` 一律传字符串（`'8a6210'`、`'D8B45A'`）。
4. **Word COM 自动转 PDF**（本机 Office16）：
   ```python
   import comtypes.client, os
   w = comtypes.client.CreateObject("Word.Application"); w.Visible=False; w.DisplayAlerts=0
   d = w.Documents.Open(os.path.abspath(docx_path))
   d.SaveAs2(os.path.abspath(pdf_path), FileFormat=17)  # 17=wdFormatPDF
   d.Close(False); w.Quit()
   ```
5. **双件交付 + 校验**：同目录出 `.docx`（可改）+ `.pdf`（呈报）；`pypdf.PdfReader` 抽第 1 页确认署名表在位、表头金块/朱砂警示块渲染正常；报两份路径 + 页数 + 大小。落 `{{WORKBUDDY}}\内容中心\` 体系。

## md→白底 Word→PDF 通用转换器

任意 `.md` 一键转白底彩色 Word + PDF：用 `templates/md2word_pdf.py`（自动插协作署名表；解析标题/表/引用/列表/代码；金底表头 + 玉青引文 + 朱砂警示）。命令 `python {{WORKBUDDY}}/工具/md2word_pdf.py a.md b.md ...`。主建议书（带封面摘要 + 署名表 + 全章节）专用脚本见 `templates/build_docx_white.py`（两者已落 `{{WORKBUDDY}}\工具\`，可直接复用/修改）。

## 关键 Pitfalls

- **WeasyPrint 在 Windows 跑不起来**：FFI 需 GTK3/Pango（`libgobject-2.0`），本机没有；`winget search pango` 只有 PangoTerm，`choco/conda/vcpkg/nuget` 未装，网络常连不上 github 拉 DLL。别在这条路上耗——彩色 PDF 一律走「python-docx + Word COM」或「HTML + Edge 无头 `--print-to-pdf`」。Edge 路径（完整 CSS/flex/grid/渐变 1:1，比 WeasyPrint 强；适合深色屏幕版，白底呈报版优先 docx+COM）：`"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --no-sandbox --user-data-dir=<tmp> --print-to-pdf-no-header --print-to-pdf=<out.pdf> --virtual-time-budget=12000 file:///<html>`。
- **python-docx `OxmlElement.set` 只收字符串**：`w:color`/`w:fill` 传 `RGBColor` 即崩，全程 hex 字符串。
- **深色底 ≠ 呈报版**：本用户「玄金红」深色板只用于屏幕 HTML；一涉「打印/投影/呈报教育局」就切白底。判据：受众屏幕交互→深色；受众纸质/会议→白底。
- **署名归属**：所有成品「成果归属」行必须写归协作团队共同所有、署名顺序以联合署名为准；提出人放次要位（用户多次纠正「我是协作人才行，把成果让给他们」）。

## 配色铁律（白底，已验全过 4.5:1）

正文 `#1a1a1a`；深墨金（标题/表头字）`#8a6210`；表头金底 `#D8B45A`+白字；玉青（正向/引文字）`#1f6b4a`+浅底 `#DCEFE4`；朱砂（警示/负向）`#9e2a20`+浅底 `#F3DEDA`；浅金要点底 `#F5EBD0`；次要灰 `#595959`。字体：正文宋体、标题黑体、引文表格 9–9.5pt。

## 验证

- 生成后 `PdfReader` 抽第 1 页文字：署名表（协作署名·联合成果 / 提出人 / 协作人 / 成果归属）应在位；金/朱色块渲染正常。
- 报双件 `<名>.docx` + `<名>.pdf`（均落 `{{WORKBUDDY}}\内容中心\`）。
