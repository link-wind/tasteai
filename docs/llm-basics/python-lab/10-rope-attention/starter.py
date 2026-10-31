import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def rotate(vector, position, base=10000):
    """TODO：对所有相邻维度对进行多频率旋转"""
    raise NotImplementedError('请完成 rotate')

def rope_attention(x, offset=0, scale=1):
    """TODO：按位置旋转Q/K，构造因果Attention并作用到未旋转V"""
    raise NotImplementedError('请完成 rope_attention')
