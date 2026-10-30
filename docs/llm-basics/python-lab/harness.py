"""浏览器与 CPython 共用的学习验证器；不是考试防作弊系统。"""
from contextlib import redirect_stdout, redirect_stderr
import json
import traceback

SCENARIOS = {
    "standard": [("low", 5), ("lower", 2), ("new", 4), ("newer", 1)],
    "overlap": [("aaa", 2), ("aaaaa", 1)],
}


class BoundedOutput:
    def __init__(self, limit=12000):
        self.parts = []
        self.left = limit
        self.truncated = False

    def write(self, text):
        text = str(text)
        self.parts.append(text[:self.left]) if self.left else None
        if len(text) > self.left:
            self.truncated = True
        self.left = max(0, self.left - len(text))
        return len(text)

    def flush(self):
        pass

    def getvalue(self):
        return "".join(self.parts) + ("\n…输出已截断。" if self.truncated else "")


def checks(count, merge):
    results = []

    def case(name, check):
        try:
            check()
            results.append({"name": name, "passed": True, "detail": "通过"})
        except Exception as error:
            results.append({"name": name, "passed": False,
                            "detail": (str(error) or type(error).__name__)[:700]})

    def equal(actual, expected):
        if actual != expected:
            raise AssertionError("预期 %r，实际 %r" % (expected, actual))

    def normal():
        ids = [108, 111, 119]
        equal(merge(ids, (108, 111), 256), [256, 119])
        equal(ids, [108, 111, 119])

    case("单次合并且不改写输入", normal)
    case("重叠：aaa → aa | a", lambda: equal(merge([97, 97, 97], (97, 97), 256), [256, 97]))
    case("连续匹配：aaaa → aa | aa", lambda: equal(merge([97] * 4, (97, 97), 256), [256, 256]))
    case("未匹配与单项保持不变", lambda: (equal(merge([1, 2, 3], (8, 9), 256), [1, 2, 3]), equal(merge([8], (8, 9), 256), [8])))
    case("空输入", lambda: equal(merge([], (1, 2), 256), []))

    def weighted():
        corpus = [{"ids": [1, 2, 1, 2], "weight": 3}, {"ids": [1, 2], "weight": 2}]
        equal(dict(count(corpus)), {(1, 2): 8, (2, 1): 3})
        equal(dict(count([])), {})

    case("相邻对频次乘以记录权重", weighted)
    return results


def piece(payload):
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return "[" + payload.hex(" ").upper() + "]"


def experiment(count, merge, scenario):
    samples = SCENARIOS[scenario]
    corpus = [{"text": text, "weight": weight, "ids": list(text.encode("utf-8"))} for text, weight in samples]
    counts = count([dict(row, ids=row["ids"][:]) for row in corpus])
    if not hasattr(counts, "items"):
        raise TypeError("count_pairs 应返回 pair → 频次 的映射，例如 Counter。")
    items = list(counts.items())
    for pair, frequency in items:
        if not isinstance(pair, tuple) or len(pair) != 2 or not all(type(v) is int and 0 <= v <= 255 for v in pair):
            raise TypeError("本轮 pair 应是两个字节编号组成的 tuple。")
        if type(frequency) is not int or frequency <= 0:
            raise TypeError("pair 频次应为正整数。")
    if not items:
        raise ValueError("语料包含相邻对，但 count_pairs 没有返回候选。")
    pair, frequency = min(items, key=lambda item: (-item[1], item[0]))
    new_id = 256
    vocab = [bytes([i]) for i in range(256)] + [bytes(pair)]
    records = []
    for row in corpus:
        after = merge(row["ids"][:], pair, new_id)
        if not isinstance(after, list) or not all(type(i) is int and 0 <= i <= 256 for i in after):
            raise TypeError("merge_pair 应返回由本轮有效 token ID 组成的 list。")
        if len(after) > 100:
            raise ValueError("输出过长；本题每条记录最多100个token。")
        records.append({"text": row["text"], "weight": row["weight"], "before": row["ids"], "after": after,
                        "before_pieces": [piece(vocab[i]) for i in row["ids"]],
                        "after_pieces": [piece(vocab[i]) for i in after]})
    before = sum(len(row["before"]) * row["weight"] for row in records)
    after = sum(len(row["after"]) * row["weight"] for row in records)
    return {"pair": list(pair), "pair_pieces": [piece(vocab[i]) for i in pair], "new_piece": piece(vocab[256]),
            "frequency": frequency, "new_id": new_id, "before": before, "after": after,
            "records": records, "scenario": scenario}


def run_lab(code, scenario="standard", mode="run"):
    stdout = BoundedOutput()
    payload = {"ok": False, "stdout": "", "checks": [], "experiment": None, "error": ""}
    with redirect_stdout(stdout), redirect_stderr(stdout):
        try:
            if len(code) > 40000:
                raise ValueError("代码最多40000个字符。")
            if scenario not in SCENARIOS or mode not in ("run", "check"):
                raise ValueError("未知的实验设置。")
            namespace = {"__name__": "__learner__"}
            exec(compile(code, "<learner.py>", "exec"), namespace)
            count, merge = namespace.get("count_pairs"), namespace.get("merge_pair")
            if not callable(count) or not callable(merge):
                raise TypeError("请保留 count_pairs 和 merge_pair 两个函数。")
            if mode == "check":
                payload["checks"] = checks(count, merge)
            payload["experiment"] = experiment(count, merge, scenario)
            payload["ok"] = True
        except Exception:
            payload["error"] = traceback.format_exc(limit=5)[-5000:]
    payload["stdout"] = stdout.getvalue()
    return json.dumps(payload, ensure_ascii=False)
