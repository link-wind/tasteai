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


def merge_tokens(ids,pair,new_id):
    output=[]
    i=0
    while i<len(ids):
        if i+1<len(ids) and tuple(ids[i:i+2])==tuple(pair):
            output.append(new_id)
            i+=2
        else:
            output.append(ids[i])
            i+=1
    return output

def encode_bpe(text,merges):
    ids=list(text.encode('utf-8'))
    vocab={i:bytes([i]) for i in range(256)}
    for a,b,new_id in merges:
        vocab[new_id]=vocab[a]+vocab[b]
    ranks={(a,b):(rank,new_id) for rank,(a,b,new_id) in enumerate(merges)}
    while len(ids)>1:
        candidates=[(ranks[pair][0],pair) for pair in zip(ids,ids[1:]) if pair in ranks]
        if not candidates:break
        _,pair=min(candidates)
        ids=merge_tokens(ids,pair,ranks[pair][1])
    decoded=b''.join(vocab[i] for i in ids).decode('utf-8')
    return {'ids':ids,'pieces':[vocab[i].hex(' ') for i in ids],'decoded':decoded}

def pretokenized_bpe(text,merges):
    # 教学预分词：字母、最多3位数字、空白、其余单字符。
    parts=re.findall(r'[A-Za-z]+|[0-9]{1,3}|\s+|[^A-Za-z0-9\s]',text)
    encoded=[encode_bpe(part,merges) for part in parts]
    return {'parts':parts,'ids':[i for row in encoded for i in row['ids']],
            'pieces':[piece for row in encoded for piece in row['pieces']],
            'decoded':''.join(row['decoded'] for row in encoded)}

if __name__ == "__main__":
    print(pretokenized_bpe(*['low 1234567!', [[108, 111, 256], [256, 119, 257]]]))
