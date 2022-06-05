from __future__ import annotations

from typing import Callable, Generic, TypeVar, Set, List

from .pyscript import console



T = TypeVar("T")
EffectType = Callable[[], None]

context: List[EffectType] = []

def update(function: EffectType):
    def wrapped(*args, **kwargs) -> None:
        _function = lambda: function(*args, **kwargs)
        context.append(_function)
        try:
            r = _function()
        finally:
            context.pop()
            return r

    return wrapped


def watch(function: EffectType):
    def wrapped(*args, **kwargs) -> None:
        _function = lambda: function(*args, **kwargs)
        context.append(_function)
        try:
            _function()
        finally:
            context.pop()
    wrapped()



class Signal(Generic[T]):
    def __init__(self, value: T | None):
        self._value = value
        self._subscribers: Set[EffectType] = set()
    
    def assign(self, new_value: T):
        console.log("setting new value", new_value)
        self._value = new_value

        for effect in self._subscribers:
            effect()
    
    def __call__(self) -> T:
        current_context = context[-1] if context else None
        if current_context is not None:
            self._subscribers.add(current_context)
        return self._value
        
    def __mul__(self, other: "Signal") -> "Signal":
        new = Signal(self._value * other._value)
        update(lambda: new.assign(self() * other()))()
        return new

    def __add__(self, other: "Signal") -> "Signal":
        new = Signal(self._value + other._value)
        update(lambda: new.assign(self() + other()))()
        return new


