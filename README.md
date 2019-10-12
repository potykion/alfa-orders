# alfa-orders

Lib for loading AlfaBank orders from https://engine.paymentgate.ru

Usage:

```python
import datetime as dt
from alfa_orders.api import AlfaService

username, password = ("**********", "**********")
service = AlfaService(username, password)

from_date, to_date = dt.datetime(2019, 9, 1), dt.datetime(2019, 10, 1)
transactions = list(service.get_transactions(from_date, to_date))
refunds = list(service.get_refunds(from_date, to_date))
```
