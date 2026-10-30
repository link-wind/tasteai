"""相邻维配对 RoPE 与参考实现；输入末两维为 T,D。"""
import math
import torch


def rope(x, positions, base=10000.0):
    d=x.shape[-1]
    if d%2: raise ValueError('RoPE 配对维度必须为偶数')
    inv=base**(-torch.arange(0,d,2,dtype=torch.float64,device=x.device)/d)
    angles=positions.to(device=x.device,dtype=torch.float64)[...,None]*inv
    cos,sin=angles.cos().to(x.dtype),angles.sin().to(x.dtype)
    even,odd=x[...,0::2],x[...,1::2]
    return torch.stack((even*cos-odd*sin,even*sin+odd*cos),dim=-1).flatten(-2)


def rope_reference(x,positions,base=10000.0):
    out=torch.empty_like(x)
    for pair in range(x.shape[-1]//2):
        angle=positions.to(x.dtype)*base**(-2*pair/x.shape[-1])
        a,b=x[...,2*pair],x[...,2*pair+1]
        out[...,2*pair]=a*angle.cos()-b*angle.sin()
        out[...,2*pair+1]=a*angle.sin()+b*angle.cos()
    return out


def sinusoidal(positions,d=4,base=10000.0):
    inv=base**(-torch.arange(0,d,2,dtype=torch.float64)/d)
    angles=positions.to(torch.float64)[:,None]*inv
    return torch.stack((angles.sin(),angles.cos()),dim=-1).flatten(-2)


def kv_bytes(layers,batch,length,kv_heads,head_dim,bytes_per_element=2):
    return 2*layers*batch*length*kv_heads*head_dim*bytes_per_element


if __name__=='__main__':
    torch.manual_seed(7)
    x=torch.randn(1,2,5,4,dtype=torch.float64)
    y=rope(x,torch.arange(5))
    assert torch.allclose(y.norm(dim=-1),x.norm(dim=-1))
    assert torch.allclose(y,rope_reference(x,torch.arange(5)))
    print('sinusoidal(pos=0,1,d=4):',sinusoidal(torch.arange(2)).tolist())
    print('q=(1,2), position=1:',rope(torch.tensor([[1.,2.]]),torch.tensor([1])).tolist())
    print('KV MiB:',kv_bytes(24,1,4096,4,64)/2**20)
    print('norm/reference checks passed')
