# Copyright 2022 (c) Vincent Dutordoir
# SPDX-License-Identifier: Apache-2.0

# type: ignore
import atexit
import os

from .signal import Computation, INode, Signal

__all__ = ["log"]

GRAPH = int(os.getenv("GRAPH", "0"))

# top_colors = {UnaryOps: "#c0c0c0", ReduceOps: "#8080ff", BinaryOps: "#c0c0c0", MovementOps: "#80ff80", ProcessingOps: "#ff8080"}
NODE_COLORS = {
    Signal: "#FFFF80",
    Computation: "#C0C0C0",
}
NODE_SHAPE = {Signal: "box", Computation: "ellipse"}

if GRAPH:
    import networkx as nx

    G = nx.DiGraph()

    def save_graph_exit():
        print("saving", G)
        nx.drawing.nx_pydot.write_dot(G, "/tmp/comp.dot")
        os.system("dot -Tsvg /tmp/comp.dot -o /tmp/comp.svg")

    atexit.register(save_graph_exit)

global_num_max = 0


def nm(x):
    global global_num_max
    if getattr(x, "global_num", None) is None:
        setattr(x, "global_num", global_num_max)
        global_num_max += 1
    return f"< {x.global_num} >"


def log(*nodes: INode):
    for node in nodes:
        _log(node)


def _log(root: INode):
    G.add_node(nm(root))

    def _style_node(cls):
        G.nodes[nm(root)]["fillcolor"] = NODE_COLORS[cls]
        G.nodes[nm(root)]["shape"] = NODE_SHAPE[cls]

        if isinstance(root, Signal):
            G.nodes[nm(root)]["label"] = str(root())
        elif isinstance(root, Computation):
            G.nodes[nm(root)]["label"] = root.name or "Anonymous comp."

        style = "filled"
        if isinstance(root, Signal) and root.computation is not None:
            style = "dashed, filled"
        G.nodes[nm(root)]["style"] = style

    if isinstance(root, Signal):
        _style_node(Signal)
    elif isinstance(root, Computation):
        _style_node(Computation)

    for child in root.get_children():
        G.add_node(nm(child))
        G.add_edge(nm(root), nm(child))
        log(child)
