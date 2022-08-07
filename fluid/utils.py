# Copyright 2022 (c) Vincent Dutordoir
# SPDX-License-Identifier: Apache-2.0

# type: ignore
from functools import wraps

__all__ = ["doublewrap"]


def doublewrap(decorator):
    """
    A decorator for a decorator, allowing the decorator to be used as:
    ```
    @decorator(with, arguments, and=kwargs)
    def foo():
        ...
    ```
    or,
    ```
    @decorator
    def foo():
        ...

    From: https://stackoverflow.com/a/14412901
    """

    @wraps(decorator)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return decorator(args[0])
        else:
            # decorator arguments
            return lambda realf: decorator(realf, *args, **kwargs)

    return new_dec
