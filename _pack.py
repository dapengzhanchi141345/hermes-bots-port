# -*- coding: utf-8 -*-
# 打包 bots 资产（脱敏 + 路径抽象）
import os, re, json, shutil, subprocess

ROOT = r"E:\workbuddy\国外模型\hermes"
OUT = r"E:\workbuddy\内容中心\交付\hermes-bots-port\bots"
shutil.rmtree(OUT, ignore_errors=True)

BUNDLED = {"apple","autonomous-ai-agents","creative","data-science","devops","email","github",
"media","mlops","model-key-pools","note-taking","productivity","research","smart-home",
"social-media","software-development","web","yuanbao"}
PROFILES = sorted([p for p in os.listdir(os.path.join(ROOT,"profiles"))
                   if os.path.isdir(os.path.join(ROOT,"profiles",p))])

PLACEHOLDER = {
  # 单反斜杠（md/py/yaml 文本源）
  r"E:\workbuddy": "{{WORKBUDDY}}",
  r"C:\Users\ASUS": "{{HERMES_HOME_PARENT}}",
  r"E:\GoldstrategyEngine": "{{JINCE_ENGINE}}",
  # 双反斜杠（JSON 转义源，jobs.json / .json 技能数据）
  r"E:\\workbuddy": "{{WORKBUDDY}}",
  r"C:\\Users\\ASUS": "{{HERMES_HOME_PARENT}}",
  r"E:\\GoldstrategyEngine": "{{JINCE_ENGINE}}",
  # 正斜杠（Windows 路径在代码里写成 /）
  "E:/workbuddy": "{{WORKBUDDY}}",
  "C:/Users/ASUS": "{{HERMES_HOME_PARENT}}",
  "E:/GoldstrategyEngine": "{{JINCE_ENGINE}}",
}
def abstract(text):
    for k,v in sorted(PLACEHOLDER.items(), key=lambda x:-len(x[0])):
        text = text.replace(k, v)
    # 个人隐私匿名化（手机号 / 微信 iLink 账号与 user_id）
    text = text.replace("15684394135", "<PHONE>")
    text = text.replace("457125012a4a@im.bot", "<WEIXIN_ACCOUNT_ID>")
    text = re.sub(r"o9cq80[0-9A-Za-z_]*@im\.wechat", "<WEIXIN_USER_ID>", text)
    return text

# 真 key 拦截正则（外发前双向往返用）
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{24,}"),       # 完整真 key
    re.compile(r"[A-Za-z0-9]{32,}"),           # 长 token/指纹兜底（谨慎，按需）
]

def scrub_config(text):
    # api_key 整值清掉（含指纹 sk-xxx...yyy 与真实值），留空串
    text = re.sub(r"(?m)^(\s*api_key:\s*)\S+", r"\1''", text)
    # provider_key 同理
    text = re.sub(r"(?m)^(\s*provider_key:\s*)\S+", r"\1'<FILL_ME>'", text)
    # session_key / token / secret 有值的一律清空
    text = re.sub(r"(?m)^(\s*(?:session_key|token|secret):\s*)\S+", r"\1''", text)
    return text

def read_text(fp):
    try:
        with open(fp, encoding="utf-8") as f: return f.read()
    except UnicodeDecodeError:
        with open(fp, encoding="gbk", errors="ignore") as f: return f.read()

def env_template(envp):
    lines=[]
    for line in read_text(envp).splitlines():
        m = re.match(r"^([A-Z_0-9]+)=(.*)$", line.strip())
        if m:
            name,val=m.group(1),m.group(2).strip("'\"")
            lines.append(f"{name}=" if not val else f"{name}=<FILL_ME>")
    return "\n".join(lines)+"\n"

def load_manifest(p):
    """读技能目录的 .bundled_manifest（官方技能名清单），没有就空集"""
    fp = os.path.join(p, ".bundled_manifest")
    names = set()
    if os.path.exists(fp):
        for line in read_text(fp).splitlines():
            line = line.strip()
            if line and ":" in line:
                names.add(line.split(":",1)[0])
    return names

TEXT_EXT = (".md",".py",".json",".txt",".yaml",".yml",".html",".js",".sh",".bat",".ps1",".toml")

