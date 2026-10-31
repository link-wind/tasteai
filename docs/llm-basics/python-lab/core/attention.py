import math
from tasteai_math import dot, matmul, softmax, identity

def project_qkv(x,wq,wk,wv):
    return {'q':matmul(x,wq),'k':matmul(x,wk),'v':matmul(x,wv)}

def attention_scores(q,k,causal=False):
    return [[dot(query,key)/math.sqrt(len(query)) if not causal or j<=i else None
             for j,key in enumerate(k)] for i,query in enumerate(q)]

def attention_weights(scores):
    return [softmax([value if value is not None else -math.inf for value in row]) for row in scores]

def attention_output(weights,v):
    return matmul(weights,v)

def self_attention(x,wq,wk,wv,causal=False):
    projected=project_qkv(x,wq,wk,wv)
    scores=attention_scores(projected['q'],projected['k'],causal)
    weights=attention_weights(scores)
    return {**projected,'scores':scores,'weights':weights,'output':attention_output(weights,projected['v'])}

def grouped_attention(x,wq,wk,wv,wo,q_heads,kv_heads,causal=True):
    q,k,v=matmul(x,wq),matmul(x,wk),matmul(x,wv)
    width=len(q[0])//q_heads
    group=q_heads//kv_heads
    all_weights=[]
    head_outputs=[]
    for head in range(q_heads):
        kv=head//group
        qh=[row[head*width:(head+1)*width] for row in q]
        kh=[row[kv*width:(kv+1)*width] for row in k]
        vh=[row[kv*width:(kv+1)*width] for row in v]
        weights=[]
        for i,query in enumerate(qh):
            scores=[dot(query,key)/math.sqrt(width) if not causal or j<=i else -math.inf for j,key in enumerate(kh)]
            weights.append(softmax(scores))
        all_weights.append(weights)
        head_outputs.append(matmul(weights,vh))
    joined=[sum((head[t] for head in head_outputs),[]) for t in range(len(x))]
    return {'weights':all_weights,'output':matmul(joined,wo),'head_map':[h//group for h in range(q_heads)]}

def cached_attention(x,wq,wk,wv,wo,q_heads,kv_heads,prefill=1):
    # prefill整块只投影一次，随后逐项decode。
    full=grouped_attention(x,wq,wk,wv,wo,q_heads,kv_heads)
    width=len(wq[0])//q_heads
    group=q_heads//kv_heads
    prefix=min(prefill,len(x))
    if prefix<1:raise ValueError('prefill必须为正整数')
    cache_k=matmul(x[:prefix],wk)
    cache_v=matmul(x[:prefix],wv)
    incremental=grouped_attention(x[:prefix],wq,wk,wv,wo,q_heads,kv_heads)['output']
    lengths=list(range(1,prefix+1))
    for row in x[prefix:]:
        query=matmul([row],wq)[0]
        cache_k.append(matmul([row],wk)[0])
        cache_v.append(matmul([row],wv)[0])
        joined=[]
        for head in range(q_heads):
            kv=head//group
            qh=query[head*width:(head+1)*width]
            keys=[k[kv*width:(kv+1)*width] for k in cache_k]
            values=[v[kv*width:(kv+1)*width] for v in cache_v]
            weights=softmax([dot(qh,key)/math.sqrt(width) for key in keys])
            joined.extend(matmul([weights],values)[0])
        incremental.append(matmul([joined],wo)[0])
        lengths.append(len(cache_k))
    error=max(abs(a-b) for r,s in zip(full['output'],incremental) for a,b in zip(r,s))
    return {'full':full['output'],'incremental':incremental,'error':error,'cache_lengths':lengths,'weights':full['weights'],'prefill_size':prefix}

def window_attention(x,window,sinks=0):
    cache_k=[]
    cache_v=[]
    positions=[]
    snapshots=[]
    output=[]
    for position,row in enumerate(x):
        cache_k.append(row[:])
        cache_v.append(row[:])
        positions.append(position)
        keep=[i for i,p in enumerate(positions) if p<sinks or p>=position-window+1]
        cache_k=[cache_k[i] for i in keep]
        cache_v=[cache_v[i] for i in keep]
        positions=[positions[i] for i in keep]
        weights=softmax([dot(row,key)/math.sqrt(len(row)) for key in cache_k])
        output.append(matmul([weights],cache_v)[0])
        snapshots.append(positions[:])
    full=self_attention(x,identity(len(x[0])),identity(len(x[0])),identity(len(x[0])),True)['output']
    return {'output':output,'full':full,'cache_positions':snapshots,'error':max(abs(a-b) for r,s in zip(full,output) for a,b in zip(r,s))}

def compare_caches(x,window,sinks):
    plain=window_attention(x,window,0)
    kept=window_attention(x,window,sinks)
    return {'full':kept['full'],'window':plain['output'],'sink':kept['output'],
            'cache_positions':kept['cache_positions'],'window_error':plain['error'],'sink_error':kept['error']}
