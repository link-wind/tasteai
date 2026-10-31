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


def byte_tokenizer(text):
    ids=list(text.encode('utf-8'))
    spans=[]
    start=0
    for char in text:
        size=len(char.encode('utf-8'))
        spans.append([start,start+size])
        start+=size
    return {'ids':ids,'spans':spans,'decoded':bytes(ids).decode('utf-8')}

if __name__ == "__main__":
    print(byte_tokenizer(*['A中🙂']))
