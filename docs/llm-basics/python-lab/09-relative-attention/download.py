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


def relative_attention(x,slope):
    scores=[]
    weights=[]
    for i,q in enumerate(x):
        row=[dot(q,k)/math.sqrt(len(q))-slope*abs(i-j) if j<=i else -math.inf for j,k in enumerate(x)]
        scores.append([v if math.isfinite(v) else None for v in row])
        weights.append(softmax(row))
    return {'scores':scores,'weights':weights,'output':matmul(weights,x)}

if __name__ == "__main__":
    print(relative_attention(*[[[1, 0], [1, 0], [1, 0]], 1]))
