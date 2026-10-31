import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def tiny_lm(ids,embedding,head):
    hidden=[embedding[i][:] for i in ids]
    dim=len(embedding[0])
    # 教学因果上下文层：前缀平均，避免把独立查表冒充语言模型。
    contextual=[[sum(hidden[j][d] for j in range(t+1))/(t+1) for d in range(dim)] for t in range(len(ids))]
    logits=matmul(contextual,head)
    return {'hidden':contextual,'logits':logits,'probabilities':[softmax(row) for row in logits]}
