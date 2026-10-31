import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def merge_tokens(ids, pair, new_id):
    """TODO：左到右非重叠合并"""
    raise NotImplementedError('请完成 merge_tokens')

def pair_counts(records):
    """TODO：加权统计相邻对"""
    raise NotImplementedError('请完成 pair_counts')

def train_bpe(corpus, steps):
    """TODO：迭代选择最高频pair并更新词表与语料"""
    raise NotImplementedError('请完成 train_bpe')
