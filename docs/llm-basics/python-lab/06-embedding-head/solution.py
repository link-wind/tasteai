import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def embedding_head(ids,embedding,head):
    if ids and isinstance(ids[0],list):
        batches=[embedding_head(row,embedding,head) for row in ids]
        return {key:[batch[key] for batch in batches] for key in ('hidden','logits','probabilities')}
    hidden=[embedding[i][:] for i in ids]
    logits=matmul(hidden,head)
    probabilities=[softmax(row) for row in logits]
    return {'hidden':hidden,'logits':logits,'probabilities':probabilities}
