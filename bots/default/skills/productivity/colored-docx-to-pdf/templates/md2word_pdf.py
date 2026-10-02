#!/usr/bin/env python3
# md -> 白底 Word（墨金/玉青/朱砂三色 + 协作署名表）-> 同名 .docx + .pdf
# 用法: python md2word_pdf.py <a.md> <b.md> ...  （输出 <名>_白底Word协作版.docx/.pdf 到同目录）
# 依赖: pip install python-docx comtypes
import sys, os, re
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# 白底学术三色（全部过 WCAG 4.5:1）
INK=RGBColor(0x1a,0x1a,0x1a); GOLD=RGBColor(0x8a,0x62,0x10); GOLD_HI=RGBColor(0x5a,0x40,0x0a)
JADE=RGBColor(0x1f,0x6b,0x4a); CINNA=RGBColor(0x9e,0x2a,0x20); GREY=RGBColor(0x59,0x59,0x59)
WHITE=RGBColor(0xff,0xff,0xff)
GOLD_FILL="D8B45A"; JADE_FILL="DCEFE4"; CINNA_FILL="F3DEDA"; GOLD_BG="F5EBD0"

# 协作署名：按当次用户点名的协作人改这里（勿沿用旧名单）
SIGNOFF = [
    ("提出人", "李彦明（初中信息科技教师 · 课题牵头）"),
    ("协作人（体育教研组）", "朱彦军 ／ 刘东明 ／ 亓会平"),
    ("协作单位", "合作校体育教研组 · 校医务室 · 健身气功协会（功法教练）"),
    ("成果归属", "本成果归协作团队共同所有，署名与署名顺序以联合署名为准"),
    ("日期 / 首考周期", "2026-09 ／ 建议首考 2029"),
]

def set_font(run, size=10.5, color=INK, bold=False, name="宋体", east="宋体"):
    run.font.size=Pt(size); run.font.color.rgb=color; run.font.bold=bold; run.font.name=name
    rpr=run._element.get_or_add_rPr()
    rf=rpr.find(qn('w:rFonts'))
    if rf is None:
        rf=OxmlElement('w:rFonts'); rpr.append(rf)
    rf.set(qn('w:eastAsia'), east)

