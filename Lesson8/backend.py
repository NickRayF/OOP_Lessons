import ast
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple, List


_ALLOWED_FUNCS = {
    "div": lambda a, b: (a % b) == 0,
    "between": lambda x, l, r: l <= x <= r,
    "in_seg": lambda x, l, r: l <= x <= r,
    "in_int": lambda x, l, r: l < x < r,
    "abs": abs,
    "max": max,
    "min": min,
}


_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Call,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.FloorDiv,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.BitAnd,
    ast.BitOr,
    ast.BitXor,
    ast.LShift,
    ast.RShift,
    ast.Invert,
    ast.UAdd,
    ast.USub,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
)


class UnsafeExpression(ValueError):
    pass


def _validate_ast(tree: ast.AST, allowed_names: set):
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise UnsafeExpression(f"Запрещённая конструкция: {type(node).__name__}")
        if isinstance(node, ast.Name):
            if node.id not in allowed_names and node.id not in _ALLOWED_FUNCS:
                raise UnsafeExpression(f"Неизвестное имя: {node.id}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise UnsafeExpression("Разрешены только вызовы функций по имени")
            if node.func.id not in _ALLOWED_FUNCS:
                raise UnsafeExpression(f"Функция запрещена: {node.func.id}")


def compile_formula(expr: str, variables: Tuple[str, ...]) -> Callable[[Dict[str, int]], bool]:
    expr = expr.strip()
    if not expr:
        raise ValueError("Пустое выражение")

    tree = ast.parse(expr, mode="eval")
    allowed_names = set(variables) | set(_ALLOWED_FUNCS.keys())
    _validate_ast(tree, allowed_names)

    code = compile(tree, "<formula>", "eval")

    def _f(env: Dict[str, int]) -> bool:
        glb = {"__builtins__": {}}
        glb.update(_ALLOWED_FUNCS)
        return bool(eval(code, glb, env))

    return _f


@dataclass
class Domain:
    lo: int
    hi: int
    step: int = 1

    def values(self):
        if self.step == 0:
            raise ValueError("step не может быть 0")
        if self.lo <= self.hi:
            x = self.lo
            while x <= self.hi:
                yield x
                x += self.step
        else:
            x = self.lo
            while x >= self.hi:
                yield x
                x -= abs(self.step)


@dataclass
class Quant:
    mode: str  # "forall" | "exists" | "none"
    domain: Optional[Domain] = None


@dataclass
class SolveConfig:
    expr: str
    ax: Quant
    ay: Quant
    a_domain: Domain
    objective: str  # "min" | "max" | "all"
    a_name: str = "A"


def _check_one_A(
    f: Callable[[Dict[str, int]], bool],
    A: int,
    cfg: SolveConfig,
) -> bool:
    env_base = {cfg.a_name: A}

    def eval_with(env_add: Dict[str, int]) -> bool:
        env = dict(env_base)
        env.update(env_add)
        return f(env)

    qx, qy = cfg.ax, cfg.ay

    if qx.mode == "none" and qy.mode == "none":
        return eval_with({})

    if qx.mode != "none" and qx.domain is None:
        raise ValueError("Задан квантор x, но нет диапазона")
    if qy.mode != "none" and qy.domain is None:
        raise ValueError("Задан квантор y, но нет диапазона")

    if qx.mode == "none":
        def check_y() -> bool:
            if qy.mode == "forall":
                for y in qy.domain.values():
                    if not eval_with({"y": y}):
                        return False
                return True
            else:
                for y in qy.domain.values():
                    if eval_with({"y": y}):
                        return True
                return False
        return check_y()

    if qy.mode == "none":
        def check_x() -> bool:
            if qx.mode == "forall":
                for x in qx.domain.values():
                    if not eval_with({"x": x}):
                        return False
                return True
            else:
                for x in qx.domain.values():
                    if eval_with({"x": x}):
                        return True
                return False
        return check_x()

    def check_for_xy() -> bool:
        if qx.mode == "forall" and qy.mode == "forall":
            for x in qx.domain.values():
                for y in qy.domain.values():
                    if not eval_with({"x": x, "y": y}):
                        return False
            return True

        if qx.mode == "forall" and qy.mode == "exists":
            for x in qx.domain.values():
                ok = False
                for y in qy.domain.values():
                    if eval_with({"x": x, "y": y}):
                        ok = True
                        break
                if not ok:
                    return False
            return True

        if qx.mode == "exists" and qy.mode == "forall":
            for x in qx.domain.values():
                ok = True
                for y in qy.domain.values():
                    if not eval_with({"x": x, "y": y}):
                        ok = False
                        break
                if ok:
                    return True
            return False

        if qx.mode == "exists" and qy.mode == "exists":
            for x in qx.domain.values():
                for y in qy.domain.values():
                    if eval_with({"x": x, "y": y}):
                        return True
            return False

        raise ValueError("Неизвестные кванторы")

    return check_for_xy()


def solve(cfg: SolveConfig) -> List[int]:
    vars_needed = {cfg.a_name}
    if cfg.ax.mode != "none":
        vars_needed.add("x")
    if cfg.ay.mode != "none":
        vars_needed.add("y")

    f = compile_formula(cfg.expr, tuple(sorted(vars_needed)))

    good: List[int] = []
    for A in cfg.a_domain.values():
        if _check_one_A(f, A, cfg):
            good.append(A)

    if cfg.objective == "all":
        return good
    if not good:
        return []
    return [min(good)] if cfg.objective == "min" else [max(good)]
