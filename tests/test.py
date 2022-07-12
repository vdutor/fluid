from fluid import Signal, createEffect, createMemo, log

n1 = Signal(10)
n2 = Signal(5)
product = createMemo(lambda: n1() * n2())


@createEffect(name="print_product")
def print_product():
    print("product:", product())


@createEffect(name="print_n1")
def print_n1():
    print("n1:\t", n1())


@createEffect(name="print_n2")
def print_n2():
    print("n2:\t", n2())


@createEffect(name="print_all")
def print_all():
    print(f"{n1()} * {n2()} = {product()}")



print(n1)
print(n2)
print(product)

n1.assign(-1)

log(n1, n2)

# with batch as bt:
#     n1.assign(3)
#     n2.assign(4)
