"""长上下文评估工具。安装: pip install torch transformers
默认--self-test只验证评估代码，不测模型能力。
真实评估: python 12-long-context-evaluation.py --model /path/to/local-causal-lm --samples evaluation.jsonl
JSONL每行: {"prompt":"...","answer":"...","length_bucket":"short/long"}
使用相同模型和数据比较不同设置；本工具不会替你修改模型RoPE配置。
"""
import argparse
import json
import math
import time

def aggregate(rows):
    groups={}
    for row in rows:groups.setdefault(row['length_bucket'],[]).append(row)
    return {key:{'samples':len(values),'exact_match':sum(v['exact_match'] for v in values)/len(values),
                 'answer_perplexity':math.exp(sum(v['answer_nll'] for v in values)/sum(v['answer_tokens'] for v in values)),
                 'mean_latency_seconds':sum(v['latency_seconds'] for v in values)/len(values)} for key,values in groups.items()}

def evaluate(model_path,samples_path,max_new_tokens):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True).eval()
    rows=[]
    for line in open(samples_path,encoding='utf-8'):
        item=json.loads(line);prompt=item['prompt'];answer=item['answer']
        # 分别编码后拼接，明确答案损失的token边界。
        prefix=tokenizer.encode(prompt,add_special_tokens=True)
        suffix=tokenizer.encode(answer,add_special_tokens=False)
        if not prefix or not suffix:raise ValueError('prompt和answer必须均有token')
        ids=torch.tensor([prefix+suffix]);labels=ids.clone();labels[:,:len(prefix)]=-100
        began=time.perf_counter()
        with torch.no_grad():
            loss=model(input_ids=ids,labels=labels).loss
            generated=model.generate(torch.tensor([prefix]),max_new_tokens=max_new_tokens,do_sample=False,pad_token_id=tokenizer.eos_token_id)
        prediction=tokenizer.decode(generated[0,len(prefix):],skip_special_tokens=True).strip()
        rows.append({'length_bucket':item['length_bucket'],'prompt_tokens':len(prefix),'answer_tokens':len(suffix),
                     'answer_nll':float(loss)*len(suffix),'exact_match':prediction==answer.strip(),'prediction':prediction,
                     'latency_seconds':time.perf_counter()-began})
    if not rows:raise ValueError('评估集为空')
    return {'model':model_path,'rows':rows,'summary':aggregate(rows)}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--model');parser.add_argument('--samples');parser.add_argument('--max-new-tokens',type=int,default=32);parser.add_argument('--self-test',action='store_true');a=parser.parse_args()
    if a.self_test:
        rows=[dict(length_bucket='fixture',exact_match=True,answer_nll=2,answer_tokens=2,latency_seconds=.1),dict(length_bucket='fixture',exact_match=False,answer_nll=2,answer_tokens=2,latency_seconds=.2)]
        result=aggregate(rows);assert result['fixture']['exact_match']==.5;assert abs(result['fixture']['answer_perplexity']-math.e)<1e-12
        print('评估器自检通过；未运行真实模型，不能据此判断长上下文质量。')
    elif a.model and a.samples:print(json.dumps(evaluate(a.model,a.samples,a.max_new_tokens),ensure_ascii=False,indent=2))
    else:parser.error('指定--self-test，或同时指定--model和--samples')
