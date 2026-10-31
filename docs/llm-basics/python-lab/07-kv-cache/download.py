"""已提供的矩阵工具；算法目标在各实验中实现。仅用于小规模教学。"""
import math

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def transpose(a):
    return [list(row) for row in zip(*a)]

def matmul(a,b):
    return [[dot(row,col) for col in transpose(b)] for row in a]

def softmax(row):
    maximum=max(row)
    values=[math.exp(x-maximum) for x in row]
    return [x/sum(values) for x in values]

def identity(n):
    return [[float(i==j) for j in range(n)] for i in range(n)]

import math
import re
from collections import Counter


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

if __name__ == "__main__":
    print(cached_attention(*[[[1, 0, 0, 1], [0, 1, 1, 0], [1, 1, 1, 1]], [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], [[1, 0], [0, 1], [0, 0], [0, 0]], [[1, 0], [0, 1], [0, 0], [0, 0]], [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], 2, 1, 2]))
