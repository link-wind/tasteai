"""真实GPT tokenizer对比。安装: pip install tiktoken
首次获取编码词表需要网络；表中数字为实际编码结果，不是教学正则估计。
"""
import argparse
import json
import tiktoken

def compare(text):
    output=[]
    for name in ('cl100k_base','o200k_base'):
        encoding=tiktoken.get_encoding(name)
        ids=encoding.encode(text,disallowed_special=())
        assert encoding.decode(ids)==text
        pieces=[encoding.decode_single_token_bytes(i).hex(' ') for i in ids]
        output.append({'encoding':name,'count':len(ids),'ids':ids,'token_bytes':pieces})
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--text',default='Hello，世界！1234567 🙂');args=parser.parse_args()
    print(json.dumps(compare(args.text),ensure_ascii=False,indent=2))
