import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def attention_output(weights, v):
    return matmul(weights, v)

def attention_weights(scores):
    return [softmax([value if value is not None else -math.inf for value in row]) for row in scores]

def attention_scores(q, k, causal=False):
    return [[dot(query, key) / math.sqrt(len(query)) if not causal or j <= i else None for j, key in enumerate(k)] for i, query in enumerate(q)]

def project_qkv(x, wq, wk, wv):
    return {'q': matmul(x, wq), 'k': matmul(x, wk), 'v': matmul(x, wv)}

def self_attention(x, wq, wk, wv, causal=False):
    projected = project_qkv(x, wq, wk, wv)
    scores = attention_scores(projected['q'], projected['k'], causal)
    weights = attention_weights(scores)
    return {**projected, 'scores': scores, 'weights': weights, 'output': attention_output(weights, projected['v'])}

def window_attention(x, window, sinks=0):
    """TODO：实际维护并裁剪K/V及位置编号，计算裁剪后的注意力"""
    raise NotImplementedError('请完成 window_attention')

def compare_caches(x, window, sinks):
    plain = window_attention(x, window, 0)
    kept = window_attention(x, window, sinks)
    return {'full': kept['full'], 'window': plain['output'], 'sink': kept['output'], 'cache_positions': kept['cache_positions'], 'window_error': plain['error'], 'sink_error': kept['error']}
