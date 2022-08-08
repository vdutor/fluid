# Copyright 2022 (c) Vincent Dutordoir
# SPDX-License-Identifier: Apache-2.0
from functools import wraps
from typing import Any, Callable, TypeVar, cast

__all__ = ["doublewrap"]

F = TypeVar('F', bound=Callable[..., Any])


def doublewrap(decorator: F) -> F:
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
    def new_dec(*args, **kwargs):  # type: ignore
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return decorator(args[0])
        else:
            # decorator arguments
            return lambda realf: decorator(realf, *args, **kwargs)

    return cast(F, new_dec)
