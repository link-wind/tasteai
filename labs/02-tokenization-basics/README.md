# Tokenization 基础实验

在仓库根目录运行（Python 3.9+，无需新包）：

```sh
python3 labs/02-tokenization-basics/01-character-and-utf8.py
python3 labs/02-tokenization-basics/01-character-and-utf8.py --text 'A猫'
python3 -m unittest discover -s tests -p 'test_tokenization_basics*.py'
```

默认输出四例：`A中🙂` 是 3 码点、8 字节；组合重音 `e\u0301` 是 2 码点、3 字节；`A猫` 的字符编号是 `[1, 0]`，字符解码为 `A<UNK>`；空文本产生空编号序列和零计数。UTF-8 对这些输入均无损往返。输入孤立代理项将明确抛出 UnicodeEncodeError，不静默替换；浏览器 TextEncoder 的替换行为见网页边界说明。

固定词表与网页一致。所有编号只是教学示例，不代表 GPT tokenizer 的结果。
