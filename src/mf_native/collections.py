"""Native collection implementations for MF07 runtime.

These are thin Python-backed implementations that the interpreter can expose
to programs via `mf.collections`.
"""

from typing import Any, Callable


class List(list):
    def append(self, item: Any):
        super().append(item)

    def insert(self, index: int, item: Any):
        super().insert(index, item)

    def remove_at(self, index: int):
        return self.pop(index)

    def remove_item(self, item: Any) -> bool:
        try:
            self.remove(item)
            return True
        except ValueError:
            return False

    def clear_all(self):
        del self[:]

    def index_of(self, item: Any) -> int:
        try:
            return self.index(item)
        except ValueError:
            return -1

    def contains(self, item: Any) -> bool:
        return item in self

    def map_fn(self, fn: Callable[[Any], Any]):
        out = List()
        for v in self:
            out.append(fn(v))
        return out

    def filter_fn(self, fn: Callable[[Any], bool]):
        out = List()
        for v in self:
            if fn(v):
                out.append(v)
        return out

    def for_each(self, fn: Callable[[Any], None]):
        for v in self:
            fn(v)

    def to_string(self) -> str:
        return "[" + ", ".join(str(x) for x in self) + "]"


class Map(dict):
    pass


class Set(set):
    pass
