import functools

from . import snarl


def snarled(func):
    func.snarl = snarl.Snarl()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with func.snarl:
            return func(*args, **kwargs)

    return wrapper
