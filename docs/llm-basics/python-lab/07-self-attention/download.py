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

if __name__ == "__main__":
    print(self_attention(*[[[1, 0], [0, 1], [1, 1]], [[1, 0], [0, 1]], [[1, 0], [0, 1]], [[1, 0], [0, 1]]]))
