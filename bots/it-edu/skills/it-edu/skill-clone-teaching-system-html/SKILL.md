---
name: skill-clone-teaching-system-html
description: "按已有单文件HTML教学系统模板为新课程做同款系统, 内容取自教材docx三件套。"
version: 1.0.0
author: li-yanming, Hermes Agent
metadata:
  hermes:
    tags: [it-edu, teaching-system, html-clone]
---

# 克隆单文件HTML教学系统

用户有成套单文件HTML教学系统(全离线零依赖, 双击即用, localStorage存进度)。给新课程做"同款"系统时, 必须严格复刻模板的页面结构与JS引擎, 只换内容。成品存 `{{WORKBUDDY}}\内容中心\教学系统\<课程名>\`。收到"按XX模板做XX教学系统/同款教学系统"类任务时加载本技能。

## 输入定位
1. 模板 = 已有系统的最新带练习版HTML(通常文件名含"含全册练习"或位于"教学系统终版"目录), 在 `{{WORKBUDDY}}\xinxikeji\做好的内容\教学系统终版\`。选体积最大、结构最全的(侧边栏+工具页+多引擎)。
2. 教材三件套 = 新课的《教学设计合订本》《导学案合订本》《配套练习合订本》docx(通常与模板同目录), 内容全部从这三份提取, 禁止凭记忆编课程。逐课数、单元划分以教学设计合订本目录为准。

## 模板解剖(先做, 决定生成器结构)
按序grep/分段读模板:
- 侧边栏导航: 每课按钮 `data-page="lN"` + 单元 `nav-group`; 工具页 pbl/design/exam/lab/dash/badge/kb/map/typing/report/practice 各自 `id="p-xxx"`。模板侧边栏的每个工具按钮都对应一个页面 div; 克隆时必须逐个确认该 div 在**主 CSS**(`<style>` 块)里有配套样式类(如 `.lab-*`/`.mp-*`/`.kb-*`/`.rpt-*`/`.pp-*`), 模板自己的 CSS 经常漏配(模板页面多但样式少), 整段抄模板 CSS 后仍会缺类, 导致工具页"看着有壳没形"。缺类要在生成器里补(如 `css_extra` 补丁), 不能假设模板 CSS 齐全。
- 工具页正文与 JS 动态填充的分工: 模板里 badge/dash/map/report 等页正文是占位 div + JS `renderBadges()/initDash()/renderMap()/rptRender()` 动态填充, 首屏"正文短"是正常形态, 判空壳要看 JS 引擎函数是否存在 + 桩驱动后 DOM 是否被填充, 不能只看 div 长度。但"按钮在、引擎函数缺失"的页是真空壳, 必须补引擎或删按钮。
- 页内 iframe 练习引擎: 模板用 `srcdoc`(同源, 主页面 JS 可跨查 contentWindow 做进度/错题回写), 不是 base64 数据 URL。克隆时把引擎 HTML 字符串经 `f.srcdoc = PRACTICE_HTML` 注入; 引擎自带的交互 JS 也嵌在同一字符串里。
- 删模块(如打字)要全链路清除: 侧边栏按钮 + 页面 div + 该模块**专属的 `<style id="xxx">` 独立块**(模板有多个 style 块, 主 style 之外还有 typingStyle/deepCss 等) + js_core.js 全局数据注入行(`var TYPING = __TYPING__` 这类残留行是**整段引擎的 ReferenceError 炸弹**: 一行抛错会让后面所有引擎函数全部未定义, 用户表现为"系统点了没反应"——删模块后必须 grep `__模块名__` 确认 0 残留) + 学情报告/进度统计里引用该模块指标的 JS 行(置 0/删行) + 文案("六位一体"改"五位一体") + localStorage 清理白名单里的旧 key。漏掉 `var TYPING = __TYPING__` 这类单行注入是删模块最常见的翻车点。
- 每课页面 `p-lN` 固定Tab结构: 知识Tab + 学习目标/深度精讲/动手实践/易错辨析/本课小结/复习·证据/AI素养/掌握度(BKT)/星级挑战 + 课末 `<div id="q-lN">` 测验容器。
- JS引擎块: 核心 `S(id)` 导航(最先执行的script里另有一份防崩版), `tab()`, `quizData`(课→题数组 {q,o,a,hint,analysis}), `lessonObj`(课→k/p/e/reflect/四维标签), `initPage`, 搜索索引, 进度/徽章/仪表盘, examQBank模拟考, TypingApp打字, kb词条数据。
- 关键: 全册练习是页内 iframe(模板多为 `srcdoc` 同源注入, 早期版本是 base64 数据 URL 嵌 `window.__PRAC_SRC`), 克隆新课必须**单独构建**配套练习引擎HTML再注入, 不能照抄旧课程的练习。

## docx 提取(无pip环境下的可靠方法)
```python
import zipfile,re
xml = zipfile.ZipFile(d).read('word/document.xml').decode('utf-8')
xml = re.sub(r'<w:p [^>]*>|<w:p>', '\n', xml)
text = re.sub(r'<[^>]+>', '', re.sub(r'<w:br[^>]*>', '\n', xml))
```
存成txt再解析。提取完立即 `json.dump` 分课: 教学设计按 `第 N 课` 头切块; 练习按 `第 N 课 · 配套练习` 切题、按附录 `附 录 参 考 答 案` 切答案; 导学案按 `第 N 课 · 导 学 单` 切。这些JSON是生成器唯一数据源, 存工作目录(如 `{{HERMES_HOME_PARENT}}\ai_course\`)。

## 验证(必须真浏览器, node冒烟会漏整类bug)
node冒烟/桩测试对**启动执行顺序bug**有盲区: 桩里"驱动全部页+调启动函数"往往在错误路径上没真正走到(或被try/catch吞掉), 报SMOKE_OK但浏览器里实际白屏。交付前用真实Chromium做一遍渲染验收:
- **浏览器后端优先, 不可用再自建 Playwright(本任务已验证可用的最快路径)**: 直接用系统自带的 `browser_exec` 工具开 `file:///E:/.../xxx.html` 最省事; 仅当该后端报"找不到Chromium/后端错误"时, 才自建: `npx --yes playwright install chromium` + `npm install playwright --no-save --registry https://registry.npmmirror.com`, 写独立 node 脚本跑。**别在 browser_exec 失败后反复重试它**(本会话在"后端找不到"上浪费了多轮)——失败即切自建 Playwright, 自建后稳定可用且能收集 `pageerror` 完整堆栈。
- 脚本要点: `chromium.launch({headless:true})` → `page.goto(file://...)` → **`page.on('pageerror')`收集全部运行时错误并打印完整堆栈**(堆栈行号直接对应HTML里的行, 是定位"某个函数报错"最快的路) → 点开练习页iframe → 统计iframe DOM节点数(题项/选项/填空区) → 确认零pageerror + 题数>0才算过。
- 用户报"点开没内容/某个页空白"时, 优先怀疑**主窗口启动脚本中途抛错导致后续注入没执行**(如 iframe srcdoc 赋值在启动链尾部), 而不是内容数据缺失; 堆栈会直接指向抛错函数。
- **拼接式单script块的启动顺序陷阱**(本类任务最隐蔽的bug): 多份JS文件由生成器拼进**同一个`<script>`块**时, 执行顺序 = 拼接顺序, 但函数声明hoisting≠var初始化执行顺序。若文件A(靠前)末尾的启动调用(`initWelcome()`等)会执行到文件B/C(靠后)里才定义的函数, 那些函数体内的 `var x = 赋值语句`(顶层var, 非函数声明)此时**尚未执行到**, `x` 提升后仍是 `undefined` → 抛ReferenceError中断整块脚本 → 块内其后的 `iframe.srcdoc=`/其他注入全部没跑 → 表现为"某页空白"而数据其实都在。修复: 把启动调用挪到**所有JS拼接完成后的块尾**执行, 或把被启动函数依赖的变量赋值挪到启动调用之前; 拼好成稿后按块内字符位置核对"启动调用行 vs 关键变量赋值行 vs 被调函数定义行"的先后。
- **`!important` 隐藏类压死内联 display(整组页打不开的独立根因)**: 工具页 div 自带 `class="hidden"`(对应 `.hidden{display:none!important}`), 而导航 `S(id)` 只设内联 `p.style.display='block'` 时, `!important` 类永远赢内联样式 → 该页及其后所有被嵌套进来的页 0×0。修复: 导航函数必须先 `p.classList.remove('hidden')` **再** `p.style.display='block'`, 两条都做, 缺前者必现"点侧栏某页空白"。这条常与 div 不平衡、启动顺序 bug 同时存在, 三者要分开各查一遍。
- **生成器拼接后先查文件完整性**: `wc -c` 逐份检查所有待拼接的 `js_*.js`, **0字节文件必是写失败/截断残留**(某次write_file超时或被覆盖清空), 它承载的整个功能模块(仪表盘/徽章/进度等)会静默丢失, 用户症状是"某功能点不动"。发现0字节文件立即从模板重新提取该模块, 别当作"本来就没有"。
- **DOM 层"页面无形"三件套(与启动顺序bug并列的"点开没内容"另一大根因, 数据全在但看不见)**: 用户报"某页点开空白"且 JS 数据侧(题数/注入/渲染函数)都验证通过时, 在真浏览器依次查: ① **生成器各页 HTML 块 div 不平衡**: 逐个页变量(或最终 HTML 里每个 `id="p-*"` 块)统计 `<div` 与 `</div>` 数必须相等——**缺一个 `</div>` 浏览器就把后续所有页解析进该页内部**(嵌套错误恢复), 该页启动时被 `display:none` 时, 套在里面的一整组页(常含练习页)全部 0×0 永远打不开。修法是给对应字符串块尾补齐 `</div>`。② **`.hidden{display:none!important}` 压死内联样式**: 页 div 自带 `class="hidden"` 而导航函数只设内联 `style.display='block'` 时, `!important` 类永远赢内联——导航函数必须 `el.classList.remove('hidden')` 再设 display, 两条都做。③ **iframe 0×0 塌高**: `#practiceFrame{height:100%}` 依赖父级 `.pp-frame` 有确定高度; 实测必须 `getBoundingClientRect()` 拿到非 0 宽高才算渲染成功(题项数>0 但 rect 0×0 = 内容在 DOM 但看不见)。
- **真浏览器结构验收(交付前必跑, 比题数统计更狠)**: 除"iframe 题项数>0"外, 还须: ① 遍历 `main [id^="p-"]`, 沿 parentElement 数到 main 的深度, **任何页 depth>2(嵌套进别的页)= div 不平衡未修好, 回炉**; ② 目标页/iframe 的 `getBoundingClientRect` 宽高非 0; ③ 沿祖先链 grep `display=none`/`hidden` 类, 定位藏住目标页的祖先。三条全过才算"点开有内容"。

