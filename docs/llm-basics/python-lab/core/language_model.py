from tasteai_math import dot, matmul, softmax

def embedding_head(ids,embedding,head):
    if ids and isinstance(ids[0],list):
        batches=[embedding_head(row,embedding,head) for row in ids]
        return {key:[batch[key] for batch in batches] for key in ('hidden','logits','probabilities')}
    hidden=[embedding[i][:] for i in ids]
    logits=matmul(hidden,head)
    probabilities=[softmax(row) for row in logits]
    return {'hidden':hidden,'logits':logits,'probabilities':probabilities}

def tied_head(ids,embedding):
    if ids and isinstance(ids[0],list):
        batches=[tied_head(row,embedding) for row in ids]
        return {key:[batch[key] for batch in batches] for key in ('hidden','logits','probabilities')}
    hidden=[embedding[i][:] for i in ids]
    logits=[[dot(row,word) for word in embedding] for row in hidden]
    return {'hidden':hidden,'logits':logits,'probabilities':[softmax(row) for row in logits]}

def tiny_lm(ids,embedding,head):
    hidden=[embedding[i][:] for i in ids]
    dim=len(embedding[0])
    # 教学因果上下文层：前缀平均，避免把独立查表冒充语言模型。
    contextual=[[sum(hidden[j][d] for j in range(t+1))/(t+1) for d in range(dim)] for t in range(len(ids))]
    logits=matmul(contextual,head)
    return {'hidden':contextual,'logits':logits,'probabilities':[softmax(row) for row in logits]}

def generate_tokens(ids,embedding,head,steps):
    sequence=ids[:]
    selected=[]
    history=[]
    for _ in range(steps):
        result=tiny_lm(sequence,embedding,head)
        last=result['logits'][-1]
        token=max(range(len(last)),key=lambda i:last[i])
        sequence.append(token)
        selected.append(token)
        history.append(result['probabilities'][-1])
    return {'ids':sequence,'generated':selected,'probabilities':history}
