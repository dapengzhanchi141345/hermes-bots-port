# CJK reportlab：字体注册、缺字形探测、文本层验证

出教学 PDF 合订本时，中文缺字形（豆腐块）是静默失败——PDF 正常生成、看起来也正常，印刷才崩。这份是操作细节。

## 字体注册（Windows）
reportlab 默认字体（Helvetica/Times）无 CJK 字形，中文全变空。必须注册 CJK TrueType 并全篇用它：

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("Hei",  "C:/Windows/Fonts/simhei.ttf"))   # 黑体
pdfmetrics.registerFont(TTFont("Kai",  "C:/Windows/Fonts/simkai.ttf"))   # 楷体
pdfmetrics.registerFont(TTFont("Fang", "C:/Windows/Fonts/simfang.ttf"))  # 仿宋
```
每个 ParagraphStyle（含 base style）都要 `fontName="Hei"`，漏一个就静默回退 Helvetica 丢中文。`.ttc` 集合（如 simsun.ttc）需 `TTFont(name, path, subfontIndex=0)`。reportlab 对 CJK 字体的 true bold 常缺失，加粗改用换色/换号，别依赖 `<b>`。

## 缺字形探测（生成前先探）
CJK 字体不完整，⑪⑫⑬⑭（U+246A+）、▶（U+25B6）、⭐（U+2B50）、⚠（U+26A0）、● 等常缺，渲染成 NUL 字节（\u0000）而非报错。探测法：先生成一页含候选符号的 throwaway PDF，再抽文本层：

```python
import pymupdf
d = pymupdf.open(tmp)
text = d[0].get_text()
# 缺字形的符号抽出来是 '\x00' 或缺失，所以用「该字符是否在 text 里」判断
for ch in ["⑫","▶","⭐","⚠","●"]:
    print(ch, "OK" if ch in text else "MISSING->replace")
```
确认后做替换表：⑪⑫⑬⑭→十一/十二/十三/十四，▶→★，⚠→!，⭐→◆。替换表放生成器顶部统一跑。

## 文本层验证（决定性，比 vision 可靠）
vision_analyze 看不出豆腐块（它读周边结构会说「看着正常」），只有文本层能抓。每册生成后：

```python
import pymupdf, re
d = pymupdf.open(out)
full = re.sub(r"\s+", "", "".join(p.get_text() for p in d))
assert full.count(chr(0)) == 0        # 无 NUL = 无缺字形豆腐块
assert "⑪" not in full                 # 圆圈数字已改中文
# 结构性标题计数 == 课数
assert full.count("教学过程") == 30
assert full.count("参考答案与深度解析") == 1
```

## 矢量导图（别占位）
reportlab `Drawing`（Rect/Line/String）画中心框 + 左右彩色分支 + 叶子 + 连线，分支主题配色，连线 ≥1.5pt，叶子字号 ≥7.5pt。数据驱动时节点取 `knowledge[]`。

## 全册数据驱动
单一 `ai_content.json`（lessons dict + _meta.units.frontier）供 3 个生成器循环读。改内容只改 JSON，重跑整册再生。pad 变长字段（activities 2-4 项→补到 3）；exercises.options 可能 None→`if e.get("options")` 守卫；frontier 喂 ⑩ 段（联网取 2025-2026 最新）。

**子代理扩题产出合并归一化（渲染/生成前必做闸门）**：
- 合并前断言当前每课题数，若已 10 题则**截断回前 10 再 append**（子代理重跑会重复注入→16 题/课）。
- 判断题 `answer` 文本化（"A"/"B"/"正确"/"错误"）→ 转 int 索引（判断题 options=['正确','错误']：A/正确→0、B/错误→1；单选 "C"→2）。前端/题卡渲染用 `String.fromCharCode(65+answer)`，文本答案全错。
- 简答题答案有时藏进 `explain`、`answer` 留空 → 合并时若 `type in(简答,挑战) and answer=="" and explain!=""` 则回填。
- `kp` 缺失 → 兜底 `e["kp"]=e.get("kp") or f"第{lid}课·题{i+1}"`（BKT/知识追踪按 kp 聚合，缺 kp 全丢）。
- 归一化在 Python 层做完写回 `ai_content.json` 再喂生成器/HTML build，**不在生成器里做防御性兜底**。
- 子代理落盘路径漂移：常写到 `{{HERMES_HOME_PARENT}}\`（家目录）而非工作目录，归位时多路径探测（`~/build_new_ex_*.json`、`build/_new_ex_*.json`、`build/build_new_ex_*.json`）。

## 新题配比与解析深度（10 题/课 配套练习制）
- **题量下限 10 题/课**：原 4 题保留，补造 6 题；题型混合 3 单选 + 2 判断 + 1 简答/挑战，难度分布基础 2 / 提升 2 / 挑战 2。题目必须避开与现有题重复（子代理读 `_exercises_full.json` 后再造）。
- **五维度解析才是出版级**：每道题的 answer 要带【考查点】考什么知识/能力、【解题思路】推理链（选择题逐项剖析 A/B/C/D 各对/错原因）、【易错警示】常见失分陷阱、【方法点拨】可迁移解法。只写「本题考查 XXX」一句话的深度 = 不合格（workbuddy 母版 676 题全配五维度解析）。
- 大扩写不手写：导出全册题 JSON → 派 6 子代理按 5 课分组并行（一组深化解析、一组补造新题）→ 合并回 `ai_content.json` → 重跑生成器。