- **多行 `\n"+` 拼接引擎字符串中改一行会静默丢整段代码**: iframe 引擎等 JS 常以 `"line\n"+
    "line\n"+...` 形式拼接, 行尾 `"\n` 与下一行首 `"` 之间的 `+` 是整段有效性的关键。往其中一行注入代码(如给 `selOpt` 加日志钩子)时: patch 的 old_string 必须覆盖**整行含续接符**(即带行尾的 `"` 与下一行起始), 且 new_string 保持同样的续接结构; 改完立即在**生成的拼接产物**(不是源文件)里 grep 该段后面的函数名(如 `toggleAns`/`showAll`)确认仍存在, 再跑 `node --check`——`node --check` 对源 .js 永远 0 错, 抓不到"拼接后函数被吞", 只有产物 grep + 真浏览器零 pageerror 能抓住。症状特征: 某交互功能整体消失且无报错, 静态兜底(base64烤死)与运行时引擎双双丢失该功能。

## 解析客观题的坑(反复踩过)
- 练习题面格式: `N. ` 独占一行, 其后是题面行, 再是 `    A.` 等4空格缩进选项行。取题面时**只收集 `N.` 到选项行之间、且不属于别的题的连续行**——遇 `数字.` 行(下一题号)、`一、/二、`章节标题行必须立即停, 否则前序填空/章节标题会污染题面(本类任务最常返工处)。
- 答案匹配: 答案册用 `单N. 【参考答案】X` 前缀对应题号N; 选项序 = ord(letter)-65; 解析整段抓 `单N.` 起含五个【】的行直到下一题标记。判断题前缀是 `判N`; 同一课题号在题区和答案区各自连续, 别混。

