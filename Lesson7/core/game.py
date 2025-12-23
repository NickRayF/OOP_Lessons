from typing import Callable, Iterable, Tuple, Optional, Set

from .actions import Action
from .rules import GameRules


class Game:
    """
    Инкапсулирует правила и операции:
    - проверка терминала;
    - генерация ходов из состояния (меняется ровно одна куча);
    - описание хода.
    """

    def __init__(self, rules: GameRules,
                 state_guard: Optional[Callable[[Tuple[int, ...]], bool]] = None):
        self.rules = rules
        self.state_guard = state_guard
        self.actions: Tuple[Action, ...] = tuple(
            [Action("add", a) for a in self.rules.adds] +
            [Action("mul", m) for m in self.rules.mults] +
            [Action("div", d) for d in self.rules.divs]
        )

    def is_terminal(self, state: Tuple[int, ...]) -> bool:
        if self.rules.target_mode == "sum":
            val = sum(state)
        elif self.rules.target_mode == "max":
            val = max(state)
        elif self.rules.target_mode == "heap":
            idx = self.rules.heap_index  # валидируется в GameRules.__post_init__
            assert idx is not None
            val = state[idx]
        else:
            raise ValueError(f"Unknown target_mode: {self.rules.target_mode}")

        if self.rules.finish_cmp == "ge":
            return val >= self.rules.target
        else:  # "lt"
            return val < self.rules.target

    def iter_moves(self, state: Tuple[int, ...]) -> Iterable[Tuple[int, ...]]:
        """Итерирует все позиции, достижимые за 1 ход (меняется ровно одна куча)."""
        n = len(state)
        seen: Set[Tuple[int, ...]] = set()
        for i in range(n):
            old = state[i]
            for act in self.actions:
                new_state = list(state)
                new_state[i] = act.apply(old)
                t = tuple(new_state)
                if t in seen:
                    continue
                if self.state_guard and not self.state_guard(t):
                    continue
                seen.add(t)
                yield t

    def describe_move(self, a: Tuple[int, ...], b: Tuple[int, ...]) -> str:
        if len(a) != len(b):
            return f"({', '.join(map(str, a))}) → ({', '.join(map(str, b))})"
        idx = [i for i in range(len(a)) if a[i] != b[i]]
        if len(idx) != 1:
            return f"({', '.join(map(str, a))}) → ({', '.join(map(str, b))})"
        i = idx[0]
        old, new = a[i], b[i]
        for act in self.actions:
            descr = act.try_describe(old, new)
            if descr is not None:
                return f"на {i + 1}-й куче: {descr}"
        return f"на {i + 1}-й куче: {old}→{new}"
