# -*- coding: utf-8 -*-
"""同目录备份 + 全量统计。用法: python backup-and-scan.py <dir>"""
import os, re, shutil, sys
from datetime import date

d = sys.argv[1] if len(sys.argv) > 1 else '.'
files = [f for f in os.listdir(d) if f.endswith('.html') and '备份' not in f and 'backup' not in f.lower()]
stamp = date.today().strftime('%Y%m%d')
bdir = os.path.join(d, f'备份_升级前_{stamp}')
os.makedirs(bdir, exist_ok=True)
for fn in files:
    shutil.copy2(os.path.join(d, fn), os.path.join(bdir, fn))
print(f'backup: {bdir} ({len(files)} files)')
for fn in sorted(files):
    raw = open(os.path.join(d, fn), encoding='utf-8').read()
    ids = re.findall(r'id="([^"]+)"', raw)
    cnt = {}
    for i in ids: cnt[i] = cnt.get(i, 0) + 1
    dups = {k: v for k, v in cnt.items() if v > 1}
    tiny = {}
    for s in map(str, range(5, 10)):
        n = len(re.findall('font-size:' + s + 'px', raw))
        if n: tiny[s] = n
    print(f'{fn}: {len(raw)>>20}MB ids={len(ids)} dups={dups or "-"} '
          f'aria={len(re.findall("aria-[a-z]+=", raw))} printCss={"@media print" in raw} tinyFonts={tiny or "-"}')
