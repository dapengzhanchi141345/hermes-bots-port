---
name: tianji-ge-delivery
description: "Use when 交付天机阁命理文化报告成品: 精密HTML, 多轮打磨定型, 归档内容中心。"
version: 1.0.0
author: Hermes Agent (curator)
metadata:
  hermes:
    tags: [tianji-ge, delivery, html]
---

# 天机阁成品交付流程（精密HTML）

## 用户铁律（本技能的最高约束）
1. **交付形态**：成品一律为**精密单文件HTML**（不是 markdown/纯文本），存 `{{WORKBUDDY}}\内容中心\` 对应目录（命理→`命理/`），并以 `MEDIA:` 卡片发送。
2. **打磨深度**：定稿前须做多轮（≥10轮量级）深度优化升级：导航/进度/数据速览/微交互/无障碍/打印样式，并实际浏览器验收后才交付。
3. **计算先行**：任何命理结论必须先经精确排盘引擎验证，先算后写，严禁凭记忆推盘。

## 标准流程（按序）
1. **农历→公历锁定**：用户给农历时，先用万年历工具转公历，禁止凭记忆推算（记忆锚点如\"中秋=某月某日\"经常整体错位且后续双验证全绿仍会排错）。命令与细节见 `references/html-recipe.md` §0。
2. **精确排盘**：调用 calc-bazi 引擎（`{{WORKBUDDY}}\国外模型\hermes\profiles\tianji-ge\skills\calc-bazi`）出四柱+藏干/十神/纳音/空亡/地势/文昌+五行力量+大运起运，做日柱双验证与时柱五鼠遁复核。节气边界（月柱、起运数节气）必须落在已锁定的公历日期上。
3. **命理解读**：按 tianji-ge 技能 `references/cheng-guan-yun.md` 的 14 章模板组织内容（程观运 persona）。女命六亲规则勿套男命；安全硬规矩自查（免责声明、不承诺吉凶、健康须转介执业医师）。
4. **生成 HTML 成品**：单文件、内联 CSS/JS、14 章全部落进 HTML；视觉骨架与可复用代码片段见 `references/html-recipe.md`（含大运时间轴、流年星级卡片、五行条形图、粘性目录、阅读进度条、返回顶部、打印样式、prefers-reduced-motion 兜底）。
5. **多轮打磨**：至少覆盖——①响应式/微交互 ②粘性目录+进度条 ③关键数据速览条 ④浏览器实测 ⑤动画兜底（确保条形图不会停在 0）⑥修 bug 复测 ⑦视觉/DOM 验收 ⑧无障碍（减少动态偏好下跳过动画）⑨页脚生成信息。每轮改完用浏览器或 DOM 断言验证，勿目视臆断。
6. **验收**：优先 DOM/JS 断言（元素计数、无横向溢出、条形图宽度=百分比、当前大运高亮、页脚标记）；`capture_screenshot` 可能超时（页面高或截图服务繁忙），失败就降级用 DOM 断言 + 重试，不要卡死在截图上。
7. **归档 + 交付**：写入 `{{WORKBUDDY}}\内容中心\命理\<姓名>_<类型>_<关键出生信息>.html`（同名旧 md 保留或覆盖由任务定），回复末尾附 `MEDIA: <绝对路径>`，并重申命理免责。

## 常见坑（附机制）
- **农历日凭记忆**：双验证只保证'两个基准自洽'，不保证'基准正确'；公历日期错→日柱全错且验证全绿。用 lunar_python 锁定后再算，连验证锚点（该年中秋/春节公历日）也须工具查，不许记。
- **动画 data-* 属性双重百分号**：把百分比文本（`"38%"`）直接存进 data 属性又拼一次 `%` 得 `"38%%"`，CSS 宽度解析失败停在 0。存纯数字，渲染时再补 `%`；加兜底定时器确保最终可见。
- **headless 里 IntersectionObserver/scroll 不稳**：滚动触发可能不生效，务必有 setTimeout 兜底展开；并在 `prefers-reduced-motion` 下直接跳过动画分支。
- **截图超时**：高页面 `capture_screenshot` 会 IPC 超时（60s+）；改用 `js()` DOM 断言验收，截图失败不阻塞交付。
- **sticky 目录负边距**：`.wrap` 有横向 padding，TOC/statbar 若放 `.wrap` 外用负 margin 对齐会溢出；改给它们独立 max-width+auto margin+自身 padding。
- **表格 nowrap 全局化**：为移动端横滚加 `table{white-space:nowrap}` 会撑爆所有表格列；只让容器 `overflow-x:auto`，单元格保持 `white-space:normal`。

## 与自有技能的关系
核心排盘规则属用户自有技能 `calc-bazi`/`tianji-ge`（非 curator 管理，自动修补被拒）。本技能只承载**交付形态与流程**；若用户希望把'农历必须工具锁定''交付=精密HTML'写进自有技能，需其执行 `hermes curator adopt calc-bazi` / `hermes curator adopt tianji-ge` 后由用户自行维护。

## 参考
- `references/html-recipe.md`：农历转换命令、HTML 视觉骨架与可复用片段、验收断言清单。
