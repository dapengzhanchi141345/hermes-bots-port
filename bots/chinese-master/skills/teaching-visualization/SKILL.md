---
name: teaching-visualization
description: 学科教学可视化/动画/交互式课件制作。适用生物/物理/化学/地理等学科。含：需求分析→全网对标调研→技术选型→迭代优化→交付。纯技术向，不涉及玄学内容。
agent_created: true
---

# 学科教学可视化制作工作流 V1.0（2026-06-24创建）

> **原则边界**：本技能仅用于**学科教学类可视化**（生物/物理/化学/地理等）。
> 命理/风水/占卜 → 使用 tianji-ge-workflow 技能
> 量化交易 → 使用相关金融技能
> 编程教学 → 直接代码开发

## 一、需求分析阶段

1. **明确教学内容**：什么学科？什么章节？面向哪个年龄段？
   - 初中生物：人体/植物/动物/细胞
   - 初中物理：力学/电学/光学/热学
   - 初中化学：分子/原子/化学反应
   - 初中地理：气候/地质/天文

2. **明确交付形式**：
   - 单HTML文件（零依赖，双击可开）→ 适合课堂展示
   - 交互式探索 → Canvas/Three.js
   - 演示动画 → SVG/Canvas 动画
   - 信息图表 → D3.js/SVG

3. **确定技术路线**：
   - 简单示意图 → SVG（轻量、清晰、无极缩放）
   - 粒子/流体效果 → Canvas 2D（高性能、灵活）
   - 3D解剖/空间展示 → Three.js WebGL（需要CDN + HTTP服务）
   - 复杂交互 → Canvas + HTML overlay

## 二、全网对标调研阶段（重要！先学再写）

**在动手之前，必须先调研全网同类作品的最高水平。**

### 调研方法

| 来源 | 搜索关键词 | 目的 |
|:----|:----------|:-----|
| **GitHub** | `[topic] visualization javascript` `[topic] three.js` | 找开源对标项目 |
| **CodePen** | `[topic] canvas animation` `[topic] particles` | 看效果创意 |
| **学术可视化** | `[topic] interactive diagram` `[topic] 3D anatomy` | 找专业级参考 |
| **教学平台** | Innerbody / BioDigital / Visible Body / Zygote | 医疗/生物教学标杆 |
| **国内** | 帧理 / 知乎 / CSDN / 简书 | 中文教学可视化 |

### 核心技术差距分析

找到对标项目后，逐项对比：

```
我方当前方案 vs 行业标杆

| 维度 | 我方 | 标杆 |
|:----|:-----|:-----|
| 渲染技术 | Canvas/SVG | Three.js/WebGL |
| 交互方式 | 点击/悬浮 | 3D旋转/飞入/层次剥离 |
| 粒子数 | ~1200 | ~2100+（GPU加速） |
| 动画质量 | 简单运动 | Catmull-Rom曲线+流体 |
| 用户体验 | 基础功能 | 声音/HUD/快捷键/平滑过渡 |
```

## 三、技术选型决策树

```
教学可视化需求
  ├─ 纯示意图/流程图 → SVG（零依赖）
  │   ├─ 简单动画 → SVG CSS animation
  │   └─ 复杂动画 → Canvas 2D
  ├─ 数据驱动可视化 → D3.js / Canvas
  ├─ 3D空间展示 → Three.js WebGL (CDN)
  │   ├─ ES模块方式 → importmap + HTTP服务
  │   └─ 老式方式 → script src CDN
  ├─ 粒子/流体效果 → Canvas 2D / Three.js
  └─ 交互式教学 → Canvas + HTML overlay
```

### 单HTML文件的条件

| 技术 | 是否可单HTML | 是否需要HTTP服务 |
|:----|:-----------|:----------------|
| SVG | ✅ 是 | ❌ 不需要（直接双击） |
| Canvas 2D | ✅ 是 | ❌ 不需要 |
| Three.js (importmap) | ✅ 是 | ✅ 必须用HTTP（file://不支持ES模块） |
| Three.js (script tag) | ✅ 是 | ❌ 不需要（但版本较旧） |

