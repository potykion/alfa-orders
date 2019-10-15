import datetime as dt
from typing import Iterable, List

from alfa_orders.config import AlfaConfig
from alfa_orders.loaders.refunds import Refund, RefundLoader
from alfa_orders.loaders.transactions import TransactionLoader, Transaction, TransactionStatus
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
        self.username = username
        self.password = password
        self.config = config or AlfaConfig()

        if self.config.LAZY_SESSION_INIT:
            self.session = None
        else:
            self.session = self.init_session()

    def init_session(self):
        self.session = create_alfa_session(self.username, self.password, self.config)
        return self.session

    def get_transactions(
        self, from_date: dt.datetime, to_date: dt.datetime, statuses: List[TransactionStatus] = None
    ) -> Iterable[Transaction]:
        assert self.session
        return TransactionLoader(self.session, self.config, statuses)(from_date, to_date)

    def get_refunds(self, from_date: dt.datetime, to_date: dt.datetime) -> Iterable[Refund]:
        assert self.session
        return RefundLoader(self.session, self.config)(from_date, to_date)

