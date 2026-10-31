"""生成可复现的检索评估集。记录数不是token数，真实token长度由评估器报告。"""
import argparse
import json
import random

def make_samples(sizes=(16,64),seed=42):
    rng=random.Random(seed)
    samples=[]
    for size in sizes:
        if size<2:raise ValueError('记录数至少2')
        for ratio in (.1,.5,.9):
            target=min(size-1,int(size*ratio))
            answer=str(rng.randrange(100000,999999))
            records=[f'记录{i:05d}的验证码是{rng.randrange(100000,999999)}。' for i in range(size)]
            records[target]=f'记录{target:05d}的验证码是{answer}。'
            prompt='阅读以下记录，最后仅回答指定记录的六位验证码，不要添加其他文字。\n'+'\n'.join(records)+f'\n问题：记录{target:05d}的验证码是什么？\n答案：'
            samples.append({'prompt':prompt,'answer':answer,'length_bucket':f'records-{size}/position-{ratio}'})
    return samples

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--records',type=int,nargs='+',default=[16,64]);a=p.parse_args()
    for sample in make_samples(a.records):print(json.dumps(sample,ensure_ascii=False))
