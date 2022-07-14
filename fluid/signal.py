# https://github.dev/solidjs/solid/blob/main/packages/solid/src/reactive/signal.ts
# https://github.dev/adamhaile/S/blob/main/src/S.ts
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Generic, Iterable, List, Set, TypeVar, cast

from .utils import doublewrap

T = TypeVar("T")
"""Generic type of signals"""

R = TypeVar("R")
"""Generic return type of functions wrapped as effects"""

VoidFunc = Callable[[], None]


class INode(abc.ABC):
    """A node in the computation directed-graph."""

    @abc.abstractmethod
    def get_parents(self) -> List[INode]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_children(self) -> List[INode]:
        raise NotADirectoryError


@dataclass(frozen=False, eq=False)
class Computation(Generic[R], INode):
    function: Callable[[], R] | None
    """Function to be recomputed on changing `Signal`s."""
    ret: R | None = None
    """Return value comutation"""
    is_memo: bool = False
    """Is `true` when computation creates a readonly-Signal"""
    sources: Set[Signal] = field(default_factory=set)
    """Set of `Signal`s the computation depends on."""
    cleanups: Set[Callable[[], None]] = field(default_factory=set)
    """Functions to be executed on updates and when computation is disposed."""
    owner: Computation | None = None
    """This computation will be disposed when owner is cleaned up."""
    children: Set[Computation] = field(default_factory=set)
    """List of `Computation`s owned by this computation"""
    name: str | None = None
    """Computation's name used for debugging and graphing"""

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

    def get_parents(self) -> List[INode]:
        return list(self.sources)

    def get_children(self) -> List[INode]:
        if self.is_memo:
            return [cast(INode, self.ret)]

        return []


class _Batch:
    def __init__(self):
        self.activated: bool = False
        self.computations: List[Computation] = []
        self.signals: List[Signal] = []

    def __enter__(self):
        self.activated = True
        return self

    def __exit__(self, *_):

        for s in self.signals:
            s._value = s._pending_value
            s._pending_value = None
            s.state = State.CLEAN

        for c in self.computations:
            c.execute()

        self.activated = False


batch = _Batch()


class State(Enum):
    CLEAN = "clean"
    PENDING = "pending"

    def is_pending(self):
        return self == State.PENDING


class Signal(Generic[T], INode):
    def __init__(self, value: T | None, readonly: bool = False):
        self._value = value
        self._pending_value = None
        self._readonly = readonly
        self.subscribed_computations: Set[Computation] = set()
        self.computation: Computation | None = None
        self.state: State = State.CLEAN

    def assign(self, new_value: T) -> Signal[T]:
        if self._readonly:
            raise Exception(
                "Not allowed to assign new value to readonly Signal."
                "Did you create this signal using 'createMemo'? That would not be allowed."
            )

        if (
            batch.activated
            and self.state.is_pending()
            and (self._pending_value != new_value)
        ):
            raise Exception(
                "Not allowed to assign another value during batching: "
                f"{self._pending_value} (PENDING) !=  {new_value}"
            )

        return self._assign(new_value)

    def _assign(self, new_value: T) -> Signal[T]:

        if batch.activated:
            self._pending_value = new_value
            self.state = State.PENDING
            batch.signals.append(self)

            for el in self.get_topo():
                if isinstance(el, Computation):
                    if el not in batch.computations:
                        batch.computations.append(el)
        else:
            self._value = new_value

            for el in self.get_topo():
                if isinstance(el, Computation):
                    el.execute()

        return self

    def get_topo(self) -> List[INode]:
        visited: Set[INode] = set()  # Set to keep track of visited nodes
        topo: List[INode] = []

        def build_topo(node: INode):
            if node not in visited:
                visited.add(node)
                for child in node.get_children():
                    build_topo(child)
                topo.append(node)

        build_topo(self)
        return reversed(topo)

    def __call__(self) -> T | None:
        if OWNER is not None:
            self.subscribed_computations.add(OWNER)
            OWNER.sources.add(self)
        return self._value

    def __str__(self) -> str:
        return f"Signal(value={self._value}, readonly={self._readonly}, len_subscribers={len(self.subscribed_computations)})"

    def get_children(self) -> List[INode]:
        return list(self.subscribed_computations)

    def get_parents(self) -> List[INode]:
        if self.computation is not None:
            return [self.computation]
        return []


# Globals:
OWNER: Computation | None = None
CURRENT_COMPUTATION: Computation | None = None
ROOT: Computation = Computation(None)


def _execute_functions(functions: Iterable[VoidFunc]) -> None:
    _ = list(map(lambda func: func(), functions))


@doublewrap
def createEffect(function: Callable[[], R], name: str | None = None) -> R | None:
    return _createComputation(function, name=name).ret


@doublewrap
def createMemo(function: Callable[[], R], name: str | None = None) -> Signal[R]:
    signal = Signal[R](None, readonly=True)
    computation = _createComputation(lambda: signal._assign(function()), name=name)
    computation.is_memo = True
    # link computation to signal
    signal.computation = computation
    return signal


def _createComputation(function: Callable[[], R], name: str | None) -> Computation[R]:
    global OWNER
    owner = OWNER

    if OWNER is None:
        # TODO: raise warning
        # raise Exception("Effects can not be created when owner is None")
        pass

    computation = Computation(function, owner=owner, name=name)
    out = computation.execute()
    computation.ret = out
    return computation


def createRoot(function: Callable[[], R]) -> R:
    return createEffect(function)


def cleanUp(function: VoidFunc) -> None:
    if CURRENT_COMPUTATION is None:
        raise Exception("cleanUp's can only be added to computations")
    CURRENT_COMPUTATION.cleanups.add(function)
