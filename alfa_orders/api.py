import datetime as dt
from typing import Iterable

import requests

from alfa_orders.loaders.transactions import TransactionLoader, Transaction
from alfa_orders.session import create_alfa_session


class AlfaService:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.session = None

    def init_session(self) -> requests.Session:
        self.session = create_alfa_session(self.username, self.password)
        return self.session

    def get_transactions(self, from_date: dt.datetime, to_date: dt.datetime) -> Iterable[Transaction]:
        return TransactionLoader(self.session)(from_date, to_date)

    # def get_refunds(self, from_date: dt.datetime, to_date: dt.datetime) -> Iterable[Refund]:
    #     yield from self._get_orders(
    #         partial(self._get_refunds_future, from_date, to_date),
    #         self._get_refunds_by_future
    #     )

    # def _get_refunds_future(self, from_date: dt.datetime, to_date: dt.datetime, offset: int = 0) -> AlfaFuture:
