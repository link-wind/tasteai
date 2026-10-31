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

def encode_bpe(text, merges):
    """TODO：按已学合并rank编码，并重建字节词表完成解码"""
    raise NotImplementedError('请完成 encode_bpe')
