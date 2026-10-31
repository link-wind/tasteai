import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def rope_attention(x, offset=0, scale=1):
    q = [rotate(row, (offset + t) / scale) for t, row in enumerate(x)]
    k = [rotate(row, (offset + t) / scale) for t, row in enumerate(x)]
    weights = []
    for i, query in enumerate(q):
        weights.append(softmax([dot(query, key) / math.sqrt(len(query)) if j <= i else -math.inf for j, key in enumerate(k)]))
    return {'before': x, 'after': q, 'weights': weights, 'output': matmul(weights, x)}

def rotate(vector, position, base=10000):
    output = []
    for i in range(len(vector) // 2):
        angle = position / base ** (2 * i / len(vector))
        c, s = (math.cos(angle), math.sin(angle))
        a, b = vector[2 * i:2 * i + 2]
        output.extend([a * c - b * s, a * s + b * c])
    return output

def scaled_cache_attention(x, scale, offset=0):
    """TODO：用同一缩放策略构建历史K与新Q，核对完整和增量输出"""
    raise NotImplementedError('请完成 scaled_cache_attention')
