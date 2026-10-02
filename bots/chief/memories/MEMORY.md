李彦明(MT5黄金/币量化,demo <MT5_ACCOUNT>当实盘练一月)。纪律:品种日≤3单计数闸,日亏10%熔断,连亏3笔24h冷却。系统16部门:高胜率≠正期望,裸反转/FVG只做否决门不正向提权。GBK子进程禁emoji。进化四段:P1风控SOP→P2放大正期望→P3飞轮→P4出徒月评审;P1已做(撤51幽灵单+7外汇休市周一清,TAOUSD多空对锁按LONG研判解=平空留多移SL,净值997.26)。order_send返OrderSendResult读.retcode(10009/10008/10010成功,10018休市跳过)。细节坑:技能mt5-multiagent-trading。
§
李老师专家团资产：导出包在 {{WORKBUDDY}}\专家团\专家团全量打包_20260920\（04_精读手册.md=人读全量、05_专家元数据.json=机读、00_README=迁移说明）；活体在 {{HERMES_HOME_PARENT}}\.workbuddy\plugins\marketplaces\my-experts\plugins\（41个）+ skills\（200+依赖技能）。路由总控见技能 expert-matrix-router；视频/单文件 HTML 教学系统见技能 teacher-video-lesson-team。两技能会话开始才加载。
§
关注的公众号「小登登」（Ai小登登/六小登登）是 AI 工具测评号；用户会丢文章让我「全部学习并融会贯通」，并按其推荐装多 agent 工具（如 Ekko Studio、agency-agents 等）。工作习惯：先全网深挖核验真实性、再固化成可反复调用的技能/专家团，而非仅做摘要。
§
铁律：李老师所有内容一律归 {{WORKBUDDY}}\内容中心\，所有会话/对话框无条件执行、不再逐次确认：收到原始素材（文章/链接/文件/截图）→ 原样存 收件箱\（按主题建子文件夹）；学到的方法论/工具核验/可复用片段 → 知识库\；备课成品（HTML教学系统/脚本/课件/视频）→ 课程\课题名\；对外成品+报告 → 交付\。根目录 00_README_使用说明书.md 是规范来源。例外：纯对话无产物时不落盘。
§
微信 iLink 通道已接入 Hermes gateway：账号 <WEIXIN_ACCOUNT_ID>（user_id <WEIXIN_USER_ID>），凭证在 {{WORKBUDDY}}\国外模型\hermes\weixin\accounts\，WEIXIN_ACCOUNT_ID 写入 .env。DM open（白名单未配，需要时再配）；仅私聊稳定，群聊收不到。
§
视频铁律：所有视频成品必须带水印「李彦明 <PHONE>」右下角、白色约40%透明、全程静态（在 Manim Base.setup 里 add，勿在剪辑层烧，换分辨率不丢）。传统文化系列用配色 C 玄金红，色板/护眼备选已写进技能 teacher-video-lesson-team「视频铁律」。
§
铁律：教学/信息科技任务先走 expert-matrix-router 路由到 it-edu-team V6.1（8席，席名/路径见技能与元数据 json）。用户会点名「码智君忘了调用」——教学任务第一动作判路由，不跳过。
§
用户有「岐黄医典」中医科普内容线：公众号号「山海拾珍」C5 类目，成品存 {{WORKBUDDY}}\公众号\山海拾珍\（按日期子目录，md+排版html+封面png）。体例：生活场景切入→六至七小节→白话翻译框→一句话收尾→文末免责声明「中医文化科普，不构成医疗建议」。已沉淀知识文档 {{WORKBUDDY}}\内容中心\知识库\中医太极深度融合_理论内核.md。
§
课题集群「中式体质测评(四维九式)」成品在 {{WORKBUDDY}}\内容中心\交付\2026-09_中式体质测评深度调研\(调研报告html/申报书md/B1单腿闭眼站立实验方案md/中考体育加试项试点方案md)。初中信息科技教师牵头,信息科技×体育×中医体质三科融合;核心论据=HRV为形-息-神内稳态现代读出头;文化阐释/机制层双线红线(经络/气/阴阳不作机制断言)。
§
GitHub 已打通（2026-09）：账号 dapengzhanchi141345，gh token 存 keyring，git 走 gh git-credential；提交身份同账号。github.com DNS 被掐：nameResolution.provider→{{HERMES_HOME_PARENT}}\.bin\resolve-dns.bat（aliyun DoH），偶发抖动重试。详见 github-auth 技能。
§
Agnes key 体系（用户只用 Agnes）：.cn 三把 key（FLASH/MEDIA 双 key 进 custom:agnes-flash 凭证池轮换；REASON 额度 0 未进池）；.com MAIN 与 legacy 同一把，RPM10 只作 fallback 跨端点兜底，.cn/.com 不互认、禁混池；V2.0 视频 9/25 下线插件自动改道 2.5-flash。