import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def grouped_attention(x, wq, wk, wv, wo, q_heads, kv_heads, causal=True):
    q, k, v = (matmul(x, wq), matmul(x, wk), matmul(x, wv))
    width = len(q[0]) // q_heads
    group = q_heads // kv_heads
    all_weights = []
    head_outputs = []
    for head in range(q_heads):
        kv = head // group
        qh = [row[head * width:(head + 1) * width] for row in q]
        kh = [row[kv * width:(kv + 1) * width] for row in k]
        vh = [row[kv * width:(kv + 1) * width] for row in v]
        weights = []
        for i, query in enumerate(qh):
            scores = [dot(query, key) / math.sqrt(width) if not causal or j <= i else -math.inf for j, key in enumerate(kh)]
            weights.append(softmax(scores))
        all_weights.append(weights)
        head_outputs.append(matmul(weights, vh))
    joined = [sum((head[t] for head in head_outputs), []) for t in range(len(x))]
    return {'weights': all_weights, 'output': matmul(joined, wo), 'head_map': [h // group for h in range(q_heads)]}

def cached_attention(x, wq, wk, wv, wo, q_heads, kv_heads, prefill=1):
    """TODO：投影并追加KV，按Q头分组查询缓存，核对完整因果前向"""
    raise NotImplementedError('请完成 cached_attention')
