import os
from pathlib import Path
from dataclasses import dataclass


def get_file_names_recursively(path: Path):
    for entry in os.scandir(path):
        if entry.is_file(follow_symlinks = False):
            yield entry.path
        elif entry.is_dir():
            yield from get_file_names_recursively(entry.path)


SNARL_FILES = set(p for p in get_file_names_recursively(Path(__file__).parent) if '__pycache__' not in p)

COMPREHENSIONS = ('<listcomp>', '<dictcomp>', '<setcomp>', '<genexpr>')


@dataclass(frozen = True)
class Func:
    name: str
    file_name: str
    line_number: int


class Tracer:
    def __init__(self, snarl):
        self.snarl = snarl

    def __call__(self, frame, event, arg):
        if event == 'call':
            file_name = get_file_name(frame)
            if file_name in SNARL_FILES or file_name == '':
                return

            function_name = get_function_name(frame)
            if function_name in COMPREHENSIONS:
                return
            func = Func(
                name = function_name,
                file_name = file_name,
                line_number = get_line_number(frame),
            )

            parent_frame = get_parent_frame(frame)
            if self.snarl.whitelist is not None and all(wl in file_name for wl in self.snarl.whitelist):
                return
            if self.snarl.blacklist is not None and any(bl in file_name for bl in self.snarl.blacklist):
                return
            parent_function_name = get_function_name(parent_frame)
            self.snarl.was_called_by[func][parent_function_name] += 1


def get_parent_frame(frame):
    f = frame.f_back
    if get_function_name(f) in COMPREHENSIONS:
        f = f.f_back

    return f


def get_function_name(frame):
    code = frame.f_code
    if len(code.co_varnames) > 0:
        if code.co_varnames[0] == 'self':  # method
            return f'{type(frame.f_locals["self"]).__name__}.{code.co_name}'
        elif code.co_varnames[0] == 'cls':  # classmethod
            return f'{frame.f_locals["cls"].__name__}.{code.co_name}'
    return code.co_name


def get_file_name(frame):
    return frame.f_code.co_filename


def get_line_number(frame):
    return frame.f_code.co_firstlineno
