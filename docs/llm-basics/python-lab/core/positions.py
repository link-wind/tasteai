import math
from tasteai_math import dot, matmul, softmax, identity

def sinusoidal_attention(x,base=10000):
    dim=len(x[0])
    encoding=[]
    for position in range(len(x)):
        row=[]
        for i in range(dim//2):
            angle=position/base**(2*i/dim)
            row.extend([math.sin(angle),math.cos(angle)])
        encoding.append(row)
    augmented=[[a+b for a,b in zip(row,pos)] for row,pos in zip(x,encoding)]
    result=self_attention(augmented,identity(dim),identity(dim),identity(dim),True)
    return {'encoding':encoding,'weights':result['weights'],'output':result['output']}

def relative_attention(x,slope):
    scores=[]
    weights=[]
    for i,q in enumerate(x):
        row=[dot(q,k)/math.sqrt(len(q))-slope*abs(i-j) if j<=i else -math.inf for j,k in enumerate(x)]
        scores.append([v if math.isfinite(v) else None for v in row])
        weights.append(softmax(row))
    return {'scores':scores,'weights':weights,'output':matmul(weights,x)}

def rotate(vector,position,base=10000):
    output=[]
    for i in range(len(vector)//2):
        angle=position/base**(2*i/len(vector))
        c,s=math.cos(angle),math.sin(angle)
        a,b=vector[2*i:2*i+2]
        output.extend([a*c-b*s,a*s+b*c])
    return output

def rope_attention(x,offset=0,scale=1):
    q=[rotate(row,(offset+t)/scale) for t,row in enumerate(x)]
    k=[rotate(row,(offset+t)/scale) for t,row in enumerate(x)]
    weights=[]
    for i,query in enumerate(q):
        weights.append(softmax([dot(query,key)/math.sqrt(len(query)) if j<=i else -math.inf for j,key in enumerate(k)]))
    return {'before':x,'after':q,'weights':weights,'output':matmul(weights,x)}

def rope_invariants(q,k,m,n,shift):
    qm,kn=rotate(q,m),rotate(k,n)
    shifted=dot(rotate(q,m+shift),rotate(k,n+shift))
    relative=dot(q,rotate(k,n-m))
    actual=dot(qm,kn)
    return {'before':[q,k],'after':[qm,kn], 'norm_error':abs(dot(q,q)-dot(qm,qm)),
            'shift_error':abs(actual-shifted),'relative_error':abs(actual-relative)}

def multihead_rope(tokens,offset=0):
    return [[[rotate(head,offset+t) for head in heads] for t,heads in enumerate(batch)] for batch in tokens]

def rope_offset_check(tokens,offset,split):
    full=multihead_rope(tokens,offset)
    prefix=multihead_rope([batch[:split] for batch in tokens],offset)
    suffix=multihead_rope([batch[split:] for batch in tokens],offset+split)
    incremental=[a+b for a,b in zip(prefix,suffix)]
    error=max(abs(a-b) for batch,other in zip(full,incremental) for t,u in zip(batch,other) for h,k in zip(t,u) for a,b in zip(h,k))
    return {'after':full,'incremental':incremental,'error':error,'positions':list(range(offset,offset+len(tokens[0])))}

def interpolated_attention(x,scale):
    if scale<=0:raise ValueError('scale必须大于0')
    original=rope_attention(x)
    scaled=rope_attention(x,scale=scale)
    return {'weights':scaled['weights'],'original_weights':original['weights'],
            'output':scaled['output'],'positions':[i/scale for i in range(len(x))], 'after':scaled['after']}

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
