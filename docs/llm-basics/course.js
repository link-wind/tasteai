'use strict';
const lesson = Number(document.body.dataset.lesson);
const demo = document.querySelector('#demo');
function read(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } }
function write(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch {} }
let completed = read('llm-basics.completed', []);
if (!Array.isArray(completed)) completed = [];
function progress() {
  const done = completed.includes(lesson);
  document.querySelector('#complete').textContent = done ? '已读 · 点击取消' : '标记本课已读';
  document.querySelector('#complete').setAttribute('aria-pressed', String(done));
  document.querySelector('#progress').textContent = ` 已读 ${completed.length} / 6 课（保存在当前浏览器）`;
}
document.querySelector('#complete').onclick = () => { completed = completed.includes(lesson) ? completed.filter(n => n !== lesson) : [...completed, lesson]; write('llm-basics.completed', completed); progress(); };
progress();
const size = document.querySelector('#size');
function fontSize(large) { document.body.classList.toggle('large', large); size.setAttribute('aria-pressed', String(large)); size.textContent = large ? '恢复字号' : '放大字号'; }
fontSize(read('llm-basics.large', false));
size.onclick = () => { const large = !document.body.classList.contains('large'); fontSize(large); write('llm-basics.large', large); };
document.querySelector('#quiz').onsubmit = e => {
  e.preventDefault(); const choice = new FormData(e.currentTarget).get('answer');
  document.querySelector('#feedback').textContent = choice === null ? '先选一个答案，再检查。' : (Number(choice) === window.lessonAnswer ? '答对了。' : '再想一想。') + window.lessonExplanation;
};
function bars(items) { return items.map(([label,value]) => `<div class="bar"><span>${label}</span><i style="width:${value * 65}%"></i><strong>${(value*100).toFixed(1)}%</strong></div>`).join(''); }
if (lesson === 1) {
  let step=0;
  const texts=['今天下雨了，出门记得带','今天下雨了，出门记得带伞','今天下雨了，出门记得带伞。'];
  const choices=[[['伞',.65],['雨衣',.15],['手机',.05],['其他',.15]],[['。',.7],['，',.2],['其他',.1]]];
  demo.innerHTML='<div id="context" class="display" aria-live="polite"></div><div id="bars"></div><div class="controls"><button id="step">生成一个 token</button><button id="reset">重新开始</button></div>';
  function render(){document.querySelector('#context').textContent=texts[step];document.querySelector('#bars').innerHTML=step<2?bars(choices[step]):'<p class="note">本次教学演示结束。实际生成也可以在结束标记或长度限制处停止。</p>';document.querySelector('#step').disabled=step===2;}
  document.querySelector('#step').onclick=()=>{step++;render();};document.querySelector('#reset').onclick=()=>{step=0;render();};render();
} else if (lesson === 2) {
  demo.innerHTML='<div class="controls" id="tokens"></div><div class="display" id="vector" aria-live="polite"></div>';
  [['今天',12,'[0.2, −0.4, 0.8]'],['下雨',42,'[−0.1, 0.6, 0.3]'],['了',7,'[0.5, 0.1, −0.2]']].forEach(([t,id,v])=>{const b=document.createElement('button');b.textContent=t;b.onclick=()=>{document.querySelector('#vector').textContent=`教学 token「${t}」→ 编号 ${id} → 查表得到向量 ${v}。编号是索引，不是数值大小的语义。`;};document.querySelector('#tokens').append(b);});document.querySelector('#tokens button').click();
} else if (lesson === 3) {
  demo.innerHTML='<label for="position">当前位置：<output id="posval"></output></label><br><input id="position" type="range" min="1" max="5" value="3"><div class="flow" id="mask"></div><p id="masktext" aria-live="polite"></p>';
  function render(){const n=Number(document.querySelector('#position').value);document.querySelector('#posval').textContent=n;document.querySelector('#mask').innerHTML=Array.from({length:5},(_,i)=>`<span style="${i<n?'background:var(--green);color:white':''}">位置 ${i+1} · ${i<n?'可见':'屏蔽'}</span>`).join('');document.querySelector('#masktext').textContent=`位置 ${n} 可参考前 ${n} 个位置，未来位置被屏蔽。`;}
  document.querySelector('#position').oninput=render;render();
} else if (lesson === 4) {
  demo.innerHTML='<label for="a">位置 A</label> <input id="a" type="range" min="0" max="10" value="2"><br><label for="b">位置 B</label> <input id="b" type="range" min="0" max="10" value="5"><div id="rotation" class="display" aria-live="polite"></div>';
  function render(){const a=Number(document.querySelector('#a').value),b=Number(document.querySelector('#b').value);document.querySelector('#rotation').textContent=`A = ${a}，B = ${b}；位置差 B − A = ${b-a}。假设这一维度对每个位置旋转 20°，则两者相对角度为 ${(b-a)*20}°。同时把两个位置平移相同距离，相对角度保持不变。`;}
  document.querySelector('#a').oninput=render;document.querySelector('#b').oninput=render;render();
} else if (lesson === 5) {
  demo.innerHTML='<label for="prob">正确 token 的概率</label><br><input id="prob" type="range" min="1" max="99" value="50"><div id="loss" class="display" aria-live="polite"></div>';
  function render(){const p=Number(document.querySelector('#prob').value)/100;document.querySelector('#loss').textContent=`p = ${p.toFixed(2)} → 损失 −ln(p) = ${(-Math.log(p)).toFixed(3)}。试着把概率向右调高，损失会怎样变化？`;}
  document.querySelector('#prob').oninput=render;render();
} else if (lesson === 6) {
  demo.innerHTML='<label for="temp">温度 T = <output id="tempval"></output></label><br><input id="temp" type="range" min="10" max="200" value="100"><div id="distribution" aria-live="polite"></div>';
  function render(){const t=Number(document.querySelector('#temp').value)/100;const weights=[3,2,1].map(v=>Math.exp((v-3)/t));const sum=weights.reduce((a,b)=>a+b,0);document.querySelector('#tempval').textContent=t.toFixed(2);document.querySelector('#distribution').innerHTML=bars(weights.map((v,i)=>[['候选 A','候选 B','候选 C'][i],v/sum]));}
  document.querySelector('#temp').oninput=render;render();
}
