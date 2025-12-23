from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Action:
    kind: str  # 'add' + | 'mul' x | 'div' /
    arg: int

    def apply(self, x: int) -> int:
        if self.kind == "add":
            return x + self.arg
        elif self.kind == "mul":
            return x * self.arg
        elif self.kind == "div":
            return x // self.arg
        raise ValueError(f"Unknown action kind: {self.kind}")

    def try_describe(self, old: int, new: int) -> Optional[str]:
        if self.apply(old) != new:
            return None
        if self.kind == "add":
            d = self.arg
            return f"{'+' if d >= 0 else '−'}{abs(d)}"
        elif self.kind == "mul":
            return f"×{self.arg}"
        elif self.kind == "div":
            return f"÷{self.arg}"
        return None
