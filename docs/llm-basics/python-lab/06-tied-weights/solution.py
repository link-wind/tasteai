def tied_logits(ids, embedding):
    hidden = [embedding[i] for i in ids]
    return [[sum(a * b for a, b in zip(h, row)) for row in embedding] for h in hidden]
