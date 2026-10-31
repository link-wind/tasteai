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


def tiny_lm(ids,embedding,head):
    hidden=[embedding[i][:] for i in ids]
    dim=len(embedding[0])
    # 教学因果上下文层：前缀平均，避免把独立查表冒充语言模型。
    contextual=[[sum(hidden[j][d] for j in range(t+1))/(t+1) for d in range(dim)] for t in range(len(ids))]
    logits=matmul(contextual,head)
    return {'hidden':contextual,'logits':logits,'probabilities':[softmax(row) for row in logits]}

def generate_tokens(ids,embedding,head,steps):
    sequence=ids[:]
    selected=[]
    history=[]
    for _ in range(steps):
        result=tiny_lm(sequence,embedding,head)
        last=result['logits'][-1]
        token=max(range(len(last)),key=lambda i:last[i])
        sequence.append(token)
        selected.append(token)
        history.append(result['probabilities'][-1])
    return {'ids':sequence,'generated':selected,'probabilities':history}

if __name__ == "__main__":
    print(generate_tokens(*[[0], [[1, 0], [0, 1], [1, 1]], [[1, 0, -1], [0, 1, 1]], 4]))
