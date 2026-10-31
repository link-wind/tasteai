import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def merge_tokens(ids, pair, new_id):
    output = []
    i = 0
    while i < len(ids):
        if i + 1 < len(ids) and tuple(ids[i:i + 2]) == tuple(pair):
            output.append(new_id)
            i += 2
        else:
            output.append(ids[i])
            i += 1
    return output

def pair_counts(records):
    counts = Counter()
    for ids, weight in records:
        if weight < 0:
            raise ValueError('权重不能为负数')
        if weight == 0:
            continue
        for pair in zip(ids, ids[1:]):
            counts[pair] += weight
    return counts

def train_local_bpe(corpus, steps):
    """TODO：维护pair倒排索引，扣旧计数、替换、加新计数，只更新受影响记录"""
    raise NotImplementedError('请完成 train_local_bpe')
