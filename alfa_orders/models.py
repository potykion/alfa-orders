from typing import TypeVar, List, Dict
from typing_extensions import TypedDict

T = TypeVar("T")

Offset = int

class AlfaFuture(TypedDict):
    # {'future': 'ea592611-558a-47ff-acd1-0f8a2f3e3ed0'}
    future: str


class AlfaFutureResult(TypedDict):
    done: bool
    success: bool
    data: List[Dict]