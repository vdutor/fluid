# Copyright 2022 (c) Vincent Dutordoir
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Tuple

import pytest

from fluid.signal import Signal, createEffect

from .utils import Out


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

    @createEffect
    def _effect():
        if fullname():
            out.write(f"{name()} {sirname()}")
        else:
            out.write(f"{name()}")

    out.assert_equal(["Joe Doe"])

    name.assign("Alice")
    sirname.assign("Adam")
    out.assert_equal(["Alice Doe", "Alice Adam"])

    fullname.assign(False)
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
    out.assert_equal([
        "Tom Kavalski",
    ])


def test_signal_composition(signals, out):
    name, sirname, fullname = signals

    def _effect_fullname_True():
        out.write(f"{name()} {sirname()}")

    def _effect_fullname_False():
        out.write(f"{name()}")

    @createEffect
    def _effect():
        if fullname():
            createEffect(_effect_fullname_True)
        else:
            createEffect(_effect_fullname_False)

    out.assert_equal([
        "Joe Doe",
    ])

    name.assign("Tom")
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
