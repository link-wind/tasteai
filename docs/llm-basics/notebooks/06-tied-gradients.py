"""PyTorch共享参数实验。安装: pip install torch
任务：补全build_tied，用同一Parameter绑定Embedding与LM Head，再验证梯度。
参考实现默认已给出，先注释赋值行自行完成。
"""
import torch
from torch import nn

def build_tied(vocab=5,dim=3):
    embedding=nn.Embedding(vocab,dim,dtype=torch.float64)
    head=nn.Linear(dim,vocab,bias=False,dtype=torch.float64)
    head.weight=embedding.weight
    return embedding,head

def verify():
    torch.manual_seed(7)
    embedding,head=build_tied()
    assert embedding.weight is head.weight
    weight=embedding.weight.detach().clone()
    ids=torch.tensor([0,2,0])
    loss=head(embedding(ids)).square().sum()
    loss.backward()
    shared=embedding.weight.grad.clone()
    # 拆开为独立参数，得到输入路径与输出路径的两份梯度。
    input_weight=weight.clone().requires_grad_()
    output_weight=weight.clone().requires_grad_()
    independent=torch.nn.functional.embedding(ids,input_weight) @ output_weight.T
    independent.square().sum().backward()
    assert torch.allclose(shared,input_weight.grad+output_weight.grad,atol=1e-10)
    optimizer=torch.optim.SGD(embedding.parameters(),lr=.001)
    optimizer.step()
    assert embedding.weight is head.weight
    assert not torch.equal(embedding.weight.detach(),weight)
    return {'parameter_identity':True,'gradient_sum_error':float((shared-input_weight.grad-output_weight.grad).abs().max()),'shared_after_update':True}

if __name__=='__main__':print(verify())
