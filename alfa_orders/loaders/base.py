import datetime as dt
from abc import abstractmethod
from itertools import count
from typing import Iterable, Generic

from more_itertools import flatten, chunked

from alfa_orders.models import AlfaFuture, T


class BaseLoader(Generic[T]):
    def __init__(self, session, config):
        self.session = session
        self.config = config

    def __call__(self, from_date, to_date):
        yield from self._load(from_date, to_date)

    def _load(self, from_date, to_date):
        futures = (self._get_future(from_date, to_date, offset) for offset in count(0, self.config.PAGE_SIZE))
        future_batches = chunked(futures, self.config.MAX_FUTURES)
        order_batches = (
            tuple(flatten(map(self._get_by_future, batch)))
            for batch in future_batches
        )
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
