import os
import sys
import collections
from pathlib import Path
from dataclasses import dataclass

from graphviz import Digraph


def get_file_names_recursively(path: Path):
    for entry in os.scandir(path):
        if entry.is_file(follow_symlinks = False):
            yield entry.path
        elif entry.is_dir():
            yield from get_file_names_recursively(entry.path)


SNARL_FILES = set(p for p in get_file_names_recursively(Path(__file__).parent) if '__pycache__' not in p)


@dataclass(frozen = True)
class Func:
    name: str
    file_name: str
    line_number: int


class TraceFunction:
    def __init__(self, snarl):
        self.snarl = snarl

    def __call__(self, frame, event, arg):
        print(event)
        print(f'frame: {get_function_name(frame)} in {get_file_name(frame)}, child of {get_function_name(get_parent_frame(frame))}')

        if event == 'call':
            # info = inspect.getframeinfo(frame)
            file_name = get_file_name(frame)
            if file_name in SNARL_FILES:
                return

            func = Func(
                name = get_function_name(frame),
                file_name = get_file_name(frame),
                line_number = frame.f_lineno,
            )

            self.snarl.was_called_by[func][get_function_name(get_parent_frame(frame))] += 1


class Snarl:
    def __init__(self):
        self.trace_function = TraceFunction(self)

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

    def dot(self):
        g = Digraph(
            'snarl',
            node_attr = {'fontname': 'Courier New'},
            edge_attr = {'fontname': 'Courier New'},
        )

        common = os.path.dirname(os.path.commonpath(k.file_name for k in self.was_called_by))

        for k in self.was_called_by.keys():
            path = os.path.relpath(k.file_name, start = common).replace(r'\ '[0], r'\\')
            g.node(k.name, label = rf'{k.name}\n{path}:{k.line_number}')

        g.node('<module>', label = '__main__')

        for k, v in self.was_called_by.items():
            for func, count in v.items():
                g.edge(func, k.name, label = str(f' {count}'))

        return g


def get_parent_frame(frame):
    return frame.f_back


def get_function_name(frame):
    return frame.f_code.co_name


def get_file_name(frame):
    return frame.f_code.co_filename
