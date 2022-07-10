# https://github.dev/solidjs/solid/blob/main/packages/solid/src/reactive/signal.ts
# https://github.dev/adamhaile/S/blob/main/src/S.ts
from __future__ import annotations
from dataclasses import dataclass, field

from typing import Callable, Generic, Iterator, Sequence, TypeVar, Set, List

# from .pyscript import console

T = TypeVar("T")
VoidFunc = Callable[[], None]


@dataclass(frozen=True, eq=False)
class Computation:
    function: Callable | None
    """Function to be recomputed on changing `Signal`s."""
    sources: Set[Signal] = field(default_factory=set)
    """Set of `Signal`s the computation depends on."""
    cleanups: Set[Callable[[], None]] = field(default_factory=set)
    """Functions to be executed on updates and when computation is disposed."""
    owner: Computation | None = None
    """This computation will be disposed when owner is cleaned up."""
    children: Set[Computation] = field(default_factory=set)
    """List of `Computation`s owned by this computation"""

    def reset(self):
        _execute_functions(self.cleanups)
        for signal in self.sources:
            signal.subscribed_computations.remove(self)
        self.sources.clear()

    def execute(self):
        global OWNER
        OWNER = self
        self.reset()
        try:
            return self.function()
        finally:
            OWNER = self.owner


class Signal(Generic[T]):
    def __init__(self, value: T | None):
        self._value = value
        self.subscribed_computations: Set[Computation] = set()
    
    def assign(self, new_value: T):
        self._value = new_value

        for computation in list(self.subscribed_computations):
            computation.execute()
    
    def __call__(self) -> T:
        if OWNER is not None:
            self.subscribed_computations.add(OWNER)
            OWNER.sources.add(self)
        return self._value


# Globals:
OWNER: Computation | None = None


def _execute_functions(functions: Iterator[VoidFunc]):
    _ = list(map(lambda func: func(), functions))


def createEffect(function: Callable):
    global OWNER
    owner = OWNER

    if OWNER is None:
        # TODO: raise warning
        pass
    
    computation = Computation(function, owner=owner)
    computation.execute()
    return computation
    

def createRoot(function: Callable):
    # TODO
    pass


def cleanUp(function: Callable):
    # TODO
    pass
