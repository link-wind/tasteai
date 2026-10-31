import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def relative_attention(x, slope):
    """TODO：把距离偏置加入因果注意力分数，再归一化并计算输出"""
    raise NotImplementedError('请完成 relative_attention')
