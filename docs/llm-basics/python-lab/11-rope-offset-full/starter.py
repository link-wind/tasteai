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

def multihead_rope(tokens, offset=0):
    """TODO：按offset+t旋转每头"""
    raise NotImplementedError('请完成 multihead_rope')

def rope_offset_check(tokens, offset, split):
    """TODO：分块计算并与完整位置序列逐元素核对"""
    raise NotImplementedError('请完成 rope_offset_check')
