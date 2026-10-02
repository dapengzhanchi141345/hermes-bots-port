# 天机阁 HTML 成品配方（可复用）

## §0 农历转公历（锁定日期，第一步必做）
```bash
pip install lunar_python
python -c "from lunar_python import Lunar; print(Lunar.fromYmd(2000,8,9).getSolar().toYmdString())"  # 2000-09-06
# 验证锚点也用工具查，不许记：
python -c "from lunar_python import Lunar; print(Lunar.fromYmd(2000,8,15).getSolar().toYmdString())"  # 该年中秋公历日
```
- 只认正常月；若该年有闰月，先确认目标月是否存在，闰月用带闰标志的 API（`Lunar.fromYmdH` 系列或加 flag）。
- 转出的公历日期是日柱/月柱/起运的根基，错了全链错。

## §1 排盘引擎调用
引擎在 `{{WORKBUDDY}}\国外模型\hermes\profiles\tianji-ge\skills\calc-bazi`，`cd` 到该目录以相对导入运行：
```python
import sys; sys.path.insert(0,'.')
from datetime import date
from scripts import calendar_utils as cu
from scripts.bazi_engine import calculate_full_bazi_report, print_report
solar = date(2000,9,6)
report = calculate_full_bazi_report(solar, 4, 0, birth_place_longitude=118.77)  # 寿光经度
print_report(report)
# 日柱双验证
print(cu.verify_day_pillar(solar, cu.get_day_gan_zhi(solar))['passed'])
# 起运：阳男阴女顺/阴男阳女逆；出生日到上/下节气天数 ÷3 取整
```
真太阳时校正：出生地经度 λ，`offset=int((λ-120)*4)` 分钟；寅时(3-5点)无子时争议，子时才需说明流派。

## §2 视觉骨架（单文件 HTML 关键 CSS 片段）
- 配色变量：宣纸底 `--paper:#f6f1e6`、墨 `--ink:#232019`、朱砂 `--cinnabar:#9e2b25`、金 `--gold:#a5813b`、玉绿 `--jade:#3e6b5a`、水 `--water:#31556b`、木 `--wood:#4a7c59`。衬线 `Noto Serif SC`。
- 页眉 `.hero`：深色渐变+内框+朱砂印章 seal；副标 letter-spacing 拉宽。
- 章节 `.sec-head`：中文序号（壹贰叁…）+h2+虚线 rule；`section[id]{scroll-margin-top:64px}`。
- 四柱盘 `.chart`：grid 4 列，日柱高亮（`.pillar.day` 朱砂顶边+红字+badge）；每柱含 天干/十神/地支/藏干/地势/空亡/纳音。
- 五行条形 `.wx-row`：grid `34px 110px 1fr 64px`；`.bar i` 宽度=百分比，五行色渐变；入场动画+兜底。
- 用神表：`.tag.yong`(朱砂底白字)/`.tag.ji`(灰底) 标注；五行色 `.tag.huo/.shou`。
- 大运时间轴 `.timeline`：flex 横滚 8 格，当前运 `.tl-item.now`（朱砂顶边+阴影+'当前'tl-flag）。
- 流年卡片 `.years`：`auto-fit minmax(230px,1fr)`；`.year-card.best`(金边渐变)/`.risk`(灰左边框)；星级 `★★★★<span class=off>★</span>`。
- 性格/六亲 `.cards3`：三列卡片+评分 `.star-line`。
- 引文/按语 `.quote`（朱砂左边框）/`.quote.master`(金边)；提示 `.tip.warn/.good/.info`。

## §3 升级层（多轮打磨逐项打勾）
1. 响应式：`@media(max-width:560px)` 四柱盘转 2 列、字号下调。
2. 粘性目录 `nav.toc`（独立 max-width+padding，勿负 margin）+阅读进度 `#progressbar`+返回顶部 `#top-btn`(scrollTop>600 显示)。
3. 关键数据速览 `.statbar`：八字/格局/用神/忌神/现运/层次 六格。
4. 浏览器实测：`new_tab(file://...)` → `js()` 断言（见 §4）。
5. 动画兜底：`.bar i` 存纯数字 data-w，`IntersectionObserver` 触发 + `setTimeout(1500)` 兜底 expandAll，确保不停在 0。
6. 修 bug 复测（v= 查询参数强制重载）。
7. 视觉/DOM 验收（元素计数、当前大运高亮、无横向溢出）。
8. 无障碍：`prefers-reduced-motion:reduce` 全局关动画，且脚本该偏好下跳过 IO 分支直接定宽。
9. 页脚生成信息：排盘引擎参数+起运+生成时间+版本。
10. 打印样式 `@media print`：隐藏 nav/进度/按钮/水印，section 避免跨页断，statbar 4 列。

## §4 验收断言清单（js 执行）
```js
({stats:q('.stat').length, pillars:q('.pillar').length, tl:q('.tl-item').length,
  years:q('.year-card').length, sec:q('section[id]').length,
  nowItem:q('.tl-item.now .gz').textContent,                          // 当前大运
  bars:[...q('.bar i')].map(i=>i.style.width),                       // 应=百分比
  hOverflow:document.body.scrollWidth>window.innerWidth+2,           // 应 false
  footer:q('footer').textContent.includes('生成时间')})
```
截图 `capture_screenshot` 可能 IPC 超时→失败就降级 DOM 断言+重试，勿阻塞。

## §5 归档与交付
- 写 `{{WORKBUDDY}}\内容中心\命理\<姓名>_<类型>_<农历日期+时辰+出生地>.html`。
- 回复末尾 `MEDIA: {{WORKBUDDY}}\内容中心\命理\<文件名>.html`。
- 必附免责声明：命理仅供文化参考，不作医疗/投资决策；健康以执业医师为准。
