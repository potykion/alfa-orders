import datetime as dt
import time
from typing import Dict, Iterable

from alfa_orders.loaders.base import BaseLoader
from alfa_orders.models import AlfaFuture, AlfaFutureResult
from alfa_orders.utils import timestamp_now

Refund = Dict


class RefundLoader(BaseLoader[Refund]):
    DATETIME_FORMAT = "%d.%m.%Y %H:%M"

    def _get_future(self, from_date: dt.datetime, to_date: dt.datetime, offset: int = 0) -> AlfaFuture:
        data = {
            'page': '1',
            'start': offset,
            'limit': self.config.PAGE_SIZE,
            'sort': 'refundDate',
            'dir': 'DESC',
            'dateFrom': (from_date - dt.timedelta(hours=3)).strftime(self.DATETIME_FORMAT),
            'dateTo':   (to_date - dt.timedelta(hours=3)).strftime(self.DATETIME_FORMAT),
        }
        response = self.session.post(
            f"{self.config.HOST}/mportal/mvc/refunds/search",
            params={"_dc": timestamp_now()},
            data=data
        )
        return response.json()

    def _get_by_future(self, future: AlfaFuture) -> Iterable[Refund]:
        url = f"{self.config.HOST}/mportal/mvc/refunds/search"
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

