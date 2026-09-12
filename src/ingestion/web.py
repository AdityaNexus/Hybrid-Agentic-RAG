from urllib.parse import urlparse

import httpx

def validate_url(url:str)->None:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"invalid url scheme: {parsed.scheme}")

    if parsed.netloc == "":
        raise ValueError(f"invalid url netloc: {parsed.netloc}")


def fetch_url(url:str)->bytes:
    validate_url(url)

    response = httpx.get(
        url,
        follow_redirects = True,
        timeout = 30.0,
    )

    response.raise_for_status()
    return response.content