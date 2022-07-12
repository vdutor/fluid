# https://github.dev/solidjs/solid/blob/main/packages/solid/src/reactive/signal.ts
# https://github.dev/adamhaile/S/blob/main/src/S.ts
from __future__ import annotations

from dataclasses import dataclass, field
from tkinter import CURRENT
from typing import Callable, Generic, Iterable, Set, TypeVar

# from .pyscript import console

T = TypeVar("T")
"""Generic type of signals"""

R = TypeVar("R")
"""Generic return type of functions wrapped as effects"""

VoidFunc = Callable[[], None]


@dataclass(frozen=True, eq=False)
class Computation(Generic[R]):
    function: Callable[[], R] | None
    """Function to be recomputed on changing `Signal`s."""
    sources: Set[Signal] = field(default_factory=set)
    """Set of `Signal`s the computation depends on."""
    cleanups: Set[Callable[[], None]] = field(default_factory=set)
    """Functions to be executed on updates and when computation is disposed."""
    owner: Computation | None = None
    """This computation will be disposed when owner is cleaned up."""
    children: Set[Computation] = field(default_factory=set)
    """List of `Computation`s owned by this computation"""

    def __post_init__(self):
        # add clean up method to list
        self.cleanups.add(self._remove_computation_from_signal_subscription_list)

    def _remove_computation_from_signal_subscription_list(self) -> None:
        for signal in self.sources:
            signal.subscribed_computations.remove(self)
        self.sources.clear()

    def cleanup(self) -> None:
        list(map(lambda func: func(), list(self.cleanups)))
        list(map(lambda child: child.cleanup(), list(self.children)))
        self.children.clear()

    def execute(self) -> R:
        global OWNER
        global CURRENT_COMPUTATION

        prev_current_computation = CURRENT_COMPUTATION
        prev_owner = OWNER

        if self.owner is not None:
            # TODO: remove the None
            self.owner.children.add(self)

        self.cleanup()
        OWNER = CURRENT_COMPUTATION = self

        try:
            assert self.function is not None
            return self.function()
        finally:
            OWNER = prev_owner
            CURRENT_COMPUTATION = prev_current_computation
        
    def is_root(self):
        return self.function is None


class Signal(Generic[T]):
    def __init__(self, value: T):
        self._value = value
        self.subscribed_computations: Set[Computation] = set()

    def assign(self, new_value: T) -> None:
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
CURRENT_COMPUTATION: Computation | None = None
ROOT: Computation = Computation(None)


def _execute_functions(functions: Iterable[VoidFunc]) -> None:
    _ = list(map(lambda func: func(), functions))


def createEffect(function: Callable[[], R]) -> R:
    global OWNER
    owner = OWNER

    if OWNER is None:
        # TODO: raise warning
        # raise Exception("Effects can not be created when owner is None")
        pass

    computation = Computation(function, owner=owner)

    return computation.execute()


def createRoot(function: Callable[[], R]) -> R:
    OWNER = ROOT
    return createEffect(function)


def cleanUp(function: VoidFunc) -> None:
    if CURRENT_COMPUTATION is None: raise Exception("cleanUp's can only be added to computations")
    CURRENT_COMPUTATION.cleanups.add(function)
