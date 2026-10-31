import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

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

def train_bpe(corpus,steps):
    records=[(list(text.encode('utf-8')),weight) for text,weight in corpus]
    merges=[]
    totals=[sum(len(ids)*w for ids,w in records)]
    for rank in range(steps):
        counts=pair_counts(records)
        if not counts:break
        pair=min(counts,key=lambda pair:(-counts[pair],pair))
        new_id=256+rank
        records=[(merge_tokens(ids,pair,new_id),w) for ids,w in records]
        merges.append([*pair,new_id])
        totals.append(sum(len(ids)*w for ids,w in records))
    return {'merges':merges,'totals':totals,'records':[ids for ids,w in records]}
