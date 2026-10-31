import math

def position_vector(position, dim, base=10000):
    result = []
    for i in range(dim // 2):
        angle = position / base ** (2 * i / dim)
        result.extend([math.sin(angle), math.cos(angle)])
    return result
