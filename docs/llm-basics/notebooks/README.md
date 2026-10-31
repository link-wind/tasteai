# 课程配套Notebook

网页算法用Python标准库运行；这里的Notebook和脚本需在本地Python环境运行。每份Notebook有待完成函数、验证和最后的参考实现。先完成TODO，再执行验证；运行所有单元前需处理初始NotImplementedError。

## 第03课：真实GPT tokenizer

安装 `pip install tiktoken`，运行 `python 03-real-tokenizers.py --text 'Hello，世界！1234567 🙂'`。首次载入词表需要网络。输出真实cl100k_base/o200k_base的ID、逐token字节和数量，并核对解码往返。单个token字节不保证构成完整UTF-8字符。

## 第06课：共享参数与梯度

安装 `pip install torch`，运行 `python 06-tied-gradients.py`。验证相同Parameter身份、输入路径与输出路径的梯度相加、优化器更新后仍然共享。Notebook将build_tied留作实现目标。

## 第12课：长上下文评估

安装 `pip install torch transformers`。`python 12-long-context-evaluation.py --self-test` 只检查指标聚合，不运行模型。

真实评估使用本地已下载的因果语言模型：

```sh
python 12-long-context-evaluation.py --model /path/to/local-model --samples retrieval-evaluation.jsonl --max-new-tokens 16
```

提供的6条样例覆盖两种记录数、三个目标位置，用于跑通流程。它们不构成长上下文能力基准；记录数不是token数。可以生成更长数据：

```sh
python 12-make-retrieval-set.py --records 1024 4096 > longer-evaluation.jsonl
```

根据模型上下文容量选择长度。评估器报告实际prompt token数、答案token困惑度、严格匹配率、样本量和平均耗时（loss+生成）。若要比较位置插值前后，分别加载对应配置的本地模型，使用同一数据集；工具不会自动替模型修改RoPE配置。完整模型能力还应覆盖其他任务及短上下文退化，不能由本检索任务单独判断。
