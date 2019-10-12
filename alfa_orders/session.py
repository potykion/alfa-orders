import requests
from alfa_orders.config import HOST


def create_alfa_session(username, password):
    session = requests.Session()
    session.headers = {
        "Accept-Language": "ru,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.97 "
                      "YaBrowser/15.9.2403.2152 (beta) Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{HOST}/mportal/",
        "Origin": f"{HOST}"
    }

    response = session.post(
        f"{HOST}/mportal/login",
        {"username": username, "password": password}
    )
    response.raise_for_status()

    return session