from dataclasses import dataclass


@dataclass
class AlfaConfig:
    HOST: str = "https://engine.paymentgate.ru"
    RETRY_SECONDS: int = 60
    PAGE_SIZE: int = 100
    MAX_FUTURES: int = 10
    PARSE_TIMESTAMP: bool = False
    PARSE_TIMESTAMP_AS_UTC3: bool = False
    MAP_RUSSIAN_COLUMNS: bool = False
    UTC_3_SEARCH: bool = True
