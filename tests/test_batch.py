from typing import Tuple

import pytest

from fluid.signal import Signal, batch, createEffect, createMemo

from .utils import Out


@pytest.fixture
def signals() -> Tuple[Signal, Signal]:
    n1 = Signal(1)
    n2 = Signal(2)
    return n1, n2


@pytest.fixture
def out() -> Out:
    return Out()


def test_no_double_assing(signals):
    n1, _ = signals
    with pytest.raises(Exception) as exception:
        with batch:
            n1.assign(-5)
            n1.assign(5)

    exception.match("Not allowed to assign another value during batching")


def test_batch(signals, out: Out):
    n1, n2 = signals

    @createEffect()
    def _foo():
        out.write(f"{n1()} * {n2()} = {n1() * n2()}")

    # clear writes from effect creation
    out.clear()

    n1.assign(5)
    n2.assign(-1)

    # two prints because signals were assigned outside batch mode
    out.assert_equal(
        [
            "5 * 2 = 10",
            "5 * -1 = -5",
        ]
    )

    with batch:
        n1.assign(3)
        n2.assign(4)

    # single print because signals were assigned inside batch
    out.assert_equal(
        [
            "3 * 4 = 12",
        ]
    )


def test_memo_and_batching(signals: Tuple[Signal, Signal], out: Out):
    n1, n2 = signals

    @createEffect(name="print product")
    def _foo():
        out.write(f"{n1()} * {n2()} = {n1() * n2()}")

    out.clear()  # clear writes from creating the effect

    def _product():
        return n1() * n2()

    n1.assign(-1)
    n2.assign(3)
    out.assert_equal(
        [
            "-1 * 2 = -2",
            "-1 * 3 = -3",
        ]
    )

    with batch:
        n1.assign(4)
        n2.assign(5)

    out.assert_equal(
        [
            "4 * 5 = 20",
        ]
    )

    createMemo(_product)