## 生成与验证
- 生成器: 读模板骨架(head/CSS/侧边栏/工具页/JS引擎) + 注入新课数据(课名/lessonObj/quizData/词条/exam bank/练习引擎), 输出单一HTML到内容中心目录。
- 数据先全部落JSON并自检(每课题数、答案全覆盖、题面无污染打印抽查), 再生成HTML, 别边写边调。
- 验证(浏览器可用时最稳): 用 node 或浏览器打开, 查 console 无 JS error、侧边栏全部课可点、quizData 注入后渲染题数>0、练习iframe能载。
- 浏览器后端无 Chromium / 被拒时, 改用 node 做运行时冒烟: ① 抓最大 `<script>` 块存成 .js 跑 `node --check`(纯语法); ② 写 DOM 桩(document/localStorage/window/requestAnimationFrame + 全量 `S(page)` 驱动各页 + 启动函数)存 smoke.js 跑 `node`, 抓 undefined 函数/运行时抛错。桩**只**补 DOM 专有 API, 绝不在桩里声明 `var Date/JSON/Array/Object/String/URL`——node 已提供这些内建, 桩里自引用 `var Date = Date` 会把自己覆盖成 undefined, 让 `Date.now()` 崩; 遇到 `Date.now`/JSON 报错先怀疑桩而非被测代码。
- **onclick 全量扫描(工具栏按钮最常翻车)**: 模板的工具栏按钮(导出/全屏/重载/打印/导入等) `onclick="fn()"` 引用的函数**不总在主 JS 里定义**——模板可能只写了按钮 HTML 而函数体在另一个 `<script>` 块或根本没写。克隆后工具栏按钮点了就 `ReferenceError` 标红。生成后必做: ① 从最终 HTML 提取所有 `onclick="(\w+)"` 调用, 与主 JS 里所有 `function \w+`/`var \w+ =`/`window.\w+ =` 定义集合求差; ② 差集非空即把缺失函数按模板标准实现补齐(exportAllData/importAllData/toggleFullscreen/reloadPractice 是高频缺失项); ③ 补完后重跑差集, 必须为 0。这一步比 node 冒烟更直接命中"按钮点了报错"这类用户投诉。
- 判分/答案类引擎(课末测验、练习答案解析)必须在桩里做**负向断言**: 对当前题先触发错误选项路径, 断言 UI 进入错误态并显示正确答案; 再触发正确选项路径, 断言正确态。node 冒烟的 SMOKE_OK 只证明"不报错", 不证明"判得对"; 未做负向断言的交付, 用户大概率回"选哪个都对/解析不出来"。
- CSS 注入位验证: 追加补丁 CSS 时确认它落在**主 `<style>` 块内**(在 `</style>` 之前)。若模板 CSS 源文件自带 `<style>...</style>` 标签对, 补丁拼在字符串尾部就落在所有 `</style>` 之后被浏览器整体忽略——生成后 grep 目标类名, 确认其在**第一个** `<style>` 块内且全文件花括号配平(可删 content 字符串再 `{` 与 `}` 计数), 不能只看补丁字符串存在。
- 删模块(如打字)后必查残留链: grep 最终 HTML 与生成器里 `__模块名__`(如 `__TYPING__`)、模块按钮/页面/指标引用、模块专属 `<style id="xxx">` 独立块, 全部 0 残留。js_core 里 `var X = __X__` 注入行若被删模块名残留, 是整段引擎的 ReferenceError 炸弹(一行抛错使后续所有函数未定义), 用户表现为"系统点了没反应"。
- 组装后必查: 对启动行引用的每个函数在最终 HTML 里 grep `function <fn>`, 断言恰好定义 1 个(去重/replace 步骤可能把唯一的真实定义误删); 占位符 `__X__` 无残留, 但练习题填空下划线 `____` 是合法内容别误判成残留。`__X__` 残留检查必须 **grep 原始生成器模板**(注入前的拼接产物)或**生成器注入代码段**, 不能只 grep 最终 HTML 里 `__X__` 的字面量——`replace` 命中后 HTML 里本来就该 0 个 `__X__`, grep 不到属正常, 漏注入(replace 静默未命中)时 `__X__` 反而以字面量原样留在最终 HTML 里变成 JS 语法错误/未定义变量。正确校验: 在生成器里注入后立即 grep 输出字符串确认 `__X__` 计数==0 **且** 对应变量(JSON.parse 注入行)非空, 两条都过才算注入成功。**同块内调用依赖检查**: 对启动调用(`initWelcome`/`initLabEvents` 等)及其调用到的每个函数, 核对其函数体内引用的顶层 `var X = ...` 赋值所在拼接文件是否在启动调用**之前**拼接; 若被调用函数与它的变量赋值都来自靠后拼接的模块文件, 启动时变量还是 undefined(见"启动顺序陷阱"), 必须调整拼接顺序或把启动调用移到块尾。
- 安全规矩: 涉AI内容评分处保留"AI初评→人工终判"字样; 引用课标/政策/前沿模型处注明"以当地最新官方文件为准"或来源+时间。

