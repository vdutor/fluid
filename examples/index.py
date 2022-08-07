# Copyright 2022 (c) Vincent Dutordoir
# SPDX-License-Identifier: Apache-2.0

from js import console, document

from fluid.components import Component, HtmlComponent
from fluid.signal import Signal

name = Signal("Vincent")
color = Signal(100)
show = Signal(False)


def on_click(e):
    name.assign(name() + "!")
    color.assign((color() + 100) % 700 + 100)
    show.assign(~show())
    console.log(show())


class MyComponent(Component):

    def __init__(self, show: Signal[bool]):
        self.show = show

    def build(self):
        if self.show():
            return HtmlComponent("div", {"class": "text-3xl"}, "Well, hello there!")
        else:
            return HtmlComponent("div", {}, '')


dom = HtmlComponent(
    "div", {"class": "text-4xl flex flex-col py-10"},
    HtmlComponent("span", {}, lambda: f"Hello, {name()}"),
    HtmlComponent(
        "button", {
            "id":
                "btn",
            "class":
                lambda:
                f"p-2 my-4 text-white bg-blue-{color()} border border-blue-{color()} rounded",
            "pys-onClick":
                "on_click"
        }, "Generate name"), MyComponent(show))

document.body.appendChild(dom.render())
