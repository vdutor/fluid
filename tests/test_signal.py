from __future__ import annotations
from typing import Tuple, List

from fluid.signal import Signal, createEffect

import pytest


class Out:
    def __init__(self):
        self.lines: List[str] = []

    def write(self, s):
        self.lines.append(s)

    def reset(self):
        self.lines.clear()

    def assert_equal(self, str_list: List[str], reset_if_succesful: bool = True):
        def _check(expected, given):
            assert expected == given, (
                f"Strings don't match. Expected: '{expected}' != Given: '{given}'"
            )

        assert len(self.lines) == len(str_list)
        list(map(lambda t: _check(t[0], t[1]), zip(self.lines, str_list)))

        if reset_if_succesful:
            self.reset()


@pytest.fixture
def signals() -> Tuple[Signal, Signal, Signal]:
    name = Signal("Joe")
    sirname = Signal("Doe")
    fullname = Signal(True)
    return name, sirname, fullname


@pytest.fixture
def out() -> Out:
    return Out()


def test_basic_properties_signal(signals):
    name: Signal = signals[0]
    assert len(name.subscribed_computations) == 0
    assert name() == "Joe"
    assert len(name.subscribed_computations) == 0
    name.assign("Tom")
    assert name() == "Tom"


def test_retracking(signals, out):
    name, sirname, fullname = signals

    def _effect():
        if fullname():
            out.write(f"{name()} {sirname()}")
        else:
            out.write(f"{name()}")
    computation = createEffect(_effect)

    assert computation.sources == set(signals)
    out.assert_equal(
        ["Joe Doe"]
    )

    name.assign("Alice")
    sirname.assign("Adam")
    out.assert_equal([
        "Alice Doe",
        "Alice Adam"
    ])

    fullname.assign(False)
    assert len(computation.sources) == 2
    out.assert_equal([
        "Alice",
    ])

    name.assign("Tom")
    out.assert_equal([
        "Tom",
    ])
    sirname.assign("Kavalski")
    out.assert_equal([])

    fullname.assign(True)
    assert len(computation.sources) == 3
    out.assert_equal([
        "Tom Kavalski",
    ])


def test_signal_composition(signals, out):
    name, sirname, fullname = signals

    def _effect_fullname_True():
        out.write(f"{name()} {sirname()}")

    def _effect_fullname_False():
        out.write(f"{name()}")

    def _effect():
        if fullname():
            createEffect(_effect_fullname_True)
        else:
            createEffect(_effect_fullname_False)

    computation = createEffect(_effect)
    assert computation.sources == set((fullname,))
    out.assert_equal([
        "Joe Doe",
    ])

    name.assign("Tom")
    assert computation.sources == set((fullname,))
    out.assert_equal([
        "Tom Doe",
    ])

    fullname.assign(False)
    out.assert_equal([
        "Tom",
    ])
    # updating sirname should not rerun _effect_fullname_True because
    # should have been disposed - we expect no output.
    sirname.assign("Kavaliski")
    out.assert_equal([])
