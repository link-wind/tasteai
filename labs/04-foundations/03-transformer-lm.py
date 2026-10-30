"""CPU 可运行的两层 GQA+RoPE decoder-only LM，无 dropout，仅验证接口。"""
import importlib.util
import math
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F


def load(name,filename):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parent/filename)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

position=load('position_math','05-position-rope.py')
att=load('attention_math','04-attention.py')


class RMSNorm(nn.Module):
    def __init__(self,d,eps=1e-6):
        super().__init__();self.weight=nn.Parameter(torch.ones(d));self.eps=eps
    def forward(self,x):
        return x*torch.rsqrt(x.square().mean(-1,keepdim=True)+self.eps)*self.weight


class Block(nn.Module):
    def __init__(self,d=16,heads=4,kv_heads=2,hidden=32):
        super().__init__();self.heads=heads;self.kv_heads=kv_heads;self.dh=d//heads
        self.norm1=RMSNorm(d);self.norm2=RMSNorm(d)
        self.wq=nn.Linear(d,heads*self.dh,bias=False)
        self.wk=nn.Linear(d,kv_heads*self.dh,bias=False);self.wv=nn.Linear(d,kv_heads*self.dh,bias=False)
        self.wo=nn.Linear(d,d,bias=False)
        self.gate=nn.Linear(d,hidden,bias=False);self.up=nn.Linear(d,hidden,bias=False);self.down=nn.Linear(hidden,d,bias=False)
    def forward(self,x):
        b,t,d=x.shape;norm=self.norm1(x)
        q=self.wq(norm).view(b,t,self.heads,self.dh).transpose(1,2)
        k=self.wk(norm).view(b,t,self.kv_heads,self.dh).transpose(1,2)
        v=self.wv(norm).view(b,t,self.kv_heads,self.dh).transpose(1,2)
        pos=torch.arange(t,device=x.device)
        q=position.rope(q,pos);k=position.rope(k,pos)
        context,_=att.attention(q,k,v)
        x=x+self.wo(context.transpose(1,2).contiguous().view(b,t,d))
        norm=self.norm2(x)
        return x+self.down(F.silu(self.gate(norm))*self.up(norm))


class TinyLM(nn.Module):
    def __init__(self,vocab=32,d=16,layers=2):
        super().__init__();self.embedding=nn.Embedding(vocab,d)
        self.blocks=nn.ModuleList([Block(d=d) for _ in range(layers)])
        self.norm=RMSNorm(d)
    def forward(self,ids):
        x=self.embedding(ids)
        for block in self.blocks:x=block(x)
        return F.linear(self.norm(x),self.embedding.weight)


def next_token_loss(logits,ids):
    return F.cross_entropy(logits[:,:-1].reshape(-1,logits.shape[-1]),ids[:,1:].reshape(-1))


if __name__=='__main__':
    torch.manual_seed(7);torch.set_num_threads(1)
    model=TinyLM();ids=torch.tensor([[1,2,3,4],[5,6,7,8]])
    logits=model(ids);loss=next_token_loss(logits,ids);loss.backward()
    changed=ids.clone();changed[:,-1]=9
    with torch.no_grad():assert torch.allclose(model(ids)[:,:-1],model(changed)[:,:-1])
    print('IDs:',tuple(ids.shape),'Embedding:',tuple(model.embedding(ids).shape),'logits:',tuple(logits.shape))
    print('shifted targets:',ids[:,1:].tolist(),'loss:',round(loss.item(),6))
    print('finite gradients:',all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters()))
    print('causal prefix invariance passed')
