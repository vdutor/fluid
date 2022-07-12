[![Quality checks and Tests](https://github.com/vdutor/fluid/actions/workflows/quality-check.yaml/badge.svg)](https://github.com/vdutor/fluid/actions/workflows/quality-check.yaml)

# Fluid: A Reactive Framework For Python

```python
from fluid.signal import Signal, createEffect, createMemo

n1 = Signal(10)
n2 = Signal(5)
product = createMemo(lambda: n1() * n2())


@createEffect
def print_product():
    print("product:", product())


@createEffect
def print_n1():
    print("n1:\t", n1())


@createEffect
def print_n2():
    print("n2:\t", n2())


n1.assign(-1)
```

Outputs:
```
> product: 50
> n1:      10
> n2:      5
> product: -5
> n1:      -1
```

## Installation: only required for development

```
make install
```

### Install graphviz 
Used for debugging and computation graph visualisation

* Ubuntu
```
sudo apt install graphviz
```

* Mac
```
brew install graphviz
```