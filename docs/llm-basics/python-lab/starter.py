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
        # TODO：若当前项与下一项匹配 pair，写入 new_id 并跳过两项。
        # 否则保留当前项，前进一项。
        out.append(ids[i])
        i += 1
    return out
