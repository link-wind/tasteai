"""已提供的矩阵工具；算法目标在各实验中实现。仅用于小规模教学。"""
import math

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def transpose(a):
    return [list(row) for row in zip(*a)]

def matmul(a,b):
    return [[dot(row,col) for col in transpose(b)] for row in a]

def softmax(row):
    maximum=max(row)
    values=[math.exp(x-maximum) for x in row]
    return [x/sum(values) for x in values]

def identity(n):
    return [[float(i==j) for j in range(n)] for i in range(n)]

import math
import re
from collections import Counter


def rotate(vector,position,base=10000):
    output=[]
    for i in range(len(vector)//2):
        angle=position/base**(2*i/len(vector))
        c,s=math.cos(angle),math.sin(angle)
        a,b=vector[2*i:2*i+2]
        output.extend([a*c-b*s,a*s+b*c])
    return output

def rope_invariants(q,k,m,n,shift):
    qm,kn=rotate(q,m),rotate(k,n)
    shifted=dot(rotate(q,m+shift),rotate(k,n+shift))
    relative=dot(q,rotate(k,n-m))
    actual=dot(qm,kn)
    return {'before':[q,k],'after':[qm,kn], 'norm_error':abs(dot(q,q)-dot(qm,qm)),
            'shift_error':abs(actual-shifted),'relative_error':abs(actual-relative)}

if __name__ == "__main__":
    print(rope_invariants(*[[1, 2], [3, 4], 2, 5, 7]))
