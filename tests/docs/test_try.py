# Copyright 2022 (c) Vincent Dutordoir
# SPDX-License-Identifier: Apache-2.0

def test_imports():

    # [first_block__start]
    from fluid import Signal

    signal = Signal(10)
    print(signal())
    # [first_block__end]

    assert signal() == 10


def test_imports2():

    # [second_block__start]
    from fluid.signal import Signal, batch
    n1 = Signal(1)
    n2 = Signal(2)

    with batch:
        n1.assign(4)
        n2.assign(5)
    # [second_block__end]
