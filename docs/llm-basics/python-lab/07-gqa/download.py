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

if __name__ == "__main__":
    print(grouped_attention(*[[[1, 0, 0, 1, 1, 0, 0, 1], [0, 1, 1, 0, 0, 1, 1, 0]], [[1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 1]], [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], [[1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 1]], 4, 2]))
