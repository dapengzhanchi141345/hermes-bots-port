# -*- coding: utf-8 -*-
"""
hermes-bots-port 一键安装器（跨平台，路径自适应）

用法：
  python install_bots.py [本仓库中 bots 目录的路径]

做的事：
  1. 自动识别目标 Hermes 主目录（hermes home）——找包含 config.yaml 的目录，
     依次尝试：环境变量 HERMES_HOME > 本文件所在目录向上找 > 常见位置。
  2. 读取可选的 paths.json（和本脚本同目录）来定制三个占位符的实际路径：
       {{WORKBUDDY}}         工作资料根目录（内容中心/金策宗师团等放哪）
       {{HERMES_HOME_PARENT}} hermes 主目录的上级目录
       {{JINCE_ENGINE}}      金策交易引擎目录
     没有 paths.json 时用默认值（见下），并在报告里列出实际落点。
  3. 逐 bot 安装：SOUL.md / profile.yaml / memories / skills / cron 全部拷进目标
     hermes home 的对应位置；已存在的文件不覆盖（只补缺），config.yaml 缺才补。
  4. 把每个 bot 目录里残留的 {{...}} 占位符替换成实际路径，保证任何安装位置都跑得通。
  5. 生成每个 bot 的 .env（从 .env.template），值留空/占位，提醒去填自己的 key。

已安装过的 bot 再跑一次 = 安全增量合并，不会破坏已有数据。
"""
import os, re, sys, json, shutil, glob

BOTS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bots")
BOTS_DIR = os.path.abspath(BOTS_DIR)

# ---------- 1. 识别 hermes home ----------
def find_hermes_home():
    explicit = None
    # 命令行显式指定优先：绝不静默回退（路径不存在则新建，保证任意位置都能装）
    for a in sys.argv[2:]:
        if a.startswith("--home="):
            explicit = a[7:]
    if explicit is not None:
        explicit = explicit.replace("/", os.sep)
        os.makedirs(explicit, exist_ok=True)
        return explicit
    cands = []
    if os.environ.get("HERMES_HOME"):
        cands.append(os.environ["HERMES_HOME"])
    # 从脚本位置向上找
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.exists(os.path.join(d, "config.yaml")) or os.path.exists(os.path.join(d, "profile.yaml")):
            cands.append(d); break
        d = os.path.dirname(d)
    # 常见位置
    for home in (os.path.expanduser("~"),):
        for rel in (".hermes", "AppData/Local/hermes", "workbuddy/hermes"):
            p = os.path.join(home, *rel.split("/"))
            if os.path.exists(os.path.join(p, "config.yaml")):
                cands.append(p)
    for c in cands:
        if os.path.isdir(c):
            return c
    raise SystemExit("找不到 Hermes 主目录（没有 config.yaml）。请用 --home=<路径> 指定。")

HERMES_HOME = find_hermes_home()
HERMES_HOME_PARENT = os.path.dirname(HERMES_HOME)

# ---------- 2. paths.json 定制 ----------
paths_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paths.json")
custom = {}
if os.path.exists(paths_file):
    with open(paths_file, encoding="utf-8") as f:
        custom = json.load(f)

RESOLVED = {
    "{{WORKBUDDY}}":         custom.get("WORKBUDDY", os.path.join(HERMES_HOME, "workbuddy")),
    "{{HERMES_HOME_PARENT}}": custom.get("HERMES_HOME_PARENT", HERMES_HOME_PARENT),
    "{{USER_HOME}}": os.path.expanduser('~'),
  "{{JINCE_ENGINE}}":      custom.get("JINCE_ENGINE", os.path.join(HERMES_HOME, "GoldstrategyEngine")),
}
# 统一成 / 分隔再写回，避免 Windows 双反斜杠进 JSON 源的问题
def norm(p): return p.replace("\\", "/")
for k in list(RESOLVED): RESOLVED[k] = norm(RESOLVED[k])
for k, v in RESOLVED.items():
    os.makedirs(v, exist_ok=True)

# ---------- 3. 逐 bot 安装 ----------
PLACE = re.compile(r"\{\{[A-Z_]+\}\}")
installed, skipped, filled = [], [], []

def resolve_placeholders(fp):
    """把文件里的 {{...}} 占位符换成实际路径；文本文件处理，二进制跳过"""
    if not os.path.isfile(fp): return
    ext = os.path.splitext(fp)[1].lower()
    if ext in (".png",".jpg",".gif",".zip",".pdf",".db",".etage",".lock"): return
    try:
        txt = open(fp, encoding="utf-8").read()
    except UnicodeDecodeError:
        return
    if "{{" not in txt: return
    new = txt
    for k, v in RESOLVED.items():
        new = new.replace(k, v)
    if new != txt:
        open(fp, "w", encoding="utf-8").write(new)

