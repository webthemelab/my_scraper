# utils/http.py
# ─────────────────────────────────────────────────────────────
# Creates a reusable HTTP session with:
#   • Automatic retry on network failures (up to 3 times)
#   • Exponential backoff: waits 1s, 2s, 4s between retries
#   • Retries on server errors: 429, 500, 502, 503, 504
#   • A browser-like User-Agent header so sites don't block us
# ─────────────────────────────────────────────────────────────

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session() -> requests.Session:
    """
    Build and return a requests Session with retry logic built in.

    Usage:
        session = create_session()
        response = session.get("https://example.com", timeout=(5, 20))
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=3,                            # max 3 attempts total
        backoff_factor=1,                   # wait 1s, 2s, 4s between retries
        status_forcelist=[429, 500, 502, 503, 504],  # retry on these HTTP codes
        allowed_methods=["GET"],            # only retry GET requests
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # A real browser User-Agent stops most basic bot-detection blocks
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    })

    return session
