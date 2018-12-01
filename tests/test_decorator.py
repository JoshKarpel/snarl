import pytest

import snarl


def test_decorator_without_call():
    @snarl.snarled
    def foo():
        pass

    assert isinstance(foo.snarl, snarl.Snarl)


def test_decorator_with_empty_call():
    @snarl.snarled()
    def foo():
        pass

    assert isinstance(foo.snarl, snarl.Snarl)


def test_decorator_with_one_positional_call():
    with pytest.raises(snarl.exceptions.InvalidDecoratorUsage):
        @snarl.snarled(['foo'])
        def foo():
            pass


def test_decorator_with_two_positional_call():
    with pytest.raises(snarl.exceptions.InvalidDecoratorUsage):
        @snarl.snarled(['foo'], ['bar'])
        def foo():
            pass


def test_decorator_with_keyword_call():
    @snarl.snarled(whitelist = ['foo'])
    def foo():
        pass

    assert isinstance(foo.snarl, snarl.Snarl)
    assert foo.snarl.whitelist == ['foo']
