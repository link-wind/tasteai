"""可手算的 UTF-8 字节级 BPE：独立加权样本，不含 GPT 预分词。"""
import argparse
from collections import Counter
import json

DEFAULT_CORPUS = [('low', 5), ('lower', 2), ('new', 4), ('newer', 1)]


def pair_counts(corpus):
    counts = Counter()
    for row in corpus:
        for pair in zip(row['ids'], row['ids'][1:]):
            counts[pair] += row['weight']
    return [{'pair': list(pair), 'count': count} for pair, count in
            sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def merge_pair(ids, pair, new_id):
    out, i = [], 0
    while i < len(ids):
        if i + 1 < len(ids) and (ids[i], ids[i + 1]) == tuple(pair):
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


def train(samples=DEFAULT_CORPUS, max_merges=7):
    if not isinstance(max_merges, int) or max_merges < 0:
        raise ValueError('max_merges 必须是非负整数')
    corpus = []
    for text, weight in samples:
        if not isinstance(weight, int) or weight <= 0:
            raise ValueError('样本权重必须是正整数')
        corpus.append({'text': text, 'weight': weight, 'ids': list(text.encode('utf-8'))})
    vocab = [bytes([i]) for i in range(256)]
    rules, states = [], []
    for turn in range(max_merges + 1):
        candidates = pair_counts(corpus)
        states.append({'corpus': corpus, 'candidates': candidates,
                       'total': sum(len(row['ids']) * row['weight'] for row in corpus)})
        if not candidates or turn == max_merges:
            break
        pair = candidates[0]['pair']
        new_id = len(vocab)
        vocab.append(vocab[pair[0]] + vocab[pair[1]])
        rules.append({'pair': pair, 'id': new_id, 'rank': turn, 'count': candidates[0]['count']})
        corpus = [dict(row, ids=merge_pair(row['ids'], pair, new_id)) for row in corpus]
    return {'vocab': vocab, 'rules': rules, 'states': states}


def encode(text, rules):
    ids = list(text.encode('utf-8'))
    steps = []
    by_pair = {tuple(rule['pair']): rule for rule in rules}
    while len(ids) >= 2:
        available = [by_pair[pair] for pair in zip(ids, ids[1:]) if pair in by_pair]
        if not available:
            break
        rule = min(available, key=lambda item: item['rank'])
        ids = merge_pair(ids, rule['pair'], rule['id'])
        steps.append({'pair': rule['pair'], 'id': rule['id'], 'rank': rule['rank'], 'ids': ids})
    return {'ids': ids, 'steps': steps}


def decode(ids, vocab):
    return b''.join(vocab[token] for token in ids).decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--merges', type=int, default=7)
    parser.add_argument('--text', default='lowest')
    args = parser.parse_args()
    model = train(max_merges=args.merges)
    print('语料：', DEFAULT_CORPUS)
    print('初始加权 token 总量：', model['states'][0]['total'])
    for rule, state in zip(model['rules'], model['states'][1:]):
        print(f"rank={rule['rank']} pair={rule['pair']} count={rule['count']} "
              f"new_id={rule['id']} bytes={model['vocab'][rule['id']]!r} total={state['total']}")
    result = encode(args.text, model['rules'])
    print(json.dumps({'text': args.text, **result, 'decoded': decode(result['ids'], model['vocab'])},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