## 交互级验收(防空壳/防假阳性, 本类任务最常被打回返工处)
node 语法+冒烟只证明"不报错", 不证明"好用"。交付前必须逐引擎做交互级自测, 任一不过即回炉:
- 侧边栏每个工具页(pbl/design/exam/lab/dash/badge/...)点进去, 正文 `id="p-xxx"` 的 div 里必须有真实教材内容, 不允许只有占位或复制自模板的空壳。按钮是模板里带过来的, 内容必须按新课教材重填; 缺内容的页要么补齐要么整段(按钮+div)删除, 不留死按钮。用户会明确打回"只复制了个空壳"。
- 课末测验: 实际渲染一题, 点错/点对各一次, 确认选项按钮可见(CSS 若用 `.qo-btn{display:none}` 做默认隐藏, 渲染时必须逐按钮 `style.display`/`block` 覆盖, 否则选项整排被藏, 用户感受就是"选哪个都对")、选错变红并显示正确答案、选对变绿、五件套解析出现。`display:none` 这类"默认藏"规则要专门 grep 出来确认有覆盖路径, 且先判断该规则是否包在 `@media print{...}` 内——print 作用域的 `display:none` 不影响屏幕渲染, 别把"选项看不见"误归因到它。最关键: node 冒烟里"驱动全部页 + 调 initQuiz"只打 SMOKE_OK、并不触发判分; 必须额外做负向断言——在 DOM 桩里对当前题手动触发一个错误选项的 select 路径, 断言结果节点进入 wrong/显示正确答案态, 再触发正确项断言 correct 态。只测"不报错"而没测"判错能判错", 用户仍会报"选哪个都对"。
- 配套练习 iframe: 确认 363 题真实渲染进 DOM(统计 `.item` 数量==题数); 且"查看解析"必须真出答案。**最稳做法是放弃 key 匹配, 改按位置对齐**: 数据侧 `secs[i].items[j]` 与 `secs_ans[i].ents[j]` 先全量校验同构(总 items==总 ents, 0 不同构 section), 引擎侧 `getAns(n,si,ii)` 直接按 段索引+项索引 取答案, 不做任何 key 字符串/类型比较——key 构造(题型前缀"单/判"+题号)与数据侧 key 的生成规则稍有出入就恒假匹配, 全部退化成"答案由教师保管"假象。注意同一 section 内可混排选择/判断(题号各自重新计 1), 所以"前缀+位置"的 key 规则天然错乱, 位置对齐是唯一可靠的。
- **渲染层题干丢失是"没内容"的另一主因**: 引擎把非选择题渲染成空 `<span class="fill"></span>` 而把题干 `it.text` 丢掉, 填空/简答/情境题在页面上就是一排空下划线, 用户报"练习没内容"但数据侧 363 题其实都在。正确渲染: `it.text` 始终进 `.item-t`(题干容器), 填空题给带虚线边框的作答区 `.fillzone`, 选择题才渲染 `.opt` 选项组; `hint` 单独成行。自检: 渲染后统计 `class="item-t"` 数==题数, 且抽样题干非空。
- 数据量基线: 用户常要求课末测验每课≥5题、解析深度丰富; 克隆前先把"题数/每课"核对到用户要的数量, 不够就从三件套补题+补五件套, 别用模板的少题数凑数。源三件套每课常只有 2 道单选(全册约 60 题), 要撑到 5 题/课需现编补足: 用本课 KB 词条(定义→"X 的本质/正确说法是哪项", 考点→易错项)+ 教学设计重难点, 每课再出 3 题、各配完整五件套(考查点/解题思路/逐项剖析/易错警示/方法点拨), 并确保每题 `o` 长度==4 且 `a`∈[0,3]; 新题内容必须可溯源到教材条目, 不凭记忆编。
- **现编题不要乱打乱选项位置**: 现编题的"逐项剖析"解析文本是按固定选项位置写的(如"A重记忆/C重操作/D缺迁移, B准确"), 若再随机 shuffle 选项又不联动改写解析, 解析与选项即错位——隐蔽的内容正确性 bug。要么解析文本按生成后的最终位置写, 要么不 shuffle(新编题全部同一正确位如 B 是可接受的, 模拟考引擎会洗牌)。
- 批量 replace 改生成器时, 必须断言替换命中: 每次 `s.replace(old,new)` 前 `assert old in s`; 替换后 grep 确认目标行已变; 含 `\n` 的长 old 字符串极易因转义/缩进差 1 字符而**静默未命中**(不报错、不替换), 之后跑出来的 HTML 还是旧代码, 浪费整轮生成+验证。
- 生成后**数据注入完整性复查**: 每个 `__X__` 占位符注入后, 必须验证目标 JS 变量确实包含有效数据: ① `node -e "...JSON.parse(...)"` 解析注入的 JSON 字面量确认非空; ② 对单元卷/整册卷等新增数据结构, 验证题目数量与源数据一致; ③ 确认 iframe 里 `PRACTICE_HTML` 渲染后的 `.item-t` 数量 == 预期题数。注入静默失败(如 `replace` 的 old 串因空白差异未命中)不会报任何错, 但页面上该模块数据全空, 用户报"没内容"。
- 是否保留打字/某工具页以用户当次要求为准(可能"删除打字"), 不要照抄模板全量工具。
- **练习页交付标准是批改闭环, 不是答案可见**: 用户会明确投诉"题目没有提交 只有查看答案"——只读答案(查看解析/显示全部答案)不算完成。配套练习页至少要有: ①可作答(选择点选、判断√×、**填空/简答给可编辑作答区**, 空 div 不算作答区); ②"提交批改"(按课或全册); ③结果面板: 选择/判断题自动初评对错(答案数据里带选项字母/√×前缀的可机判, 抽取首字母比对), 填空/开放题列"学生作答 vs 参考答案+知识点"待教师终判清单, 全页标注「AI初评→人工终判」; ④错题清单可回跳原题; ⑤提交结果写 localStorage 并经 `parent.aiLogPush` 同步主窗(为 AI 助教实验数据侧留口, 脱敏: 班级-学号式编码, 不含真名)。
- 判"有没有内容": 用正则 `re.findall(r'id="p-<pid>"(.*?)(?=<(?:div|aside|main)[\s>]|$)',html)` 抓各页正文再 `len()` 与"是否含汉字≥4"双判, 空壳会露馅。纯靠 node 冒烟 SMOKE_OK 不等于页面有货。

