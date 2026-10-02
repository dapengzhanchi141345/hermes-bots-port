#!/usr/bin/env python3
"""
格阅卷 · 物理评分引擎 v1.0
==========================
功能：OCR识别试卷 → 分步评分 → 生成报告
用法：
  1. 标准答案入库:  python grader_engine.py --mode store-answers --images img1.jpg img2.jpg
  2. 批量批改学生:  python grader_engine.py --mode grade --student-dir ./student_papers/ --answer-key ./answer_key.json
  3. 手动评分:      python grader_engine.py --mode manual --answer-key ./ak.json --student-json ./s.json
"""

import base64, json, os, sys, glob, re, time
from pathlib import Path

# ─── 配置 ──────────────────────────────────────────
AGNES_API_KEY_PATH = os.path.expanduser("~/.workbuddy/skills/agnes-ai-support/.agnes-key")
AGNES_API_URL = "https://apihub.agnes-ai.com/v1/chat/completions"
AGNES_MODEL = "agnes-2.0-flash"

# ─── 核心工具函数 ──────────────────────────────────

def load_api_key():
    try:
        with open(AGNES_API_KEY_PATH) as f:
            for line in f:
                if line.startswith("AGNES_API_KEY="):
                    return line.strip().split("=", 1)[1]
    except: pass
    return os.environ.get("AGNES_API_KEY", "")

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def call_agnes(messages, temperature=0.1, max_tokens=8192):
    """调用Agnes AI多模态模型"""
    import urllib.request
    key = load_api_key()
    if not key:
        return {"error": "API Key未找到"}
    data = json.dumps({
        "model": AGNES_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }).encode("utf-8")
    req = urllib.request.Request(AGNES_API_URL, data=data, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"text": result["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": str(e)}

# ─── OCR识别 ──────────────────────────────────────

def ocr_exam_images(image_paths):
    """识别试卷图片，返回结构化答案"""
    content = [{"type": "text", "text": "请仔细识别这张物理试卷中的所有题目编号和手写答案。逐题输出JSON，格式：{\"题号\": \"答案内容\"}"}]
    for p in image_paths[:4]:  # 最多4张
        b64 = encode_image(p)
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

    result = call_agnes([
        {"role": "system", "content": "你是一个物理阅卷OCR系统。仔细识别试卷图片中的题目编号和学生手写答案，输出JSON格式的题号->答案映射。"},
        {"role": "user", "content": content}
    ])
    return result

def ocr_single_exam(image_path):
    """识别单张试卷，返回答案映射"""
    b64 = encode_image(image_path)
    result = call_agnes([
        {"role": "system", "content": "你是一个精确的物理试卷OCR识别系统。请识别图片中的所有题目编号和学生手写答案，输出JSON格式。"},
        {"role": "user", "content": [
            {"type": "text", "text": "识别这张物理试卷图片中每一道题的题号和手写答案。请逐题列出，输出JSON。"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]}
    ])
    return result

# ─── 分步评分引擎 ──────────────────────────────────

def grade_choice(student_ans, standard_ans, score=2):
    """选择题评分"""
    sa = student_ans.strip().upper() if student_ans else ""
    st = standard_ans.strip().upper() if standard_ans else ""
    if sa == st:
        return {"earned": score, "total": score, "detail": "✓", "passed": True}
    return {"earned": 0, "total": score, "detail": f"✗ 应为{st}", "passed": False}

def grade_fill(student_ans, standard_ans, score=2):
    """填空题评分（关键词+数值容差）"""
    s = (student_ans or "").strip()
    st = (standard_ans or "").strip()
    if not s or not st:
        return {"earned": 0, "total": score, "detail": "未作答", "passed": False}
    # 数值容差
    n1 = re.search(r"[\d.]+", s.replace(",",""))
    n2 = re.search(r"[\d.]+", st.replace(",",""))
    if n1 and n2:
        v1, v2 = float(n1.group()), float(n2.group())
        if v1 == v2 or (v2 != 0 and abs(v1-v2)/abs(v2) <= 0.05):
            return {"earned": score, "total": score, "detail": "✓ 数值匹配", "passed": True}
    # 关键词匹配
    clean_s = re.sub(r"[\s，。、；：]", "", s)
    clean_st = re.sub(r"[\s，。、；：]", "", st)
    if clean_s == clean_st or clean_st in clean_s or clean_s in clean_st:
        return {"earned": score, "total": score, "detail": "✓ 关键词匹配", "passed": True}
    return {"earned": 0, "total": score, "detail": f"✗ 应为{st}", "passed": False}

def grade_calc(student_ans, standard_ans, score=10):
    """计算题四步分步评分"""
    s = (student_ans or "").strip()
    st = (standard_ans or "").strip()
    if not s:
        return {"earned": 0, "total": score, "detail": "未作答", "steps": {}}

    # 分配步分值
    fs = max(1, round(score * 0.3))   # 公式分
    ss = max(1, round(score * 0.3))   # 代入分
    rs = max(1, round(score * 0.25))  # 结果分
    us = score - fs - ss - rs         # 单位分
    if us < 0: rs += us; us = 0

    formula = sub = result = unit = 0
    has_f = bool(re.search(r"[=＝≈]", s)) and bool(re.search(r"[FGPWηρmghvtsSa-zA-Z]", s))
    has_sub = len(re.findall(r"\d+", s)) >= 2
    has_res = bool(re.search(r"[=＝≈]\s*[\d.]+", s)) or bool(re.search(r"[1-9]\d*\.?\d*", s))
    has_unit = bool(re.search(r"[NPaJWSmgk%→℃ΩVAC]|牛顿|帕|焦|瓦|米|千克|牛|秒|赫", s))

    if has_f: formula = fs
    if has_sub: sub = ss
    if has_res: result = rs
    if has_unit: unit = us

    earned = formula + sub + result + unit
    # 精确匹配提升分数
    nums_s = re.findall(r"[\d.]+", s)
    nums_st = re.findall(r"[\d.]+", st)
    if nums_s and nums_st and nums_s[-1] == nums_st[-1]:
        result = rs
        if has_f: formula = fs
        if has_sub: sub = ss
        earned = formula + sub + result + unit

    detail = f"公式{formula}/{fs} 代入{sub}/{ss} 结果{result}/{rs} 单位{unit}/{us}"
    return {"earned": min(earned, score), "total": score, "detail": detail,
            "steps": {"formula": f"{formula}/{fs}", "sub": f"{sub}/{ss}", "result": f"{result}/{rs}", "unit": f"{unit}/{us}"}}

def grade_experiment(student_ans, standard_ans, score=4):
    """实验题分步评分"""
    s = (student_ans or "").strip()
    st = (standard_ans or "").strip()
    if not s:
        return {"earned": 0, "total": score, "detail": "未作答"}

    pts = max(1, score // 4)
    earned = 0
    checks = {
        "method": bool(re.search(r"实验|方法|步骤|原理|控制变量|对比|转换", s)),
        "data": bool(re.search(r"\d+\.?\d*", s)) and bool(re.search(r"[NPaJWSmg]|记录|数据", s)),
        "conclusion": bool(re.search(r"结论|所以|因此|可知|可以|说明|因为", s)),
        "match": (re.sub(r"[\s，。、；：]", "", st) in re.sub(r"[\s，。、；：]", "", s) or
                  re.sub(r"[\s，。、；：]", "", s) in re.sub(r"[\s，。、；：]", "", st))
    }
    for v in checks.values():
        if v: earned += pts
    return {"earned": min(earned, score), "total": score,
            "detail": "方法✓"*checks["method"] + "数据✓"*checks["data"] + "结论✓"*checks["conclusion"] + "匹配✓"*checks["match"]}

# ─── 完整评分流程 ──────────────────────────────────

def grade_all_questions(student_answers, standard_bank):
    """用标准答案库评分所有题目"""
    results = {}
    total_earned = 0
    total_score = 0

    for q in standard_bank:
        qid = str(q["id"])
        sa = student_answers.get(qid, "")
        st = q["answer"]
        score = q.get("score", 2)
        qtype = q.get("type", "fill")

        if qtype == "choice":
            r = grade_choice(sa, st, score)
        elif qtype == "fill":
            r = grade_fill(sa, st, score)
        elif qtype == "calc":
            r = grade_calc(sa, st, score)
        elif qtype in ("experiment", "expt"):
            r = grade_experiment(sa, st, score)
        else:
            r = grade_fill(sa, st, score)

        results[qid] = r
        total_earned += r["earned"]
        total_score += score

    return results, total_earned, total_score

# ─── 报告生成 ──────────────────────────────────────

def generate_report(student_name, results, total_earned, total_score, details=None):
    """生成结构化评分报告"""
    pct = round(total_earned / total_score * 100, 1) if total_score > 0 else 0
    grade = "优秀" if pct >= 85 else ("良好" if pct >= 70 else ("及格" if pct >= 50 else "不及格"))

    lines = [
        f"📄 【{student_name}】评分报告：{total_earned}/{total_score}分（{pct}%）",
        "=" * 50
    ]
    for qid, r in sorted(results.items(), key=lambda x: x[0]):
        icon = "✅" if r.get("passed") or (r["earned"] >= r["total"]) else ("⚠️" if r["earned"] > 0 else "❌")
        lines.append(f"  {qid} {icon} {r['earned']}/{r['total']}分 | {r['detail']}")
        if "steps" in r and r["steps"]:
            steps = r["steps"]
            lines.append(f"     ├─ 公式{steps.get('formula','-')} 代入{steps.get('sub','-')} 结果{steps.get('result','-')} 单位{steps.get('unit','-')}")

    lines.append("=" * 50)
    lines.append(f"✅ 总分：{total_earned}/{total_score} | 正确率：{pct}% | 评级：{grade}")
    return "\n".join(lines)

def generate_class_report(all_reports, total_score):
    """生成班级统计报告"""
    if not all_reports:
        return "无数据"
    scores = [r["score"] for r in all_reports]
    pcts = [s/total_score*100 for s in scores]
    avg = sum(scores)/len(scores)
    best = max(scores)
    worst = min(scores)
    sorted_s = sorted(scores)
    median = sorted_s[len(sorted_s)//2] if len(sorted_s)%2 else (sorted_s[len(sorted_s)//2-1]+sorted_s[len(sorted_s)//2])/2
    var = sum((s-avg)**2 for s in scores)/len(scores)
    std = var**0.5
    pass_rate = sum(1 for s in scores if s/total_score>=0.6)/len(scores)*100

    lines = [
        "📊 班级学情报告",
        "=" * 50,
        f"总人数：{len(scores)} | 满分：{total_score}",
        f"平均分：{avg:.1f} | 中位数：{median:.1f}",
        f"最高分：{best} | 最低分：{worst}",
        f"标准差：{std:.1f} | 及格率(≥60%)：{pass_rate:.0f}%",
        "-" * 50,
        "排名："
    ]
    for i, r in enumerate(sorted(all_reports, key=lambda x: -x["score"]), 1):
        lines.append(f"  {i}. {r['name']}：{r['score']}分（{r['pct']:.0f}%）")
    return "\n".join(lines)

# ─── 主入口 ────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="格阅卷 · 物理评分引擎")
    parser.add_argument("--mode", required=True, choices=["ocr", "grade", "batch", "store-answers"])
    parser.add_argument("--images", nargs="+", help="试卷图片路径")
    parser.add_argument("--answer-key", help="标准答案库JSON文件路径")
    parser.add_argument("--student-dir", help="学生试卷文件夹")
    parser.add_argument("--student-json", help="学生答案JSON文件")
    parser.add_argument("--output", help="输出文件路径")
    args = parser.parse_args()

    if args.mode == "ocr":
        if not args.images:
            print("❌ 请指定图片路径")
            return
        for img in args.images:
            print(f"\n📷 OCR识别: {os.path.basename(img)}")
            result = ocr_single_exam(img)
            if "text" in result:
                print(result["text"][:3000])
            else:
                print(f"❌ {result.get('error', '未知错误')}")

    elif args.mode == "store-answers":
        """标准答案入库：OCR识别图片 → 保存答案库JSON"""
        if not args.images:
            print("❌ 请指定标准答案卷图片")
            return
        result = ocr_exam_images(args.images)
        if "text" in result:
            print("📋 OCR识别结果：")
            print(result["text"])
            out = args.output or "answer_key.json"
            with open(out, "w", encoding="utf-8") as f:
                # 尝试提取JSON部分
                text = result["text"]
                json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
                if json_match:
                    f.write(json_match.group(1))
                else:
                    f.write(text)
            print(f"\n✅ 标准答案库已保存: {out}")
        else:
            print(f"❌ {result.get('error', 'OCR失败')}")

    elif args.mode == "grade":
        """单学生评分：学生答案JSON + 标准答案库"""
        if not args.student_json or not args.answer_key:
            print("❌ 请指定学生答案JSON和标准答案库")
            return
        with open(args.answer_key, encoding="utf-8") as f:
            bank_raw = json.load(f)
        bank = bank_raw if isinstance(bank_raw, list) else bank_raw.get("answer_key", [])
        total = sum(q.get("score", 2) for q in bank)

        with open(args.student_json, encoding="utf-8") as f:
            students = json.load(f)
        if not isinstance(students, list):
            students = [students]

        all_reports = []
        for s in students:
            results, earned, _ = grade_all_questions(s.get("answers", {}), bank)
            report = generate_report(s.get("name", "未知"), results, earned, total)
            print(report + "\n")
            all_reports.append({"name": s.get("name","未知"), "score": earned, "pct": round(earned/total*100,1)})

        if len(all_reports) > 1:
            print(generate_class_report(all_reports, total))

    elif args.mode == "batch":
        """批量处理：文件夹中的所有学生试卷图片"""
        if not args.student_dir or not args.answer_key:
            print("❌ 请指定学生试卷文件夹和标准答案库")
            return
        with open(args.answer_key, encoding="utf-8") as f:
            bank_raw = json.load(f)
        bank = bank_raw if isinstance(bank_raw, list) else bank_raw.get("answer_key", [])
        total = sum(q.get("score", 2) for q in bank)

        images = sorted(glob.glob(os.path.join(args.student_dir, "*.jpg")) +
                        glob.glob(os.path.join(args.student_dir, "*.jpeg")) +
                        glob.glob(os.path.join(args.student_dir, "*.png")))
        if not images:
            print(f"❌ 未在 {args.student_dir} 中找到图片文件")
            return

        print(f"📂 找到 {len(images)} 份学生试卷，开始批量评分...\n")
        all_reports = []
        for img_path in images:
            name = os.path.splitext(os.path.basename(img_path))[0]
            print(f"  [{all_reports.count()+1}/{len(images)}] {name}...", end=" ", flush=True)
            result = ocr_single_exam(img_path)
            if "error" in result:
                print(f"❌ OCR失败")
                continue
            # 解析OCR结果为答案映射
            try:
                text = result["text"]
                json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
                if json_match:
                    answers = json.loads(json_match.group(1))
                else:
                    answers = json.loads(text)
            except:
                print(f"⚠️ 解析失败，跳过")
                continue
            # 评分
            results, earned, _ = grade_all_questions(answers, bank)
            report = generate_report(name, results, earned, total)
            print(f"✅ {earned}/{total}分")
            all_reports.append({"name": name, "score": earned, "pct": round(earned/total*100,1)})

        print("\n" + generate_class_report(all_reports, total))

        # 保存CSV
        if args.output:
            csv_path = args.output
            with open(csv_path, "w", encoding="utf-8-sig") as f:
                f.write("姓名,得分,满分,正确率\n")
                for r in all_reports:
                    f.write(f"{r['name']},{r['score']},{total},{r['pct']}%\n")
            print(f"\n📁 成绩表已导出: {csv_path}")

if __name__ == "__main__":
    main()
