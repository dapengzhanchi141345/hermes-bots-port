---
name: color-design-sota
description: "Use when 配色/设计Token/UI无障碍/数据可视化配色任务需要引用最新 SOTA 工具与标准。"
---

# 色彩/视觉设计域 SOTA 增强技能（2026 版）

> 检索日 2026-09-27 · 带来源。配色产物遵守李老师护眼偏好（低饱和/避免红绿并置）；成品带右下角水印。

## 1. 设计 Token 体系 2026 SOTA
- **DTCG Specification 2025.10**（首个稳定版，2025-10-28 发布，Adobe/Google/Microsoft/Meta/Figma/Sony 等 20+ 编辑参与）：三层结构 = 原始值（primitive）→ 语义别名（semantic）→ 组件 token；支持 theming/多品牌/暗色模式/Display P3/OKLCH。参考实现：Style Dictionary 4.0、Tokens Studio、Terrazzo；支持工具 10+（Figma/Sketch/Framer/Penpot/zeroheight）。
- **最佳实践**：语义命名（`text-on-surface` 而非裸 `blue-600`）；在 token 层一次性校验对比度，组件作者只能引用已验证的配对。

## 2. 无障碍配色（WCAG 2.2 + APCA）
- **当前法律线 = WCAG 2.2 AA**：正文 4.5:1 / 大文本 3:1 / 非文本 UI 3:1（准则 1.4.11）。EU《欧洲无障碍法案》2025-06-28 起生效，卖欧洲产品有法定对比度门槛。
- **APCA**：更优对比模型（计字重/字号/极性），但 2023 被移出 WCAG 3 草案；**合规认 WCAG 2.2，APCA 作前瞻性加保**（Radix 用 APCA Lc60/90 保证文本步骤，监管读者需再按 2.2 AA 复核）。
- **色盲友好**：不单独用颜色传信息（WCAG 1.4.1），配图标/文字/形状；语义色跑 Machado-Olivia-Fernandes(2009) 变换 + ΔE-OK 距离检查。

## 3. 感知均匀色空间（关键技巧）
- **OKLCH**（CSS Color 4，Baseline 2023-05 起）：亮度感知均匀，等亮度步进可预测映射到对比度。
- **Material HCT Tone 差规则**：tone 差 40 保证 ≥3:1，tone 差 50 保证 ≥4.5:1 —— 无障碍变算术，不需事后 checker。
- **HSL 的坑**：同 50% 亮度不同色相实际亮度差很多（黄刺眼/蓝偏暗），按 HSL 建色板会反复踩坑。

## 4. 工具链（可落地）
1. **OKLCH/HCT 建 ramp**，按 tone 差 40/50 直接保证对比度。
2. **Adobe Leonardo**：给背景 + 目标比值（如 4.5:1）→ 反推生成颜色（目标当输入，hex 当输出）。
3. **Style Dictionary 4.0 + 自定义 contrast action**：CI 里遍历语义色对，低于 4.5:1 直接挂 build。
4. **axe-core**（真浏览器跑 CI，jest-axe 对颜色是盲的）。
5. **CSS `contrast-color()`**（Chrome 147/Firefox 146/Safari 26）：按背景亮度自动选黑/白文本，配 oklch/color-mix 无 JS 自校正主题。
6. Figma 侧：Variables（多 mode）+ Able 插件（免费，实时标 WCAG 违规）+ Tokens Studio。

## 5. 可落地 5 项（教师/教学场景）
1. 教学课件/单文件 HTML 用 DTCG 2025.10 语义 token，明暗双主题一次定义。
2. 护眼配色：低饱和 OKLCH ramp，正文文本 ≥4.5:1，避免红绿并置（色盲安全）。
3. 数据可视化：颜色只作辅助，关键差异靠形状/位置/标签（WCAG 1.4.1）。
4. 交付前用 Style Dictionary 对比度 action + axe-core 跑一遍，挂在 CI。
5. 引用标准时注明 WCAG 2.2 AA 为法律线，APCA 作前瞻。

## 来源（访问 2026-09-27）
- https://buildmvpfast.com/blog/accessible-color-systems-design-tokens-wcag-contrast-2026
- https://accessibility.build/guides/oklch-apca-color-systems
- https://dev.to/mr_manushukla/product-design-scoping-in-2026-7-deliverables-that-decide-whether-design-survives-engineering-1olg （DTCG 2025.10 发布时间/参与方）
- https://lenkastudio.com/blog/how-to-build-accessible-color-system-figma （Figma Able 插件流程）
- https://ayclaude.com/skills/moai-design-systems （对比度校验代码模板）
