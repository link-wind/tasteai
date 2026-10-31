import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def attention_output(weights,v):
    return matmul(weights,v)

def attention_weights(scores):
    return [softmax([value if value is not None else -math.inf for value in row]) for row in scores]

def attention_scores(q,k,causal=False):
    return [[dot(query,key)/math.sqrt(len(query)) if not causal or j<=i else None
             for j,key in enumerate(k)] for i,query in enumerate(q)]

def project_qkv(x,wq,wk,wv):
    return {'q':matmul(x,wq),'k':matmul(x,wk),'v':matmul(x,wv)}

def self_attention(x,wq,wk,wv,causal=False):
    projected=project_qkv(x,wq,wk,wv)
    scores=attention_scores(projected['q'],projected['k'],causal)
    weights=attention_weights(scores)
    return {**projected,'scores':scores,'weights':weights,'output':attention_output(weights,projected['v'])}
