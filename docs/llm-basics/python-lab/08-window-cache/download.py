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

if __name__ == "__main__":
    print(window_attention(*[[[1, 0], [0, 1], [1, 1]], 2]))
