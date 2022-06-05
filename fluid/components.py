from __future__ import annotations
from dataclasses import dataclass

from typing import Callable, List, Mapping

import abc
import uuid

from .signal import update, watch
from .pyscript import Element, console


SAFE_ATTRIBUTES = {
    "klass": "class",
    "py_onclick": "pys-onClick"
}

TEMPLATE_NO_INNER_HTML = """
<{tag}{space}{attributes}></{tag}>
"""

TEMPLATE_INNER_HTML = """
<{tag}{space}{attributes}>
{inner_html}
</{tag}>
"""

def create_compoment(tag, inner_html, **kwargs):
    template = TEMPLATE_NO_INNER_HTML if inner_html is None else TEMPLATE_INNER_HTML
    return template.format(
        tag=tag,
        space=' ' if len(kwargs) > 0 else '',
        attributes=" ".join([f"{SAFE_ATTRIBUTES.get(key, key)}=\"{value}\"" for key, value in kwargs.items() if value is not None]),
        inner_html=inner_html or ''
    )


# @dataclass
# class Component:
#     tag: str
#     attributes: Mapping[str, str]
#     inner_html: str

#     def add_attribute(self, **kwargs):
#         self.attributes = {**self.attributes, **kwargs}

#     def render


class HtmlComponent(abc.ABC):
    def __init__(self, child: "HtmlComponent" | List["HtmlComponent"] | str | None = None, klass: str | None = None, tag: str | None = None):
        self._child = child
        self._klass = klass
        self._tag = tag
        self._id = "fluid-" + str(uuid.uuid4())
        self._rendered = False
    
    def inner_html(self) -> str:
        if isinstance(self._child, HtmlComponent):
            return self._child.render()
        if isinstance(self._child, str):
            return self._child
        if isinstance(self._child, Callable):
            return self._child()
        if self._child is None:
            return ''
        raise NotImplementedError()
    
    def render(self):
        self._rendered = True
        return create_compoment(self._tag, self.inner_html(), id=self._id, klass=self._klass)
    

class List_(HtmlComponent):
    def __init__(self, *childeren: "HtmlComponent"):
        super().__init__(childeren)

    def render(self):
        rendered_childeren = [
           child.render() for child in self._child
        ]
        return " ".join(rendered_childeren)


class Div(HtmlComponent):
    def __init__(self, child: "HtmlComponent" | None, klass: str | None = None):
        super().__init__(child, klass, "div")


class Text(HtmlComponent):
    def __init__(self, text: Callable, klass: Callable):
        super().__init__(text(), klass(), "span")
        self._text_fn = text
        self._klass_fn = klass

        @watch
        def _update_inner_html():
            console.log("_update_inner_html")
            Element(self._id).write(self._text_fn())
        
        @watch
        def _update_class():
            old = self._klass
            new = self._klass_fn()
            if self._rendered:
                Element(self._id).remove_class(old)
                Element(self._id).add_class(new)

    def render(self):
        self._rendered = True
        return create_compoment(self._tag, self.inner_html(), id=self._id, klass=self._klass)
    
class Button(HtmlComponent):
    def __init__(self, child: Callable | HtmlComponent | str | None = None, klass: Callable | str | None = None, on_click: str | None = None):
        self._on_click = on_click
        super().__init__(child(), klass(), "button")

        self._child_fn = child
        self._klass_fn = klass

        @watch
        def _update_inner_html():
            console.log("_update_inner_html")
            Element(self._id).write(self._child_fn())
        
        @watch
        def _update_class():
            old = self._klass
            new = self._klass_fn()
            if self._rendered:
                Element(self._id).remove_class(old.split(" "))
                Element(self._id).add_class(new.split(" "))
            self._klass = new


    def render(self):
        self._rendered = True
        return create_compoment(self._tag, self.inner_html(), id=self._id, klass=self._klass, py_onclick=self._on_click)
