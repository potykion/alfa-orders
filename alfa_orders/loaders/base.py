from itertools import count
from typing import Iterable, Callable, Generic

from more_itertools import flatten, chunked

from alfa_orders.config import PAGE_SIZE, MAX_FUTURES
from alfa_orders.models import Offset, AlfaFuture, T


class BaseLoader(Generic[T]):
    def _get_orders(self, request_page: Callable[[Offset], AlfaFuture], fetch_page: Callable[[AlfaFuture], Iterable[T]]) -> Iterable[T]:
        # 0, 100, 200, ...
        offsets = count(0, PAGE_SIZE)
        # request_transactions(0), request_transactions(100), ...
        transaction_requests = map(request_page, offsets)
        # [request_transactions(0), request_transactions(100), ...], [request_transactions(500), request_transactions(600), ...], ...
        transaction_request_batches = chunked(transaction_requests, MAX_FUTURES)
        # [trans_1, ..., trans_1000], [trans_1001, ..., trans_2000], ...
        transaction_batches = (
            tuple(flatten(map(fetch_page, future_batch)))
            for future_batch in transaction_request_batches
        )

        for batch in transaction_batches:
            yield from batch
            if len(batch) < PAGE_SIZE * MAX_FUTURES:
                break