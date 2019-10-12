import datetime as dt
from typing import Iterable


from alfa_orders.config import AlfaConfig
from alfa_orders.loaders.transactions import TransactionLoader, Transaction
from alfa_orders.session import create_alfa_session


class AlfaService:
    def __init__(self, username: str, password: str, config: AlfaConfig = None) -> None:
        self.config = config or AlfaConfig()
        self.session = create_alfa_session(username, password, self.config)

    def get_transactions(self, from_date: dt.datetime, to_date: dt.datetime) -> Iterable[Transaction]:
        return TransactionLoader(self.session, self.config)(from_date, to_date)

    # def get_refunds(self, from_date: dt.datetime, to_date: dt.datetime) -> Iterable[Refund]:
    #     yield from self._get_orders(
    #         partial(self._get_refunds_future, from_date, to_date),
    #         self._get_refunds_by_future
    #     )

    # def _get_refunds_future(self, from_date: dt.datetime, to_date: dt.datetime, offset: int = 0) -> AlfaFuture:
