"""采集固定 tiktoken 实测样本；首次 get_encoding 会下载并缓存词表。"""
from importlib.metadata import version
import json
from pathlib import Path
import tiktoken

SAMPLES = ['Hello, world!', 'hello', ' hello', '你好，世界！', 'A中🙂', '1234567890', '<|endoftext|>']


def collect():
    output = {'library': 'tiktoken', 'version': version('tiktoken'), 'checked_at': '2026-10-29', 'samples': []}
    for text in SAMPLES:
        row = {'text': text, 'encodings': []}
        for name in ['r50k_base', 'cl100k_base', 'o200k_base']:
            enc = tiktoken.get_encoding(name)
            ids = enc.encode(text, disallowed_special=())
            chunks = [enc.decode_single_token_bytes(i) for i in ids]
            assert b''.join(chunks).decode('utf-8') == text
            row['encodings'].append({'name': name, 'ids': ids, 'count': len(ids),
                                     'hex': [part.hex(' ').upper() for part in chunks]})
        output['samples'].append(row)
    enc = tiktoken.get_encoding('cl100k_base')
    try:
        enc.encode('<|endoftext|>')
    except ValueError:
        output['special_default'] = 'ValueError'
    output['special_allowed'] = enc.encode('<|endoftext|>', allowed_special={'<|endoftext|>'})
    return output


if __name__ == '__main__':
    data = collect()
    root = Path(__file__).resolve().parents[2]
    dest = root/'docs/llm-basics/tokenizer-samples.js'
    dest.write_text('/* 固定版本实测快照；不执行远程分词。 */\nwindow.TokenizerSamples = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
    (Path(__file__).parent/'tokenizer-samples.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('tiktoken',data['version'],'样本数',len(data['samples']))
    for row in data['samples']:
        print(repr(row['text']),[(r['name'],r['count'],r['ids']) for r in row['encodings']])
