from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GameRules:
    """
    Правила игры.
    - target_mode: 'sum' | 'max' | 'heap'
    - target: порог (целое > 0)
    - finish_cmp: 'ge' (>= target) или 'lt' (< target)
    - heap_index: индекс кучи для режима 'heap'
    - adds: целочисленные сдвиги (могут быть отрицательными), 0 исключается
    - mults: множители (целые >= 2)
    - divs: делители (целые >= 2), результат — целочисленное деление (округление вниз)
    - heaps: количество куч (1 или 2)
    """
    target_mode: str = "sum"
    target: int = 100
    finish_cmp: str = "ge"
    heap_index: Optional[int] = None

    adds: List[int] = field(default_factory=lambda: [1])
    mults: List[int] = field(default_factory=lambda: [3])
    divs: List[int] = field(default_factory=list)

    heaps: int = 2

    def __post_init__(self):
        if self.heaps not in (1, 2):
            raise ValueError("heaps должен быть 1 или 2")

        if self.finish_cmp not in ("ge", "lt"):
            raise ValueError("finish_cmp должен быть 'ge' или 'lt'")

        # Нормализация списков действий
        self.adds = sorted({a for a in self.adds if a != 0})
        self.mults = sorted({m for m in self.mults if m >= 2})
        self.divs = sorted({d for d in self.divs if d >= 2})

        if self.target <= 0:
            raise ValueError("target должен быть положительным")

        if self.target_mode == "heap":
            if self.heap_index is None:
                raise ValueError("heap_index must be set for target_mode='heap'")
            if not (0 <= self.heap_index < self.heaps):
                raise ValueError("heap_index вне диапазона куч")
