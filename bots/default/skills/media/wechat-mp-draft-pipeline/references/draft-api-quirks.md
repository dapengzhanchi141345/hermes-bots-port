# 微信草稿箱/素材 API 端点行为表（山海拾珍实测）

| 端点 | 方法 | 说明 |
|---|---|---|
| `cgi-bin/token` | GET | appid+secret 换 access_token（7200s）；40164 = 出口 IP 不在白名单 |
| `cgi-bin/draft/count` | GET | 草稿箱总数，最廉价的连通+计数探针 |
| `cgi-bin/draft/batchget` | **POST** | 请求体 `{"offset":0,"count":N}`；**GET 报 43002**；返回列表含 media_id + 首条图文 title/digest/content |
| `cgi-bin/draft/add` | POST | 推草稿箱不限量不耗群发额度；成功返回 `{media_id, item:[]}` |
| `cgi-bin/draft/get` | GET | 个人号有**缓存滞后**：刚推的常回空内容，属已知现象；回读校验主要用途是查 `\u` 乱码残留 |
| `cgi-bin/freepublish/submit` | POST | **个人订阅号 48001 api unauthorized**：群发只能人工点；1 次/日、每次 ≤8 篇 |
| `cgi-bin/material/add_material?type=image` | POST | 封面上传；53402/53403 偶发，重试 3 次内可恢复（mp_auto_publish.upload_image 已内置） |
| `cgi-bin/account/info` | GET | 报 40066 invalid url（端点名/方法不适配订阅号），别用它探活 |

排障序：draft/count（最便宜）→ draft/batchget POST → 看 40164/43002 定位白名单或方法问题。token 过期（40001/40014）时重建 token 续推即可，不回退到重推已完成篇（去重表兜底）。
