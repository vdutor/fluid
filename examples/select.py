
from fluid.signal import Signal
from fluid.components import *

current = Signal("foo")

btn_foo_on_click = lambda _: current.assign("foo")
btn_bar_on_click = lambda _: current.assign("bar")
btn_baz_on_click = lambda _: current.assign("baz")

txt = Span(
    lambda: f"pressed: {current()}",
    klass=lambda: "my-4",
)

base_btn_style = "my-2 p-2 text-white border rounded"
btn_foo = Button(
    "foo",
    klass=lambda: f"{'bg-blue-600' if current() == 'foo' else 'bg-red-600'} {base_btn_style}",
    on_click="btn_foo_on_click"
)

btn_bar = Button(
    "bar",
    klass=lambda: f"{'bg-blue-600' if current() == 'bar' else 'bg-red-600'} {base_btn_style}",
    on_click="btn_bar_on_click"
)

btn_baz = Button(
    "baz",
    klass=lambda: f"{'bg-blue-600' if current() == 'baz' else 'bg-red-600'} {base_btn_style}",
    on_click="btn_baz_on_click"
)

# map(lambda el: print(el.__html__()), [txt, btn_foo, btn_bar, btn_baz])
# List_(
#     txt,
#     btn_foo,
#     btn_bar,
#     btn_baz,
# ).render()

print(txt.__html__())
print(btn_foo.__html__())
print(btn_bar.__html__())
print(btn_baz.__html__())


console.log(current._subscribers)