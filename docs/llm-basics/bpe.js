/* 独立字节级 BPE 内核：浏览器与 Node 使用同一份实现。 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.ByteBPE = factory();
})(typeof window !== 'undefined' ? window : this, function () {
  'use strict';
  const defaultCorpus = [['low', 5], ['lower', 2], ['new', 4], ['newer', 1]];
  function pairCounts(corpus) {
    const counts = new Map();
    for (const row of corpus) {
      for (let i = 0; i + 1 < row.ids.length; i++) {
        const pair = [row.ids[i], row.ids[i + 1]], key = pair.join(',');
        const entry = counts.get(key) || {pair, count: 0};
        entry.count += row.weight; counts.set(key, entry);
      }
    }
    return Array.from(counts.values()).sort((a, b) => b.count - a.count || a.pair[0] - b.pair[0] || a.pair[1] - b.pair[1]);
  }
  function mergePair(ids, pair, newId) {
    const out = [];
    for (let i = 0; i < ids.length;) {
      if (i + 1 < ids.length && ids[i] === pair[0] && ids[i + 1] === pair[1]) { out.push(newId); i += 2; }
      else { out.push(ids[i]); i++; }
    }
    return out;
  }
  function train(samples = defaultCorpus, maxMerges = 7) {
    if (!Number.isInteger(maxMerges) || maxMerges < 0) throw new Error('maxMerges 必须是非负整数');
    let corpus = samples.map(([text, weight]) => {
      if (!Number.isInteger(weight) || weight <= 0) throw new Error('样本权重必须是正整数');
      return {text, weight, ids: Array.from(new TextEncoder().encode(text))};
    });
    const vocab = Array.from({length: 256}, (_, i) => [i]), rules = [], states = [];
    for (let turn = 0; turn <= maxMerges; turn++) {
      const candidates = pairCounts(corpus);
      states.push({corpus, candidates, total: corpus.reduce((n, row) => n + row.ids.length * row.weight, 0)});
      if (!candidates.length || turn === maxMerges) break;
      const pair = candidates[0].pair, id = vocab.length;
      vocab.push([...vocab[pair[0]], ...vocab[pair[1]]]);
      rules.push({pair, id, rank: turn, count: candidates[0].count});
      corpus = corpus.map(row => ({...row, ids: mergePair(row.ids, pair, id)}));
    }
    return {vocab, rules, states};
  }
  function encode(text, rules) {
    let ids = Array.from(new TextEncoder().encode(text));
    const steps = [], byPair = new Map(rules.map(rule => [rule.pair.join(','), rule]));
    while (ids.length >= 2) {
      let choice = null;
      for (let i = 0; i + 1 < ids.length; i++) {
        const rule = byPair.get([ids[i], ids[i + 1]].join(','));
        if (rule && (!choice || rule.rank < choice.rank)) choice = rule;
      }
      if (!choice) break;
      ids = mergePair(ids, choice.pair, choice.id);
      steps.push({pair: choice.pair, id: choice.id, rank: choice.rank, ids});
    }
    return {ids, steps};
  }
  function decode(ids, vocab) {
    return new TextDecoder('utf-8', {fatal: true}).decode(new Uint8Array(ids.flatMap(id => vocab[id])));
  }
  return {defaultCorpus, pairCounts, mergePair, train, encode, decode};
});
