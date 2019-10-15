from abc import abstractmethod
from typing import Iterable, Dict

from alfa_orders.config import AlfaConfig
from alfa_orders.loaders.base import BaseLoader
from alfa_orders.utils import parse_timestamp


class BaseProcessor:
    def __init__(self, loader: BaseLoader, config: AlfaConfig):
        self.loader = loader
        self.config = config

    @abstractmethod
    def __call__(self, orders: Iterable[Dict]) -> Iterable[Dict]:
        pass


class TimestampProcessor(BaseProcessor):
    def __call__(self, orders: Iterable[Dict]) -> Iterable[Dict]:
        return self._parse_timestamps(orders)

    def _parse_timestamps(self, orders: Iterable[Dict]) -> Iterable[Dict]:
        for order in orders:
            yield {
                **order,
                **{
                    field: parse_timestamp(value, self.config.PARSE_TIMESTAMP_AS_UTC3)
                    for field, value in order.items()
                    if "Date" in field
                }
            }


class RussianColumnProcessor(BaseProcessor):
    def __call__(self, orders: Iterable[Dict]) -> Iterable[Dict]:
        for order in orders:
            yield {self.loader.columns.get(field, field): value for field, value in order.items()}


class ParseAmountProcessor(BaseProcessor):
    def __call__(self, orders: Iterable[Dict]) -> Iterable[Dict]:
        for order in orders:
            yield {
                **order,
                **{
                    # '3500,00' > 3500
                    field: float(value.replace(",", ".")) if value else value
                    for field, value in order.items()
                    if "amount" in field.lower()
                }
            }