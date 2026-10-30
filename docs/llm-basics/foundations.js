'use strict';
(() => {
  const math=window.FoundationMath;
  const widget=document.querySelector('.foundation-widget');
  if(!widget||!math)return;
  const kind=widget.dataset.experiment;
  widget.replaceChildren();
  function el(tag,text,cls){const node=document.createElement(tag);if(text!==undefined)node.textContent=String(text);if(cls)node.className=cls;return node;}
  function paragraph(text){widget.insertBefore(el('p',text,'caption'),controls);}
  const controls=el('div',undefined,'foundation-controls');widget.append(controls);
  const output=el('div',undefined,'foundation-output');output.setAttribute('aria-live','polite');widget.append(output);
  const fields={};let render=()=>{};
  function select(id,label,options,value){const wrap=el('label',label);const input=el('select');input.id=id;for(const [v,t] of options){const op=el('option',t);op.value=String(v);input.append(op);}input.value=String(value);wrap.append(input);controls.append(wrap);fields[id]=input;input.addEventListener('change',()=>render());return input;}
  function range(id,label,min,max,value,step=1){const wrap=el('label');const title=el('span');const input=el('input');input.type='range';input.id=id;input.min=min;input.max=max;input.step=step;input.value=value;wrap.append(title,input);controls.append(wrap);fields[id]=input;const update=()=>{title.textContent=label+'：'+input.value;render();};input.addEventListener('input',update);title.textContent=label+'：'+value;return input;}
  function value(id){return Number(fields[id].value);}
  function table(headers,rows){const wrap=el('div',undefined,'table-wrap');const t=el('table');t.dataset.columns=String(headers.length);const head=t.createTHead().insertRow();headers.forEach(h=>{const th=el('th',h);th.scope='col';head.append(th);});const body=t.createTBody();rows.forEach(row=>{const tr=body.insertRow();row.forEach(v=>tr.append(el('td',v)));});wrap.append(t);output.append(wrap);}
  function text(s){output.append(el('p',s));}
  function fmt(v){return Number(v).toFixed(6);}
  function vector(v){return '['+v.map(fmt).join(', ')+']';}
  if(kind==='tokenizer'){
    paragraph('固定版本 tiktoken 实测快照；不在网页实时执行完整 tokenizer，也不上传文本。带空格的样本用引号显示。');
    const data=window.TokenizerSamples;
    select('tokenizer-sample','预置文本',data.samples.map((r,i)=>[i,JSON.stringify(r.text)]),0);
    render=()=>{output.replaceChildren();const row=data.samples[value('tokenizer-sample')];text('原文：'+JSON.stringify(row.text)+'；版本 '+data.version+'；采集 '+data.checked_at);for(const item of row.encodings){output.append(el('h3',item.name+' · '+item.count+' tokens'));text('IDs：'+JSON.stringify(item.ids));text('逐 token 字节：'+item.hex.map(h=>'['+h+']').join(' | '));}text('特殊标记对照：默认识别到未许可拼写会报 '+data.special_default+'；显式许可 endoftext 的 cl100k_base 结果为 '+JSON.stringify(data.special_allowed)+'。快照中该字符串则按普通文本处理。');};
  }else if(kind==='engineering'){
    paragraph('下表是配套脚本的处理计数，不是运行时长；局部方案可能增加其他工作。');
    select('engineering-corpus','固定测试集',[['tiny','四条主语料'],['many_short_rows','主语料 + 200 条单字符记录']],'tiny');
    render=()=>{output.replaceChildren();const r=window.EngineeringCounts[fields['engineering-corpus'].value];table(['实现','记录访问次数','相邻位置检查数'],[['全量重计数',r.baseline.row_visits,r.baseline.pair_checks],['局部记录更新',r.local.row_visits,r.local.pair_checks]]);text('规则与最终序列逐项一致：'+(r.rules_equal?'是':'否')+'。局部更新要先扣旧再加新，因此本例 pair 检查反而增加。');};
  }else if(kind==='shapes'){
    paragraph('教学尺寸计算，不运行浏览器神经网络。D=16、V=32、两层结构固定。');
    select('shape-b','批量 B',[[1,'1'],[2,'2'],[4,'4']],2);range('shape-t','序列长度 T',2,8,4);
    render=()=>{output.replaceChildren();const b=value('shape-b'),t=value('shape-t');table(['阶段','shape'],[['输入 IDs',`[${b},${t}]`],['Embedding',`[${b},${t},16]`],['各 decoder block',`[${b},${t},16]`],['logits',`[${b},${t},32]`],['训练预测',`[${b},${t-1},32]`],['训练标签',`[${b},${t-1}]`]]);text('一条教学输入 '+JSON.stringify(Array.from({length:t},(_,i)=>i+1))+' 的目标为 '+JSON.stringify(Array.from({length:t-1},(_,i)=>i+2))+'；最后位置预测用于继续生成，不在这段有限目标中计损失。');};
  }else if(kind==='embedding'){
    paragraph('固定教学向量表 E=[[1,0],[0,1],[1,1]]；调整最终隐藏向量 h，看点积与概率。');
    range('embedding-x','h 的第一坐标',-3,3,2,.25);range('embedding-y','h 的第二坐标',-3,3,-1,.25);
    render=()=>{output.replaceChildren();const h=[value('embedding-x'),value('embedding-y')],r=math.embedding(h);text('h = '+vector(h));table(['候选 ID','E 的向量','内积分数','softmax 概率'],[[0,'[1,0]',fmt(r.logits[0]),fmt(r.probabilities[0])],[1,'[0,1]',fmt(r.logits[1]),fmt(r.probabilities[1])],[2,'[1,1]',fmt(r.logits[2]),fmt(r.probabilities[2])]]);};
  }else if(kind==='attention'){
    paragraph('前半是固定三位置 Q=K=V 的手算例；后半是 L=24、B=1、Hq=16、dh=64、每元素2字节的组件估算。');
    select('attention-row','查询位置',[[0,'0'],[1,'1'],[2,'2']],2);select('attention-kv','缓存 KV 头数',[[1,'1 / MQA'],[4,'4 / GQA'],[16,'16 / MHA']],4);range('attention-length','缓存长度',256,16384,4096,256);
    render=()=>{output.replaceChildren();const r=math.attention(value('attention-row'));table(['键位置','可见分数','权重'],r.weights.map((w,j)=>[j,Number.isFinite(r.scores[j])?fmt(r.scores[j]):'屏蔽 / −∞',fmt(w)]));text('加权输出 '+vector(r.output));const kv=value('attention-kv');text('每组服务 '+(16/kv)+' 个查询头；KV 估算 '+fmt(math.kvBytes(24,1,value('attention-length'),kv,64)/2**20)+' MiB，不是总显存。');};
  }else if(kind==='sink'){
    paragraph('人为 logits 示意，不是从真实模型提取的注意力。缓存索引也只是策略示意。');
    range('sink-logit','首位置分数',-2,6,3,.25);range('sink-prefix','保留前缀位置数 S',0,8,4);range('sink-recent','最近窗口 W',2,16,6);
    render=()=>{output.replaceChildren();const scores=[value('sink-logit'),1,0,2],p=math.softmax(scores),rest=math.softmax(scores.slice(1));table(['位置','人为分数','完整集合概率','删除首项后概率'],scores.map((s,i)=>[i,fmt(s),fmt(p[i]),i===0?'已删除':fmt(rest[i-1])]));text('长度100时保留索引：'+JSON.stringify(math.retainedPositions(100,value('sink-prefix'),value('sink-recent'))));text('这些索引不包含被逐出的中间文本；保留前缀不等于自动记住全部历史。');};
  }else if(kind==='position'){
    paragraph('位置向量为 D=4 的 sin/cos 示例；下表只展示内容与位置的配对，不模拟完整模型。');
    range('position-t','位置 t',0,10,1);select('position-order','内容顺序',[['cat','小猫 / 追 / 小狗'],['dog','小狗 / 追 / 小猫']],'cat');
    render=()=>{output.replaceChildren();text('PE(t)='+vector(math.sinusoidal(value('position-t'))));const tokens=fields['position-order'].value==='cat'?['小猫','追','小狗']:['小狗','追','小猫'];table(['位置','内容','固定位置向量'],tokens.map((t,i)=>[i,t,vector(math.sinusoidal(i))]));text('改变内容顺序后，各位置的坐标仍与该位置对应；无位置全可见 attention 的排列等变由配套 Python 测试验证。');};
  }else if(kind==='rope'){
    paragraph('二维单平面：q=(1,2)、k=(3,4)，弧度制；可同时平移位置检查相对内积。');
    range('rope-m','查询位置 m',0,20,2);range('rope-n','键位置 n',0,20,7);range('rope-shift','共同平移 c',0,100,0);select('rope-frequency','频率 ω',[[1,'1'],[.01,'0.01']],1);
    render=()=>{output.replaceChildren();const m=value('rope-m'),n=value('rope-n'),c=value('rope-shift'),f=value('rope-frequency'),q=math.rotate([1,2],m,f),k=math.rotate([3,4],n,f);const qs=math.rotate([1,2],m+c,f),ks=math.rotate([3,4],n+c,f);table(['量','数值'],[['旋转后的 q',vector(q)],['旋转后的 k',vector(k)],['共同平移后的 q',vector(qs)],['共同平移后的 k',vector(ks)],['相对角度 (n−m)ω',fmt((n-m)*f)],['原位置内积',fmt(math.dot(q,k))],['同时平移后内积',fmt(math.dot(qs,ks))],['公式 11cosδ+2sinδ',fmt(11*Math.cos((n-m)*f)+2*Math.sin((n-m)*f))]]);};
  }else if(kind==='offset'){
    paragraph('同一二维向量 (1,2)，频率1：比较正确逻辑位置与错误重置为0。不是完整 KV 服务模拟。');range('offset-position','新 token 的逻辑位置',0,200,100);
    render=()=>{output.replaceChildren();const t=value('offset-position');table(['路径','旋转位置','输出'],[['完整前向中的位置',t,vector(math.rotate([1,2],t))],['增量使用正确 offset',t,vector(math.rotate([1,2],t))],['增量错误地归零',0,vector(math.rotate([1,2],0))]]);text('位置非零时，错误归零通常产生不同结果；旧缓存不应被再次旋转。');};
  }else if(kind==='length'){
    paragraph('只验证线性位置插值和组件容量，不预测真实长上下文质量。原训练长度固定2048。');
    select('length-scale','目标长度倍率',[[2,'2 倍'],[4,'4 倍'],[8,'8 倍']],4);const p=range('length-position','目标序列位置',0,8191,8191);
    render=()=>{output.replaceChildren();const scale=value('length-scale'),target=2048*scale;p.max=String(target-1);if(Number(p.value)>target-1)p.value=String(target-1);p.parentElement.querySelector('span').textContent='目标序列位置：'+p.value;const t=Number(p.value);table(['量','结果'],[['目标长度',target],['末位置',target-1],['当前位置 t',t],['插值后 t/s',fmt(math.interpolation(t,scale))],['相邻有效位置间距',fmt(1/scale)],['该长度 KV 估算（24层/4KV头/64维/2字节）',fmt(math.kvBytes(24,1,target,4,64)/2**20)+' MiB'],['相对2048的 KV 倍率',scale],['朴素 T² 分数元素倍率',scale*scale]]);};
  }
  const renderNumbers=render;
  render=()=>{renderNumbers();window.CourseVisuals?.renderFoundation(kind,fields,output);};
  render();
})();
