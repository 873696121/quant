from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValueObject:
    """值对象基类 - 不可变"""

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.as_tuple() == other.as_tuple()

    def __hash__(self) -> int:
        return hash(self.as_tuple())

    def as_tuple(self) -> tuple:
        return tuple(v for k, v in self.__dict__.items() if not k.startswith('_'))
