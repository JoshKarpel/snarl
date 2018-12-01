import functools

from . import snarl, exceptions


def snarled(*func, **kwargs):
    if len(func) > 1:
        raise exceptions.InvalidDecoratorUsage('snarled can only have one positional argument: the function to be decorated')

    s = snarl.Snarl(**kwargs)

    if len(func) == 0:
        return lambda f: make_wrapper(f, s)

    elif len(func) == 1:
        func = func[0]

        if not callable(func):
            raise exceptions.InvalidDecoratorUsage('the function you tried to decorate was not actually a function!')

        return make_wrapper(func, s)


def make_wrapper(func, snarl):
    setattr(func, 'snarl', snarl)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with func.snarl:
            return func(*args, **kwargs)

    return wrapper
