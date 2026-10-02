# calc-bazi：八字排盘计算引擎

## 适用场景

需要精确计算八字四柱（年/月/日/时柱），或验证已有排盘是否准确。

## 能力

- ✅ 天数差法计算日柱（基准：2000.1.7=甲子日）
- ✅ 日柱双验证（主基准+副基准+已知点三重校验）
- ✅ 年柱（立春分界）+ 月柱（节气分界+五虎遁）+ 时柱（五鼠遁+真太阳时）
- ✅ 十神/藏干/纳音/空亡/地势/文昌（口诀法）
- ✅ 五行力量统计

## 使用方法

### 方式一：代码调用

```python
from datetime import date
from scripts.bazi_engine import calculate_full_bazi_report, print_report

# 刘东明案例
solar = date(1980, 12, 16)
report = calculate_full_bazi_report(solar, 4, 0, birth_place_longitude=118.73)
print_report(report)

# 输出：
# 八字: 庚申戊子癸亥甲寅
# 日主: 癸
```

### 方式二：验证已有排盘

```python
from scripts.bazi_validator import verify_day_pillar
from datetime import date

vr = verify_day_pillar(date(1980, 12, 16), "癸亥")
print("通过:", vr["passed"])
for c in vr["checks"]:
    print(c["method"], c["result"], "OK" if c["passed"] else "FAIL")
```

## 排盘铁律（内置验证）

1. **日柱双验证**：每次计算自动用2个基准日校验，不一致则报警
2. **文昌口诀法优先**：禁止用推导代替口诀（如乙日文昌在午，非巳）
3. **五鼠遁复核**：时柱自动基于日干重算
4. **节气月令**：月柱以节气为界

## 已知参考点（内置校验用）

| 日期 | 干支 | 用途 |
|------|------|------|
| 2000-01-07 | 甲子 | 主基准 |
| 2024-01-01 | 甲子 | 副基准 |
| 1980-12-16 | 癸亥 | 用户案例 |
