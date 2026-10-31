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
    """TODO：聚合每条记录的权重"""
    raise NotImplementedError('请完成 pair_counts')

def train_bpe(corpus, steps):
    """TODO：用加权统计执行完整训练"""
    raise NotImplementedError('请完成 train_bpe')
