from collections import Counter

def weighted_pairs(records):
    counts = Counter()
    for ids, weight in records:
        for left, right in zip(ids, ids[1:]):
            counts[(left, right)] += weight
    return [[a, b, n] for (a, b), n in sorted(counts.items()) if n]
