from fluid.logging import log
from fluid.signal import Signal, batch, createEffect

n1 = Signal(1)
n2 = Signal(2)


@createEffect(name="print product")
def _foo():
    print(f"{n1()} * {n2()} = {n1() * n2()}")


# createEffect(_foo, name="print product")


log(n1, n2)

print("-" * 30, "w/o batching")
n1.assign(-1)
n2.assign(-1)


print("-" * 30, "with batching")
with batch:
    n1.assign(-5)
    n2.assign(5)
    # print(n1())

# print(n1())
