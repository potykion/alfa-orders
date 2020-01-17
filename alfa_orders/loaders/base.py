import datetime as dt
from abc import abstractmethod
from functools import partial
from itertools import count
from typing import Generic, Iterable

import requests
from more_itertools import flatten, chunked
from toolz import pipe

from alfa_orders.config import AlfaConfig
from alfa_orders.models import AlfaFuture, T


class BaseLoader(Generic[T]):
    def __init__(self, session: requests.Session, config: AlfaConfig):
        self.session = session
        self.config = config
        self.post_processors = []
        if config.PARSE_TIMESTAMP:
            from alfa_orders.processors import TimestampProcessor
            self.post_processors.append(TimestampProcessor(self, self.config))
        if config.PARSE_AMOUNT:
            from alfa_orders.processors import ParseAmountProcessor
            self.post_processors.append(ParseAmountProcessor(self, self.config))
        # should be in the end
        if config.MAP_RUSSIAN_COLUMNS:
            from alfa_orders.processors import RussianColumnProcessor
            self.post_processors.append(RussianColumnProcessor(self, self.config))

    def __call__(self, from_date, to_date):
        yield from self._load(from_date, to_date)

    @property
    @abstractmethod
    def columns(self):
        pass

    def _load(self, from_date, to_date):
        # делаем фьюча-батчи:
        #   делаем оффсеты (0, 100, ...),
        #   оффсеты -> фьючи - асинхронно берем заказы за период с оффсетом,
        #   фьючи -> фьюча-батчи: [f1, f2, f3, f4] -> [[f1, f2], [f3, f4]]
        future_batches = pipe(
            count(0, self.config.PAGE_SIZE),
            lambda offsets: (self._get_future(from_date, to_date, offset) for offset in offsets),
            lambda futures: chunked(futures, self.config.MAX_FUTURES)
        )
        # для каждого фьюча-батча:
        #   получаем заказы,
        #   делаем пост-обработку,
        #   уменьшаем размерность: [[o1, o2], [o3, o4]] -> [o1, o2, o3, o4],
        #   конвертим в кортеж
        order_batches = (
            pipe(
                batch,
                partial(map, self._get_by_future),
                partial(map, self._post_process),
                flatten,
                tuple
            )
            for batch in future_batches
        )
        # отдаем заказы, пока они есть
        for batch in order_batches:
            yield from batch
            if len(batch) < self.config.PAGE_SIZE * self.config.MAX_FUTURES:
                break

    @abstractmethod
    def _get_future(self, from_date: dt.datetime, to_date: dt.datetime, offset: int = 0) -> AlfaFuture:
        pass

    @abstractmethod
    def _get_by_future(self, future: AlfaFuture) -> Iterable[T]:
        pass

    def _post_process(self, orders: Iterable[T]) -> Iterable[T]:
        for proc in self.post_processors:
            orders = proc(orders)
        return orders
