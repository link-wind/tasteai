# 基础知识配套实验

在仓库根目录运行，核心模型/数学实验复用 `.venv` 中的 PyTorch，不需要 GPU。模型是随机初始化的接口验证，不能当作已训练的语言模型。

```sh
.venv/bin/python labs/04-foundations/02-bpe-engineering.py
.venv/bin/python labs/04-foundations/03-transformer-lm.py
.venv/bin/python labs/04-foundations/04-attention.py
.venv/bin/python labs/04-foundations/05-position-rope.py
.venv/bin/python -m unittest discover -s tests -p 'test_foundations*.py'
```

| 课目 | 对应实验 | 核对点 |
| --- | --- | --- |
| GPT 系列 Tokenizer | 01-gpt-tokenizers.py | 固定版本三编码、IDs/字节、特殊 token |
| BPE 训练工程化 | 02-bpe-engineering.py | 全量/局部规则一致；访问计数不同 |
| 从 IDs 到 logits、Embedding/Head | 03-transformer-lm.py | [2,4]→[2,4,16]→[2,4,32]，标签移位/梯度/因果性 |
| Self-Attention/GQA、Sink | 04-attention.py | 三位置因果权重、分组映射、人工 softmax 示例 |
| 四课位置编码 | 05-position-rope.py | sinusoidal、二维旋转、参考/增量一致、KV 容量 |

## 可选的真实分词库与快照

```sh
.venv/bin/python -m pip install -r labs/04-foundations/requirements-tokenizer.txt
.venv/bin/python labs/04-foundations/01-gpt-tokenizers.py
```

固定版本为 tiktoken 0.12.0。首次 get_encoding 需要联网下载相应词表并缓存在本机；不需要 API 密钥，不调用模型 API。当前 Python 3.9 环境使用 LibreSSL，requests 的 urllib3 可能发出兼容性警告，本次采集成功，未屏蔽警告。

脚本生成 `tokenizer-samples.json` 与页面使用的 `docs/llm-basics/tokenizer-samples.js`。浏览器只展示这些实测固定样本，不实时运行完整 tokenizer。默认端到端测试读取已保存快照，即使未安装可选 tiktoken，也可进行字节拼接核对。

BPE 工程脚本同样生成 `engineering-counts.json` 与同目录网页快照 `engineering-counts.js`。记录访问和相邻位置检查数不是运行时间；局部实现多做旧/新直方图计算，不保证每种语料更快。

## 数学约定与精度

RoPE 按相邻维配对，输入布局 [B,H,T,d]，positions 为 [T]。如每个样本有不同 positions，需要显式准备正确的广播轴；不可直接把 [B,T] 当作本函数所有布局都支持的输入。函数构造 float64 角度后转回输入 dtype；测试同时使用独立复数参考与逐对参考。

TinyLM 不包含 padding 或 KV 存储接口；全序列/增量一致性测试针对 RoPE 旋转层及逻辑位置，不冒充完整模型缓存服务。Attention Sink 实验的 logits 是人为设置，不能证明真实训练中的 sink 行为。长度外推交互只计算坐标与资源，不评估真实模型长文能力。
