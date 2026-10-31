import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def tied_head(ids,embedding):
    if ids and isinstance(ids[0],list):
        batches=[tied_head(row,embedding) for row in ids]
        return {key:[batch[key] for batch in batches] for key in ('hidden','logits','probabilities')}
    hidden=[embedding[i][:] for i in ids]
    logits=[[dot(row,word) for word in embedding] for row in hidden]
    return {'hidden':hidden,'logits':logits,'probabilities':[softmax(row) for row in logits]}
