import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def grouped_attention(x, wq, wk, wv, wo, q_heads, kv_heads, causal=True):
    """TODO：Q/K/V投影、分头、连续KV共享、因果遮罩、合头和输出投影"""
    raise NotImplementedError('请完成 grouped_attention')
