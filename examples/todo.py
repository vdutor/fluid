import random

from fluid.components import *
from fluid.signal import Signal

todos: List[str] = [
    "Finish homework",
    "Make lunch",
]

map(
    List()
)

todos = SignalList(todos)
todos.append()
todos.pop()
todos.


Div(
    List_(
        *[
            Text(todo) for todo in todos
        ]
    )
    class_=""
)


