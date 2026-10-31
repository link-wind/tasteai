import math

def rotate_plane(vector, position, frequency):
    angle = position * frequency
    c, s = math.cos(angle), math.sin(angle)
    x, y = vector
    return [x*c-y*s, x*s+y*c]
