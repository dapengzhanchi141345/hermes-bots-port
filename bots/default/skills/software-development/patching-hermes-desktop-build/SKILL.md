---
name: patching-hermes-desktop-build
description: "Use when patching a packaged Hermes desktop app's renderer."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, electron, asar, win-unpacked, build, hot-patch]
    related_skills: [hermes-agent, inspecting-hermes-desktop-dom]
---

# 给打包态 Hermes 桌面端打 UI 补丁并让运行中应用加载

Hermes 桌面端在 Windows 上跑的是 electron-builder 打包出的 `Hermes.exe`，它的**渲染进程资产不是从你改的源码或 `dist/` 加载，而是从打包输出目录 `win-unpacked` 下的 loose 文件读**。改一个 UI 常量（如 `GROUP_CHAT_MAX_MEMBERS`）想要让正在运行的桌面端生效，直接改源码 + `npm run build` 是**不够的**——必须把新 build 产物同步到运行副本的 unpacked 区并重启。本技能管这条「改源码 → build → 落到运行副本 → 重启生效」的完整工序。

## 先判定运行态（决定改哪里）

1. **当前 exe 从哪加载 renderer**：`Get-Process -Name Hermes | Select Path`（或 `tasklist`）看路径。若是 `...\apps\desktop\release\win-unpacked\Hermes.exe`，运行副本 = `win-unpacked/resources/`：
   - `app.asar` —— 打包态，renderer 的 index.html 等**没被 unpack** 的文件在这里面（需 asar 重打，成本高）。
   - `app.asar.unpacked/dist/` —— **被 unpack 的 loose 文件**（electron-builder 把 `dist/index.html` 和 `dist/assets/*.js` 标 unpacked，直接以 loose 文件落在这里，electron main 优先读这里，不走 asar 内嵌）。这是热补丁的落点。
2. 看 `win-unpacked/resources/app.asar.unpacked/dist/index.html` 引用的 bundle 名（`index-<hash>.js`），与 `dist/assets/` 里新 build 的 index 名对比——**两者 hash 名不同**（旧 `index-HX2wgsDm.js` vs 新 `index-BX0KkxoG.js`），不能只改 asar 内嵌，必须让 unpacked 的 index.html 指向新 bundle。

## 工序（改 UI 常量为例，以 GROUP_CHAT_MAX_MEMBERS 为实例）

1. **改源码**：`apps/desktop/src/plugins/hermes-bots/group-chat.ts` 里 `export const GROUP_CHAT_MAX_MEMBERS = 6` → 目标值。这是单一事实源，UI 文案 `Pick 2–X bots` 和 `slice(0, X)` 全引用它，改 1 处全联动。
2. **build**：`cd apps/desktop && npm run build`（跑 `assert-root-install` + `vite build` + `bundle-electron-main` + `stage-native-deps`，产物在 `dist/` + `dist/assets/`）。build 不会自动重打 asar 或碰 win-unpacked。
3. **同步到运行副本 unpacked**（关键步，否则重启无效）：
   - 备份：`cp win-unpacked/resources/app.asar.unpacked/dist/assets/index-<旧hash>.js .../backup_index_<旧hash>.js`、`cp .../index.html .../backup_index_html.html`。
   - 覆盖 loose index：`cp dist/assets/index-<新hash>.js win-unpacked/resources/app.asar.unpacked/dist/assets/index-<旧hash>.js` **（保持旧名）**——让旧 index.html 在改前仍指向旧名也能命中新内容；再单独把新名 bundle 也拷进 unpacked/assets（`cp dist/assets/index-<新hash>.js ...`）。
   - 换 index.html 引用：`cp dist/index.html win-unpacked/resources/app.asar.unpacked/dist/index.html`（新 index.html 引用新 hash 名 `index-<新hash>.js`）。
   - **同步全部新 assets**：`cp dist/assets/*.js win-unpacked/resources/app.asar.unpacked/dist/assets/`（新 build 可能引用了改名/新增的 chunk，漏拷会 404/白屏；`cp -f` 覆盖同名旧文件补齐差量）。
