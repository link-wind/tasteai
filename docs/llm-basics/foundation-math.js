/* 本地数学内核：浏览器与 Node 对照测试共用。 */
(function(root,factory){
  if(typeof module==='object'&&module.exports) module.exports=factory();
  else root.FoundationMath=factory();
})(typeof window!=='undefined'?window:this,function(){
  'use strict';
  function softmax(values){const max=Math.max(...values);if(!Number.isFinite(max))throw new Error('至少需要一个有限分数');const exp=values.map(v=>Math.exp(v-max)),sum=exp.reduce((a,b)=>a+b,0);return exp.map(v=>v/sum);}
  function dot(a,b){return a.reduce((sum,v,i)=>sum+v*b[i],0);}
  function rotate(x,position,frequency=1){const a=position*frequency,c=Math.cos(a),s=Math.sin(a);return [x[0]*c-x[1]*s,x[0]*s+x[1]*c];}
  function sinusoidal(position){return [Math.sin(position),Math.cos(position),Math.sin(position*.01),Math.cos(position*.01)];}
  function kvBytes(layers,batch,length,heads,dim,bytes=2){return 2*layers*batch*length*heads*dim*bytes;}
  function attention(row){const x=[[1,0],[0,1],[1,1]],scores=x.map((key,j)=>j>row?-Infinity:dot(x[row],key)/Math.sqrt(2));const weights=softmax(scores);return {scores,weights,output:[0,1].map(d=>weights.reduce((s,w,j)=>s+w*x[j][d],0))};}
  function embedding(h){const E=[[1,0],[0,1],[1,1]],logits=E.map(e=>dot(h,e));return {logits,probabilities:softmax(logits)};}
  function retainedPositions(length,sinks,recent){return Array.from({length},(_,i)=>i).filter(i=>i<sinks||i>=length-recent);}
  function interpolation(position,scale){return position/scale;}
  return {softmax,dot,rotate,sinusoidal,kvBytes,attention,embedding,retainedPositions,interpolation};
});
