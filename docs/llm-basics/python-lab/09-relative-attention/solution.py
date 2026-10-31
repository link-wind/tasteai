import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def relative_attention(x,slope):
    scores=[]
    weights=[]
    for i,q in enumerate(x):
        row=[dot(q,k)/math.sqrt(len(q))-slope*abs(i-j) if j<=i else -math.inf for j,k in enumerate(x)]
        scores.append([v if math.isfinite(v) else None for v in row])
        weights.append(softmax(row))
    return {'scores':scores,'weights':weights,'output':matmul(weights,x)}
