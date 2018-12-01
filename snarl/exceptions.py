class SnarlException(Exception):
    """Base exception for all Snarl exceptions."""
    pass


class InvalidDecoratorUsage(SnarlException):
    """The @snarled decorator was not used correctly."""
    pass
