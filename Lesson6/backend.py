# backend.py
import collections
import re
from typing import Dict, List, Tuple, Set


def solve(matrix_str, edges_str, targets_str, is_weighted=True):
    try:
        if is_weighted:
            table_adj, table_weights = _parse_matrix_weighted(matrix_str)
        else:
            m = _parse_matrix_unweighted(matrix_str)
            table_adj = _adj_from_matrix_unweighted(m)
            table_weights = []

        if is_weighted:
            graph_adj, graph_nodes, graph_weights = _parse_edges_weighted(edges_str)
        else:
            graph_adj, graph_nodes = _parse_edges_unweighted(edges_str)
            graph_weights = []

        targets = _parse_targets(targets_str)
        _validate_inputs(len(table_adj), graph_nodes, targets)

        td = {k: len(v) for k, v in table_adj.items()}
        gd = {k: len(v) for k, v in graph_adj.items()}
        if sorted(td.values()) != sorted(gd.values()):
            return _degree_error(gd, td)

        if is_weighted and sorted(table_weights) != sorted(graph_weights):
            return (
                "Ошибка: Набор длин дорог графа и таблицы не совпадает.\n\n"
                f"Длины из графа: {sorted(graph_weights)}\n"
                f"Длины из таблицы: {sorted(table_weights)}"
            )

        maps = _find_all_isomorphisms(graph_adj, table_adj, is_weighted)
        if not maps:
            return "Ошибка: Не удалось сопоставить граф с таблицей."

        res: Set[int] = set()
        for m in maps:
            for t in targets:
                if t in m:
                    res.add(m[t])

        if not res:
            return "Ошибка: Искомые вершины не найдены."

        return "".join(map(str, sorted(res)))

    except Exception as e:
        return f"Ошибка: {e}"


def _parse_targets(s):
    p = [x.strip().upper() for x in re.split(r"[\s,;]+", s) if x.strip()]
    if not p:
        raise ValueError("Искомые вершины не указаны.")
    return p


def _validate_inputs(n, nodes, targets):
    if n != len(nodes):
        raise ValueError("Размерности не совпадают.")
    miss = [x for x in targets if x not in nodes]
    if miss:
        raise ValueError(f"Вершины {miss} отсутствуют.")


def _degree_error(g, t):
    return (
        "Ошибка: Степени вершин не совпадают.\n\n"
        f"Степени графа: {sorted(g.values())}\n"
        f"Степени таблицы: {sorted(t.values())}"
    )


def _parse_matrix_weighted(s):
    m = []
    for l in s.strip().splitlines():
        r = [int(x) if x.isdigit() else 0 for x in l.split()]
        if r:
            m.append(r)
    if not m:
        raise ValueError("Матрица пуста.")
    n = len(m)
    if any(len(r) != n for r in m):
        raise ValueError("Матрица должна быть квадратной.")
    adj = {i + 1: {} for i in range(n)}
    w = []
    for i in range(n):
        for j in range(i + 1, n):
            if m[i][j] > 0:
                adj[i + 1][j + 1] = m[i][j]
                adj[j + 1][i + 1] = m[i][j]
                w.append(m[i][j])
    return adj, w


def _parse_matrix_unweighted(s):
    m = []
    for l in s.strip().splitlines():
        r = [int(x) if x.isdigit() else 0 for x in l.split()]
        if r:
            m.append(r)
    if not m:
        raise ValueError("Матрица пуста.")
    n = len(m)
    if any(len(r) != n for r in m):
        raise ValueError("Матрица должна быть квадратной.")
    return m


def _adj_from_matrix_unweighted(m):
    n = len(m)
    adj = {i + 1: {} for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if m[i][j] == 1:
                adj[i + 1][j + 1] = 1
                adj[j + 1][i + 1] = 1
    return adj


def _parse_edges_weighted(s):
    adj = collections.defaultdict(dict)
    nodes = set()
    w = []
    seen = {}
    for raw in s.strip().splitlines():
        l = raw.strip().upper()
        if not l:
            continue
        l = l.replace("—", "-").replace("–", "-").replace("−", "-")
        l = re.sub(r"[;,]", " ", l)
        p = [x for x in re.split(r"\s+|-", l) if x]
        if len(p) == 1:
            nodes.add(p[0])
            adj.setdefault(p[0], {})
            continue
        if len(p) >= 3 and p[-1].isdigit():
            u, v, wt = p[0], p[1], int(p[-1])
            if u == v:
                raise ValueError("Петля.")
            k = tuple(sorted((u, v)))
            if k in seen and seen[k] != wt:
                raise ValueError("Дубликат с разным весом.")
            if k not in seen:
                seen[k] = wt
                adj[u][v] = wt
                adj[v][u] = wt
                nodes |= {u, v}
                w.append(wt)
            continue
        raise ValueError("Неверный формат ребра.")
    if not nodes:
        raise ValueError("Граф пуст.")
    for n in nodes:
        adj.setdefault(n, {})
    return adj, sorted(nodes), w


def _parse_edges_unweighted(s):
    adj = collections.defaultdict(dict)
    nodes = set()
    seen = set()
    for raw in s.strip().splitlines():
        l = raw.strip().upper()
        if not l:
            continue
        l = l.replace("—", "-").replace("–", "-").replace("−", "-")
        l = re.sub(r"[;,]", " ", l)
        p = [x for x in re.split(r"\s+|-", l) if x]
        if len(p) == 1:
            nodes.add(p[0])
            adj.setdefault(p[0], {})
            continue
        if len(p) >= 2:
            u, v = p[0], p[1]
            if u == v:
                raise ValueError("Петля.")
            k = tuple(sorted((u, v)))
            if k not in seen:
                seen.add(k)
                adj[u][v] = 1
                adj[v][u] = 1
                nodes |= {u, v}
            continue
        raise ValueError("Неверный формат.")
    if not nodes:
        raise ValueError("Граф пуст.")
    for n in nodes:
        adj.setdefault(n, {})
    return adj, sorted(nodes)


def _find_all_isomorphisms(graph, table, weighted):
    g = list(graph)
    t = list(table)
    gd = {u: len(graph[u]) for u in g}
    td = {v: len(table[v]) for v in t}

    def sig(adj, deg, n):
        d = deg[n]
        nd = sorted(deg[x] for x in adj[n])
        if weighted:
            w = sorted(adj[n][x] for x in adj[n])
            wd = sorted((adj[n][x], deg[x]) for x in adj[n])
            return d, tuple(nd), tuple(w), tuple(wd)
        return d, tuple(nd)

    gs = {u: sig(graph, gd, u) for u in g}
    ts = collections.defaultdict(list)
    for v in t:
        ts[sig(table, td, v)].append(v)

    cand = {u: set(ts.get(gs[u], [])) for u in g}
    if any(not v for v in cand.values()):
        return []

    used = set()
    cur = {}
    res = []
    order = sorted(g, key=lambda x: len(cand[x]))

    def ok(u, v):
        for u2 in graph[u]:
            if u2 in cur:
                v2 = cur[u2]
                if v2 not in table[v]:
                    return False
                if weighted and table[v][v2] != graph[u][u2]:
                    return False
        return True

    def bt(i):
        if i == len(order):
            res.append(dict(cur))
            return
        u = order[i]
        for v in cand[u] - used:
            if ok(u, v):
                cur[u] = v
                used.add(v)
                bt(i + 1)
                used.remove(v)
                del cur[u]

    bt(0)
    return res
