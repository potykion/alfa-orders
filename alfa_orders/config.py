from dataclasses import dataclass


@dataclass
class AlfaConfig:
    HOST = "https://engine.paymentgate.ru"
    RETRY_SECONDS = 60
    PAGE_SIZE = 100
    MAX_FUTURES = 10
