from abc import abstractmethod
from typing import Iterable, Dict

from alfa_orders.config import AlfaConfig
from alfa_orders.utils import parse_timestamp


class BaseProcessor:
    @abstractmethod
    def __call__(self, orders: Iterable[Dict]) -> Iterable[Dict]:
        pass


class TimestampProcessor(BaseProcessor):
    def __init__(self, config: AlfaConfig):
        self.config = config

    def __call__(self, orders: Iterable[Dict]) -> Iterable[Dict]:
        return self._parse_timestamps(orders)

    def _parse_timestamps(self, transactions: Iterable[Dict]) -> Iterable[Dict]:
        for trans in transactions:
            yield {
                **trans,
                **{
                    field: parse_timestamp(value, self.config.PARSE_TIMESTAMP_AS_UTC3)
                    for field, value in trans.items()
                    if "Date" in field
                }
            }
