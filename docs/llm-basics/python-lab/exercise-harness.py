from contextlib import redirect_stdout, redirect_stderr
import json, math, traceback, sys, copy, types
if "MATH_SOURCE" in globals():
    module=types.ModuleType("tasteai_math")
    exec(MATH_SOURCE,module.__dict__)
    sys.modules["tasteai_math"]=module

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

def trace_snapshot(frame, event, arg):
    values = {}
    for key, value in list(frame.f_locals.items())[:16]:
        if key.startswith("__") or callable(value):
            continue
        if type(value) in (int, float, str, bool, list, tuple, dict, type(None)) or isinstance(value, dict):
            values[key] = repr(value)[:600]
    if event == "return":
        values["返回值"] = repr(arg)[:600]
    return {"line": frame.f_lineno, "function": frame.f_code.co_name,
            "event": event, "variables": values}

def close(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and set(actual)==set(expected) and all(close(actual[k],v) for k,v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(close(a,b) for a,b in zip(actual, expected))
    if isinstance(expected, (int,float)):
        return type(actual) in (int,float) and math.isfinite(actual) and math.isclose(actual,expected,rel_tol=1e-8,abs_tol=1e-8)
    return type(actual) is type(expected) and actual == expected


def run_lab(code, scenario="standard", mode="run"):
    config = next(x for x in json.loads(EXERCISE_JSON) if x['id'] == LAB_ID)
    trace, results = [], []
    truncated = False
    payload = dict(ok=False, stdout='', checks=results, experiment=None, error='', trace=trace)
    stdout = BoundedOutput()
    old_trace = sys.gettrace()
    def observe(frame,event,arg):
        nonlocal truncated
        if frame.f_code.co_filename == '<learner.py>' and event in ('line','return'):
            if len(trace) < 1500:
                trace.append(trace_snapshot(frame,event,arg))
            else:
                truncated = True
        return observe
    with redirect_stdout(stdout), redirect_stderr(stdout):
        try:
            if len(code)>40000 or mode not in ('run','check','trace') or scenario not in ('standard','overlap'):
                raise ValueError('未知设置或代码过长。')
            namespace = {'__name__':'__learner__'}
            if mode == 'trace': sys.settrace(observe)
            exec(compile(code,'<learner.py>','exec'), namespace)
            function = namespace.get(config['function'])
            if not callable(function): raise TypeError('请保留题目中的函数名。')
            if mode == 'check':
                for test in config['cases']:
                    args=copy.deepcopy(test['args']); before=copy.deepcopy(args)
                    try:
                        tested=namespace.get(test.get('function',config['function']))
                        actual=tested(*args)
                        for key in test.get('path','').split('.') if test.get('path') else []:
                            actual=actual[int(key)] if isinstance(actual,list) else actual[key]
                        passed='raises' not in test and close(actual,test['expected']) and args==before
                        detail='通过' if passed else '实际：'+repr(actual)[:300]+'；预期：'+repr(test.get('expected',test.get('raises')))[:300]+'；输入不得被修改'
                    except Exception as error:
                        passed=type(error).__name__==test.get('raises')
                        detail='通过' if passed else type(error).__name__+': '+str(error)[:300]
                    results.append(dict(name=test['name'],passed=passed,detail=detail))
            sample=config['scenarios'][0 if scenario=='standard' else 1]
            args=copy.deepcopy(sample['args'])
            actual=function(*args)
            # Limit graph data; never substitute the reference answer for actual output.
            packed=json.dumps(actual,ensure_ascii=False,allow_nan=False)
            if len(packed)>30000: raise ValueError('结果过长，请缩短输出。')
            if not isinstance(actual,(list,dict)): raise TypeError('请按题目约定返回结构化结果。')
            payload['visual']=dict(title=sample['label'],input=sample['args'],value=actual,views=config.get('views',[]))
            payload['ok']=True
        except Exception:
            payload['error']=traceback.format_exc(limit=5)[-5000:]
        finally:
            sys.settrace(old_trace)
    payload['stdout']=stdout.getvalue()
    payload['trace_truncated']=truncated
    return json.dumps(payload,ensure_ascii=False)
