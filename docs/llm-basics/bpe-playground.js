'use strict';
(() => {
  if (!document.querySelector('#bpe-text')) return;
  const bpe = window.ByteBPE;
  const model = bpe.train(bpe.defaultCorpus, 100);
  let turn = 0;
  const input = document.querySelector('#bpe-text');
  const next = document.querySelector('#bpe-next'), back = document.querySelector('#bpe-back');
  const set = (id, value) => { document.getElementById(id).textContent = value; };
  function piece(id) {
    try { return JSON.stringify(new TextDecoder('utf-8', {fatal:true}).decode(new Uint8Array(model.vocab[id]))); }
    catch { return '[' + hex(model.vocab[id]) + ']'; }
  }
  function hex(bytes) { return bytes.map(n => n.toString(16).toUpperCase().padStart(2,'0')).join(' '); }
  function table(id, headers, rows, empty) {
    const target = document.getElementById(id);
    if (!rows.length) { const p = document.createElement('p'); p.className = 'caption'; p.textContent = empty; target.replaceChildren(p); return; }
    const element = document.createElement('table');
    const head = element.createTHead().insertRow();
    headers.forEach(text => { const th = document.createElement('th'); th.scope = 'col'; th.textContent = text; head.append(th); });
    const body = element.createTBody();
    rows.forEach(values => { const row = body.insertRow(); values.forEach(value => { row.insertCell().textContent = String(value); }); });
    target.replaceChildren(element);
  }
  function encodeInput() {
    const text = input.value;
    if (text.length > 240 || Array.from(text).length > 120) {
      set('bpe-input-status', '超过 120 个码点，请缩短输入。结果已清空，没有对截断文本计算。');
      for (const id of ['bpe-byte-count','bpe-ids','bpe-pieces','bpe-decoded']) set(id,'—');
      document.querySelector('#bpe-encoding-steps').replaceChildren(); return;
    }
    const result = bpe.encode(text, model.rules.slice(0, turn));
    const decoded = bpe.decode(result.ids, model.vocab);
    set('bpe-byte-count', String(new TextEncoder().encode(text).length));
    set('bpe-ids', JSON.stringify(result.ids));
    set('bpe-pieces', result.ids.map(piece).join(' | ') || '空序列');
    set('bpe-decoded', JSON.stringify(decoded));
    table('bpe-encoding-steps', ['步数','应用 rank','合并对 → 新 ID','合并后 IDs'], result.steps.map((step,i) => [i+1,step.rank,step.pair.join(' + ')+' → '+step.id,JSON.stringify(step.ids)]), '没有应用合并规则，保持基础字节序列。');
    set('bpe-input-status', decoded !== text
      ? '输入含孤立代理项，TextEncoder 已替换为 U+FFFD，无法恢复原始异常字符串；Python 严格模式会报错。'
      : !text ? '空输入：0 字节、0 token，解码为空字符串。'
      : `使用当前 ${turn} 条规则，${new TextEncoder().encode(text).length} 个字节编码为 ${result.ids.length} 个 token；完整解码与输入一致。训练状态未改变。`);
  }
  function render() {
    const state = model.states[turn];
    set('bpe-turn', String(turn)); set('bpe-vocab-size', String(256+turn)); set('bpe-total', String(state.total));
    next.disabled = turn === model.rules.length; back.disabled = turn === 0;
    const choice = state.candidates[0];
    set('bpe-status', choice
      ? `已完成 ${turn} / ${model.rules.length} 轮。下一轮选择 ${piece(choice.pair[0])} + ${piece(choice.pair[1])}，频次 ${choice.count}，将分配 ID ${256+turn}。`
      : `已完成 ${turn} / ${model.rules.length} 轮。每条样本只剩一个 token，已无段内相邻对，训练停止。`);
    table('bpe-corpus', ['样本','权重','当前片段','当前 IDs'], state.corpus.map(row=>[row.text,row.weight,row.ids.map(piece).join(' | '),JSON.stringify(row.ids)]),'无训练语料');
    table('bpe-candidates', ['排序','相邻片段','ID 对','加权频次'],state.candidates.map((item,i)=>[i===0?'1 · 下一对':i+1,item.pair.map(piece).join(' + '),item.pair.join(', '),item.count]),'没有可合并相邻对。');
    table('bpe-rules', ['rank','输入 ID 对','新 ID','字节十六进制','对应片段'],model.rules.slice(0,turn).map(rule=>[rule.rank,rule.pair.join(', '),rule.id,hex(model.vocab[rule.id]),piece(rule.id)]),'尚未学习规则。基础词表已有全部 256 个单字节。');
    window.CourseVisuals?.mount(document.querySelector('.bpe-experiment'),window.CourseVisuals.bpe(state,model,turn));
    encodeInput();
  }
  next.addEventListener('click',()=>{ if(turn<model.rules.length){turn++;render();} });
  back.addEventListener('click',()=>{ if(turn>0){turn--;render();} });
  document.querySelector('#bpe-reset').addEventListener('click',()=>{turn=0;render();});
  input.addEventListener('input',encodeInput);
  const samples = {lowest:'lowest',lower:'lower',unicode:'A中🙂',empty:''};
  document.querySelectorAll('[data-bpe-sample]').forEach(button=>button.addEventListener('click',()=>{input.value=samples[button.dataset.bpeSample];encodeInput();}));
  render();
})();
