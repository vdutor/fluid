from __future__ import annotations

from js import console, document  # type: ignore

__all__ = ["Element", "TextNode", "Console"]


class Element:
    def __init__(self, tag: str):
        self.node = document.createElement(tag)

    def set_attribute(self, key: str, value: str) -> None:
        self.node.setAttribute(key, value)

    def append_child(self, el: "Element" | TextNode) -> Element:
        return self.node.appendChild(el.node)


class TextNode:
    def __init__(self, text: str):
        self.node = document.createTextNode(text)

    def update_text(self, text: str) -> None:
        self.node.nodeValue = text


class Console:
    @staticmethod
    def log(s: str) -> None:
        console.log(s)
