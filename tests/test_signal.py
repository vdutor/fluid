from __future__ import annotations

from dataclasses import dataclass
from fluid.signal import Signal, createEffect

name = Signal("Joe")
sirname = Signal("Doe")
fullname = Signal(True)


def Comp():
    if fullname():
        print(f"{name()} {sirname()}")
    else:
        print(f"{name()}")


comp = createEffect(Comp)

# print(comp.sources)
# print(comp.sources[0]._subscribers)

name.assign("Alice")
sirname.assign("Adam")
assert len(comp.sources) == 3
fullname.assign(False)
assert len(comp.sources) == 2
sirname.assign("Doe")
fullname.assign(True)