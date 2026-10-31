import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def attention_output(weights,v):
    return matmul(weights,v)

def attention_weights(scores):
    return [softmax([value if value is not None else -math.inf for value in row]) for row in scores]

def attention_scores(q,k,causal=False):
    return [[dot(query,key)/math.sqrt(len(query)) if not causal or j<=i else None
             for j,key in enumerate(k)] for i,query in enumerate(q)]

def project_qkv(x,wq,wk,wv):
    return {'q':matmul(x,wq),'k':matmul(x,wk),'v':matmul(x,wv)}

def self_attention(x,wq,wk,wv,causal=False):
    projected=project_qkv(x,wq,wk,wv)
    scores=attention_scores(projected['q'],projected['k'],causal)
    weights=attention_weights(scores)
    return {**projected,'scores':scores,'weights':weights,'output':attention_output(weights,projected['v'])}

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
