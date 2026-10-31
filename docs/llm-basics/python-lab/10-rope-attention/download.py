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

def rope_attention(x,offset=0,scale=1):
    q=[rotate(row,(offset+t)/scale) for t,row in enumerate(x)]
    k=[rotate(row,(offset+t)/scale) for t,row in enumerate(x)]
    weights=[]
    for i,query in enumerate(q):
        weights.append(softmax([dot(query,key)/math.sqrt(len(query)) if j<=i else -math.inf for j,key in enumerate(k)]))
    return {'before':x,'after':q,'weights':weights,'output':matmul(weights,x)}

if __name__ == "__main__":
    print(rope_attention(*[[[1, 0], [1, 0], [1, 0]]]))
