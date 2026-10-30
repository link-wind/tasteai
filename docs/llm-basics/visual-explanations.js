/* 本地图形：纯 SVG 生成可由 Node 验证；浏览器适配层只读取本课控件。 */
(function(root,factory){
  if(typeof module==='object'&&module.exports)module.exports=factory(require('./foundation-math.js'));
  else root.CourseVisuals=factory(root.FoundationMath);
})(typeof window!=='undefined'?window:this,function(math){
  'use strict';
  const C={ink:'#24372e',green:'#275d46',blue:'#356f95',orange:'#ac6432',purple:'#80609b',gray:'#69766c',line:'#dce1d6',wash:'#eef2e9'};
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
  const num=n=>Number(n).toFixed(3),percent=n=>(n*100).toFixed(1)+'%';
  function tx(x,y,s,size=18,color=C.ink,anchor='start'){return `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" text-anchor="${anchor}">${esc(s)}</text>`;}
  function rect(x,y,w,h,fill=C.wash,stroke=C.line,extra=''){return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="${fill}" stroke="${stroke}" ${extra}/>`;}
  function line(a,b,c,d,color=C.gray,dash='',arrow=false){return `<path d="M${a},${b} L${c},${d}" fill="none" stroke="${color}" stroke-width="2"${dash?` stroke-dasharray="${dash}"`:''}${arrow?' marker-end="url(#v-arrow)"':''}/>`;}
  function box(x,y,w,h,label,sub='',fill=C.wash){return rect(x,y,w,h,fill)+tx(x+w/2,y+h/2+(sub?-2:6),label,18,C.ink,'middle')+(sub?tx(x+w/2,y+h/2+23,sub,15,C.gray,'middle'):'');}
  function svg(title,desc,body,height=330){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 ${height}" role="img" aria-labelledby="v-title v-desc"><title id="v-title">${esc(title)}</title><desc id="v-desc">${esc(desc)}</desc><defs><marker id="v-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="${C.gray}"/></marker><pattern id="v-mask" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#efeee8"/><path d="M0,8 L8,0" stroke="#d4d4ca"/></pattern></defs><rect width="720" height="${height}" fill="#fffefb"/><g font-family="PingFang SC,Microsoft YaHei,sans-serif">${body}</g></svg>`;}
  function bars(labels,values,options={}){
    const max=options.max||Math.max(...values,1),start=options.y||48,width=options.width||425,x=options.x||165;
    return values.map((v,i)=>{const y=start+i*57;return tx(x-12,y+22,labels[i],17,C.ink,'end')+rect(x,y,width,30,'#f0f1eb','none')+rect(x,y,Math.max(0,width*v/max),30,options.colors?.[i]||C.green,'none')+tx(x+width+13,y+22,options.percent?percent(v):v,17);}).join('');
  }
  function timeline(sinks,recent){
    let b=tx(25,252,'缓存时间线：100 个原始逻辑位置',18);
    for(let i=0;i<100;i++){
      const kept=i<sinks||i>=100-recent,fill=i<sinks?'#92b79f':kept?'#91b3cd':'#eeece5';
      b+=rect(25+i*6.65,272,5.8,35,fill,'none',`data-position="${i}" data-kept="${kept}"`);
    }
    return b+tx(25,333,`前缀 ${sinks} 个`,17,C.green)+tx(254,333,'浅灰：已逐出',17,C.gray)+tx(490,333,`最近 ${recent} 个`,17,C.blue);
  }
  function plane(vectors,opts={}){
    const cx=opts.cx||351,cy=opts.cy||242,scale=opts.scale||25,radius=opts.radius||150;
    let b=line(cx-radius-20,cy,cx+radius+20,cy)+line(cx,cy+radius+20,cx,cy-radius-20)+tx(cx+radius+25,cy+7,'x',16)+tx(cx+8,cy-radius-15,'y',16);
    b+=`<circle cx="${cx}" cy="${cy}" r="${scale}" fill="none" stroke="${C.line}" stroke-dasharray="3 5"/>`;
    for(const item of vectors){const [x,y]=item.v,px=cx+x*scale,py=cy-y*scale;
      if(item.circle)b+=`<circle cx="${cx}" cy="${cy}" r="${Math.hypot(x,y)*scale}" fill="none" stroke="${C.line}" stroke-dasharray="4 6"/>`;
      b+=line(cx,cy,px,py,item.color,item.dash||'',true)+`<circle cx="${px}" cy="${py}" r="4" fill="${item.color}" data-vector="${esc(item.name)}" data-x="${num(x)}" data-y="${num(y)}"/>`;
    }
    return b;
  }
  function waves(t,max=100){
    let b='';
    for(const [row,f,color,label] of [[0,1,C.green,'sin(t)'],[1,.01,C.blue,'sin(0.01t)']]){
      const cy=110+row*145;b+=line(130,cy,665,cy)+tx(25,cy-47,label,18,color);
      const points=Array.from({length:501},(_,i)=>{const x=max*i/500;return `${130+x/max*535},${cy-Math.sin(x*f)*42}`;}).join(' ');
      b+=`<polyline points="${points}" fill="none" stroke="${color}" stroke-width="2.4"/>`+line(130+t/max*535,cy-51,130+t/max*535,cy+51,C.orange,'4 4');
      for(const p of [0,max/2,max])b+=tx(130+p/max*535,cy+73,p,16,C.gray,'middle');
    }
    return b+tx(25,380,`虚线标记位置 t=${t}；cos 通道仍见数值表。`,17,C.orange);
  }
  function foundation(kind,s,data={}){
    let body='',title='',caption='',height=330;
    if(kind==='tokenizer'){
      title='同一段字节，三种 token 边界';const r=data.samples[s['tokenizer-sample']];
      body=tx(25,35,'每个框是一枚 token；框内标记 ID 与字节数。',18);
      let y=80;
      for(const e of r.encodings){body+=tx(25,y,e.name+' · '+e.count+' tokens',18,C.green);y+=18;
        e.ids.forEach((id,i)=>{const col=i%4,row=Math.floor(i/4),hex=e.hex[i].trim().split(/\s+/).filter(Boolean);body+=box(25+col*172,y+row*66,160,55,'ID '+id,hex.length+' 字节',i%2?'#eaf0f5':C.wash);});
        y+=Math.ceil(e.ids.length/4)*66+38;
      }height=y;caption='每框一个token，总字节不变，分组随编码变化。数据为固定实测快照。';
    }else if(kind==='engineering'){
      title='实际访问记录数对比';const r=data[s['engineering-corpus']];body=bars(['全量扫描','局部更新'],[r.baseline.row_visits,r.local.row_visits],{max:Math.max(r.baseline.row_visits,r.local.row_visits),y:75,width:370});body+=tx(25,235,'柱长表示访问次数；不表示耗时或总工作量。',18,C.gray);caption='柱长为记录访问次数；实际耗时和索引内存需另行测量。';height=280;
    }else if(kind==='shapes'){
      title='张量沿模型流动';const b=s['shape-b'],t=s['shape-t'];
      for(const [i,label,shape] of [[0,'token IDs',`[${b},${t}]`],[1,'Embedding',`[${b},${t},16]`],[2,'Decoder × 2',`[${b},${t},16]`],[3,'LM Head',`[${b},${t},32]`]]){const x=25+i*174;body+=box(x,60,152,87,label,shape,i===2?'#eee8f3':C.wash);if(i<3)body+=line(x+156,104,x+169,104,C.gray,'',true);}
      body+=tx(25,205,'训练：输入位置 0…T−2  →  目标位置 1…T−1',19)+tx(25,251,`当前 batch=${b}；每个序列 ${t} 个 token。只计算教学尺寸。`,17,C.gray);caption='观察T保持不变，最后一维从D映射到V。图中只计算教学尺寸。';height=292;
    }else if(kind==='embedding'){
      title='候选 token 的 softmax 概率';const r=math.embedding([s['embedding-x'],s['embedding-y']]);body=bars(['ID 0 · (1,0)','ID 1 · (0,1)','ID 2 · (1,1)'],r.probabilities,{max:1,percent:true,y:50,width:400});body+=tx(25,260,`h=(${s['embedding-x']},${s['embedding-y']})；分数=(${r.logits.join(', ')})`,18);caption='改变h，对照点积与候选概率；向量为手工数据。';height=300;
    }else if(kind==='attention'){
      title='因果 Attention 热力图与 KV 共享';const row=s['attention-row'],kv=s['attention-kv'];
      body=tx(25,34,'列：键位置（颜色越深，权重越大）',18)+tx(427,34,`当前查询：位置 ${row}`,18,C.green);
      for(let j=0;j<3;j++)body+=tx(175+j*95,70,'K'+j,17,C.gray,'middle');
      for(let i=0;i<3;i++){
        const r=math.attention(i);body+=tx(90,113+i*65,'Q'+i+(i===row?' →':''),18,i===row?C.green:C.gray,'end');
        for(let j=0;j<3;j++){
          const w=r.weights[j],blocked=j>i,fill=blocked?'url(#v-mask)':`rgb(${Math.round(235-192*w)},${Math.round(242-144*w)},${Math.round(235-162*w)})`;
          body+=rect(130+j*95,83+i*65,90,58,fill,i===row?C.orange:C.line,`data-query="${i}" data-key="${j}" data-weight="${w}" data-masked="${blocked}"`)+tx(175+j*95,119+i*65,blocked?'屏蔽':percent(w),17,w>.6?'#fff':C.ink,'middle');
        }
      }
      const a=math.attention(row);body+=tx(445,120,'选中行权重',17,C.gray)+tx(445,155,a.weights.map(v=>v.toFixed(3)).join(' / '),18)+tx(445,215,'橙色边框：当前行',16,C.orange)+tx(445,248,'斜线格：未来位置',16,C.gray);
      body+=tx(25,320,`16 个 Q 头 → ${kv} 组 KV（每组 ${16/kv} 个 Q）`,19);
      for(let i=0;i<16;i++){
        const x=28+i*42,group=Math.floor(i/(16/kv)),target=49+(group+.5)*(650/kv);
        body+=line(x+16,382,target,460,group%2?C.blue:C.green)+box(x,345,32,37,i,'',i%2?'#eaf0f5':C.wash);
      }
      for(let g=0;g<kv;g++){const w=650/kv;body+=box(49+g*w,460,w-5,45,kv===16?g:'KV '+g,'',g%2?'#eaf0f5':C.wash);}
      body+=tx(25,544,'上方每个小框为 Q 头；下方框为共享的 KV 组。',17,C.gray)+tx(25,581,`当前缓存长度 ${s['attention-length']}；KV 估算 ${num(math.kvBytes(24,1,s['attention-length'],kv,64)/2**20)} MiB`,17,C.green);height=610;caption='切换查询位置看遮罩，切换KV头数看共享。权重来自三位置教学算例。';
    }else if(kind==='sink'){
      title='首位置分数改变，概率怎样重新分配';const p=math.softmax([s['sink-logit'],1,0,2]);body=bars(['位置 0','位置 1','位置 2','位置 3'],p,{max:1,percent:true,y:25,width:390});body+=timeline(s['sink-prefix'],s['sink-recent']);height=365;caption='上方为人为logits；下方展示前缀加滑窗的缓存索引。';
    }else if(kind==='position'){
      title='相同位置轴上的快、慢频率';body=waves(s['position-t'],10);const tokens=s['position-order']==='dog'?['小狗','追','小猫']:['小猫','追','小狗'];tokens.forEach((word,i)=>{body+=box(25+i*230,411,210,72,word,'配对位置 '+i);});height=510;caption='虚线标记t，图只画sin通道；下方框表示内容与位置配对。';
    }else if(kind==='rope'){
      title='Q/K 在二维平面上按位置旋转';const m=s['rope-m'],n=s['rope-n'],c=s['rope-shift'],f=s['rope-frequency'];
      const q=math.rotate([1,2],m+c,f),k=math.rotate([3,4],n+c,f);
      body=tx(25,35,`实际位置：m+c=${m+c}，n+c=${n+c}；ω=${f}`,18)+plane([{name:'q0',v:[1,2],color:C.blue,dash:'5 5'},{name:'k0',v:[3,4],color:C.orange,dash:'5 5'},{name:'q',v:q,color:C.blue,circle:true},{name:'k',v:k,color:C.orange,circle:true}],{cy:232,scale:27,radius:150});
      body+=tx(25,435,'蓝色实线：旋转后 Q；橙色实线：旋转后 K',18)+tx(25,467,'虚线箭头：原始向量；虚线圆：各自保持的范数',17,C.gray)+tx(25,503,`δ=(n−m)ω=${num((n-m)*f)} rad；点积=${num(math.dot(q,k))}`,19,C.green);height=534;caption='共同平移使Q/K一起旋转，固定内容的内积保持。虚线为原向量，δ未取模。';
    }else if(kind==='offset'){
      title='正确 offset 与错误归零的方向对照';const t=s['offset-position'];const v=math.rotate([1,2],t);
      body=tx(25,35,`新 token 的逻辑位置：${t}`,19)+plane([{name:'reset',v:[1,2],color:C.orange,dash:'5 5',circle:true},{name:'correct',v,color:C.green}],{cy:200,scale:53,radius:125})+tx(25,385,'绿色实线：完整前向 = 正确增量位置',18,C.green)+tx(25,423,'橙色虚线：错误地在新输入中归零',18,C.orange);height=455;caption='比较正确逻辑位置与错误归零；t=0时两者重合。';
    }else if(kind==='length'){
      title='线性插值把更长的位置轴压回原范围';const scale=s['length-scale'],max=2048*scale-1,t=s['length-position'],mapped=t/scale;
      for(const [y,label,start,end,pos] of [[110,'目标序列',0,max,t],[270,'位置插值',0,2048,mapped]]){
        body+=tx(25,y-42,label,18)+line(90,y,650,y,C.gray,'',true)+tx(90,y+35,start,17,C.gray,'middle')+tx(650,y+35,end,17,C.gray,'middle');
        const x=90+pos/end*560;body+=`<circle cx="${x}" cy="${y}" r="7" fill="${C.blue}" data-axis="${y===110?'target':'mapped'}" data-position="${pos}"/>`+tx(x,y-17,num(pos),17,C.blue,'middle');
      }
      body+=line(90+t/max*560,155,90+mapped/2048*560,211,C.blue,'',true)+tx(25,359,`除以 ${scale}；相邻位置间距 1/${scale} = ${1/scale}`,19)+tx(25,401,`KV 容量 ×${scale}；朴素 T² 分数元素 ×${scale*scale}`,18,C.gray);height=435;caption='上下轴范围不同，蓝点按t→t/s对应。扩大倍率会压缩相邻间距。';
    }
    return {title,caption,markup:svg(title,caption,body,height)};
  }
  function bpe(state,model,turn){
    let body=tx(25,36,`已完成 ${turn} 轮；橙色框标出下一轮要合并的相邻对`,18),y=80;
    const chosen=state.candidates[0]?.pair;
    for(const row of state.corpus){body+=tx(25,y+31,`${row.text} ×${row.weight}`,17);const matches=new Set();if(chosen)for(let i=0;i<row.ids.length-1;i++){if(row.ids[i]===chosen[0]&&row.ids[i+1]===chosen[1]){matches.add(i);matches.add(i+1);i++;}}
      row.ids.forEach((id,j)=>{const bytes=model.vocab[id];let label;try{label=new TextDecoder('utf-8',{fatal:true}).decode(new Uint8Array(bytes));}catch{label=bytes.map(v=>v.toString(16)).join(' ');}const x=180+j*84;body+=rect(x,y,76,55,matches.has(j)?'#faecd9':C.wash,matches.has(j)?C.orange:C.line,`data-token-id="${id}"`)+tx(x+38,y+24,label,17,C.ink,'middle')+tx(x+38,y+46,id,14,C.gray,'middle');});y+=83;
    }
    const caption='每行一条训练记录，×后为权重；橙框标出下一轮的合并对。';
    return {title:'逐轮 BPE 合并带',caption,markup:svg('逐轮 BPE 合并带',caption,body,y+5)};
  }
  function bytes(text){
    let body=tx(25,35,'每行一个 Unicode 码点 → 对应的 UTF-8 字节',18),y=65;const chars=Array.from(text);
    for(const [i,ch] of chars.slice(0,12).entries()){
      body+=box(25,y,160,49,JSON.stringify(ch),'','#eef2e9')+line(190,y+24,222,y+24,C.gray,'',true);
      [...new TextEncoder().encode(ch)].forEach((v,j)=>body+=box(237+j*106,y,94,49,v.toString(16).toUpperCase().padStart(2,'0'),'','#eaf0f5'));y+=62;
    }
    if(!chars.length){body+=tx(25,90,'空输入：没有码点，也没有字节。',18);y=120;}
    if(chars.length>12){body+=tx(25,y+15,`图中只显示前 12 个码点；全部 ${chars.length} 个的数值见下表。`,17,C.gray);y+=45;}
    const caption='逐码点展开UTF-8字节；这是字符编码，不是GPT分词结果。';
    return {title:'字符到 UTF-8 字节的展开图',caption,markup:svg('字符到 UTF-8 字节的展开图',caption,body,y+12)};
  }
  function mount(parent,result,id='interactive-diagram'){
    let fig=parent.querySelector('#'+id);
    if(!fig){fig=document.createElement('figure');fig.id=id;fig.className='interactive-figure';parent.prepend(fig);}
    const heading=document.createElement('h3');heading.textContent=result.title;
    const frame=document.createElement('div');frame.className='diagram-frame';frame.tabIndex=0;frame.setAttribute('role','region');frame.setAttribute('aria-label',result.title+'，窄屏可横向滚动');frame.innerHTML=result.markup;
    const caption=document.createElement('figcaption');caption.textContent=result.caption;
    fig.replaceChildren(heading,frame,caption);
  }
  function renderFoundation(kind,fields,output){const s={};for(const [key,input]of Object.entries(fields))s[key]=input.type==='range'||input.id!=='engineering-corpus'&&input.id!=='position-order'?Number(input.value):input.value;const data=kind==='tokenizer'?window.TokenizerSamples:kind==='engineering'?window.EngineeringCounts:{};mount(output,foundation(kind,s,data));}
  return {foundation,bpe,bytes,renderFoundation,mount};
});
