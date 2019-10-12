import datetime as dt
import time
from functools import partial
from itertools import takewhile, count, repeat

import requests
from typing import List, Dict, Iterable

from more_itertools import flatten, chunked
from typing_extensions import TypedDict
from utils import timestamp_now

HOST = "https://engine.paymentgate.ru"
ALFA_DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
RETRY_SECONDS = 60
PAGE_SIZE = 100
MAX_FUTURES = 10

# see data/transaction.json and data/transaction_columns.json for order fields
Transaction = Dict


class AlfaFuture(TypedDict):
    # {'future': 'ea592611-558a-47ff-acd1-0f8a2f3e3ed0'}
    future: str


class AlfaFutureResult(TypedDict):
    done: bool
    success: bool
    data: List[Transaction]


class AlfaService:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.session = None

    def init_session(self) -> requests.Session:
        session = requests.Session()
        session.headers = {
            "Accept-Language": "ru,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.97 "
                          "YaBrowser/15.9.2403.2152 (beta) Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{HOST}/mportal/",
            "Origin": f"{HOST}"
        }

        response = session.post(
            f"{HOST}/mportal/login",
            {"username": self.username, "password": self.password}
        )
        response.raise_for_status()

        self.session = session
        return self.session

    def get_transactions(self, from_date: dt.datetime, to_date: dt.datetime) -> Iterable[Transaction]:
        request_transactions = partial(self._get_transactions_async, from_date, to_date)

        # 0, 100, 200, ...
        offsets = count(0, PAGE_SIZE)
        # request_transactions(0), request_transactions(100), ...
        transaction_requests = map(request_transactions, offsets)
        # [request_transactions(0), request_transactions(100), ...], [request_transactions(500), request_transactions(600), ...], ...
        transaction_request_batches = chunked(transaction_requests, MAX_FUTURES)
        # [trans_1, ..., trans_1000], [trans_1001, ..., trans_2000], ...
        transaction_batches = map(self._get_transactions_by_future_batch, transaction_request_batches)

        for batch in transaction_batches:
            yield from batch
            if len(batch) < PAGE_SIZE * MAX_FUTURES:
                break

    def _get_transactions_by_future_batch(self, future_batch: Iterable[AlfaFuture]):
        return tuple(flatten(map(self._get_transactions_by_future, future_batch)))

    def _get_transactions_by_future(self, future: AlfaFuture):
        print(future)
        url = f"{HOST}/mportal/mvc/transaction"
        params = {"_dc": timestamp_now()}
        data = future

        for _ in range(RETRY_SECONDS):
            resp = self.session.post(url, data, params=params)

            resp_json: AlfaFutureResult = resp.json()
            if resp_json["done"]:
                return resp_json["data"]

            time.sleep(1)
        else:
            raise LookupError(f"No orders for future {future['future']} in {RETRY_SECONDS} seconds")

    def _get_transactions_async(self, from_date: dt.datetime, to_date: dt.datetime, offset: int = 0) -> AlfaFuture:
        print(offset)
        url = f"{HOST}/mportal/mvc/transaction"
        params = {"_dc": timestamp_now()}
        data = {
            "start": offset,
            "limit": PAGE_SIZE,
            "dateFrom": from_date.strftime(ALFA_DATETIME_FORMAT),
            "dateTo": to_date.strftime(ALFA_DATETIME_FORMAT),
            "orderStateStr": "DEPOSITED,REFUNDED",
            "page": '1',
            "dateMode": "CREATION_DATE",
            "merchants": "",
        }
        response = self.session.post(url, data, params=params)
        response.raise_for_status()
        response_json = response.json()
        print(response_json)
        return response_json