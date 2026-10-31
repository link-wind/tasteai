import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def rope_attention(x,offset=0,scale=1):
    q=[rotate(row,(offset+t)/scale) for t,row in enumerate(x)]
    k=[rotate(row,(offset+t)/scale) for t,row in enumerate(x)]
    weights=[]
    for i,query in enumerate(q):
        weights.append(softmax([dot(query,key)/math.sqrt(len(query)) if j<=i else -math.inf for j,key in enumerate(k)]))
    return {'before':x,'after':q,'weights':weights,'output':matmul(weights,x)}

def rotate(vector,position,base=10000):
    output=[]
    for i in range(len(vector)//2):
        angle=position/base**(2*i/len(vector))
        c,s=math.cos(angle),math.sin(angle)
        a,b=vector[2*i:2*i+2]
        output.extend([a*c-b*s,a*s+b*c])
    return output

def scaled_cache_attention(x,scale,offset=0):
    if scale<=0:raise ValueError('scale必须大于0')
    keys=[]
    values=[]
    output=[]
    for t,row in enumerate(x):
        query=rotate(row,(offset+t)/scale)
        keys.append(rotate(row,(offset+t)/scale))
        values.append(row[:])
        weights=softmax([dot(query,key)/math.sqrt(len(row)) for key in keys])
        output.append(matmul([weights],values)[0])
    full=rope_attention(x,offset,scale)['output']
    return {'full':full,'incremental':output,'error':max(abs(a-b) for r,s in zip(full,output) for a,b in zip(r,s)),
            'positions':[(offset+t)/scale for t in range(len(x))]}
