# 单文件 HTML 教学系统全量静态审计
# 输出: 重复 id / JS 语法 / aria 属性数 / 外链 / 大 base64 blob / 打印样式 / 5-9px 字号分布
# 用法: node audit-html.js <dir>
const fs = require('fs');
const path = require('path');
const dir = process.argv[2] || '.';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.html') && !f.includes('备份') && !f.includes('backup'));
for (const fn of files) {
  const raw = fs.readFileSync(path.join(dir, fn), 'utf8');
  const ids = [...raw.matchAll(/\bid=\"([^\"]+)\"/g)].map(m => m[1]);
  const cnt = {};
  ids.forEach(id => cnt[id] = (cnt[id] || 0) + 1);
  const dups = Object.entries(cnt).filter(([k, v]) => v > 1);
  const blocks = [...raw.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  const jsErr = [];
  blocks.forEach((m, i) => { try { new Function(m[1]); } catch (e) { jsErr.push({ block: i, msg: e.message.slice(0, 80) }); } });
  const aria = (raw.match(/aria-[a-z]+=|role="/g) || []).length;
  const ext = [...raw.matchAll(/src=\"(https?:[^"]+)\"|href=\"(https?:[^"]+)\"/g)].length;
  const bigB64 = [...raw.matchAll(/[A-Za-z0-9+/=]{100000,}/g)].map(m => m[0].length);
  const hasPrint = /@media\s+print/.test(raw);
  const tinyFonts = {};
  for (let sz = 5; sz <= 9; sz++) {
    const n = (raw.match(new RegExp('font-size:' + sz + 'px', 'g')) || []).length;
    if (n) tinyFonts[sz] = n;
  }
  console.log(JSON.stringify({ file: fn, kb: raw.length >> 10, dupIds: dups, jsErrors: jsErr, ariaAttrs: aria, externalRefs: ext, bigBase64Blobs: bigB64, hasPrintCss: hasPrint, tinyFonts }, null, 1));
}
