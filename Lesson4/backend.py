import re
from itertools import product

def get_vars(expr):
    r = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)
    bad = {"and","or","not","True","False"}
    return sorted(list(set([x for x in r if x not in bad])))

def safe_eval(expr, d):
    return bool(eval(expr, {"__builtins__": {}}, d))

def truth_table(expr):
    vs = get_vars(expr)
    res = []
    for combo in product([0,1], repeat=len(vs)):
        d = dict(zip(vs, combo))
        val = safe_eval(expr, d)
        d["result"] = val
        res.append(d)
    return vs, res

def filtered(data, kind):
    if kind == "true":
        return [r for r in data if r["result"]==1]
    if kind == "false":
        return [r for r in data if r["result"]==0]
    return data