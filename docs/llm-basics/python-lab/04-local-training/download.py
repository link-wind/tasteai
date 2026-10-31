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

def pair_counts(records):
    counts=Counter()
    for ids,weight in records:
        if weight<0:raise ValueError('权重不能为负数')
        if weight==0:continue
        for pair in zip(ids,ids[1:]):
            counts[pair]+=weight
    return counts

def train_local_bpe(corpus,steps):
    records=[(list(text.encode('utf-8')),weight) for text,weight in corpus]
    counts=pair_counts(records)
    index={}
    def index_row(row_id,ids,add):
        for pair in set(zip(ids,ids[1:])):
            if add:index.setdefault(pair,set()).add(row_id)
            elif pair in index:
                index[pair].discard(row_id)
    for row_id,(ids,_) in enumerate(records):index_row(row_id,ids,True)
    merges=[]
    totals=[sum(len(ids)*w for ids,w in records)]
    touched=[]
    for rank in range(steps):
        candidates=[pair for pair,n in counts.items() if n>0]
        if not candidates:break
        pair=min(candidates,key=lambda p:(-counts[p],p))
        affected=sorted(index.get(pair,set()))
        touched.append(len(affected))
        new_id=256+rank
        for row_id in affected:
            ids,weight=records[row_id]
            counts.subtract(pair_counts([(ids,weight)]))
            index_row(row_id,ids,False)
            ids=merge_tokens(ids,pair,new_id)
            records[row_id]=(ids,weight)
            counts.update(pair_counts([(ids,weight)]))
            index_row(row_id,ids,True)
        merges.append([*pair,new_id])
        totals.append(sum(len(ids)*w for ids,w in records))
    return {'merges':merges,'totals':totals,'records':[ids for ids,w in records], 'touched':touched}

if __name__ == "__main__":
    print(train_local_bpe(*[[['low', 5], ['lower', 2], ['new', 4], ['newer', 1]], 7]))