def merge_jobs_json(dst):
    """cron/jobs.json 合并：两边 jobs 列表并集（按 prompt 前 80 字去重）"""
    try:
        d = json.load(open(dst, encoding="utf-8"))
        existing = d.get("jobs", d if isinstance(d, list) else [])
    except Exception:
        existing = []
    def norm_j(j): return (j.get("prompt") or j.get("name") or str(j))[:80]
    seen = {norm_j(j) for j in existing if isinstance(j, dict)}
    added = 0
    for j in NEW_JOBS:
        if isinstance(j, dict) and norm_j(j) not in seen:
            existing.append(j); seen.add(norm_j(j)); added += 1
    if isinstance(d, dict): d["jobs"] = existing
    else: d = {"jobs": existing}
    json.dump(d, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return added

for name in sorted(os.listdir(BOTS_DIR)):
    src = os.path.join(BOTS_DIR, name)
    if not os.path.isdir(src) or name.startswith("."): continue

    if name == "default":
        # default = hermes home 根目录本身
        dst_root = HERMES_HOME
        is_default = True
    else:
        dst_root = os.path.join(HERMES_HOME, "profiles", name)
        os.makedirs(dst_root, exist_ok=True)
        is_default = False

    got = []
    # 单文件：SOUL.md / profile.yaml（缺才补）
    for f in ("SOUL.md", "profile.yaml"):
        s, t = os.path.join(src, f), os.path.join(dst_root, f)
        if os.path.exists(s):
            if not os.path.exists(t):
                shutil.copy2(s, t); got.append(f)
            # 已存在不覆盖
    # config.yaml：缺才补；已有则保留目标的（里面是目标机自己的 key）
    cfg_s, cfg_t = os.path.join(src, "config.yaml"), os.path.join(dst_root, "config.yaml")
    if os.path.exists(cfg_s) and not os.path.exists(cfg_t):
        shutil.copy2(cfg_s, cfg_t); got.append("config.yaml")
    # .env：缺才从模板建
    env_s = os.path.join(src, ".env.template")
    env_t = os.path.join(dst_root, ".env")
    if os.path.exists(env_s) and not os.path.exists(env_t):
        shutil.copy2(env_s, env_t); got.append(".env(模板)")
    # memories / skills 整树合并（skills 目录逐技能合并，不覆盖同名）
    for sub in ("memories", "skills"):
        s_dir = os.path.join(src, sub)
        if not os.path.isdir(s_dir): continue
        t_dir = os.path.join(dst_root, sub)
        os.makedirs(t_dir, exist_ok=True)
        n = 0
        for entry in os.walk(s_dir):
            for f in entry[1] + entry[2]:
                pass
        # 简化：整目录递归拷，目标已有同名则跳过
        def walkmerge(s, t):
            c = 0
            for root, dirs, files in os.walk(s):
                rel = os.path.relpath(root, s)
                tr = t if rel == "." else os.path.join(t, rel)
                os.makedirs(tr, exist_ok=True)
                for f in files:
                    if f.startswith("."): continue
                    fp_t = os.path.join(tr, f)
                    if not os.path.exists(fp_t):
                        shutil.copy2(os.path.join(root, f), fp_t); c += 1
            return c
        n = walkmerge(s_dir, t_dir)
        if n: got.append(f"{sub}/(+{n})")
    # cron/jobs.json 合并
    cj_s = os.path.join(src, "cron", "jobs.json")
    if os.path.exists(cj_s):
        NEW_JOBS = json.load(open(cj_s, encoding="utf-8")).get("jobs", [])
        dst_j = os.path.join(dst_root, "cron", "jobs.json")
        os.makedirs(os.path.dirname(dst_j), exist_ok=True)
        if not os.path.exists(dst_j):
            shutil.copy2(cj_s, dst_j); got.append("cron/jobs.json")
        else:
            added = merge_jobs_json(dst_j)
            got.append(f"cron/jobs.json(合并+{added})")
    # 占位符替换（目标侧）
    nph = 0
    for root, dirs, files in os.walk(dst_root):
        for f in files:
            before = None
            fp = os.path.join(root, f)
            resolve_placeholders(fp)
    resolved = len(got)
    if got: installed.append((name, got))
    else: skipped.append(name)

# 报告
print("=" * 60)
print("Hermes home :", HERMES_HOME)
print("路径定制     :", json.dumps(RESOLVED, ensure_ascii=False, indent=1))
print("-" * 60)
for name, got in installed:
    print(f"  [装] {name}: {', '.join(got)}")
for name in skipped:
    print(f"  [=] {name}: 全已存在，无新内容")
print("-" * 60)
print("请进各 bot 目录的 .env 填入你自己的 key（AGNES_* 等，模板里 <FILL_ME> 处）。")
print("提示：改完路径/重装可再跑一次本脚本，安全增量合并。")
