import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def rotate(vector,position,base=10000):
    output=[]
    for i in range(len(vector)//2):
        angle=position/base**(2*i/len(vector))
        c,s=math.cos(angle),math.sin(angle)
        a,b=vector[2*i:2*i+2]
        output.extend([a*c-b*s,a*s+b*c])
    return output

def multihead_rope(tokens,offset=0):
    return [[[rotate(head,offset+t) for head in heads] for t,heads in enumerate(batch)] for batch in tokens]

def rope_offset_check(tokens,offset,split):
    full=multihead_rope(tokens,offset)
    prefix=multihead_rope([batch[:split] for batch in tokens],offset)
    suffix=multihead_rope([batch[split:] for batch in tokens],offset+split)
    incremental=[a+b for a,b in zip(prefix,suffix)]
    error=max(abs(a-b) for batch,other in zip(full,incremental) for t,u in zip(batch,other) for h,k in zip(t,u) for a,b in zip(h,k))
    return {'after':full,'incremental':incremental,'error':error,'positions':list(range(offset,offset+len(tokens[0])))}
