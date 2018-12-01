from typing import Optional

import collections
import os
import sys
import time

from graphviz import Digraph

from .tracer import Tracer


class Snarl:
    def __init__(self, whitelist = None, blacklist = None, timer = time.perf_counter_ns):
        self.whitelist = whitelist
        self.blacklist = blacklist

        self.was_called_by = collections.defaultdict(lambda: collections.defaultdict(int))

        self.timer = timer
        self.total_time = collections.defaultdict(int)
        self.own_time = collections.defaultdict(int)
        self.func_start_times = {}

        self.trace_function = Tracer(self)

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
        name: Optional[str] = None,
        call_counts: bool = True,
        timing: bool = True,
        format: str = 'png',
        dpi: int = 600,
    ):
        g = Digraph(
            name or 'snarl',
            graph_attr = {
                'dpi': str(dpi),
            },
            node_attr = {
                'fontname': 'Courier New',
                'shape': 'box',
            },
            edge_attr = {
                'fontname': 'Courier New',
            },
        )
        g.format = format

        func_names = set(k.name for k in self.was_called_by)

        try:
            common = os.path.dirname(os.path.commonpath(k.file_name for k in self.was_called_by))
            paths = (os.path.relpath(k.file_name, start = common).replace(r'\ '[0], r'\\') for k in self.was_called_by.keys())
        except ValueError:
            paths = (k.file_name.replace(r'\ '[0], r'\\') for k in self.was_called_by.keys())

        for k, path in zip(self.was_called_by.keys(), paths):
            label_lines = [
                rf'{k.name}',
                rf'{path}:{k.line_number}',
            ]

            if timing:
                label_lines.append(rf'Total: {fmt_ns(self.total_time[k])} | Own: {fmt_ns(self.own_time[k])}')

            g.node(
                k.name,
                label = r'\n'.join(label_lines),
            )

        for k, v in self.was_called_by.items():
            for func, count in v.items():
                if func in func_names:
                    g.edge(func, k.name, label = str(f' {count:,}') if call_counts else None)

        return g


units = ('ns', 'us', 'ms', 's')


def fmt_ns(t):
    for unit in units[:-1]:
        if t < 1000:
            return f'{t:.3f} {unit}'
        t /= 1000
    return f'{t:.3f} {units[-1]}'
