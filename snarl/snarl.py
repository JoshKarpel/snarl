import collections
import os
import sys

from graphviz import Digraph

from .tracer import Tracer


class Snarl:
    def __init__(self, whitelist = None, blacklist = None):
        self.trace_function = Tracer(self)
        self.whitelist = whitelist
        self.blacklist = blacklist

        self.was_called_by = collections.defaultdict(lambda: collections.defaultdict(int))

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        sys.settrace(self.trace_function)

    def stop(self):
        sys.settrace(None)

    def dot(
        self,
        call_counts: bool = True,
        dpi: int = 600,
    ):
        g = Digraph(
            'snarl',
            graph_attr = {
                'dpi': str(dpi),
            },
            node_attr = {
                'fontname': 'Courier New',
            },
            edge_attr = {
                'fontname': 'Courier New',
            },
        )

        try:
            common = os.path.dirname(os.path.commonpath(k.file_name for k in self.was_called_by))
            paths = (os.path.relpath(k.file_name, start = common).replace(r'\ '[0], r'\\') for k in self.was_called_by.keys())
        except ValueError:
            paths = (k.file_name.replace(r'\ '[0], r'\\') for k in self.was_called_by.keys())

        for k, path in zip(self.was_called_by.keys(), paths):
            g.node(k.name, label = rf'{k.name}\n{path}:{k.line_number}')

        g.node('<module>', label = '__main__')

        for k, v in self.was_called_by.items():
            for func, count in v.items():
                g.edge(func, k.name, label = str(f' {count}') if call_counts else None)

        return g