def abstract_skill_tree(src, dst):
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        dirs[:] = [x for x in dirs if not x.startswith(".") and x != "__pycache__"]
        rel = os.path.relpath(root, src)
        for f in files:
            if f.startswith("."): continue
            sp = os.path.join(root,f)
            dp = os.path.join(dst, rel, f) if rel != "." else os.path.join(dst,f)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            if f.endswith(TEXT_EXT):
                open(dp,"w",encoding="utf-8").write(abstract(read_text(sp)))
            else:
                shutil.copy2(sp, dp)

def copy_root_skills(target_root):
    sk_root = os.path.join(ROOT,"skills")
    bundled = load_manifest(sk_root)
    for cat in os.listdir(sk_root):
        cp = os.path.join(sk_root,cat)
        if cat.startswith("."): continue
        if cat.endswith(".json"):
            dst = os.path.join(target_root,"skills",cat)
            os.makedirs(os.path.dirname(dst),exist_ok=True)
            open(dst,"w",encoding="utf-8").write(abstract(read_text(cp)))
            continue
        if not os.path.isdir(cp): continue
        for s in os.listdir(cp):
            sp = os.path.join(cp,s)
            if s.startswith(".") or s in bundled: continue
            if os.path.isdir(sp):
                abstract_skill_tree(sp, os.path.join(target_root,"skills",cat,s))

manifest = {"profiles": []}

# ---- default（root）----
d = os.path.join(OUT,"default"); os.makedirs(d, exist_ok=True)
man = {"name":"default","desc":"总调度 bot（root）"}
for f in ["SOUL.md","profile.yaml","memories/MEMORY.md","memories/USER.md"]:
    src=os.path.join(ROOT,f)
    if os.path.exists(src):
        dst=os.path.join(d,f); os.makedirs(os.path.dirname(dst),exist_ok=True)
        open(dst,"w",encoding="utf-8").write(abstract(read_text(src)))
open(os.path.join(d,"config.yaml"),"w",encoding="utf-8").write(scrub_config(abstract(read_text(os.path.join(ROOT,"config.yaml")))))
open(os.path.join(d,".env.template"),"w",encoding="utf-8").write(env_template(os.path.join(ROOT,".env")))
cj=os.path.join(ROOT,"cron","jobs.json")
if os.path.exists(cj):
    os.makedirs(os.path.join(d,"cron"),exist_ok=True)
    open(os.path.join(d,"cron","jobs.json"),"w",encoding="utf-8").write(abstract(read_text(cj)))
copy_root_skills(d)
manifest["profiles"].append(man)

# ---- 各 profile ----
for p in PROFILES:
    base=os.path.join(ROOT,"profiles",p)
    d=os.path.join(OUT,p); os.makedirs(d, exist_ok=True)
    man={"name":p,"desc":""}
    py=os.path.join(base,"profile.yaml")
    if os.path.exists(py):
        txt=abstract(read_text(py))
        open(os.path.join(d,"profile.yaml"),"w",encoding="utf-8").write(txt)
        m=re.search(r"^description:\s*(.+)$", txt, re.M)
        man["desc"]=(m.group(1).strip() if m else "")[:100]
    soul=os.path.join(base,"SOUL.md")
    if os.path.exists(soul):
        open(os.path.join(d,"SOUL.md"),"w",encoding="utf-8").write(abstract(read_text(soul)))
    cfg=os.path.join(base,"config.yaml")
    if os.path.exists(cfg):
        open(os.path.join(d,"config.yaml"),"w",encoding="utf-8").write(scrub_config(abstract(read_text(cfg))))
    envp=os.path.join(base,".env")
    if os.path.exists(envp):
        open(os.path.join(d,".env.template"),"w",encoding="utf-8").write(env_template(envp))
    mdir=os.path.join(base,"memories")
    if os.path.isdir(mdir):
        for f in os.listdir(mdir):
            if f.endswith(".lock"): continue
            fp=os.path.join(mdir,f); dst=os.path.join(d,"memories",f)
            os.makedirs(os.path.dirname(dst),exist_ok=True)
            open(dst,"w",encoding="utf-8").write(abstract(read_text(fp)))
    sdir=os.path.join(base,"skills")
    if os.path.isdir(sdir):
        bundled = load_manifest(sdir) | BUNDLED
        for s in os.listdir(sdir):
            sp=os.path.join(sdir,s)
            if s.startswith(".") or s in bundled: continue
            if s.endswith(".json"):
                dst=os.path.join(d,"skills",s); os.makedirs(os.path.dirname(dst),exist_ok=True)
                open(dst,"w",encoding="utf-8").write(abstract(read_text(sp)))
            elif os.path.isdir(sp):
                abstract_skill_tree(sp, os.path.join(d,"skills",s))
    cj=os.path.join(base,"cron","jobs.json")
    if os.path.exists(cj):
        os.makedirs(os.path.join(d,"cron"),exist_ok=True)
        open(os.path.join(d,"cron","jobs.json"),"w",encoding="utf-8").write(abstract(read_text(cj)))
    manifest["profiles"].append(man)

