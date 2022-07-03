from js import document, console

from fluid.components import *
from fluid.signal import Signal


name = Signal("Vincent")
color = Signal(100)


def on_click(e):
    name.assign(name() + "!")
    color.assign((color() + 100) % 700 + 100)
    console.log("Hello!")
    console.log(len(name._subscribers))


dom = HtmlComponent(
    "div",
    {"class": "text-4xl flex flex-col py-10"},
    HtmlComponent("span", {}, lambda: f"Hello, {name()}"),
    HtmlComponent(
        "button",
        {
            "id": "btn",
            "class": lambda: f"p-2 my-4 text-white bg-blue-{color()} border border-blue-{color()} rounded",
            "pys-onClick": "on_click"
        },
        "Generate name"
    ),
)

document.body.appendChild(dom.render());
