import math

def apply_rope(tokens, offset=0, base=10000):
    output = []
    for t, heads in enumerate(tokens):
        rotated_heads = []
        for vector in heads:
            dim = len(vector)
            out = []
            for i in range(dim // 2):
                angle = (offset+t) / base ** (2*i/dim)
                c, s = math.cos(angle), math.sin(angle)
                x, y = vector[2*i:2*i+2]
                out.extend([x*c-y*s, x*s+y*c])
            rotated_heads.append(out)
        output.append(rotated_heads)
    return output
