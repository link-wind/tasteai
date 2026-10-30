from collections import Counter


def count_pairs(corpus):
    counts = Counter()
    for row in corpus:
        for pair in zip(row["ids"], row["ids"][1:]):
            counts[pair] += row["weight"]
    return counts


def merge_pair(ids, pair, new_id):
    """左到右合并；每个输入位置最多使用一次。"""
    out = []
    i = 0
    while i < len(ids):
        if i + 1 < len(ids) and (ids[i], ids[i + 1]) == tuple(pair):
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out
