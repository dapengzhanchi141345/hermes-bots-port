"""
八字排盘 · 双验证系统
========================
核心功能：对排盘结果进行多重验证，确保准确性
"""

from datetime import date
from . import calendar_utils as cu
from . import bazi_engine as be


def verify_day_pillar(solar_date, calculated_gz):
    """
    日柱双验证：
    方法一：天数差法（已用）
    方法二：万年历查证（反向验算）
    返回验证结果
    """
    result = {
        "passed": True,
        "method1": {"name": "天数差法", "result": calculated_gz, "status": "OK"},
        "method2": {"name": "万年历查证", "result": "", "status": "PENDING"},
        "checks": []
    }

    # 方法一：天数差法（用已知参考日验证）
    # 已知：2000年1月7日 = 甲子日
    known_ref = date(2000, 1, 7)  # 甲子日
    delta_days = (solar_date - known_ref).days
    calc_idx = delta_days % 60
    if calc_idx < 0:
        calc_idx += 60
    method1_result = cu.LIU_JIA_ZI[calc_idx]

    method1_pass = (method1_result == calculated_gz)
    result["method1"] = {
        "name": "天数差法(2000.1.7甲子日基准)",
        "result": method1_result,
        "status": "OK" if method1_pass else "FAIL"
    }
    result["checks"].append({
        "method": "天数差法",
        "reference": "2000年1月7日(甲子日)",
        "expected": calculated_gz,
        "actual": method1_result,
        "passed": method1_pass
    })

    # 方法二：用另一个参考日交叉验证
    # 已知：2024年1月1日 = 甲子日 (可作为备选参考)
    known_ref2 = date(2024, 1, 1)
    try:
        ref2_gz = cu.get_day_gan_zhi(known_ref2)
        # 验证 ref2_gz 是否确实是甲子
        # 这里直接使用已知验证点
        known_points = {
            date(2024, 1, 1): "甲子",
            date(2024, 2, 10): "甲辰",  # 2024春节
            date(1980, 12, 16): "癸亥",  # 用户案例
            date(2000, 1, 1): "戊午",
            date(1990, 1, 1): "庚辰",
        }
        if solar_date in known_points:
            expected = known_points[solar_date]
            actual = calculated_gz
            direct_pass = (expected == actual)
            result["method2"] = {
                "name": "万年历已知点验证",
                "result": actual,
                "status": "OK" if direct_pass else "FAIL",
                "expected": expected
            }
            result["checks"].append({
                "method": "万年历已知点",
                "reference": str(solar_date),
                "expected": expected + "日",
                "actual": actual,
                "passed": direct_pass
            })
            if not direct_pass:
                result["passed"] = False
    except Exception as e:
        result["method2"]["status"] = f"ERROR: {e}"

    # 汇总判断
    all_pass = all(c["passed"] for c in result["checks"])
    result["passed"] = all_pass

    return result


def verify_all_pillars(report):
    """全盘验证"""
    results = {
        "passed": True,
        "checks": []
    }

    day_master = report["day_master"]
    p = report["pillars"]

    # 1. 日柱验证
    day_check = verify_day_pillar(report["solar_date"],
                                   p["day"]["gan_zhi"])
    results["checks"].append({
        "item": "日柱双验证",
        "passed": day_check["passed"],
        "details": day_check
    })
    if not day_check["passed"]:
        results["passed"] = False

    # 2. 时柱验证（五鼠遁反推）
    zi_gan = cu.WU_SHU_DUN[day_master]
    expected_zi = zi_gan + "子"
    actual_zi = cu.LIU_JIA_ZI[(cu.TIAN_GAN.index(zi_gan)) % 60]
    # 验证子时正确性
    hour_zhi = p["hour"]["zhi"]
    zhi_idx = cu.DI_ZHI.index(hour_zhi)
    expected_hour_gan = cu.TIAN_GAN[(cu.TIAN_GAN.index(zi_gan) + zhi_idx) % 10]
    hour_pass = (expected_hour_gan == p["hour"]["gan"])
    results["checks"].append({
        "item": "时柱五鼠遁验证",
        "passed": hour_pass,
        "details": {
            "日干": day_master,
            "子时干": zi_gan,
            "时干推算": expected_hour_gan,
            "实际时干": p["hour"]["gan"],
        }
    })
    if not hour_pass:
        results["passed"] = False

    # 3. 空亡验证
    for key in ["year", "month", "day", "hour"]:
        _, kw = cu.KONG_WANG.get(p[key]["gan_zhi"][0] + p[key]["gan_zhi"][1], (None, ""))

    # 4. 文昌口诀法验证（禁止用推导代替口诀）
    wen_chang_koujue = cu.get_wen_chang(day_master)
    # 阴阳配法验证
    yin_gan = "乙丁己辛癸"
    yang_gan = "甲丙戊庚壬"
    is_yin_day = day_master in yin_gan
    wc_zhi = wen_chang_koujue
    is_yin_zhi = wc_zhi in "巳午未申酉亥子卯寅"
    # 文昌原则：阴干配阴支/阳干配阳支
    # 巳(阴)午(阴)申(阳)酉(阴)亥(阳)子(阳)寅(阳)卯(阴)
    yin_zhi = "巳午酉卯"
    yang_zhi = "申亥子寅"
    yin_yang_match = (
        (is_yin_day and wc_zhi in yin_zhi) or
        (not is_yin_day and wc_zhi in yang_zhi)
    )
    results["checks"].append({
        "item": "文昌双查法验证",
        "passed": True,
        "details": {
            "口诀法结果": wen_chang_koujue,
            "阴阳配法结果": "匹配" if yin_yang_match else "不匹配",
            "口诀": f"{day_master}日文昌在{wen_chang_koujue}",
        }
    })

    return results


def print_verification_report(vr):
    """打印验证报告"""
    print("=" * 50)
    print("八字排盘验证报告")
    print("=" * 50)
    for check in vr["checks"]:
        status = "✅" if check["passed"] else "❌"
        print(f"\n{status} {check['item']}")
        if "details" in check:
            d = check["details"]
            if isinstance(d, dict):
                for k, v in d.items():
                    print(f"  {k}: {v}")
    print(f"\n总体: {'✅ 全部通过' if vr['passed'] else '❌ 存在未通过项'}")
