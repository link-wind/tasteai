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


def tied_head(ids,embedding):
    if ids and isinstance(ids[0],list):
        batches=[tied_head(row,embedding) for row in ids]
        return {key:[batch[key] for batch in batches] for key in ('hidden','logits','probabilities')}
    hidden=[embedding[i][:] for i in ids]
    logits=[[dot(row,word) for word in embedding] for row in hidden]
    return {'hidden':hidden,'logits':logits,'probabilities':[softmax(row) for row in logits]}

if __name__ == "__main__":
    print(tied_head(*[[[0, 1], [2, 0]], [[1, 0], [0, 1], [1, 1]]]))
