'use strict';
(() => {
  const lab=document.querySelector('#python-workbench');if(!lab)return;
  const $=id=>document.getElementById(id);
  const editor=$('python-code'),mirror=$('python-highlight'),status=$('python-status'),output=$('python-result');
  const scenario=$('python-scenario'),run=$('python-run'),check=$('python-check'),stop=$('python-stop');
  const starter=editor.defaultValue,solution=$('python-solution').content.textContent.trim()+'\n';
  const draftKey=lab.dataset.exercise?'tasteai.python.'+lab.dataset.exercise+'.v1':'tasteai.bpe-python.code.v1';
  let traceSteps=[],traceIndex=0,playTimer=null;
  let worker=null,ready=false,busy=false,requestId=0,pending=null,timer=null;
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const keywords=new Set('from import def for in return if else while and or not True False None as with try except raise pass'.split(' '));
  function highlight(code){
    const pattern=/"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#[^\n]*|\b\d+\b|\b[A-Za-z_]\w*\b/g;
    let result='',last=0;
    for(const m of code.matchAll(pattern)){
      result+=esc(code.slice(last,m.index));const word=m[0];let kind='';
      if(word.startsWith('#'))kind='comment';else if(word.startsWith('"')||word.startsWith("'"))kind='string';else if(/^\d/.test(word))kind='number';else if(keywords.has(word))kind='keyword';
      result+=kind?`<span class="syntax-${kind}">${esc(word)}</span>`:esc(word);last=m.index+word.length;
    }
    return result+esc(code.slice(last));
  }
  function paint(){mirror.innerHTML=highlight(editor.value)+'\n';mirror.parentElement.scrollTop=editor.scrollTop;mirror.parentElement.scrollLeft=editor.scrollLeft;$('python-lines').textContent=editor.value.split('\n').length+' 行';}
  function pauseTrace(){clearInterval(playTimer);playTimer=null;$('trace-play').textContent='自动播放';}
  function clearTrace(){pauseTrace();traceSteps=[];$('python-trace-panel').hidden=true;paint();}
  function drawTrace(){
    const step=traceSteps[traceIndex];if(!step)return;
    mirror.innerHTML=editor.value.split('\n').map((line,i)=>'<span class="trace-code-line'+(i+1===step.line?' trace-current':'')+'">'+highlight(line)+'<br></span>').join('');
    const lineHeight=parseFloat(getComputedStyle(editor).lineHeight);
    editor.scrollTop=Math.max(0,(step.line-4)*lineHeight);mirror.parentElement.scrollTop=editor.scrollTop;
    $('trace-position').textContent=`${traceIndex+1} / ${traceSteps.length} · 第 ${step.line} 行 · ${step.function}${step.event==='return'?' · 返回':''}`;
    $('trace-variables').textContent=Object.entries(step.variables).map(([key,value])=>key+' = '+value).join('\n')||'尚无局部变量';
    $('trace-prev').disabled=traceIndex===0;$('trace-next').disabled=traceIndex===traceSteps.length-1;
  }
  $('trace-prev').addEventListener('click',()=>{pauseTrace();traceIndex=Math.max(0,traceIndex-1);drawTrace();});
  $('trace-next').addEventListener('click',()=>{pauseTrace();traceIndex=Math.min(traceSteps.length-1,traceIndex+1);drawTrace();});
  $('trace-play').addEventListener('click',()=>{
    if(playTimer){pauseTrace();return;}
    if(traceIndex===traceSteps.length-1)traceIndex=0;
    $('trace-play').textContent='暂停';drawTrace();
    playTimer=setInterval(()=>{if(traceIndex>=traceSteps.length-1){pauseTrace();return;}traceIndex++;drawTrace();},650);
  });
  function save(){try{localStorage.setItem(draftKey,editor.value);}catch{}}
  function empty(message='点击“运行代码”，这里将显示 Python 的实际返回结果。'){
    output.replaceChildren();const p=document.createElement('p');p.className='lab-empty';p.textContent=message;output.append(p);
  }
  function setStatus(message,state='idle'){status.textContent=message;status.dataset.state=state;}
  function setBusy(value){busy=value;$('python-trace').disabled=value;run.disabled=value;check.disabled=value;stop.disabled=!value;editor.readOnly=value;scenario.disabled=value;$('python-reset').disabled=value;$('python-load-solution').disabled=value;lab.setAttribute('aria-busy',String(value));}
  function terminate(message,state='idle'){
    clearTimeout(timer);timer=null;worker?.terminate();worker=null;ready=false;pending=null;requestId++;setBusy(false);setStatus(message,state);empty(message);
  }
  function el(tag,text,cls){const node=document.createElement(tag);if(text!==undefined)node.textContent=String(text);if(cls)node.className=cls;return node;}
  function tokens(ids,pieces){const band=el('div',undefined,'python-token-band');ids.forEach((id,i)=>{const chip=el('span',undefined,'python-token');chip.append(el('b',JSON.stringify(pieces[i])),el('small','ID '+id));chip.dataset.tokenId=String(id);band.append(chip);});return band;}
  function showVisual(data){
    output.append(el('h3',data.title));
    const views=data.views||[];
    const get=path=>path?path.split('.').reduce((v,k)=>v?.[k],data.value):data.value;
    function vectorRows(value){
      if(!Array.isArray(value))return [];
      if(!value.some(Array.isArray))return [value];
      return value.flatMap(vectorRows);
    }
    function chips(parent,values){const band=el('div',undefined,'exercise-cells');values.slice(0,100).forEach((v,i)=>{const chip=el('div',undefined,'exercise-cell');chip.append(el('small',i),el('code',typeof v==='string'?JSON.stringify(v):v));band.append(chip);});parent.append(band);}
    function svgNode(name,attrs={}){const n=document.createElementNS('http://www.w3.org/2000/svg',name);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));return n;}
    for(const [kind,title,path]of views){
      const value=get(path);if(value===undefined)continue;
      const figure=el('figure',undefined,'algorithm-figure');figure.append(el('figcaption',title));
      if(kind==='metric')figure.append(el('strong',typeof value==='number'?value.toExponential(3):value,'algorithm-metric'));
      else if(kind==='text')figure.append(el('pre',typeof value==='string'?value:JSON.stringify(value,null,2),'python-console'));
      else if(kind==='tokens'){vectorRows(value).slice(0,20).forEach(row=>chips(figure,row));}
      else if(kind==='merges'){value.slice(0,30).forEach((row,i)=>figure.append(el('p',`第${i+1}轮：${row[0]} + ${row[1]} → ${row[2]}`)));}
      else if(kind==='cache'){
        const rows=Array.isArray(value[0])?value:value.map(n=>path==='cache_lengths'?Array.from({length:n},(_,i)=>i):[n]);
        rows.slice(0,24).forEach((row,i)=>{figure.append(el('small','步骤 '+i));chips(figure,row);});
      }else if(kind==='curve'){
        const values=value.filter(v=>typeof v==='number');const svg=svgNode('svg',{viewBox:'0 0 380 130',role:'img','aria-label':title});
        const max=Math.max(1,...values),min=Math.min(0,...values);const points=values.map((v,i)=>[20+i*340/Math.max(1,values.length-1),110-(v-min)/(max-min)*90]);
        svg.append(svgNode('path',{d:'M20 15V110H365',fill:'none',stroke:'#aaa'}));svg.append(svgNode('polyline',{points:points.map(p=>p.join(',')).join(' '),fill:'none',stroke:'#247550','stroke-width':2}));
        points.forEach(([cx,cy],i)=>{svg.append(svgNode('circle',{cx,cy,r:3,fill:'#247550'}));const t=svgNode('text',{x:cx,y:cy-7,'text-anchor':'middle','font-size':10});t.textContent=values[i];svg.append(t);});figure.append(svg);figure.append(el('small','横轴：轮次；纵轴：实际计数。'));
      }else if(kind==='rotation'){
        const before=vectorRows(data.value.before||[]),after=vectorRows(value);after.slice(0,4).forEach((row,i)=>{
          const old=before[i];if(!old)return;const max=Math.max(1,...old.map(Math.abs),...row.map(Math.abs));
          const svg=svgNode('svg',{viewBox:'0 0 180 180',role:'img','aria-label':title+' 向量'+i});
          svg.append(svgNode('path',{d:'M10 90H170M90 10V170',stroke:'#ddd'}));
          [[old,'#a0a5aa'],[row,'#247550']].forEach(([v,color])=>svg.append(svgNode('line',{x1:90,y1:90,x2:90+v[0]/max*65,y2:90-v[1]/max*65,stroke:color,'stroke-width':3})));
          figure.append(svg);
        });figure.append(el('small','灰：旋转前；绿：旋转后。每幅图显示一个向量的首个二维平面。'));
      }else{
        const rows=vectorRows(value);const scale=Math.max(1e-12,...rows.flat().filter(v=>typeof v==='number').map(Math.abs));
        const table=el('table',undefined,'algorithm-matrix');rows.slice(0,40).forEach((row,i)=>{const tr=el('tr');tr.append(el('th',i));row.slice(0,40).forEach(v=>{const td=el('td',v===null?'×':typeof v==='number'?Number(v.toPrecision(5)):v);if(typeof v==='number')td.style.backgroundColor=`rgba(${v<0?'183,80,65':'40,130,85'},${.08+.65*Math.abs(v)/scale})`;tr.append(td);});table.append(tr);});figure.append(table);
        figure.append(el('small',kind==='heatmap'?'行：查询位置；列：键位置。多头矩阵按头依次纵向排列；颜色表示本图数值大小。':'行列对应返回张量顺序；多批次/多头按顺序纵向展开。×表示被遮罩。'));
      }
      output.append(figure);
    }
    const detail=el('details',undefined,'supplement');detail.append(el('summary','查看输入与完整返回值'),el('pre',JSON.stringify({input:data.input,result:data.value},null,2),'python-console'));output.append(detail);
  }
  function show(payload,mode){
    output.replaceChildren();
    if(mode==='trace'&&payload.trace?.length){traceSteps=payload.trace;traceIndex=0;$('python-trace-panel').hidden=false;drawTrace();}
    if(payload.trace_truncated)output.append(el('p','轨迹超过 1500 步，仅回放前 1500 步。'));
    if(payload.visual)showVisual(payload.visual);
    if(payload.experiment){
      const data=payload.experiment;
      const heading=el('h3','候选：'+data.pair_pieces.map(s=>JSON.stringify(s)).join(' + ')+' → '+JSON.stringify(data.new_piece));output.append(heading);
      const stats=el('div',undefined,'python-result-metrics');
      for(const [value,label]of [[data.frequency,'候选加权频次'],[`${data.before} → ${data.after}`,'加权 token 总量'],[data.before-data.after,'本轮实际减少']]){
        const item=el('div');item.append(el('strong',value),el('span',label));stats.append(item);
      }output.append(stats);
      const graph=el('figure',undefined,'python-merge-figure');graph.setAttribute('aria-label','Python 返回的合并前后 token 边界');
      for(const row of data.records){const record=el('div',undefined,'python-record');record.append(el('strong',row.text+' × '+row.weight));
        const before=el('div',undefined,'python-token-row');before.append(el('span','合并前'),tokens(row.before,row.before_pieces));
        const after=el('div',undefined,'python-token-row');after.append(el('span','合并后'),tokens(row.after,row.after_pieces));record.append(before,after);graph.append(record);
      }
      graph.append(el('figcaption','每个框是一枚 token；图形直接来自你这次执行的 Python。'));output.append(graph);
    }
    if(mode==='check'&&payload.checks?.length){
      const results=payload.checks||[],passed=results.filter(t=>t.passed).length;
      const summary=el('h3',`检查结果：${passed} / ${results.length} 通过`);summary.id='python-check-summary';output.append(summary);
      const list=el('ul',undefined,'python-check-list');for(const test of results){const item=el('li');item.dataset.passed=String(test.passed);item.append(el('strong',(test.passed?'✓ 通过 · ':'× 未通过 · ')+test.name));if(!test.passed)item.append(el('span',test.detail));list.append(item);}output.append(list);
    }
    if(payload.error){output.append(el('h3','Python 报错'),el('pre',payload.error,'python-console'));}
    if(payload.stdout){output.append(el('h3','标准输出'),el('pre',payload.stdout,'python-console'));}
    const all=mode==='check'&&payload.checks.length>0&&payload.checks.every(t=>t.passed);
    if(!payload.ok)setStatus('代码执行出错；编辑器已保留，请查看错误后重试。','error');
    else if(mode==='check')setStatus(all?(lab.dataset.exercise?'全部检查通过。试试切换另一组输入。':'全部检查通过。试试切换“重叠匹配”语料。'):'检查完成，仍有未通过项。可以先看提示再修改。',all?'success':'feedback');
    else if(mode==='trace')setStatus('轨迹已准备好。点击下一步观察代码与变量。','success');
    else if(payload.experiment?.before===payload.experiment?.after)setStatus('Python 已运行，本轮尚未减少 token。试着补全 TODO。','feedback');
    else setStatus('Python 已运行。修改代码或切换输入，再观察结果。','success');
  }
  function execute(){
    if(!pending||!worker)return;
    setStatus('Python 正在执行…','running');
    clearTimeout(timer);timer=setTimeout(()=>terminate('执行超过8秒，已停止。修改代码后可重新运行。','error'),8000);
    worker.postMessage({type:'run',...pending});
  }
  function start(mode){
    if(busy)return;
    if(editor.value.length>40000){setStatus('代码最多40000个字符。','error');return;}
    clearTrace();save();setBusy(true);empty('等待本次 Python 执行结果…');pending={id:++requestId,code:editor.value,scenario:scenario.value,mode};
    if(ready&&worker){execute();return;}
    setStatus('首次运行正在加载 Python；下载完成前也可以点击停止。','loading');
    timer=setTimeout(()=>terminate('Python 加载超时；请检查网络后重新点击运行。','error'),90000);
    try{
      worker=new Worker(new URL(lab.dataset.worker,location.href),{type:'module'});
      const currentWorker=worker;
      worker.onmessage=({data})=>{
        if(!pending||data.id!==pending.id)return;
        if(data.type==='ready'){ready=true;execute();}
        else if(data.type==='result'){clearTimeout(timer);const mode=pending.mode;pending=null;setBusy(false);show(data.payload,mode);}
        else if(data.type==='error')terminate('Python 加载或执行失败：'+data.error+' 请重试。','error');
      };
      worker.onerror=()=>{if(worker===currentWorker)terminate('Python 运行时未能加载。请检查网络后重试；代码已保留。','error');};
      worker.postMessage({type:'init',id:pending.id,exercise:lab.dataset.exercise,configURL:lab.dataset.config?new URL(lab.dataset.config,location.href).href:undefined,harnessURL:new URL(lab.dataset.harness,location.href).href});
    }catch(error){terminate('无法启动 Python：'+error.message,'error');}
  }
  try{const saved=localStorage.getItem(draftKey);if(saved&&saved.length<=40000)editor.value=saved;}catch{}
  editor.addEventListener('input',()=>{clearTrace();paint();save();empty('代码已修改，运行后显示新结果。');setStatus('代码已修改。按 Ctrl / ⌘ + Enter 运行。');});
  editor.addEventListener('scroll',()=>{mirror.parentElement.scrollTop=editor.scrollTop;mirror.parentElement.scrollLeft=editor.scrollLeft;});
  editor.addEventListener('keydown',event=>{
    if(event.key==='Enter'&&(event.ctrlKey||event.metaKey)){event.preventDefault();start('run');}
    else if(event.key==='Tab'&&!event.shiftKey&&!editor.readOnly){event.preventDefault();editor.setRangeText('    ',editor.selectionStart,editor.selectionEnd,'end');editor.dispatchEvent(new Event('input'));}
  });
  function load(code){clearTrace();editor.value=code;paint();save();empty();setStatus('代码已载入；点击运行或检查答案。');}
  $('python-trace').addEventListener('click',()=>start('trace'));
  run.addEventListener('click',()=>start('run'));check.addEventListener('click',()=>start('check'));
  stop.addEventListener('click',()=>terminate('已停止。代码已保留，下次运行会重新初始化 Python。'));
  $('python-reset').addEventListener('click',()=>load(starter));
  $('python-load-solution').addEventListener('click',()=>load(solution));
  scenario.addEventListener('change',()=>{clearTrace();empty('输入已切换，请重新运行代码。');setStatus('语料已切换。');});
  $('python-download').addEventListener('click',()=>{const helper=$('python-math')?.content.textContent;const downloaded=helper?helper+'\n'+editor.value.replace(/^from tasteai_math import .+$/gm,''):editor.value;const url=URL.createObjectURL(new Blob([downloaded],{type:'text/x-python;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=lab.dataset.exercise?'tasteai-'+lab.dataset.exercise+'.py':'tasteai-bpe.py';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  window.addEventListener('pagehide',()=>{pauseTrace();clearTimeout(timer);worker?.terminate();worker=null;ready=false;pending=null;setBusy(false);});
  paint();editor.closest('.python-editor').classList.add('editor-enabled');setBusy(false);
})();
