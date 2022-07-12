# https://github.dev/solidjs/solid/blob/main/packages/solid/src/reactive/signal.ts
# https://github.dev/adamhaile/S/blob/main/src/S.ts
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, List, Set, TypeVar, cast

# from .pyscript import console

T = TypeVar("T")
"""Generic type of signals"""

R = TypeVar("R")
"""Generic return type of functions wrapped as effects"""

VoidFunc = Callable[[], None]


class INode(abc.ABC):
    """Node in computation graph"""

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

    def reset(self) -> None:
        _execute_functions(list(self.cleanups))
        for signal in self.sources:
            signal.subscribed_computations.remove(self)
        self.sources.clear()

    def execute(self) -> R:
        global OWNER
        OWNER = self
        self.reset()
        try:
            assert self.function is not None
            return self.function()
        finally:
            OWNER = self.owner

    def get_parents(self) -> List[INode]:
        return list(self.sources)

    def get_children(self) -> List[INode]:
        if self.is_memo:
            return [cast(INode, self.ret)]

        return []


class Signal(Generic[T], INode):
    def __init__(self, value: T | None, readonly: bool = False):
        self._value = value
        self._readonly = readonly
        self.subscribed_computations: Set[Computation] = set()
        self.computation: Computation | None = None

    def assign(self, new_value: T) -> Signal[T]:
        if self._readonly:
            raise Exception(
                "Not allowed to assign new value to readonly Signal."
                "Did you create this signal using createMemo? That would not be allowed."
            )
        return self._assign(new_value)

    def _assign(self, new_value: T) -> Signal[T]:
        self._value = new_value

        for computation in list(self.subscribed_computations):
            computation.execute()

        return self

    def __call__(self) -> T | None:
        if OWNER is not None:
            self.subscribed_computations.add(OWNER)
            OWNER.sources.add(self)
        return self._value

    def __str__(self) -> str:
        return f"Signal(value={self._value}, readonly={self._readonly}, len_subscribed_computations={len(self.subscribed_computations)})"

    def get_children(self) -> List[INode]:
        return list(self.subscribed_computations)

    def get_parents(self) -> List[INode]:
        if self.computation is not None:
            return [self.computation]
        return []


# Globals:
OWNER: Computation | None = None


def _execute_functions(functions: Iterable[VoidFunc]) -> None:
    _ = list(map(lambda func: func(), functions))


def createEffect(function: Callable[[], R]) -> R | None:
    return createComputation(function).ret


def createComputation(function: Callable[[], R]) -> Computation[R]:
    global OWNER
    owner = OWNER

    if OWNER is None:
        # TODO: raise warning
        pass

    computation = Computation(function, owner=owner)
    out = computation.execute()
    computation.ret = out
    return computation


def createMemo(function: Callable[[], R]) -> Signal[R]:
    signal = Signal[R](None, readonly=True)
    computation = createComputation(lambda: signal._assign(function()))
    computation.is_memo = True
    # link computation to signal
    signal.computation = computation
    return signal


def createRoot(function: Callable[[], R]) -> R:
    pass


def cleanUp(function: Callable) -> None:
    # TODO
    pass


def batch(function: Callable) -> None:
    pass


import os
import atexit
from collections import defaultdict

GRAPH = int(os.getenv("GRAPH", "0"))


top_colors = {Signal: '#FFFF80', Computation: "#c0c0c0"}
# dashed = 
# dashed = optype == LoadOps and getattr(ret, "_backing", None) is not None

if GRAPH:
    import networkx as nx  # type: ignore
    G = nx.DiGraph()
    def save_graph_exit():
        print("saving", G)
        nx.drawing.nx_pydot.write_dot(G, '/tmp/comp.dot')
        # -Gnslimit=100 can make it finish, but you won't like results
        os.system('dot -Tsvg /tmp/comp.dot -o /tmp/comp.svg')
    atexit.register(save_graph_exit)

global_num_max = 0
def nm(x):
    global global_num_max
    if getattr(x, 'global_num', None) is None:
        setattr(x, 'global_num', global_num_max)
        global_num_max += 1
    return f"<<< {x.global_num} >>>"


def log(root: INode):
    G.add_node(nm(root))

    if isinstance(root, Signal):
        G.nodes[nm(root)]['fillcolor'] = top_colors[Signal]
    elif isinstance(root, Computation):
        G.nodes[nm(root)]['fillcolor'] = top_colors[Computation]

    for child in root.get_children():
        G.add_node(nm(child))
        G.add_edge(nm(root), nm(child))
        log(child)
