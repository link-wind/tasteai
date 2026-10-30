"""因果缩放点积注意力与 GQA；人为分数用于 sink 几何示意。"""
import math
import torch


def attention(q,k,v,causal=True):
    if q.shape[-3]%k.shape[-3]: raise ValueError('查询头数必须是 KV 头数的整数倍')
    repeat=q.shape[-3]//k.shape[-3]
    k=k.repeat_interleave(repeat,dim=-3);v=v.repeat_interleave(repeat,dim=-3)
    scores=q@k.transpose(-1,-2)/math.sqrt(q.shape[-1])
    if causal:
        # 本函数是等长训练/前向示例；增量 cache 的绝对位置遮罩另行构造。
        if q.shape[-2]!=k.shape[-2]: raise ValueError('此教学因果路径要求 Q/K 等长')
        mask=torch.ones(scores.shape[-2:],dtype=torch.bool,device=q.device).triu(1)
        scores=scores.masked_fill(mask,float('-inf'))
    weights=scores.softmax(dim=-1)
    return weights@v,weights


if __name__=='__main__':
    q=torch.tensor([[[[1.,0.],[0.,1.],[1.,1.]]]])
    out,weights=attention(q,q,q)
    print('causal weights:',weights.tolist())
    logits=torch.tensor([3.,1.,0.,2.],dtype=torch.float64)
    print('人为 sink 分数 softmax:',logits.softmax(0).tolist())
    print('移除首位置再归一化:',logits[1:].softmax(0).tolist())
