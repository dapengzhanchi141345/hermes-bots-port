// 单文件 HTML 教学系统校验脚本（交付前跑一遍）
// 用法：node run-template-check.mjs <course.html>
// 校验：① 零外链（无 http(s) src/href、无 fetch/XHR）
//       ② 引擎要件齐全（slides / go / QUIZ / draw / progress）
//       ③ 关键标签平衡；统计 [FILL] 残留与测验题数（仅提示，不阻断）
// 全过 → PASS 并 exit 0；任一硬性项失败 → exit 1。
import {readFileSync} from "node:fs";
const p=process.argv[2];
if(!p){console.error("用法: node run-template-check.mjs <course.html>");process.exit(2)}
const s=readFileSync(p,"utf8");
let fail=0;
const ok=(c,m)=>{if(c)console.log("  ✓ "+m);else{console.log("  ✗ "+m);fail++}};
console.log("校验 "+p);
// ① 零外链
const extSrc=[...s.matchAll(/\b(?:src|href)\s*=\s*["']https?:\/\/["'\s\/]+/g)].map(m=>m[0].trim());
ok(extSrc.length===0,"无 http(s) 外链 (发现 "+extSrc.length+")"+(extSrc.length?"\n    "+extSrc.slice(0,5).join("\n    "):""));
ok(!/\bfetch\s*\(|XMLHttpRequest/.test(s),"无 fetch/XHR 网络调用");
// ② 引擎要件
for(const need of ["const slides","function go","const QUIZ","function draw","getElementById(\"progress\")"]){
  ok(s.includes(need),"引擎要件存在: "+need)}
// ③ 标签平衡
for(const tag of ["section","div","button","script","style"]){
  const open=(s.match(new RegExp("<"+tag+"(?=\\s|>)","g"))||[]).length;
  const close=(s.match(new RegExp("<\\/"+tag+">","g"))||[]).length;
  ok(open===close,"<"+tag+"> 标签平衡 ("+open+"/"+close+")")}
// 统计（不阻断）
const fills=(s.match(/\[FILL[^\]]*\]/g)||[]).length;
console.log(fills?"  ⚠ 还有 "+fills+" 处 [FILL] 待补（模板状态下属正常，成品课件应为 0）":"  ✓ 无 [FILL] 残留");
const quizN=(s.match(/\bq:\s*["']/g)||[]).length;
console.log("  幻灯片 "+(s.match(/class=\"slide/g)||[]).length+" 页 · 测验题 "+quizN+" 道 · 总字符 "+s.length);
console.log(fail?"FAIL（"+fail+" 项未过）":"PASS：单文件教学系统校验全部通过");
process.exit(fail?1:0);
