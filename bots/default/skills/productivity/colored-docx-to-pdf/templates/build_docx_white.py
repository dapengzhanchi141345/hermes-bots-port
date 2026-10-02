# 主建议书专用：白底 Word（三色 + 协作署名 + 全部章节）-> .docx
# 用法: python build_docx_white.py  （按本用户当次建议书内容改 SIGNOFF 与各章节文本）
# 依赖: pip install python-docx
# 转 PDF: 见 colored-docx-to-pdf 技能 SKILL.md 的 Word COM 段（comtypes, FileFormat=17）
# 复用值：颜色 hex 见技能「配色铁律」；set_font/shade_cell/cell_borders/build 各节与 md2word_pdf.py 同源。
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INK=RGBColor(0x1a,0x1a,0x1a); GOLD=RGBColor(0x8a,0x62,0x10); GOLD_HI=RGBColor(0x5a,0x40,0x0a)
JADE=RGBColor(0x1f,0x6b,0x4a); CINNA=RGBColor(0x9e,0x2a,0x20); GREY=RGBColor(0x59,0x59,0x59)
WHITE=RGBColor(0xff,0xff,0xff)
GOLD_FILL="D8B45A"; JADE_FILL="DCEFE4"; CINNA_FILL="F3DEDA"; GOLD_BG="F5EBD0"
OUT=r"{{WORKBUDDY}}\内容中心\交付\2026-09_中式体质测评深度调研\中考体育双赛道改革建议书_白底Word协作版.docx"

def set_font(run,size=10.5,color=INK,bold=False,name="宋体",east="宋体"):
    run.font.size=Pt(size); run.font.color.rgb=color; run.font.bold=bold; run.font.name=name
    rpr=run._element.get_or_add_rPr()
    rf=rpr.find(qn('w:rFonts'))
    if rf is None:
        rf=OxmlElement('w:rFonts'); rpr.append(rf)
    rf.set(qn('w:eastAsia'),east)

def shade_cell(cell,fill):
    tcPr=cell._tc.get_or_add_tcPr()
    shd=OxmlElement('w:shd'); shd.set(qn('w:val'),'clear'); shd.set(qn('w:fill'),fill); tcPr.append(shd)

def cell_borders(cell,color="BFBFBF",sz="4"):
    tcPr=cell._tc.get_or_add_tcPr()
    b=OxmlElement('w:tcBorders')
    for e in ('top','left','bottom','right'):
        x=OxmlElement(f'w:{e}'); x.set(qn('w:val'),'single'); x.set(qn('w:sz'),sz); x.set(qn('w:color'),str(color)); b.append(x)
    tcPr.append(b)

def main():
    doc=Document()
    for s in doc.sections:
        s.top_margin=Cm(2.0); s.bottom_margin=Cm(2.0); s.left_margin=Cm(2.2); s.right_margin=Cm(2.2)
    # 封面标题
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("从「跑得快」到「调得稳」"); set_font(r,24,GOLD_HI,True,"黑体","黑体")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(16)
    r=p.add_run("—— 中考体育双赛道改革建议书"); set_font(r,17,INK,True,"黑体","黑体")
    # 协作署名表（SIGNOFF 按当次点名改）
    SIGNOFF=[("提出人","李彦明（初中信息科技教师 · 课题牵头）"),
             ("协作人（体育教研组）","朱彦军 ／ 刘东明 ／ 亓会平"),
             ("协作单位","合作校体育教研组 · 校医务室 · 健身气功协会（功法教练）"),
             ("成果归属","本建议书及配套量表、表单归协作团队共同所有，署名与署名顺序以联合署名为准"),
             ("日期 / 首考周期","2026-09 ／ 建议首考 2029")]
    t=doc.add_table(rows=len(SIGNOFF),cols=2); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for ri,(a,bb) in enumerate(SIGNOFF):
        c0=t.rows[ri].cells[0]; c1=t.rows[ri].cells[1]; c0.text=""; c1.text=""
        pa=c0.paragraphs[0]; ra=pa.add_run(a); set_font(ra,9.5,GOLD,True,"黑体","黑体")
        shade_cell(c0,GOLD_BG); cell_borders(c0)
        pb=c1.paragraphs[0]; rb=pb.add_run(bb); set_font(rb,9.5,INK); cell_borders(c1)
        c0.width=Cm(4.2); c1.width=Cm(12.5)
    doc.add_page_break()
    # 各章节：用 make_table(texts...) 自建（表头金底白字、首列上色、引文/警示块 shd）
    # 示例调用（把正文章节按此模式补齐）：
    #   h2 = lambda txt: (章节标题段落: 黑体 14pt GOLD_HI + w:pBdr left 8a6210)
    #   tbl = 表: style='Table Grid', 表头格 shd GOLD_FILL + 白字黑体, 首列 GOLD/JADE 加粗
    #   blk = 引文/警示单格表 + shd (jade=JADE_FILL / cinnabar=CINNA_FILL / gold=GOLD_BG) + 对应边框色
    pass  # 见 {{WORKBUDDY}}\工具\build_docx_white.py 完整可运行版（本模板只给骨架 + 已验证原语）
    doc.save(OUT)
    print("SAVED", OUT)

if __name__=="__main__":
    main()
