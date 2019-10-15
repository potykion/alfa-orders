import datetime as dt
import time
from typing import Dict, Iterable

from alfa_orders.columns import RefundColumns
from alfa_orders.loaders.base import BaseLoader
from alfa_orders.models import AlfaFuture, AlfaFutureResult
from alfa_orders.utils import timestamp_now

Refund = Dict

RefundStatuses = {
    "POSTED": "Отправлен"
}

class RefundLoader(BaseLoader[Refund]):
    DATETIME_FORMAT = "%d.%m.%Y %H:%M"
    columns = RefundColumns

    def _get_future(self, from_date: dt.datetime, to_date: dt.datetime, offset: int = 0) -> AlfaFuture:
        shift = dt.timedelta(hours=3 if self.config.UTC_3_SEARCH else 0)
        alfa_from_date = (from_date - shift).strftime(self.DATETIME_FORMAT)
        alfa_to_date = (to_date - shift).strftime(self.DATETIME_FORMAT)

        data = {
            'page': '1',
            'start': offset,
            'limit': self.config.PAGE_SIZE,
            'sort': 'refundDate',
            'dir': 'DESC',
            'dateFrom': alfa_from_date,
            'dateTo': alfa_to_date,
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
                return tuple(map(self.__map_refund_status, resp_json["data"]))

            time.sleep(1)
        else:
            raise LookupError(f"No orders for future {future['future']} in {self.config.RETRY_SECONDS} seconds")

    def __map_refund_status(self, refund: Dict) -> Dict:
        if self.config.MAP_REFUND_STATUS:
            refund["refundState"] = RefundStatuses[refund["refundState"]]

        return refund
