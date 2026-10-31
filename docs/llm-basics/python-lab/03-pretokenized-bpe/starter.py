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
    ids = list(text.encode('utf-8'))
    vocab = {i: bytes([i]) for i in range(256)}
    for a, b, new_id in merges:
        vocab[new_id] = vocab[a] + vocab[b]
    ranks = {(a, b): (rank, new_id) for rank, (a, b, new_id) in enumerate(merges)}
    while len(ids) > 1:
        candidates = [(ranks[pair][0], pair) for pair in zip(ids, ids[1:]) if pair in ranks]
        if not candidates:
            break
        _, pair = min(candidates)
        ids = merge_tokens(ids, pair, ranks[pair][1])
    decoded = b''.join((vocab[i] for i in ids)).decode('utf-8')
    return {'ids': ids, 'pieces': [vocab[i].hex(' ') for i in ids], 'decoded': decoded}

def pretokenized_bpe(text, merges):
    """TODO：保留预分词边界，在各片段内运行完整BPE并还原文本"""
    raise NotImplementedError('请完成 pretokenized_bpe')
