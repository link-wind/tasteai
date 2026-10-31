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


def rotate(vector,position,base=10000):
    output=[]
    for i in range(len(vector)//2):
        angle=position/base**(2*i/len(vector))
        c,s=math.cos(angle),math.sin(angle)
        a,b=vector[2*i:2*i+2]
        output.extend([a*c-b*s,a*s+b*c])
    return output

def multihead_rope(tokens,offset=0):
    return [[[rotate(head,offset+t) for head in heads] for t,heads in enumerate(batch)] for batch in tokens]

def rope_offset_check(tokens,offset,split):
    full=multihead_rope(tokens,offset)
    prefix=multihead_rope([batch[:split] for batch in tokens],offset)
    suffix=multihead_rope([batch[split:] for batch in tokens],offset+split)
    incremental=[a+b for a,b in zip(prefix,suffix)]
    error=max(abs(a-b) for batch,other in zip(full,incremental) for t,u in zip(batch,other) for h,k in zip(t,u) for a,b in zip(h,k))
    return {'after':full,'incremental':incremental,'error':error,'positions':list(range(offset,offset+len(tokens[0])))}

if __name__ == "__main__":
    print(rope_offset_check(*[[[[[1, 0, 1, 0], [0, 1, 0, 1]], [[1, 0, 1, 0], [0, 1, 0, 1]], [[1, 1, 1, 1], [2, 0, 0, 2]]]], 3, 1]))
