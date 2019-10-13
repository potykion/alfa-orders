import datetime as dt
from typing import Optional


def timestamp_now() -> int:
    return int(dt.datetime.now().timestamp())


def parse_timestamp(timestamp: Optional[int], as_utc3: bool = False) -> Optional[dt.datetime]:
    if not timestamp:
        return timestamp

    datetime = dt.datetime.utcfromtimestamp(timestamp / 1000)

    if as_utc3:
        datetime += dt.timedelta(hours=3)

    return datetime
