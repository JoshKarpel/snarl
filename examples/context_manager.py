from snarl import Snarl


def a():
    b()
    recurse(2)


def b():
    for _ in range(10):
        c()
    recurse(3)

    f = Foo()
    f.method(5)


def c():
    def inner():
        pass

    inner()


def recurse(n):
    if n == 0:
        return
    recurse(n - 1)


class Foo:
    def method(self, x):
        pass

    @classmethod
    def clsmethod(cls):
        return cls()


with Snarl() as snarl:
    a()
    recurse(5)

    Foo.clsmethod()

dot = snarl.dot(name = 'context_manager', format = 'png')
dot.render(view = True)
