from dataclasses import dataclass


@dataclass
class AlfaConfig:
    HOST: str = "https://engine.paymentgate.ru"
    RETRY_SECONDS: int = 60
    PAGE_SIZE: int = 100
    MAX_FUTURES: int = 10
    UTC_3_SEARCH: bool = True
    PARSE_TIMESTAMP: bool = False
    PARSE_TIMESTAMP_AS_UTC3: bool = False
    PARSE_AMOUNT: bool = False
    MAP_RUSSIAN_COLUMNS: bool = False
    MAP_REFUND_STATUS: bool = False
    LAZY_SESSION_INIT: bool = False
