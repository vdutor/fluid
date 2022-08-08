# Copyright 2022 (c) Vincent Dutordoir
# SPDX-License-Identifier: Apache-2.0

# code based on:
# https://github.dev/solidjs/solid/blob/main/packages/solid/src/reactive/signal.ts
# https://github.dev/adamhaile/S/blob/main/src/S.ts
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, List, Set, TypeVar, cast

from fluid.utils import doublewrap

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
    """Return value computation"""
    is_memo: bool = False
    """Is `true` when computation returns a readonly-Signal"""
    sources: Set[Signal[Any]] = field(default_factory=set)
    """Set of `Signal`s the computation depends on."""
    cleanups: Set[Callable[[], None]] = field(default_factory=set)
    """Functions to be executed on updates and when computation is disposed."""
    owner: Computation[Any] | None = None
    """This computation will be disposed when owner is cleaned up."""
    children: Set[Computation[Any]] = field(default_factory=set)
    """List of `Computation`s owned by this computation"""
    name: str | None = None
    """Computation's name used for debugging and graphing"""

    def __post_init__(self) -> None:
        # add clean up method to list
        self.cleanups.add(self._remove_computation_from_signal_subscription_list)

    def _remove_computation_from_signal_subscription_list(self) -> None:
        for signal in self.sources:
            signal.subscribed_computations.remove(self)
        self.sources.clear()

    def cleanup(self) -> None:
        # clean up node: execute all clean up functions
        list(map(lambda func: func(), list(self.cleanups)))
        # clean up children
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

    def is_root(self) -> bool:
        return self.function is None

    def get_parents(self) -> List[INode]:
        return list(self.sources)

    def get_children(self) -> List[INode]:
        if self.is_memo:
            return [cast(INode, self.ret)]

        return []


class Batch:

    def __init__(self) -> None:
        self.activated: bool = False
        self.computations: List[Computation[Any]] = []
        self.signals: List[Signal[Any]] = []

    def __enter__(self) -> "Batch":
        if self.activated:
            raise Exception("Batch already activated.")

        self.computations.clear()
        self.signals.clear()
        self.activated = True
        return self

    def __exit__(self, *_: Any) -> None:

        i = 0
        while len(self.signals) > 0 or len(self.computations) > 0:
            print("Executing step:", i)
            for s in self.signals:
                print("setting", s)
                s._value = s._pending_value
                s._pending_value = None
                s.state = State.CLEAN

            self.signals.clear()

            computation_snapshot = list(self.computations)
            self.computations.clear()

            for c in computation_snapshot:
                c.execute()

            i += 1
            if i > 1_000_000:
                print("Assume run-away computation...")

        self.activated = False


class State(Enum):
    CLEAN = "clean"
    PENDING = "pending"
    """New value has been computed but not set"""
    STALE = "stale"
    """Sources have changed but pending value has not been set"""


class Signal(Generic[T], INode):

    def __init__(self, value: T | None, readonly: bool = False):
        self._value: T | None = value
        self._pending_value: T | None = None
        self._readonly: bool = readonly
        """If `True`, trying to assign a new value will raise an Exception."""
        self.subscribed_computations: Set[Computation[Any]] = set()
        """Set of computations that depend on signal. This set will be re-executed on signal changes."""
        self.computation: Computation[Signal[T]] | None = None
        """When Signal was created by a memo"""
        self.state: State = State.CLEAN

    def assign(self, new_value: T) -> Signal[T]:
        if self._readonly:
            raise Exception(
                "Not allowed to assign new value to readonly Signal."
                "Did you create this signal using 'createMemo'? That would not be allowed.")

        if (batch.activated and self.state == State.PENDING and (self._pending_value != new_value)):
            raise Exception("Not allowed to assign another value during batching: "
                            f"{self._pending_value} (PENDING) !=  {new_value}")

        return self._assign(new_value)

    def _assign(self, new_value: T) -> Signal[T]:
        # *Not* is batch mode. Logic is fairly simple:
        # (1) Set new value
        # (2) Run through dependency graph and re-execute all computations
        # self._value = new_value
        # for el in self.get_topo():
        #     if isinstance(el, Computation):
        #         el.execute()
        # return self

        activated_batch = False
        if not batch.activated:
            activated_batch = True
            batch.__enter__()

        self._pending_value = new_value
        self.state = State.PENDING
        batch.signals.append(self)

        for el in self.get_topo():
            if el == self:
                continue

            if isinstance(el, Signal) and el.is_created_by_memo():
                # There is a signal in the dependency graph created by a
                # memo.  The signal's value will only be updated once the
                # corresponding computation has ran. For now, simply set the
                # signal's state to `STALE`, so that depending computations
                # know their sources are outdated (state).
                el.state = State.STALE

            if isinstance(el, Computation):
                computation = el

                if computation in batch.computations:
                    # Computation is already scheduled to be executed. Nothing more to do.
                    continue

                if any(s.state == State.STALE for s in computation.sources):
                    # Don't schedule the computation because at least one of
                    # it sources is stale. The computation will be scheduled
                    # for execution once the stale signal is updated.
                    continue

                batch.computations.append(computation)

        if activated_batch:
            batch.__exit__()

        return self

    def get_topo(self) -> List[INode]:
        visited: Set[INode] = set()  # Set to keep track of visited nodes
        topo: List[INode] = []

        def build_topo(node: INode) -> None:
            if node not in visited:
                visited.add(node)
                for child in node.get_children():
                    build_topo(child)
                topo.append(node)

        build_topo(self)
        return list(reversed(topo))

    def __call__(self) -> T | None:
        if OWNER is not None:
            self.subscribed_computations.add(OWNER)
            OWNER.sources.add(self)
        return self._value

    def __str__(self) -> str:
        return "Signal(value={}, pending={}, readonly={}, state={}, number_subs={})".format(
            self._value,
            self._pending_value,
            self._readonly,
            self.state,
            len(self.subscribed_computations),
        )

    def is_created_by_memo(self) -> bool:
        return self.computation is not None

    def get_children(self) -> List[INode]:
        return list(self.subscribed_computations)

    def get_parents(self) -> List[INode]:
        if self.computation is not None:
            return [self.computation]
        return []


# Globals:
batch = Batch()
OWNER: Computation[Any] | None = None
CURRENT_COMPUTATION: Computation[Any] | None = None
ROOT: Computation[Any] = Computation(None)


@doublewrap
def createEffect(function: Callable[[], R], name: str | None = None) -> R | None:
    return _createComputation(function, name=name).ret


@doublewrap
def createMemo(function: Callable[[], R], name: str | None = None) -> Signal[R]:
    signal = Signal[R](None, readonly=True)
    computation = _createComputation(lambda: signal._assign(function()), name="memo")
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


def createRoot(function: Callable[[], R]) -> R | None:
    return createEffect(function)


def cleanUp(function: VoidFunc) -> None:
    if CURRENT_COMPUTATION is None:
        raise Exception("cleanUp's can only be added to computations")
    CURRENT_COMPUTATION.cleanups.add(function)
