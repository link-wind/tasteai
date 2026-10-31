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

def rope_invariants(q,k,m,n,shift):
    qm,kn=rotate(q,m),rotate(k,n)
    shifted=dot(rotate(q,m+shift),rotate(k,n+shift))
    relative=dot(q,rotate(k,n-m))
    actual=dot(qm,kn)
    return {'before':[q,k],'after':[qm,kn], 'norm_error':abs(dot(q,q)-dot(qm,qm)),
            'shift_error':abs(actual-shifted),'relative_error':abs(actual-relative)}
