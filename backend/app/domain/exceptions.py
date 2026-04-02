class DomainException(Exception):
    """领域层基础异常"""
    pass


class OrderNotFoundException(DomainException):
    pass


class InsufficientPositionException(DomainException):
    pass


class InvalidOrderStateException(DomainException):
    pass


class StrategyNotFoundException(DomainException):
    pass
