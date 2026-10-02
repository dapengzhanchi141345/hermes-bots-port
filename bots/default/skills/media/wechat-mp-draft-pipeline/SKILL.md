---
name: wechat-mp-draft-pipeline
description: "Use when 推山海拾珍公众号稿件进草稿箱、查草稿箱状态或补推积压稿。API 直连+去重表+排期目录。"
version: 0.1.0
author: li-yanming, Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [wechat, 公众号, 草稿箱, 山海拾珍, 排期]
---

# 公众号草稿箱管线（山海拾珍单号）

李老师公众号已合并为单号「山海拾珍」（旧双号瀚海/云海配置已废弃，`双号API配置.json` 里只看 `shanhai` 段）。

## 基本事实（不变量）
- 个人订阅号：API 只能推**草稿箱**（`draft/add` 不限量）；**群发无 API 权限**（freepublish 48001）→ 最后的「发表」由李老师手动点，1 次/日、每次最多 8 篇。规划里任何「全自动发布」表述都要落到这个边界。
- 凭证：`{{WORKBUDDY}}\公众号\双号API配置.json` 的 shanhai 段（appid/secret/whitelist_ip）。token 报 40164 = 出口 IP 不在白名单（家宽 IP 会漂，建议白名单按 /16 段配）。
- 排期目录：`{{WORKBUDDY}}\公众号\山海拾珍\<YYYY-MM-DD>\`，每篇三件套：`<stem>.md`（精修稿，front-matter 含 标题A/摘要/发布日期/类目）+ `<stem>_排版.html`（`tools\wechat_typeset.py` 产物，须回显「版式校验通过」）+ `<stem>_封面_16x9.png`（`tools\cover_design.py` 程序化产物，零 AI 画中文）。
- 去重唯一事实源：`tools\_pushed.json`（`push_state.py` 读写；`norm_title` 剥离【】日期前缀再比对，所以「带前缀推」和「不带前缀推」记同一条，跨管线不重复）。
- 数据回流：`数据回流\<日期>.md`（时间|栏目|排版皮|封面|media_id|状态）。
- 既有 cron：「教联日更流水线」每日 05:00 与「论文课题流水线」周六 09:00，切轨前挂起态（见 `hermes cron list`）——不要重复建。

## 标准动作（按序，全部已验证）
1. **连通性一枪验完**（execute_code，无 LLM 参与）：取 token（`cgi-bin/token`）→ `draft/count`（GET）→ `draft/batchget` **必须 POST**（GET 报 43002）。`account/info` 返回 40066 属正常，别当故障。token 成功即 API 全通。
2. **缺料补齐**：缺 `_排版.html` → `wechat_typeset.py <md> <html>`（跑完必须确认文件真实存在且回显「版式校验通过」，勿信被截断的回显）；缺封面 → `cover_design.py <日期> <stem> <标题A> <类目>`（第一参数是**日期目录名**不是全路径，输出默认 `ROOT\山海拾珍\<日期>\<stem>_封面_16x9.png`）。
3. **批量推进箱**：`tools\batch_push_all.py`（`--from YYYY-MM-DD` 支持断点范围）；标题自动加【X月X日】前缀（取 front-matter 发布日期，缺则目录名）；单篇失败不阻塞；重跑自动跳过已推。
4. **记账**：每篇成功后 `mark_pushed(原始标题A, media_id)`；批末用 `draft/count` 总量核对。
5. 中文编码铁律：所有 API 请求体 `ensure_ascii=False`（`mp_auto_publish.http_json` 已内置 + 对字面 `\u` 转义就地拦截）；响应按原始字节 UTF-8 解码，不信 Content-Type 头。

## Pitfalls（类级）
- **bash 变量展开会吃掉中文文件名**：`"$f_排版.html"` 在 git-bash 里被解析为 `$f_`（空）+「排版.html」，静默生成错误文件名且后续步骤全报「缺排版」。涉及中文路径/文件名的拼接一律用 Python subprocess，不做 shell 插值。
- **draft/get 回读缓存滞后**：个人号推完立即 `draft/get` 常返回空内容，`verify_draft` 会报「暂未返回内容」——这是已知现象不是失败，向用户说「后台目检一次」即可，别反复重推（重推靠去重表拦截）。
- **字段截断**：digest ≤38 字（≈120 字节）、标题整体 ≤64 字节、payload 不传 author（带值 45110）——`mp_auto_publish.add_draft` 已处理，手写 payload 时照抄。
- **规划先落盘再建任务**：李老师的模式是「先给规划汇报 → 拍板 → 落地」；cron 若未到期生效要先以 paused 态建好并写明恢复条件，避免提前空跑撞存量排期。
- 批量任务用后台 terminal + notify，跑完核对 `draft/count` 与日志尾行 `done: 新推 X / 跳过 Y / 失败 Z`，失败项单独补推后再报完成。

## references/
- `references/draft-api-quirks.md`：草稿箱/素材 API 端点行为表（GET vs POST、错误码语义、缓存滞后），排障时查。
