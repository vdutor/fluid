
from fluid.signal import Signal
from fluid.components import *

current = Signal("foo")

btn_foo_on_click = lambda _: current.assign("foo")
btn_bar_on_click = lambda _: current.assign("bar")
btn_baz_on_click = lambda _: current.assign("baz")

txt = Text(
    text=lambda: f"pressed: {current()}",
    klass=lambda: "bg-black text-white p-2 my-4",
)

base_btn_style = "my-2 p-2 text-white border rounded"
btn_foo = Button(
    lambda: "foo",
    klass=lambda: f"{'bg-blue-600' if current() == 'foo' else 'bg-red-600'} {base_btn_style}",
    on_click="btn_foo_on_click"
)

btn_bar = Button(
    lambda: "bar",
    klass=lambda: f"{'bg-blue-600' if current() == 'bar' else 'bg-red-600'} {base_btn_style}",
    on_click="btn_bar_on_click"
)

btn_baz = Button(
    lambda: "baz",
    klass=lambda: f"{'bg-blue-600' if current() == 'baz' else 'bg-red-600'} {base_btn_style}",
    on_click="btn_baz_on_click"
)

List_(
    txt,
    btn_foo,
    btn_bar,
    btn_baz,
).render()