import math
import re
from collections import Counter
from tasteai_math import dot, matmul, softmax, identity

def character_tokenizer(train_text,text=None):
    text=train_text if text is None else text
    vocab=sorted(set(train_text))
    table={char:i for i,char in enumerate(vocab)}
    ids=[table.get(char,len(vocab)) for char in text]
    decoded=''.join(vocab[i] if i<len(vocab) else '[UNK]' for i in ids)
    return {'ids':ids,'pieces':list(text),'decoded':decoded,'vocab':vocab}
