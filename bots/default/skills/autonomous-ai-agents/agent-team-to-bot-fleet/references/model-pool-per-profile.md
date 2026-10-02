# 每个 bot profile 的模型池落地细节

目标：N 个 bot profile 各自能用共享的 Agnes key 池对话，不重复填 key、不撞 provider 名、不泄漏 key。

## 结构（与既有 chief/risk-officer profile 同构）
每个 `profiles/<bot>/config.yaml` 顶层：
```yaml
model:
  default: agnes-3.0-flash
  provider: agnes-<bot>      # 该 bot 专属池名，指向共享端点
  base_url: https://api.agnes-ai.cn/v1
  context_length: 512000
providers:
  agnes-flash:
    api: https://api.agnes-ai.cn/v1
    base_url: ...
    api_key: <从 source config 提取，勿手敲>
    key_env: AGNES_FLASH_API_KEY
    discover_models: false
    models: {agnes-3.0-flash: {}, agnes-2.5-flash: {}, ...}
  agnes-reason: / agnes-media: / agnes-main: ...   # 复用 4 池
  agnes-<bot>:
    api: https://api.agnes-ai.cn/v1
    base_url: https://api.agnes-ai.cn/v1
    key_env: AGNES_KEY_<BOT>   # 指向 .env 里该 bot 的 key 变量
    models: {agnes-3.0-flash: {}}
fallback_providers:
- provider: agnes-main
  model: agnes-3.0-flash
- provider: agnes-flash
  model: agnes-3.0-flash
```

## 关键点
- **池名隔离 vs key 复用**：若所有 bot 都写同一个 provider 名会串到同一池。每个 bot 用独立池名 `agnes-<bot>`，但 `base_url`/`key_env` 可指向同一端点 + 同一 key 变量（key 复用，池名隔离，互不影响）。
- **fallback 只挂文本模型**：`fallback_providers` 每条目 `{provider, model}`，model 必须是该 provider `models:` 白名单里的文本模型；挂 image/video 是语义错误（对话补位时拿视频模型当文本调，400）。规则同 provider-pool-audit。
- **key 提取不 echo**：从已知好的 source config（default/chief 的 config.yaml）用正则按池名取 `api_key:` 值写进模板；输出/日志/聊天只报「池名+模型名」，不打 key。config 内 `api_key:` 是快照，`.env` 的 `*_API_KEY` 是实际凭证，两边都查。
- **key_env 变量**：主池 provider 的 `key_env: AGNES_KEY_<BOT>` 要在该 bot `.env` 有值（从 default `.env` 拷），否则池解析不到 key。缺则取值追加，不打印。

## 分组共用 key（N 个 key 管 M 个 bot）
用户常按「功能组」申请 key：每组共用一把 key，组内多个 bot 共享配额但彼此独立计费。落地形态：
- **每个 bot 的池仍读自己的 `AGNES_KEY_<BOT>` 变量**（保持池名隔离、计费隔离），只是同组各 bot 的 `.env` 里写入**同一把 key 值**。既满足「同组共用一个 key」，又保住各 bot 独立 key_env 槽位。
- 批量写入用脚本：`组 -> (key值, [bot...])` 映射，对每个 bot 用正则 `^AGNES_KEY_<BOT>=.*$` 精准替换该 bot `.env` 里那一行（勿 `>>` 追加产生重复行）。
- **写后全量核对**（关键步，防变量错配）：每个 bot 取其 `config.yaml` 里主池的 `key_env` 名，断言该变量在 `.env` 已含 `sk-`。一行命令：`grep -oE 'AGNES_KEY_[A-Z_0-9]+' config.yaml` 拿到变量名，再 `grep -cE "^${var}=sk-" .env` 应为 1。22/22 全过才算配齐；有异常单独报出。
- **抽 2 个不同组的 bot 实测**：`hermes -p <bot> chat -q` 真出答案（证明走的是新 key 而非 fallback 共享池），不同组各抽一个确认 key 真的分开了。
- 金策等独立 runtime 岗用独立 key 变量（`_CHIEF`/`_RD`/`_RISK`），不进功能组分池，物理隔离交易与教学流。

## 验证
- `hermes profile list` 全在册，Model 列显示 `agnes-3.0-flash`。
- 冒烟 `hermes -p <bot> chat -q "你好"` 能出字（池通）。出字 = key + provider + fallback 链全对。
- gateway 不热加载 `fallback_providers`：改兜底链要重启 gateway 才生效，别把「文件改了」说成「已生效」。