## 四、迭代优化流程

```
V1 基础版 → 展示核心功能（客户反馈）
V2 优化版 → 改进视觉效果（客户反馈）
V3 深度版 → 增加交互/动画（客户反馈）
V4 对标版 → 研究标杆后重写底层（客户反馈）
V5 终极版 → 技术升维+全功能（最终定稿）
```

### 各级别质量标准

| 级别 | 粒子数 | 交互 | 动画 | 视觉 | 数据面板 |
|:----|:------|:----|:----|:----|:--------|
| ★☆☆☆☆ | <100 | 无 | 简单 | 基础 | 无 |
| ★★★☆☆ | ~500 | 点击 | 中等 | 较好 | 有 |
| ★★★★★ | 2000+ | 3D/旋转/飞入 | 粒子流体/ECG同步 | 发光/自发光/阴影 | 完整+冷知识 |

## 五、已固化的最佳实践

### 血细胞粒子系统

```javascript
// Catmull-Rom 样条插值（直接从HÆMA项目学习）
function catmullRom(pts, t) {
  const n = pts.length;
  const seg = (n - 1) * t;
  const idx = Math.min(Math.floor(seg), n - 2);
  const lt = seg - idx;
  const p0 = pts[Math.max(0, idx - 1)];
  const p1 = pts[idx];
  const p2 = pts[Math.min(n - 1, idx + 1)];
  const p3 = pts[Math.min(n - 1, idx + 2)];
  const t2 = lt * lt, t3 = t2 * lt;
  const x = 0.5 * ((2*p1[0]) + (-p0[0]+p2[0])*lt + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3);
  const y = 0.5 * ((2*p1[1]) + (-p0[1]+p2[1])*lt + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3);
  return [x, y];
}
```

### BioRender风格科学绘图规范（对标BioRender全球标准）

生成生物示意图时，遵循以下标准：

| 图类型 | 适用场景 | 配色方案 | 标注规范 |
|:-------|:---------|:---------|:---------|
| 流程图 | 代谢途径/信号通路 | 深底#0d0d1a + 金边#d4af37 | 关键酶标注E.C.编号 |
| 结构标注 | 细胞器/解剖图 | 半透明填充+轮廓线 | 引出线+中英双语 |
| 比对图 | 进化/分类对比 | 分类颜色编码(每类一色) | 特征矩阵行 |
| 概念图 | 知识体系梳理 | 层级颜色递减 | 关联线+关键词 |

### 跨学科PBL项目可视化规范

当生成STEM项目可视化时，按以下结构输出：

```
🎯 PBL项目模板
├─ 驱动问题
├─ 学科融合清单（生物+XX+XX）
├─ 学习目标（按Bloom分类）
├─ 活动时间线（4-6周）
└─ 评估矩阵
```

### Three.js血细胞粒子（HÆMA架构）

```javascript
// GPU BufferGeometry 粒子系统
const cellGeo = new THREE.BufferGeometry();
const pos = new Float32Array(CELL_COUNT * 3);
// 按路径长度分配粒子到各血管
// 每帧更新 position.attributes.needsUpdate = true
const cellMat = new THREE.PointsMaterial({
  size: .12, map: discTexture,
  vertexColors: true, sizeAttenuation: true
});
```

### 心脏脉动算法（从HÆMA学习）

```javascript
// 收缩期(systole)快速缩 → 舒张期(diastole)缓慢恢复
if (p < 0.13) squeeze = 1 - sin((p/0.13)*PI) * 0.16;  // 快速收缩
else if (p < 0.30) squeeze = 1 - sin(((0.30-p)/0.17)*PI) * 0.05;  // 缓慢恢复
else squeeze = 1;  // 静止
```

## 六、参考资料

- HÆMA 项目 (GitHub): `https://github.com/christianpasinrey/human-blood-system`
- Three.js 官方: `https://threejs.org/`
- BioDigital Human: `https://www.biodigital.com/`
- Innerbody: `https://www.innerbody.com/image/cardov.html`
