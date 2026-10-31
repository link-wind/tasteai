import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def tiny_lm(ids, embedding, head):
    hidden = [embedding[i][:] for i in ids]
    dim = len(embedding[0])
    contextual = [[sum((hidden[j][d] for j in range(t + 1))) / (t + 1) for d in range(dim)] for t in range(len(ids))]
    logits = matmul(contextual, head)
    return {'hidden': contextual, 'logits': logits, 'probabilities': [softmax(row) for row in logits]}

def generate_tokens(ids, embedding, head, steps):
    """TODO：逐步调用前向，选择最后位置最大logit并追加token"""
    raise NotImplementedError('请完成 generate_tokens')
