import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def byte_tokenizer(text):
    ids=list(text.encode('utf-8'))
    spans=[]
    start=0
    for char in text:
        size=len(char.encode('utf-8'))
        spans.append([start,start+size])
        start+=size
    return {'ids':ids,'spans':spans,'decoded':bytes(ids).decode('utf-8')}
