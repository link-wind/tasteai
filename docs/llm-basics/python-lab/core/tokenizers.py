import re
from collections import Counter

def character_tokenizer(train_text,text=None):
    text=train_text if text is None else text
    vocab=sorted(set(train_text))
    table={char:i for i,char in enumerate(vocab)}
    ids=[table.get(char,len(vocab)) for char in text]
    decoded=''.join(vocab[i] if i<len(vocab) else '[UNK]' for i in ids)
    return {'ids':ids,'pieces':list(text),'decoded':decoded,'vocab':vocab}

def byte_tokenizer(text):
    ids=list(text.encode('utf-8'))
    spans=[]
    start=0
    for char in text:
        size=len(char.encode('utf-8'))
        spans.append([start,start+size])
        start+=size
    return {'ids':ids,'spans':spans,'decoded':bytes(ids).decode('utf-8')}

def pair_counts(records):
    counts=Counter()
    for ids,weight in records:
        if weight<0:raise ValueError('权重不能为负数')
        if weight==0:continue
        for pair in zip(ids,ids[1:]):
            counts[pair]+=weight
    return counts

def merge_tokens(ids,pair,new_id):
    output=[]
    i=0
    while i<len(ids):
        if i+1<len(ids) and tuple(ids[i:i+2])==tuple(pair):
            output.append(new_id)
            i+=2
        else:
            output.append(ids[i])
            i+=1
    return output

def train_bpe(corpus,steps):
    records=[(list(text.encode('utf-8')),weight) for text,weight in corpus]
    merges=[]
    totals=[sum(len(ids)*w for ids,w in records)]
    for rank in range(steps):
        counts=pair_counts(records)
        if not counts:break
        pair=min(counts,key=lambda pair:(-counts[pair],pair))
        new_id=256+rank
        records=[(merge_tokens(ids,pair,new_id),w) for ids,w in records]
        merges.append([*pair,new_id])
        totals.append(sum(len(ids)*w for ids,w in records))
    return {'merges':merges,'totals':totals,'records':[ids for ids,w in records]}

def encode_bpe(text,merges):
    ids=list(text.encode('utf-8'))
    vocab={i:bytes([i]) for i in range(256)}
    for a,b,new_id in merges:
        vocab[new_id]=vocab[a]+vocab[b]
    ranks={(a,b):(rank,new_id) for rank,(a,b,new_id) in enumerate(merges)}
    while len(ids)>1:
        candidates=[(ranks[pair][0],pair) for pair in zip(ids,ids[1:]) if pair in ranks]
        if not candidates:break
        _,pair=min(candidates)
        ids=merge_tokens(ids,pair,ranks[pair][1])
    decoded=b''.join(vocab[i] for i in ids).decode('utf-8')
    return {'ids':ids,'pieces':[vocab[i].hex(' ') for i in ids],'decoded':decoded}

def pretokenized_bpe(text,merges):
    # 教学预分词：字母、最多3位数字、空白、其余单字符。
    parts=re.findall(r'[A-Za-z]+|[0-9]{1,3}|\s+|[^A-Za-z0-9\s]',text)
    encoded=[encode_bpe(part,merges) for part in parts]
    return {'parts':parts,'ids':[i for row in encoded for i in row['ids']],
            'pieces':[piece for row in encoded for piece in row['pieces']],
            'decoded':''.join(row['decoded'] for row in encoded)}

def train_local_bpe(corpus,steps):
    records=[(list(text.encode('utf-8')),weight) for text,weight in corpus]
    counts=pair_counts(records)
    index={}
    def index_row(row_id,ids,add):
        for pair in set(zip(ids,ids[1:])):
            if add:index.setdefault(pair,set()).add(row_id)
            elif pair in index:
                index[pair].discard(row_id)
    for row_id,(ids,_) in enumerate(records):index_row(row_id,ids,True)
    merges=[]
    totals=[sum(len(ids)*w for ids,w in records)]
    touched=[]
    for rank in range(steps):
        candidates=[pair for pair,n in counts.items() if n>0]
        if not candidates:break
        pair=min(candidates,key=lambda p:(-counts[p],p))
        affected=sorted(index.get(pair,set()))
        touched.append(len(affected))
        new_id=256+rank
        for row_id in affected:
            ids,weight=records[row_id]
            counts.subtract(pair_counts([(ids,weight)]))
            index_row(row_id,ids,False)
            ids=merge_tokens(ids,pair,new_id)
            records[row_id]=(ids,weight)
            counts.update(pair_counts([(ids,weight)]))
            index_row(row_id,ids,True)
        merges.append([*pair,new_id])
        totals.append(sum(len(ids)*w for ids,w in records))
    return {'merges':merges,'totals':totals,'records':[ids for ids,w in records], 'touched':touched}
