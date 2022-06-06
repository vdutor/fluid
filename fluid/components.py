from __future__ import annotations
from dataclasses import dataclass

from typing import Callable, List, Mapping, Optional, overload

import abc
import uuid

from .signal import update, watch
from .pyscript import Element, console, create


SAFE_ATTRIBUTES = {
    "klass": "class",
    "py_onclick": "pys-onClick"
}
"""
Certain HTML class attributes are no valid python variable names.
This mapping stores the translation between the valid variable names and the
HTML attributes.

.. code-block::

    btn = Button(..., py_onclick='func')

The keyword argument `py_onclick` is mapped to `pys-onClick` in the DOM.
"""

_TEMPLATE_NO_INNER_HTML = """
<{tag}{space}{attributes}></{tag}>
"""

_TEMPLATE_INNER_HTML = """
<{tag}{space}{attributes}>
{inner_html}
</{tag}>
"""

def _create_compoment(tag, inner_html, **kwargs):
    template = _TEMPLATE_NO_INNER_HTML if inner_html is None else _TEMPLATE_INNER_HTML
    return template.format(
        tag=tag,
        space=' ' if len(kwargs) > 0 else '',
        attributes=" ".join([f"{SAFE_ATTRIBUTES.get(key, key)}=\"{value}\"" for key, value in kwargs.items() if value is not None]),
        inner_html=inner_html or ''
    )



C = Callable[[], str]
"""
Type to represent a function which produces a string.
Typically, the function will contain `Signal`s.
"""

class HtmlComponent(abc.ABC):
    """
    Represents HTML components such as `div`, `button`, `span`, etc.
    """

    def __init__(self, tag: str, child: Optional["HtmlComponent" | List["HtmlComponent"] | C | str] = None, klass: Optional[C | str] = None, **attributes):
        """
        :param tag: indicates the beginning and end of an HTML element <tag> </tag>
        :param child: element rendered inside the component
        :param klass: class attributes of the component
        :param attributes: other class attributes
        """
        self._tag = tag
        self._child = child
        self._attributes = attributes
        self._id = "fluid-" + str(uuid.uuid4())
        self._rendered = False
        
        # make sure klass is a function
        if isinstance(klass, str):
            klass = lambda: klass
        self._klass = klass

        self._element = create(self._tag, self._id, self._klass())
        # self._klass_value = self._klass()
        console.log(self._element._element.classList.value)

        @watch
        def _update_inner_html():
            self._element.write(self._inner_html())
        
        @watch
        def _update_class():
            if not self._rendered:
                self._klass()
                return

            el = Element(self._id)
            old = el.element.classList.value
            el.remove_class(old.split(" "))
            el.add_class(self._klass().split(" "))

        
    def _inner_html(self) -> str:
        if isinstance(self._child, HtmlComponent):
            return self._child.__html__()
        if isinstance(self._child, str):
            return self._child
        if isinstance(self._child, Callable):
            return self._child()
        if self._child is None:
            return ''
        if isinstance(self._child, list):
            return " ".join(map(lambda x: x.__html__(), self._child))
        raise NotImplementedError()
    
    def __html__(self):
        self._rendered = True
        return _create_compoment(self._tag, self._inner_html(), id=self._id, klass=self._klass(), **self._attributes)
    

# class List_(HtmlComponent):
#     def __init__(self, *childeren: "HtmlComponent"):
#         super().__init__(childeren)

#     def render(self):
#         rendered_childeren = [
#            child.render() for child in self._child
#         ]
#         return " ".join(rendered_childeren)


class Div(HtmlComponent):
    def __init__(self, child: Optional["HtmlComponent" | List["HtmlComponent"] | C | str] = None, klass: Optional[C | str] = None, **attributes):
        """
        :param child: element rendered inside the component
        :param klass: class attributes of the component
        :param attributes: other class attributes
        """
        super().__init__("div", child, klass, **attributes)


class Span(HtmlComponent):

    def __init__(self, child: Optional["HtmlComponent" | List["HtmlComponent"] | C | str] = None, klass: Optional[C | str] = None, **attributes):
        """
        :param child: element rendered inside the component
        :param klass: class attributes of the component
        :param attributes: other class attributes
        """
        super().__init__("span", child, klass, **attributes)

    
class Button(HtmlComponent):

    def __init__(self, child: Optional["HtmlComponent" | List["HtmlComponent"] | C | str] = None, klass: Optional[C | str] = None, on_click: Optional[str] = None, **attributes):
        """
        :param child: (reactive) element(s) rendered inside the component
        :param klass: (reactive) class attributes of the component
        :param on_click: name of the callback to execute when button is clicked.
            The function needs to accepts `*args` and `**kwargs`. For example:

            .. code::

                def handle_on_click(*args, **kwargs):
                    # increases the count by one.
                    count.assign(count() + 1)

        :param attributes: other class attributes
        """
        super().__init__("button", child, klass, py_onclick=on_click, **attributes)
