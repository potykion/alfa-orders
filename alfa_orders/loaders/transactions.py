import datetime as dt
import time
from enum import Enum

from typing import Dict, List

import requests

from alfa_orders.columns import TransactionColumns
from alfa_orders.config import AlfaConfig
from alfa_orders.loaders.base import BaseLoader
from alfa_orders.models import AlfaFutureResult, AlfaFuture
from alfa_orders.utils import timestamp_now

# see data/transaction.json and data/transaction_columns.json for order fields
Transaction = Dict


class TransactionStatus(Enum):
    DEPOSITED = "DEPOSITED"
    REFUNDED = "REFUNDED"


class TransactionLoader(BaseLoader[Transaction]):
    DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
    columns = TransactionColumns

    def __init__(self, session: requests.Session, config: AlfaConfig, statuses: List[TransactionStatus] = None):
        super().__init__(session, config)
        self.statuses: List[TransactionStatus] = statuses or [TransactionStatus.DEPOSITED, TransactionStatus.REFUNDED]

    def _get_future(self, from_date: dt.datetime, to_date: dt.datetime, offset: int = 0) -> AlfaFuture:
        shift = dt.timedelta(hours=3 if self.config.UTC_3_SEARCH else 0)
        alfa_from_date = (from_date - shift).strftime(self.DATETIME_FORMAT)
        alfa_to_date = (to_date - shift).strftime(self.DATETIME_FORMAT)

        url = f"{self.config.HOST}/mportal/mvc/transaction"
        params = {"_dc": timestamp_now()}
        data = {
            "start": offset,
            "limit": self.config.PAGE_SIZE,
            "dateFrom": alfa_from_date,
            "dateTo": alfa_to_date,
            "orderStateStr": ",".join(self.statuses),
            "page": '1',
            "dateMode": "CREATION_DATE",
            "merchants": "",
        }
        response = self.session.post(url, data, params=params)
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def _get_by_future(self, future: AlfaFuture):
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
