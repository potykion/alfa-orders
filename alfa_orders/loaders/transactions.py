import datetime as dt
import time
from functools import partial

from typing import Dict

from alfa_orders.loaders.base import BaseLoader
from alfa_orders.models import AlfaFutureResult, AlfaFuture
from alfa_orders.utils import timestamp_now

# see data/transaction.json and data/transaction_columns.json for order fields
Transaction = Dict

class TransactionLoader(BaseLoader[Transaction]):
    def __call__(self, from_date, to_date):
        yield from self._get_orders(
            partial(self._get_transactions_future, from_date, to_date),
            self._get_transactions_by_future
        )

    def _get_transactions_future(self, from_date: dt.datetime, to_date: dt.datetime, offset: int = 0) -> AlfaFuture:
        url = f"{self.config.HOST}/mportal/mvc/transaction"
        params = {"_dc": timestamp_now()}
        data = {
            "start": offset,
            "limit": self.config.PAGE_SIZE,
            "dateFrom": from_date.strftime(self.config.ALFA_DATETIME_FORMAT),
            "dateTo": to_date.strftime(self.config.ALFA_DATETIME_FORMAT),
            "orderStateStr": "DEPOSITED,REFUNDED",
            "page": '1',
            "dateMode": "CREATION_DATE",
            "merchants": "",
        }
        response = self.session.post(url, data, params=params)
        response.raise_for_status()
        response_json = response.json()
        return response_json


    def _get_transactions_by_future(self, future: AlfaFuture):
        url = f"{self.config.HOST}/mportal/mvc/transaction"
        params = {"_dc": timestamp_now()}
        data = future

        for _ in range(self.config.RETRY_SECONDS):
            resp = self.session.post(url, data, params=params)

            resp_json: AlfaFutureResult = resp.json()
            if resp_json["done"]:
                return resp_json["data"]

            time.sleep(1)
        else:
            raise LookupError(f"No orders for future {future['future']} in {self.config.RETRY_SECONDS} seconds")