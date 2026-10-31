import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def attention_output(weights, v):
    """TODO：第四步：用权重对V加权求和"""
    raise NotImplementedError('请完成 attention_output')

def attention_weights(scores):
    """TODO：第三步：对分数逐行做稳定softmax"""
    raise NotImplementedError('请完成 attention_weights')

def attention_scores(q, k, causal=False):
    """TODO：第二步：缩放点积与可选因果遮罩"""
    raise NotImplementedError('请完成 attention_scores')

def project_qkv(x, wq, wk, wv):
    """TODO：第一步：完成Q/K/V投影"""
    raise NotImplementedError('请完成 project_qkv')

def self_attention(x, wq, wk, wv, causal=False):
    projected = project_qkv(x, wq, wk, wv)
    scores = attention_scores(projected['q'], projected['k'], causal)
    weights = attention_weights(scores)
    return {**projected, 'scores': scores, 'weights': weights, 'output': attention_output(weights, projected['v'])}
