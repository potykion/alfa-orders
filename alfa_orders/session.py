import requests


def create_alfa_session(username, password, config):
    session = requests.Session()
    session.headers = {
        "Accept-Language": "ru,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.97 "
                      "YaBrowser/15.9.2403.2152 (beta) Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{config.HOST}/mportal/",
        "Origin": f"{config.HOST}"
    }

    response = session.post(
        f"{config.HOST}/mportal/login",
        {"username": username, "password": password}
    )
    response.raise_for_status()

    return session