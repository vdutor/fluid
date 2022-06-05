import random

from fluid.signal import Signal
from fluid.components import *


NAMES = [
    "Noah Garcia",
    "Harmony Lucero",
    "Casey Knapp",
    "Erika Christian",
    "Thaddeus May",
    "Samara Martinez",
    "Noe Knight",
    "Cynthia Snyder",
    "Cesar Norton",
    "Felicity Maxwell",
    "Chloe Grimes",
    "Katelyn Mercado",
]

def on_click1(*args, **kwargs):
    name.assign(NAMES[random.randint(0, len(NAMES) - 1)])


name = Signal("Vincent")

div = Div(
    child=List_(
        Div(Text(lambda: f"Hello, {name()}"), class_="my-4"),
        Button(
            Text(lambda: "Random name"),
            class_="p-2 text-white bg-blue-600 border border-blue-600 rounded",
            on_click="on_click1"
        ),
    ),
    class_="text-4xl"
)
print(div.render())


value1 = Signal(0)
value2 = Signal(1)
product = value1 * value2
complex = value1 * value2 + value2

   


def add_one_to_value1(*args, **kwargs):
    value1.assign(value1() + 1)

def add_two_to_value2(*args, **kwargs):
    value2.assign(value2() + 2)

div = Div(
    child=List_(
        Div(Text(lambda: f"{value1()} * {value2()} = {product()}"), class_="my-4"),
        Div(Text(lambda: f"{value1()} * {value2()} + {value2()} = {complex()}"), class_="my-4"),
        Button(
            Text(lambda: "Add 1 to value 1"),
            class_="p-2 text-white bg-blue-600 border border-blue-600 rounded",
            on_click="add_one_to_value1"
        ),
        Button(
            Text(lambda: "Add 2 to value 2"),
            class_="p-2 mt-2 text-white bg-blue-600 border border-blue-600 rounded",
            on_click="add_two_to_value2"
        ),
    ),
    class_="text-4xl"
)
print(div.render())