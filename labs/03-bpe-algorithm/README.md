# BPE 算法详解：配套实验

Python 3.9+，实验运行只需标准库。在仓库根目录执行：

```sh
python3 labs/03-bpe-algorithm/01-byte-bpe.py
python3 labs/03-bpe-algorithm/01-byte-bpe.py --merges 2 --text lower
python3 labs/03-bpe-algorithm/01-byte-bpe.py --merges 6 --text 'A中🙂'
python3 -m unittest discover -s tests -p 'test_bpe*.py'
```

测试中的 Python/JS 对照会调用工作区的 Node.js；实验脚本自身不需要 Node。

固定样本为 low×5、lower×2、new×4、newer×1。样本之间不跨界统计；以全部 256 个单字节为基础，按当前相邻 token 对统计加权频次。并列时按整数对升序选择；左到右非重叠替换。

预期新增 token：256=lo、257=low、258=ew、259=new、260=er、261=lower、262=newer。对应频次为 7、7、5、5、3、2、1；初始及每轮加权 token 总量为 42、35、28、23、18、15、13、12。

两轮后 lower 编码为 [257,101,114]。六轮后 lowest 编码为 [257,101,115,116]；A中🙂 保留基础字节 [65,228,184,173,240,159,153,130]，拼接后可恢复原文。

编码只使用已经学到的规则，按 rank 优先级合并；不会按新文本的频次重新训练。解码先拼接完整字节再按 UTF-8 严格解码；单个 token 的字节不一定独立合法。Python 对孤立代理项报错；网页 TextEncoder 会替换并给出提示。

这是教学 tokenizer，没有真实 GPT 预分词、特殊 token 规则与生产优化，不等同于 tiktoken。
