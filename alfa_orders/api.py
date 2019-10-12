import datetime as dt
from typing import Iterable


from alfa_orders.config import AlfaConfig
from alfa_orders.loaders.refunds import Refund, RefundLoader
from alfa_orders.loaders.transactions import TransactionLoader, Transaction
from alfa_orders.session import create_alfa_session


class AlfaService:
    """
    Usage:
    >>> username, password = ("**********", "**********")
    >>> service = AlfaService(username, password)
    >>> from_date, to_date = dt.datetime(2019, 9, 1), dt.datetime(2019, 10, 1)
    >>> transactions = list(service.get_transactions(from_date, to_date))
    >>> refunds = list(service.get_refunds(from_date, to_date))
    """
    def __init__(self, username: str, password: str, config: AlfaConfig = None) -> None:
        self.config = config or AlfaConfig()
        self.session = create_alfa_session(username, password, self.config)

    def get_transactions(self, from_date: dt.datetime, to_date: dt.datetime) -> Iterable[Transaction]:
        return TransactionLoader(self.session, self.config)(from_date, to_date)

    def get_refunds(self, from_date: dt.datetime, to_date: dt.datetime) -> Iterable[Refund]:
        return RefundLoader(self.session, self.config)(from_date, to_date)