def shade_cell(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr()
    shd=OxmlElement('w:shd'); shd.set(qn('w:val'),'clear'); shd.set(qn('w:fill'),fill); tcPr.append(shd)

def cell_borders(cell, color="BFBFBF", sz="4"):
    tcPr=cell._tc.get_or_add_tcPr()
    b=OxmlElement('w:tcBorders')
    for e in ('top','left','bottom','right'):
        x=OxmlElement(f'w:{e}'); x.set(qn('w:val'),'single'); x.set(qn('w:sz'),sz); x.set(qn('w:color'),str(color)); b.append(x)
    tcPr.append(b)

def build(doc, mdtext):
    for s in doc.sections:
        s.top_margin=Cm(2.0); s.bottom_margin=Cm(2.0); s.left_margin=Cm(2.2); s.right_margin=Cm(2.2)
    lines=mdtext.replace("\r\n","\n").split("\n")
    # 标题（首行 # 开头）
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run(lines[0].lstrip("#").strip()); set_font(r,18,GOLD_HI,True,"黑体","黑体")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(8)
    r=p.add_run("协作署名 · 联合成果"); set_font(r,10.5,JADE,True,"黑体","黑体")
    # 协作署名表
    t=doc.add_table(rows=len(SIGNOFF), cols=2); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for ri,(a,bb) in enumerate(SIGNOFF):
        c0=t.rows[ri].cells[0]; c1=t.rows[ri].cells[1]; c0.text=""; c1.text=""
        pa=c0.paragraphs[0]; ra=pa.add_run(a); set_font(ra,9.5,GOLD,True,"黑体","黑体")
        shade_cell(c0,GOLD_BG); cell_borders(c0)
        pb=c1.paragraphs[0]; rb=pb.add_run(bb); set_font(rb,9.5,INK); cell_borders(c1)
        c0.width=Cm(4.2); c1.width=Cm(12.5)
    doc.add_paragraph()
    # 正文（跳过首行标题）
    in_code=False; code=[]; i=0
    while i < len(lines):
        line=lines[i]
        if line.strip().startswith("```"):
            if in_code:
                p=doc.add_paragraph(); r=p.add_run("\n".join(code)); set_font(r,9,INK,False,"Consolas","Consolas"); code=[]; in_code=False
            else: in_code=True
            i+=1; continue
        if in_code:
            code.append(line); i+=1; continue
        if line.strip()=="": i+=1; continue
        m=re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl=len(m.group(1))
            p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(10 if lvl>=3 else 14); p.paragraph_format.space_after=Pt(4 if lvl>=3 else 6)
            sz = 14 if lvl<=2 else (12 if lvl==3 else 10.5)
            col = GOLD_HI if lvl<=2 else (GOLD if lvl==3 else JADE)
            r=p.add_run(m.group(2)); set_font(r,sz,col,True,"黑体","黑体")
            if lvl<=2:
                pPr=p._p.get_or_add_pPr(); pBdr=OxmlElement('w:pBdr')
                l=OxmlElement('w:left'); l.set(qn('w:val'),'single'); l.set(qn('w:sz'),'18'); l.set(qn('w:color'),'8a6210'); l.set(qn('w:space'),'6'); pBdr.append(l); pPr.append(pBdr)
            i+=1; continue
        if line.strip().startswith(">"):
            txt=line.strip().lstrip(">").strip()
            tb=doc.add_table(rows=1,cols=1); tb.alignment=WD_TABLE_ALIGNMENT.CENTER
            c=tb.rows[0].cells[0]; c.width=Cm(16.5); c.text=""
            shade_cell(c,JADE_FILL); cell_borders(c,"1f6b4a","6")
            p=c.paragraphs[0]; r=p.add_run(txt); set_font(r,10,INK)
            doc.add_paragraph().paragraph_format.space_after=Pt(2); i+=1; continue
        if line.strip().startswith("|") and line.strip().endswith("|"):
            if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
                i+=1; continue
            rows=[c for c in line.strip().strip("|").split("|")]
            more=[]; k=1
            while i+k < len(lines) and lines[i+k].strip().startswith("|"):
                ml=lines[i+k]
                if not re.match(r"^\s*\|[\s\-:|]+\|\s*$", ml):
                    more.append([c for c in ml.strip().strip("|").split("|")])
                i+=1; k+=1
            tb=doc.add_table(rows=1, cols=len(rows)); tb.style='Table Grid'; tb.alignment=WD_TABLE_ALIGNMENT.CENTER
            hdr=tb.rows[0].cells
            for hi,h in enumerate(rows):
                hdr[hi].text=""; ph=hdr[hi].paragraphs[0]; rh=ph.add_run(h.strip())
                set_font(rh,9.5,WHITE,True,"黑体","黑体"); shade_cell(hdr[hi],GOLD_FILL); cell_borders(hdr[hi])
            for rr in more:
                cells=tb.add_row().cells
                for ci,cv in enumerate(rr):
                    if ci>=len(cells): break
                    cells[ci].text=""; pc=cells[ci].paragraphs[0]
                    first=(ci==0)
                    rc=pc.add_run(cv.strip()); set_font(rc,9,(GOLD if first else INK),first); cell_borders(cells[ci])
            doc.add_paragraph().paragraph_format.space_after=Pt(2)
            continue
        if re.match(r"^\s*[-*]\s+", line):
            content=re.sub(r"^\s*[-*]\s+","",line)
            p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(2)
            r=p.add_run(re.sub(r"\*\*(.+?)\*\*", r"\1", content)); set_font(r,10.5,INK); i+=1; continue
        if re.match(r"^\s*\d+\.\s+", line):
            content=re.sub(r"^\s*\d+\.\s+","",line)
            p=doc.add_paragraph(style="List Number"); p.paragraph_format.space_after=Pt(2)
            r=p.add_run(content); set_font(r,10.5,INK); i+=1; continue
        if re.match(r"^\s*---+\s*$", line):
            doc.add_paragraph().paragraph_format.space_after=Pt(4); i+=1; continue
        # 普通段落（解析 **bold** / *em*）
        p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(6)
        for s in re.split(r"(\*\*.+?\*\*|\*.+?\*)", line):
            if s.startswith("**") and s.endswith("**"):
                r=p.add_run(s[2:-2]); set_font(r,10.5,GOLD,True)
            elif s.startswith("*") and s.endswith("*") and len(s)>2:
                r=p.add_run(s[1:-1]); set_font(r,10.5,CINNA)
            else:
                r=p.add_run(s); set_font(r,10.5,INK)
        i+=1

def main():
    import comtypes.client
    for md in sys.argv[1:]:
        if not os.path.exists(md):
            print("MISS", md); continue
        text=open(md, encoding="utf-8").read()
        doc=Document(); build(doc, text)
        dpath=os.path.splitext(md)[0]+"_白底Word协作版.docx"
        ppath=os.path.splitext(md)[0]+"_白底Word协作版.pdf"
        doc.save(dpath)
        print("DOCX", dpath, os.path.getsize(dpath)//1024, "KB")
        w=comtypes.client.CreateObject("Word.Application"); w.Visible=False; w.DisplayAlerts=0
        d=w.Documents.Open(os.path.abspath(dpath))
        d.SaveAs2(os.path.abspath(ppath), FileFormat=17)
        d.Close(False); w.Quit()
        print("PDF ", ppath, os.path.getsize(ppath)//1024, "KB")

if __name__=="__main__":
    main()
