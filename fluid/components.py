from __future__ import annotations

import abc
from typing import Any, Callable, Mapping

from .js import Console, Element, TextNode
from .signal import createEffect  # noqa: ignore

C = Callable[[], str]

"""
Type to represent a function which produces a string.
Typically, the function will contain `Signal`s.
"""


class UpdateableStr:
    def __init__(self, f: C):
        self.f = f
        self._rendered = False

    # @createEffect
    def render(self, parent: Element) -> None:
        Console.log("re-render updateable str")
        if not self._rendered:
            self.node = TextNode(self.f())
            parent.append_child(self.node)
            self._rendered = True
        else:
            self.node.update_text(self.f())


class Component(abc.ABC):
    def build(self) -> Component | HtmlComponent:
        raise NotImplementedError()

    # @createEffect
    def render(self, parent: Element) -> Element:
        return self.build().render(parent)


class HtmlComponent:
    """
    Represents HTML components such as `div`, `button`, `span`, etc.
    """

    def __init__(self, tag: str, attributes: Mapping[str, str | C], *children: Any):
        """
        :param tag: indicates the beginning and end of an HTML element <tag> </tag>
        :param attributes: properties such as 'id', 'class', 'pys-onClick', etc.
        :param children: element rendered inside the component
        """
        self._tag = tag
        self._children = children
        self._attributes = attributes

    def render(self, parent: Element | None = None) -> Element:
        Console.log("re-render htmlcomponent")

        def _mount(el: Element) -> Element:
            return el if parent is None else parent.append_child(el)

        self._element = Element(self._tag)
        dom = _mount(self._element)

        for child in self._children:
            if isinstance(child, (str, float)):
                node = TextNode(str(child))
                dom.append_child(node)
            elif isinstance(child, bool):
                node = TextNode("")
                dom.append_child(node)
            elif callable(child):
                UpdateableStr(child).render(dom)
            elif isinstance(child, (HtmlComponent, Component)):
                child.render(dom)

        for key, value in self._attributes.items():
            if key == "class":
                self.set_class(value)
            else:
                assert isinstance(value, str)
                self._element.set_attribute(key, value)

        return dom

    # @createEffect
    def set_class(self, value: str | C) -> None:
        # TODO: clean up expression. Awkwardly written to make mymy happy
        func: C
        if isinstance(value, str):
            func = lambda: str(value)
        else:
            func = value
        self._element.set_attribute("class", func())
