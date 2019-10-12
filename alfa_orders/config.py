from dataclasses import dataclass


@dataclass
class AlfaConfig:
    HOST = "https://engine.paymentgate.ru"
    ALFA_DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
    RETRY_SECONDS = 60
    PAGE_SIZE = 100
    MAX_FUTURES = 10
