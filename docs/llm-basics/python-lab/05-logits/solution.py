def project_logits(hidden, weight):
    return [[sum(a * b for a, b in zip(h, w)) for w in weight] for h in hidden]
