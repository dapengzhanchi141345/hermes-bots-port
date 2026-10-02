# 双闸门验证: 全部 <script> 块 JS 语法 + 静态/模板 id 重复扫描
# 用法: node verify-all.js <dir>
const fs = require('fs');
const path = require('path');
const dir = process.argv[2] || '.';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.html') && !f.includes('备份') && !f.includes('backup'));
let allClean = true;
for (const fn of files) {
  const raw = fs.readFileSync(path.join(dir, fn), 'utf8');
  const blocks = [...raw.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  const bad = [];
  blocks.forEach((m, i) => { try { new Function(m[1]); } catch (e) { bad.push(i + ': ' + e.message.slice(0, 60)); } });
  const ids = [...raw.matchAll(/\bid=\"([^\"]+)\"/g)].map(m => m[1]);
  const cnt = {};
  ids.forEach(id => cnt[id] = (cnt[id] || 0) + 1);
  const dups = Object.entries(cnt).filter(([, v]) => v > 1);
  if (bad.length || dups.length) allClean = false;
  console.log(fn, bad.length ? 'JS-ERR: ' + bad.slice(0, 2).join(' | ') : 'JS-OK', dups.length ? 'DUP: ' + JSON.stringify(dups) : 'ID-OK');
}
console.log(allClean ? 'ALL CLEAN' : 'ISSUES REMAIN (人工判定误报后在报告中标注理由)');