4. **核对**：grep 运行副本新 bundle 确认新值落地（如 `grep -c '1e5' .../index-<旧hash>.js`、`grep -oE 'slice\(0,nO\)' .../index-<旧hash>.js`、`grep -oE 'nO=1e5' ...`）。minifier 把 `100000` 编成 `1e5`、把常量编成短变量名（如 `nO`），核对要认 minified 形式而非源码字面量。
5. **重启桌面端**：完全退出（托盘右键退出，不只关窗）再重开。exe 启动时读 unpacked 的 index.html → 新 bundle → 新值生效。

## 验证改对了（别假设）
- 重启后到对应 UI 路径目测新行为（建群弹窗文案变 `Pick 2–<新值> bots`、可拉满 N 个 bot）。
- 回滚预案：用第 3 步备份的 `backup_index_<旧hash>.js` + `backup_index_html.html` 覆盖回 unpacked，再同步回旧 `dist/assets/*.js`，重启恢复旧值。

## Pitfalls

- **`npm run build` 不碰 win-unpacked**：它只写 `dist/`。改完源码 build 完就告诉用户「已生效」是错的——必须做第 3 步同步 unpacked + 重启。判「生效」看 exe 启动是否读到新 bundle（运行副本 unpacked 的 index.html + 其引用的 js），不看 `dist/`。
- **asar 内嵌 vs unpacked 双层**：electron main 加载顺序是「unpacked 同名 loose 文件优先，否则读 asar 内嵌」。`dist/index.html` 与 `dist/assets/*.js` 在本仓库标 `unpacked: true`（asar header 里查 `unpacked` 字段可证），所以热补丁走 unpacked 即可，不必重打 asar；只有未 unpack 的内嵌文件才需要 asar 重打（`@electron/asar` 或 `npm run builder`）。
- **bundle 是 minified 的，常量被改名**：`GROUP_CHAT_MAX_MEMBERS=100000` 在 bundle 里是短变量名 + `1e5`（科学计数法）。核对时 `grep 100000` 会漏，要 `grep 1e5` 或反查该组件的 `slice(0, <短名>)`。定位短名：grep 组件里的稳定文案（如 `Pick 2`）拿到上下文，再找上下文里的 `slice(0,X)` / `length>=X` 变量。
- **index.html 与 bundle 的 hash 名要一致**：旧 index.html 引 `index-旧hash`、新 build 出 `index-新hash`。只拷 js 不换 index.html → exe 仍引旧名（旧名被新内容覆盖则 OK）；最稳做法是 index.html + 旧名 js + 新名 js 三者都同步到位，避免任何一处引用悬空。
- **重命名/新增的 chunk 漏拷会白屏**：新 build 可能拆出改名 chunk，unpacked 里还留着旧名集合。`cp dist/assets/*.js` 全量同步一次最省心（多出来的旧文件无害）。
- **多 bot 同群放大了 429 风险**：把 `GROUP_CHAT_MAX_MEMBERS` 拉满后，一个群里 N 个 bot 并发响应吃同一把 key（若它们属同一功能组共用 key）+ 撞 `gateway.bot_loop_guard`（默认 300s 内 20 条触发全群 600s 冷却）。拉大上限是体验目的时要预期这点；必要时同步把 loop guard 的 `max_events` 调高或退回小群玩法。
- **`hermes.exe` 有主+GPU+renderer 多个进程**：改文件不影响正在跑的旧进程，必须整个桌面端完全退出再重开才加载新 bundle；托盘退出要确认进程数归 0（`Get-Process -Name Hermes` 空）。

## Verification

- 运行副本 `win-unpacked/resources/app.asar.unpacked/dist/` 里：index.html 引用 bundle 名 = 已同步 js 名；该 js 含 minified 新值；`Get-Process -Name Hermes` 重启后为空→非 0（新进程起来了）。
- UI 目测对应交互项的新行为（文案/上限/可选数量）符合目标值，且无白屏/控制台 404（新 chunk 全拷齐）。
