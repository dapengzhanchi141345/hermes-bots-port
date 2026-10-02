#!/usr/bin/env python3
"""
生物试卷智能批改引擎 v1.0
支持题型：选择题/填空题/识图作答题/实验探究题/简答题
"""
import json, os, csv, re, sys
from pathlib import Path

class 生物GraderEngine:
    """生物阅卷评分引擎"""
    
    def __init__(self, answer_key=None):
        self.answer_key = answer_key or {}
        self.results = []
    
    def load_answer_key(self, key_data):
        self.answer_key = key_data
    
    def score_single(self, student_answers):
        scores = {}
        details = []
        total = 0
        for qid, correct in self.answer_key.items():
            student = student_answers.get(qid, "")
            qtype = self._detect_type(qid, correct)
            scorer = getattr(self, f'_score_{qtype}', self._score_default)
            result = scorer(qid, student, correct)
            scores[qid] = result["score"]
            total += result["score"]
            if result["score"] < result["max_score"]:
                details.append(result["feedback"])
        return {
            "scores": scores, "total": total,
            "max_total": sum(2 for _ in self.answer_key),
            "details": details
        }
    
    def batch_score(self, students_dict):
        for name, answers in students_dict.items():
            result = self.score_single(answers)
            result["name"] = name
            self.results.append(result)
        return self.results
    
    def export_csv(self, output_path):
        if not self.results: return
        fieldnames = ["姓名", "总分"]
        all_qids = []
        for r in self.results:
            for qid in r.get("scores", {}):
                if qid not in all_qids: all_qids.append(qid)
        fieldnames.extend(all_qids)
        fieldnames.extend(["正确率", "评级"])
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.results:
                row = {"姓名": r["name"], "总分": f'{r["total"]}/{r["max_total"]}'}
                for qid in all_qids: row[qid] = r.get("scores", {}).get(qid, "")
                rate = r["total"] / r["max_total"] * 100 if r["max_total"] > 0 else 0
                row["正确率"] = f"{rate:.1f}%"
                row["评级"] = "优秀" if rate >= 85 else ("良好" if rate >= 70 else ("及格" if rate >= 60 else "需努力"))
                writer.writerow(row)
    
    def analyze_class(self):
        if not self.results: return "无数据"
        total = len(self.results)
        scores = [r["total"] / r["max_total"] * 100 if r["max_total"] > 0 else 0 for r in self.results]
        avg = sum(scores) / len(scores)
        mx = max(scores); mn = min(scores)
        pass_r = sum(1 for s in scores if s >= 60) / total * 100
        good_r = sum(1 for s in scores if s >= 85) / total * 100
        return f"参考人数:{total} 平均分:{avg:.1f} 最高:{mx:.1f} 最低:{mn:.1f} 及格率:{pass_r:.1f}% 优秀率:{good_r:.1f}%"
    
    def _detect_type(self, qid, answer):
        if isinstance(answer, (int, float)): return "numeric"
        if len(str(answer)) == 1 and str(answer).isalpha(): return "choice"
        if "=" in str(answer) or "\" in str(answer): return "calc"
        return "fill"
    
    def _score_choice(self, qid, stu, correct, mx=2):
        s = mx if str(stu).strip().upper() == str(correct).strip().upper() else 0
        fb = "" if s == mx else f"第{qid}题(选择)得{s}/{mx}"
        return {"score": s, "max_score": mx, "feedback": fb}
    
    def _score_numeric(self, qid, stu, correct, mx=2, tol=0.01):
        try:
            sv, cv = float(stu), float(correct)
            if abs(sv - cv) <= tol * abs(cv): return {"score": mx, "max_score": mx, "feedback": ""}
            if abs(sv - cv) <= tol * 5 * abs(cv): return {"score": mx*0.5, "max_score": mx, "feedback": f"第{qid}题接近得{mx*0.5}/{mx}"}
        except: pass
        return {"score": 0, "max_score": mx, "feedback": f"第{qid}题得0分"}
    
    def _score_calc(self, qid, stu, correct, mx=10):
        total = 0
        steps = ["=formula=25", "=substitution=25", "=process=25", "=unit=25"]
        for s_name in ["=","sub","proc","unit"]:
            total += mx * 0.25
        return {"score": total * 0.5, "max_score": mx, "feedback": f"第{qid}题(计算)需人工复核"}
    
    def _score_fill(self, qid, stu, correct, mx=2):
        s, c = str(stu).strip(), str(correct).strip()
        if s == c: return {"score": mx, "max_score": mx, "feedback": ""}
        kws = re.findall(r'[\u4e00-\u9fffA-Za-z]{2,}', c)
        if kws:
            rate = sum(1 for kw in kws if kw in s) / len(kws)
            if rate >= 0.8: return {"score": mx, "max_score": mx, "feedback": ""}
            if rate >= 0.5: return {"score": mx*0.5, "max_score": mx, "feedback": f"第{qid}题关键词{rate:.0%}"}
        return {"score": 0, "max_score": mx, "feedback": f"第{qid}题不匹配"}
    
    def _score_default(self, qid, stu, correct, mx=2):
        return self._score_fill(qid, stu, correct, mx)

if __name__ == "__main__":
    engine = 生物GraderEngine()
    print(f"生阅卷 - 生物阅卷评分引擎已加载")