## 自学闭环增强(用户要求"学生能完全自学掌握"时)
基础克隆交付后, 用户常追加"进一步深度优化丰富教学内容, 学生能完全自学掌握"。这是**第二层任务**, 在第一层(页面/引擎/内容齐全)之上再叠自学引导, 不要重做基础克隆:
- **先量化现状再动手**: 逐课正文字数(`len` 去标签)、每课现有 Tab 数、练习/测验题量, 找出薄弱处(通常: 无"学→练→测→复习"的门控、无 30 秒速记卡、无追问式问题链), 再补, 别凭感觉堆内容。
- **自学深化包数据源**: 用 `lessons_design.json`(每课 6000 字教案)的 `⑤-1 核心问题链`+`⑤ 突破策略`+`keypts` 生成每课 `qchain`(4 条追问, 各带**不重复**的 hint 提示)+ `flash`(3 要点 + 1 押韵口诀 `mnemo`)。脚本落 `selfstudy.json`, 经 `__SELFSTUDY__` 占位注入 JS 全局 `var SELFSTUDY`, 课页 `l{n}zs` 自学通关 Tab 读它渲染。**关键质量红线: hint 必须逐课个性化, 严禁 4~5 条模板句循环 30 课**——用 LLM 逐课生成后全册查重(`Counter(hint)` top 频次应分散), 口诀全册不得雷同(口诀 30 句两两不重复, 押韵优先)。数据生成优先本地直连免费 API: 读环境变量 `AGNES_API_KEY` POST `https://api.agnes-ai.cn/v1/chat/completions`(model `agnes-3.0-flash`, 零成本), 脚本逐课串行+每课落盘检查点到 selfstudy.json(失败课保留旧数据), 单课失败单独补跑该课号即可。子代理生成若遇 429 限流直接放弃改走本地 API, 别在子代理上反复重试。数据生产方与渲染消费方的 JSON 字段名必须严格对齐(如生产方写 `mnemo` 而渲染代码读 `mnemonic` = 口诀全册静默丢失、零报错)——接线前抽 1 课样本打印实际 keys 确认, 渲染端兼容两种写法(`get("mnemo") or get("mnemonic")`)双保险。
- **自学 Tab 命名陷阱**: 课页自学 Tab 的 div id 是 `l{n}zs`, 但 `tabs_html` 里 `tab(this,'l{n}zs')` 的 **`{n}` 若写成 f-string 会正确**, 而**在 `%` 格式化串里 `l%s` 会填成 `l1` 而非 `l1zs`**——本类任务最高频翻车点。生成后用 node 真浏览器统计 `document.querySelectorAll('#l'+n+'zs .zs-qa')` 应 ==30 课都 ≥2, 若 0/30 基本就是 id 少拼了 `zs` 后缀, 回查 `%s` 占位是否漏了固定后缀字面量。
- **测验门控(自学"考过"自动点亮)**: `js_quiz.js` 在全部题答完进结果页时, `pct>=80` 调 `zsSet(lessonNo,3)` 自动点亮第 3 步; 答错路径不点亮, 而是往 `qfb` 追加"下一步: 进易错辨析页签"的 `.zs-hint`。门控函数 `zsStep/zsSync/zsAll/zsSet` 挂 `js_core.js` 末, 用独立 localStorage key `ai8_zs`(存 `{课号:{步号:true}}`), 别混进 `ai8_progress`。
- **门控调用必须真浏览器验证落地, 代码看着对≠会触发**: 实现门控后交付前, 在 Playwright 里把一门课测验全对跑完, 断言 `JSON.parse(localStorage.getItem('ai8_zs'))['2']` 非 null(且答错课不点亮)才过关。最高频杀手是**从页 id 提取课号的隐式 slice 假设**: 页 id 是 `l{n}`(字母 l 在第 0 位, 数字从第 1 位起), `parseInt(id.slice(2))` 对个位课号解析成 NaN, 调用静默 no-op——语法检查、代码审查、甚至函数体里手动裸调全部正常, 唯独线上不触发。写这类调用时顺手在浏览器里打印解析出的课号确认不是 NaN, 或直接对 `id.slice(1)` 这类提取逻辑单独写断言。
- **每课页尾加引导钩子**: `summ` 的"下节预告"行后追加"学完本页请点『自学通关』完成 4 步打卡(看懂→动手→考过→复习)", 让自学闭环有入口可见性, 否则学生不知道有这个功能。
- 增强后**全量回归**基础验收(配套练习 iframe 题数/rect、嵌套 depth、pageerror==0), 防止叠加自学 Tab 又把前面修好的页推回空白。

