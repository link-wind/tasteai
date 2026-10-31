import math

def causal_gqa(q, k, v, position):
    group = len(q) // len(k)
    output = []
    for head, query in enumerate(q):
        kv = head // group
        scores = [sum(a*b for a,b in zip(query, key)) / math.sqrt(len(query)) for key in k[kv][:position+1]]
        peak = max(scores)
        weights = [math.exp(s - peak) for s in scores]
        total = sum(weights)
        output.append([sum(weights[t] * v[kv][t][d] for t in range(len(weights))) / total for d in range(len(query))])
    return output
