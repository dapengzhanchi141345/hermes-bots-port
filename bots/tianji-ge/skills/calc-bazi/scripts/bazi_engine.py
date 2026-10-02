"""
八字排盘 · 核心计算引擎
直接调用 calendar_utils 中的函数，完成完整排盘
"""
from datetime import date
from . import calendar_utils as cu


def calculate_full_bazi_report(solar_date, hour, minute,
                               birth_place_longitude=None):
    """
    完整八字排盘（基于公历日期）

    参数：
        solar_date: datetime.date 公历日期
        hour: 出生小时（24小时制）
        minute: 出生分钟
        birth_place_longitude: 出生地经度（可选，用于真太阳时校正）

    返回：
        dict: 完整的排盘报告
    """
    # 真太阳时校正
    tz_offset = 0
    if birth_place_longitude is not None:
        tz_offset = int((birth_place_longitude - 120) * 4)

    # 年柱
    year_gz, real_year = cu.get_year_gan_zhi(solar_date.year, solar_date)
    year_gan, year_zhi = year_gz[0], year_gz[1]

    # 月柱
    month_gz = cu.get_month_gan_zhi(year_gan, solar_date.month, solar_date.day)
    month_gan, month_zhi = month_gz[0], month_gz[1]

    # 日柱
    day_gz = cu.get_day_gan_zhi(solar_date)
    day_gan, day_zhi = day_gz[0], day_gz[1]

    # 时柱
    hour_gz, adj_hour, adj_min = cu.get_hour_gan_zhi(
        day_gan, hour, minute, tz_offset
    )
    hour_gan, hour_zhi = hour_gz[0], hour_gz[1]

    # 构建四柱
    pillars = {}
    pillar_data = [
        ("year", year_gan, year_zhi, year_gz),
        ("month", month_gan, month_zhi, month_gz),
        ("day", day_gan, day_zhi, day_gz),
        ("hour", hour_gan, hour_zhi, hour_gz),
    ]

    for key, gan, zhi, gz in pillar_data:
        pillars[key] = {
            "gan": gan,
            "zhi": zhi,
            "gan_zhi": gz,
            "shi_shen": cu.get_shi_shen(gan, day_gan),
            "cang_gan": cu.get_cang_gan(zhi),
            "na_yin": cu.NA_YIN.get(gz, ""),
            "kong_wang": cu.get_kong_wang(gz),
            "di_shi": cu.get_di_shi(day_gan, zhi),
        }

    # 五行统计
    wuxing = {"金": 0.0, "木": 0.0, "水": 0.0, "火": 0.0, "土": 0.0}
    GAN_WX = {"甲乙": "木", "丙丁": "火", "戊己": "土", "庚辛": "金", "壬癸": "水"}
    ZHI_WX = {"寅卯": "木", "巳午": "火", "申酉": "金", "亥子": "水", "辰戌丑未": "土"}

    for key, p in pillars.items():
        for ks, wx in GAN_WX.items():
            if p["gan"] in ks:
                wuxing[wx] += 2.0
                break
        for ks, wx in ZHI_WX.items():
            if p["zhi"] in ks:
                wuxing[wx] += 2.0
                break
        for cg, level in p["cang_gan"]:
            for ks, wx in GAN_WX.items():
                if cg in ks:
                    wt = 1.5 if level == "本气" else (0.8 if level == "中气" else 0.4)
                    wuxing[wx] += wt
                    break

    return {
        "solar_date": solar_date,
        "adjusted_time": f"{adj_hour:02d}:{adj_min:02d}",
        "timezone_offset": tz_offset,
        "pillars": pillars,
        "day_master": day_gan,
        "wuxing": wuxing,
        "wen_chang": cu.get_wen_chang(day_gan),
        "bazi_str": year_gz + month_gz + day_gz + hour_gz,
    }


def print_report(report):
    """打印排盘报告"""
    print(f"公历日期: {report['solar_date']}")
    print(f"校正时间: {report['adjusted_time']}")
    print(f"真太阳时校正: {report['timezone_offset']:+d}分钟")
    print()
    print(f"八字: {report['bazi_str']}")
    print(f"日主: {report['day_master']}")
    print(f"文昌（口诀法）: {report['wen_chang']}")
    print()
    for key in ["year", "month", "day", "hour"]:
        p = report["pillars"][key]
        cg = ", ".join([f"{g}({l})" for g, l in p["cang_gan"]])
        print(f"  {key}: {p['gan_zhi']} | 十神: {p['shi_shen']} | "
              f"藏干: {cg} | 纳音: {p['na_yin']} | "
              f"空亡: {p['kong_wang']} | 地势: {p['di_shi']}")

    print("\n五行统计:")
    total = sum(report["wuxing"].values())
    for wx, val in sorted(report["wuxing"].items(), key=lambda x: -x[1]):
        pct = val / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {wx}: {bar} {pct:.0f}%")
