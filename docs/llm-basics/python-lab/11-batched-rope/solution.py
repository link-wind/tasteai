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
