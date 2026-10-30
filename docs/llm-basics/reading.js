'use strict';
(() => {
  const courseNavigation = document.querySelector('.course-nav');
  if (window.matchMedia('(max-width: 760px)').matches && courseNavigation) courseNavigation.open = false;
  const fontToggle = document.querySelector('#font-toggle');
  if (fontToggle) {
    let large = false;
    try { large = localStorage.getItem('llm-detailed.font-large') === 'true'; } catch {}
    function applySize() {
      document.body.classList.toggle('large', large);
      fontToggle.setAttribute('aria-pressed', String(large));
      fontToggle.textContent = large ? '恢复字号' : '放大字号';
    }
    fontToggle.addEventListener('click', () => {
      large = !large; applySize();
      try { localStorage.setItem('llm-detailed.font-large', String(large)); } catch {}
    });
    applySize();
  }
  // 复制正文代码；工具栏不参与源码文本。
  document.querySelectorAll('main pre:not([data-editor-mirror])').forEach(pre=>{
    const code=pre.querySelector('code');if(!code)return;
    const block=document.createElement('div');block.className='code-block';
    const toolbar=document.createElement('div');toolbar.className='code-toolbar';
    const label=document.createElement('span');label.textContent=pre.dataset.language||'示例';
    const copy=document.createElement('button');copy.type='button';copy.className='code-copy';copy.textContent='复制';
    copy.setAttribute('aria-label','复制'+label.textContent+'代码');copy.setAttribute('aria-live','polite');
    copy.addEventListener('click',async()=>{
      try{await navigator.clipboard.writeText(code.textContent);copy.textContent='已复制';}
      catch{copy.textContent='请选中代码复制';}
      setTimeout(()=>{copy.textContent='复制';},1800);
    });
    toolbar.append(label,copy);pre.before(block);block.append(toolbar,pre);
  });
  function revealAnchor(){
    if(!location.hash)return;
    let target;try{target=document.getElementById(decodeURIComponent(location.hash.slice(1)));}catch{return;}
    if(!target)return;
    let parent=target.closest('details');
    while(parent){parent.open=true;parent=parent.parentElement?.closest('details');}
    target.querySelectorAll(':scope > details.supplement').forEach(detail=>{detail.open=true;});
    requestAnimationFrame(()=>window.scrollTo({top:target.getBoundingClientRect().top+window.scrollY-82,behavior:'instant'}));
  }
  window.addEventListener('hashchange',revealAnchor);
  requestAnimationFrame(revealAnchor);
  const outlineLinks=[...document.querySelectorAll('.page-toc a')];
  const sections=[...document.querySelectorAll('main section[id]')];
  if(outlineLinks.length&&'IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>{
      const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);
      if(!visible.length)return;
      for(const link of outlineLinks){if(link.hash==='#'+visible[0].target.id)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');}
    },{rootMargin:'-80px 0px -65% 0px',threshold:0});
    sections.forEach(section=>observer.observe(section));
  }
  document.querySelectorAll('.inline-toc a,.course-nav a').forEach(link=>link.addEventListener('click',()=>{
    if(window.matchMedia('(max-width: 760px)').matches){link.closest('details.inline-toc')?.removeAttribute('open');if(link.closest('.course-nav'))courseNavigation.open=false;}
  }));
  let printDetails=[];
  window.addEventListener('beforeprint',()=>{printDetails=[...document.querySelectorAll('details')].map(detail=>[detail,detail.open]);printDetails.forEach(([detail])=>{detail.open=true;});});
  window.addEventListener('afterprint',()=>{printDetails.forEach(([detail,open])=>{detail.open=open;});});
  // 原生 dialog 支持 Escape、焦点管理；无脚本时图片仍可阅读。
  const zoomButtons=document.querySelectorAll('.figure-zoom');
  if(zoomButtons.length){
    const dialog=document.createElement('dialog');dialog.className='figure-dialog';dialog.setAttribute('aria-labelledby','figure-dialog-title');
    const heading=document.createElement('h2');heading.id='figure-dialog-title';
    const close=document.createElement('button');close.type='button';close.textContent='关闭大图（Esc）';
    const viewport=document.createElement('div');viewport.className='figure-dialog-viewport';viewport.tabIndex=0;
    const img=document.createElement('img');viewport.append(img);
    const caption=document.createElement('p');caption.className='caption';
    dialog.append(close,heading,viewport,caption);document.body.append(dialog);let opener;
    close.addEventListener('click',()=>dialog.close());
    dialog.addEventListener('close',()=>opener?.focus());
    for(const button of zoomButtons){button.hidden=false;button.addEventListener('click',()=>{
      opener=button;const fig=button.closest('figure'),source=fig.querySelector('img');
      heading.textContent=fig.querySelector('strong').textContent;img.src=source.src;img.alt=source.alt;
      caption.textContent=fig.querySelector('figcaption').textContent;dialog.showModal();
    });}
  }
  const input = document.querySelector('#text-input');
  if (!input) return;
  const vocabulary = ['<UNK>', 'A', '中', '🙂', 'e', '\u0301', ' ', '!'];
  const lookup = new Map(vocabulary.slice(1).map((char, i) => [char, i + 1]));
  const samples = {mixed: 'A中🙂', accent: 'e\u0301', unknown: 'A猫', empty: ''};
  const ids = ['char-ids', 'char-decoded', 'unknown-chars', 'byte-hex', 'byte-ids', 'byte-decoded'];
  const set = (id, value) => { document.getElementById(id).textContent = value; };
  const hex = byte => byte.toString(16).toUpperCase().padStart(2, '0');
  const codepoint = char => 'U+' + char.codePointAt(0).toString(16).toUpperCase().padStart(4, '0');
  function update() {
    const text = input.value;
    // 超长输入不展开渲染，避免极大码点表占用页面。
    if (text.length > 240 || Array.from(text).length > 120) {
      set('lab-status', '最多输入120个码点；结果已清空，请缩短文本。');
      for (const id of ['count-codepoints', 'count-bytes', 'count-units', ...ids]) set(id, '—');
      document.querySelector('#codepoint-rows').replaceChildren();
      document.querySelector('#byte-diagram')?.remove();
      return;
    }
    window.CourseVisuals?.mount(input.closest('.experiment'),window.CourseVisuals.bytes(text),'byte-diagram');
    const chars = Array.from(text);
    const bytes = new TextEncoder().encode(text);
    const decodedBytes = new TextDecoder('utf-8', {fatal: true}).decode(bytes);
    const tokenIds = chars.map(char => lookup.get(char) ?? 0);
    const unknown = chars.filter(char => !lookup.has(char));
    set('count-codepoints', String(chars.length));
    set('count-bytes', String(bytes.length));
    set('count-units', String(text.length));
    set('char-ids', JSON.stringify(tokenIds));
    set('char-decoded', JSON.stringify(tokenIds.map(id => vocabulary[id]).join('')));
    set('unknown-chars', unknown.length ? unknown.map(char => `${JSON.stringify(char)} (${codepoint(char)})`).join('、') : '无');
    set('byte-hex', Array.from(bytes, hex).join(' ') || '空字节序列');
    set('byte-ids', JSON.stringify(Array.from(bytes)));
    set('byte-decoded', JSON.stringify(decodedBytes));
    const table = document.createElement('table');
    const thead = table.createTHead();
    const header = thead.insertRow();
    for (const title of ['位置（从 1 起）', '显示/转义', '码点', 'UTF-8 字节']) {
      const th = document.createElement('th'); th.scope = 'col'; th.textContent = title; header.append(th);
    }
    const body = table.createTBody();
    chars.forEach((char, index) => {
      const row = body.insertRow();
      const values = [String(index + 1), JSON.stringify(char), codepoint(char), Array.from(new TextEncoder().encode(char), hex).join(' ')];
      for (const value of values) row.insertCell().textContent = value;
    });
    document.querySelector('#codepoint-rows').replaceChildren(table);
    if (decodedBytes !== text) {
      set('lab-status', '输入含孤立 UTF-16 代理项。TextEncoder 已将其替换为 U+FFFD，字节解码不等于原串；Python 严格实验会拒绝此类输入。');
    } else if (!text) {
      set('lab-status', '空输入：0 个码点、0 个字节，编码为空序列，解码为空字符串。');
    } else if (unknown.length) {
      set('lab-status', `未知码点${unknown.length}个：字符词表使用<UNK>并丢失信息；UTF-8仍可恢复原文。`);
    } else {
      set('lab-status', '所有码点均在教学词表中，两种方案都能恢复原文。');
    }
  }
  input.addEventListener('input', update);
  document.querySelectorAll('[data-sample]').forEach(button => button.addEventListener('click', () => {
    input.value = samples[button.dataset.sample]; update();
  }));
  update();
})();
