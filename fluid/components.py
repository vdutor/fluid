from __future__ import annotations
from dataclasses import dataclass

from typing import Callable, Mapping, Optional, TypeVar

import abc

from .signal import update

from js import document, console


JsElement = TypeVar("JsElement")
C = Callable[[], str]

"""
Type to represent a function which produces a string.
Typically, the function will contain `Signal`s.
"""


class UpdateableStr:

    def __init__(self, f: C):
        self.f = f
        self._rendered = False

    @update
    def render(self, parent):
        console.log("re-render updateable str")
        if not self._rendered:
            self.node = document.createTextNode(self.f())
            parent.appendChild(self.node)
            self._rendered = True
        else:
            self.node.nodeValue = self.f()


class Component(abc.ABC):

    def build(self) -> Component | HtmlComponent:
        raise NotImplementedError()
    
    @update
    def render(self, parent):
        return self.build().render(parent)


class HtmlComponent:
    """
    Represents HTML components such as `div`, `button`, `span`, etc.
    """

    def __init__(
        self,
        tag: str,
        attributes: Mapping[str, str | C],
        *children
    ):
        """
        :param tag: indicates the beginning and end of an HTML element <tag> </tag>
        :param attributes: properties such as 'id', 'class', 'pys-onClick', etc.
        :param children: element rendered inside the component
        """
        self._tag = tag
        self._children = children
        self._attributes = attributes
        # self._id = attributes.get("id", "fluid-" + str(uuid.uuid4()))
        
    def render(self, parent: Optional[JsElement] = None) -> JsElement:
        console.log("re-render htmlcomponent")
        def _mount(el: JsElement) -> JsElement:
            return el if parent is None else parent.appendChild(el)

        self._element = document.createElement(self._tag)
        dom = _mount(self._element)

        for child in self._children:
            if isinstance(child, (str, float)):
                node = document.createTextNode(str(child))
                dom.appendChild(node)
            elif isinstance(child, bool):
                node = document.createTextNode('')
                dom.appendChild(node)
            elif isinstance(child, Callable):
                UpdateableStr(child).render(dom)
            elif isinstance(child, (HtmlComponent, Component)):
                child.render(dom)

        for key, value in self._attributes.items():
            if key == "class":
                self.set_class(value)
            else:
                self._element.setAttribute(key, value)
        
        return dom
    
    @update
    def set_class(self, value):
        func = value if isinstance(value, Callable) else (lambda: value)
        self._element.setAttribute("class", func())


