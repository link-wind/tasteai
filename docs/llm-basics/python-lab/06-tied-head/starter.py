import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def tied_head(ids, embedding):
    """TODO：同一Embedding用于输入查表与转置词表投影"""
    raise NotImplementedError('请完成 tied_head')
