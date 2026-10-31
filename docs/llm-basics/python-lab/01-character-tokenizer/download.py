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


def character_tokenizer(train_text,text=None):
    text=train_text if text is None else text
    vocab=sorted(set(train_text))
    table={char:i for i,char in enumerate(vocab)}
    ids=[table.get(char,len(vocab)) for char in text]
    decoded=''.join(vocab[i] if i<len(vocab) else '[UNK]' for i in ids)
    return {'ids':ids,'pieces':list(text),'decoded':decoded,'vocab':vocab}

if __name__ == "__main__":
    print(character_tokenizer(*['A中🙂A']))
