"""
八字排盘 · 自测脚本 v2
验证已知案例的正确性 + 直接在天机阁Skill中调用的路径
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import bazi_engine as be
from scripts import bazi_validator as bv
from scripts import calendar_utils as cu
from datetime import date


def test_known_day_pillars():
    """测试多个已知日柱（天数差法基准）"""
    print("\n📌 日柱基准测试")
    print("-" * 50)
    # 用推算逻辑验证的结果，而非随便假设
    tests = [
        # (公历年, 月, 日, 期望日柱, 说明)
        (1980, 12, 16, "癸亥", "刘东明生日"),
        (2000, 1, 1,  "戊午", "2000年元旦·已知基准"),
        (2024, 1, 1,  "甲子", "2024年元旦"),
        (2024, 2, 10, "甲辰", "2024年春节·甲辰年正月初一"),
        (1990, 1, 1,  "丙寅", "1990年元旦·距戊午基准-52"),
        (2026, 6, 24, "己巳", "今天·2026年6月24日"),
        (1949, 10, 1, "甲子", "1949年国庆"),
        (1976, 9, 9,  "甲子", "1976年9月9日"),
    ]
    all_pass = True
    for y, m, d, expected, desc in tests:
        result = cu.get_day_gan_zhi(date(y, m, d))
        passed = (result == expected)
        status = "✅" if passed else "❌"
        if not passed:
            all_pass = False
        print(f"  {status} {desc}: {y}-{m:02d}-{d:02d} → {result} (期望{expected})")
    return all_pass


def test_liu_dong_ming():
    """测试刘东明的八字（之前排错的核心案例）"""
    print("\n📌 刘东明·完整排盘测试")
    print("-" * 50)
    # 使用公历日期直接调用（这是天机阁Skill实际调用的路径）
    solar = date(1980, 12, 16)
    report = be.calculate_full_bazi_report(
        solar_date=solar,
        hour=4, minute=0,
        birth_place_longitude=118.73  # 山东寿光
    )
    be.print_report(report)

    # 验证四柱
    bazi = (report["pillars"]["year"]["gan_zhi"] +
            report["pillars"]["month"]["gan_zhi"] +
            report["pillars"]["day"]["gan_zhi"] +
            report["pillars"]["hour"]["gan_zhi"])
    expected = "庚申戊子癸亥甲寅"
    print(f"\n  八字: {bazi}")
    print(f"  期望: {expected}")
    match = (bazi == expected)
    print(f"  {'✅ 完全匹配！' if match else '❌ 不匹配！'}")

    if not match:
        print(f"  差异: {expected} vs {bazi}")

    return match


def test_double_verification():
    """测试三重验证机制"""
    print("\n📌 三重验证测试")
    print("-" * 50)
    solar = date(1980, 12, 16)
    report = be.calculate_full_bazi_report(
        solar_date=solar, hour=4, minute=0,
        birth_place_longitude=118.73
    )
    vr = bv.verify_all_pillars(report)
    bv.print_verification_report(vr)
    return vr["passed"]


def test_extra_cases():
    """额外边界测试（仅验证能正常调用不报错）"""
    print("\n📌 边界案例测试（仅检查无异常）")
    print("-" * 50)
    from datetime import date as dt
    cases = [
        dt(2024, 1, 1),
        dt(2024, 2, 10),
        dt(2000, 1, 1),
        dt(2026, 6, 24),
        dt(1949, 10, 1),
    ]
    all_pass = True
    for d in cases:
        try:
            report = be.calculate_full_bazi_report(d, hour=12, minute=0)
            bazi = (report["pillars"]["year"]["gan_zhi"] +
                    report["pillars"]["month"]["gan_zhi"] +
                    report["pillars"]["day"]["gan_zhi"] +
                    report["pillars"]["hour"]["gan_zhi"])
            print(f"  ✅ {d}: {bazi}")
        except Exception as e:
            print(f"  ❌ {d}: {e}")
            all_pass = False
    return all_pass


if __name__ == "__main__":
    print("=" * 55)
    print("  八字排盘引擎 · 完整自测 v2")
    print("  calc-bazi 脚本直调路径验证")
    print("=" * 55)

    results = []
    results.append(test_known_day_pillars())
    results.append(test_liu_dong_ming())
    results.append(test_double_verification())
    results.append(test_extra_cases())

    print("\n" + "=" * 55)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"  测试结果: {passed}/{total} 通过")
    if all(results):
        print("  ✅ 全部通过！排盘引擎健康。")
    else:
        print("  ⚠️ 存在失败用例，请检查。")
    print("=" * 55)
