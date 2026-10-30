"""字符级词表与 UTF-8 教学实验，仅使用 Python 标准库。"""
import argparse
import json

# 与网页一致：这里的字符均指 Unicode 码点，不是字素簇。
VOCAB = ('<UNK>', 'A', '中', '🙂', 'e', '\u0301', ' ', '!')
CHAR_TO_ID = {char: index for index, char in enumerate(VOCAB) if index}


def encode_characters(text):
    return [CHAR_TO_ID.get(char, 0) for char in text]


def decode_characters(ids):
    return ''.join(VOCAB[index] for index in ids)


def inspect_text(text):
    """输入应为合法 Unicode 标量序列；孤立代理项明确拒绝。"""
    encoded = text.encode('utf-8')
    ids = encode_characters(text)
    return {
        'text': text,
        'codepoints': [f'U+{ord(char):04X}' for char in text],
        'codepoint_count': len(text),
        'utf8_hex': encoded.hex(' ').upper(),
        'byte_count': len(encoded),
        'utf8_roundtrip': encoded.decode('utf-8'),
        'ids': ids,
        'character_decoded': decode_characters(ids),
        'unknown': [char for char in text if char not in CHAR_TO_ID],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--text', help='自行输入一段文本；省略时运行四个示例')
    args = parser.parse_args()
    print('教学词表：', json.dumps(dict(enumerate(VOCAB)), ensure_ascii=False))
    samples = [args.text] if args.text is not None else ['A中🙂', 'e\u0301', 'A猫', '']
    for text in samples:
        print(json.dumps(inspect_text(text), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