# ---- 后处理：其余敏感项 ----
import glob
mt5=0
for fp2 in glob.glob(os.path.join(OUT,"**","*"), recursive=True):
    if os.path.isfile(fp2) and fp2.lower().endswith((".md",".yaml",".json",".py",".txt")):
        t=open(fp2,encoding="utf-8",errors="ignore").read()
        if "60137964" in t:
            open(fp2,"w",encoding="utf-8").write(t.replace("60137964","<MT5_ACCOUNT>")); mt5+=1
print("MT5-account files:", mt5)
# 手机号匿名（sota 技能示例数据）：任意 11 位 1 开头手机号 -> <PHONE>
import re as _re
p_hits=0
for fp2 in glob.glob(os.path.join(OUT,"**","*"), recursive=True):
    if os.path.isfile(fp2) and fp2.lower().endswith((".md",".json",".yaml",".py",".txt")):
        t=open(fp2,encoding="utf-8",errors="ignore").read()
        nt=_re.sub(r"(?<!\d)(?<!\.)1[3-9]\d{9}(?!\d)(?!\.)", "<PHONE>", t)
        if nt!=t: open(fp2,"w",encoding="utf-8").write(nt); p_hits+=1
print("phone anonymized files:", p_hits)
# profile.yaml 里 ui_meta 的群聊历史全丢，只留 groups 名
stripped=[]
for p in os.listdir(OUT):
    py=os.path.join(OUT,p,"profile.yaml")
    if not os.path.exists(py): continue
    txt=open(py,encoding="utf-8").read()
    if "hermes-bots-groups" in txt:
        new=[]; skip=False
        for line in txt.splitlines():
            if "hermes-bots-groups" in line: skip=True; continue
            if skip:
                if line.startswith("  ") and not line.startswith("    "): skip=False
                else: continue
            new.append(line)
        open(py,"w",encoding="utf-8").write("\n".join(new)+"\n")
        stripped.append(p)
print("chat-log stripped:", stripped)

json.dump(manifest, open(os.path.join(OUT,"manifest.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("packed:", 1+len(PROFILES), "profiles")

# ---- 校验（纯 Python，无 shell 转义坑）----
import glob
def scan(pat):
    rx = re.compile(pat)
    hits = []
    for f in glob.glob(os.path.join(OUT, "**", "*"), recursive=True):
        if not os.path.isfile(f): continue
        if f.lower().endswith((".png",".jpg",".zip",".pdf",".db")): continue
        t = open(f, encoding="utf-8", errors="ignore").read()
        for m in set(rx.findall(t)):
            hits.append((f.replace(OUT,""), m[:40]))
    return hits
real_key = scan(r"sk-[A-Za-z0-9]{24,}")
phone    = scan(r"1[3-9]" + chr(92) + "d{9}")
weix     = scan(r"(?:457125012a4a|o9cq80[0-9A-Za-z_]*@im" + chr(92) + r".(?:wechat|bot)|im" + chr(92) + r".wechat)")
acct     = scan(r"60137964")
absleft  = scan(r"E:[/\\]workbuddy")
print("REAL-KEY hits:", len(real_key)); [print(" ",h) for h in real_key[:10]]
print("PHONE hits:", len(phone)); [print(" ",h) for h in phone[:5]]
print("WECHAT hits:", len(weix)); [print(" ",h) for h in weix[:5]]
print("MT5-ACCT hits:", len(acct))
print("ABS-LEFT hits:", len(absleft)); [print(" ",h) for h in absleft[:10]]
tot=0; n=0
for dp,dn,fn in os.walk(OUT):
    for f in fn:
        n+=1; tot+=os.path.getsize(os.path.join(dp,f))
print("total files:", n, "size MB: %.1f" % (tot/1048576))
print("total files:", n, "size MB: %.1f" % (tot/1048576))
