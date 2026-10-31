import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def rotate(vector, position, base=10000):
    output = []
    for i in range(len(vector) // 2):
        angle = position / base ** (2 * i / len(vector))
        c, s = (math.cos(angle), math.sin(angle))
        a, b = vector[2 * i:2 * i + 2]
        output.extend([a * c - b * s, a * s + b * c])
    return output

def rope_invariants(q, k, m, n, shift):
    """TODO：计算范数、共同平移内积及相对旋转等式误差"""
    raise NotImplementedError('请完成 rope_invariants')