## 成本纪律
教材三件套数据量大, 用 execute_code 持久 kernel 一次加载JSON复用; 长HTML分段读写(offset/limit), 勿整读2MB+文件。生成失败优先修数据JSON而非重解析docx。若 session 在生成前被截断, 下一轮直接从已落盘的 JSON 续做, 不重新提取。

## 生成器写法纪律(防截断/转义坑)
- 新增数据源若在**模块级函数**(如逐课页面构造函数 `lesson_html(n)`)里消费, 必须也在**模块级**载入(文件顶部 `SELFSTUDY = json.load(...)` 全局变量, `os.path.exists` 包裹、缺失给空 dict 兜底); 塞进 `build_html()` 内部的局部变量会 `NameError` 掉整轮生成。
- 生成器脚本本身用 Python 字符串拼 HTML。三引号嵌套/转义极易写出 SyntaxError —— **不要**在 execute_code 里写 `code = '''...含f-string和emoji...'''` 再执行(emoji 在部分解析路径下会报 invalid character, 且嵌套引号必炸)。正确做法: 用 write_file 直接写 .py 脚本文件(内容里可安全含 emoji 与嵌套引号), 再 `python 脚本` 运行; 或把脚本分段(每段 < 8K token)先落盘再 `cat 段 >> gen_main.py` 追加。
- 单次 write_file / patch 内容超过 ~8K token 会流式超时: 把生成器拆成 数据层 / KB+课页 / 工具页 / JS引擎 几个小文件分别写, 末尾 cat 合并成 gen_main.py 再运行。
- shell heredoc(`cat >> f << 'EOF'`)含单引号 emoji 易触发 bash 引号错: 优先 write_file 写文件, 不要 heredoc 拼接。
- 每段写完立即 `python -c "import ast; ast.parse(open(...))"` 验语法, 别攒到最后一次全验。
- **HTML 模板字符串一律用 `+` 拼接(优先), 确需动态插值(题数/单元名/课号)时可用 `%` 格式化但占位符必须逐行点检**: CSS 里 `linear-gradient(135deg,rgb(…0%))`、`width:100%`、`height:calc(100vh - 140px)` 含字面 `%`, 模板字符串里任何未配对的裸 `%` 遇 `%s`/`%d` 占位就 `ValueError: unsupported format character`(或运行时 `TypeError: not all arguments converted`), 且报错定位在 CSS/HTML 文本里极难排查。若因模板已有大量插值改用 `%` 格式化(如逐课页面 `zs_pass = (... '%s' x N) % (n,n,n,qh,flash_html)`): ① 占位符个数必须与参数个数精确匹配, 写完后立即单独 `python -c` 对**该格式串**做一次 % 格式化试跑(参数用假值)抓 `TypeError`, 不要等整轮生成才发现; ② 字面百分号一律 `%%`; ③ 每行独立可校验。推荐更稳的做法: 把动态值先拼进局部变量再用 `+` 连接, 整段不用 `%`, 从根上避掉 `%%`/参数错位两类坑。

