"""全量重计数与受影响样本局部更新：对照正确性与实际处理数。"""
from collections import Counter, defaultdict
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('reference_bpe',Path(__file__).parents[1]/'03-bpe-algorithm/01-byte-bpe.py')
bpe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bpe)


def train_counted(samples, incremental=False, budget=7):
    corpus = [{'text':text,'weight':weight,'ids':list(text.encode())} for text,weight in samples]
    counts, index = Counter(), defaultdict(set)
    stats = {'row_visits':0,'pair_checks':0}
    def histogram(row):
        stats['row_visits'] += 1
        stats['pair_checks'] += max(0,len(row['ids'])-1)
        return Counter(zip(row['ids'],row['ids'][1:]))
    if incremental:
        for i,row in enumerate(corpus):
            for pair,n in histogram(row).items():
                counts[pair] += n*row['weight']; index[pair].add(i)
    rules=[]
    for rank in range(budget+1):
        if not incremental:
            counts=Counter()
            for row in corpus:
                for pair,n in histogram(row).items(): counts[pair]+=n*row['weight']
        positive={p:n for p,n in counts.items() if n>0}
        if not positive or rank==budget: break
        pair=min(positive,key=lambda p:(-positive[p],p))
        rule={'pair':list(pair),'id':256+rank,'rank':rank,'count':positive[pair]}; rules.append(rule)
        affected=sorted(index[pair]) if incremental else range(len(corpus))
        for i in affected:
            row=corpus[i]
            if incremental:
                for old,n in histogram(row).items():
                    counts[old]-=n*row['weight'];index[old].discard(i)
            row['ids']=bpe.merge_pair(row['ids'],pair,rule['id'])
            if incremental:
                for new,n in histogram(row).items():
                    counts[new]+=n*row['weight'];index[new].add(i)
    return {'rules':rules,'corpus':corpus,'stats':stats}


if __name__=='__main__':
    result={}
    for name,samples in [('tiny',bpe.DEFAULT_CORPUS),('many_short_rows',bpe.DEFAULT_CORPUS+[('x',1)]*200)]:
        full=train_counted(samples);local=train_counted(samples,True)
        assert full['rules']==local['rules'] and full['corpus']==local['corpus']
        result[name]={'baseline':full['stats'],'local':local['stats'],'rules_equal':True}
    target=Path(__file__).parent/'engineering-counts.json';target.write_text(json.dumps(result,indent=2)+'\n')
    (Path(__file__).resolve().parents[2]/'docs/llm-basics/engineering-counts.js').write_text('/* 配套脚本实测处理计数；不是计时数据。 */\nwindow.EngineeringCounts = '+json.dumps(result,indent=2)+';\n')
    print(json.dumps(result,indent=2))
