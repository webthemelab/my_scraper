# scrapers/base_scraper.py
# ─────────────────────────────────────────────────────────────
# BaseScraper holds all the logic that every scraper shares:
#   • Creating the HTTP session
#   • Fetching a URL safely
#   • Tracking failures
#   • Looping through all URLs with a polite delay
#
# Each website gets its own subclass (e.g. MinimoScraper) that
# only needs to define:
#   • self.urls   → list of URLs to visit
#   • parse()     → how to extract data from one page's HTML
#
# This pattern means adding a new website = 1 new file,
# zero changes to existing code.
# ─────────────────────────────────────────────────────────────

import time
import random
from typing import List, Dict, Tuple, Optional

import requests
from bs4 import BeautifulSoup

from utils.http import create_session
from utils.logger import logger


class BaseScraper:
    """
    Inherit from this class to build a scraper for any website.

    Minimum required in your subclass:
        urls = ["https://...", "https://..."]

        def parse(self, soup: BeautifulSoup, url: str) -> dict:
            return { "field": soup.select_one(".selector").get_text() }
    """

    # Subclasses set this to their list of URLs
    urls: List[str] = []

    # Delay between requests (seconds). Randomised so we look less like a bot.
    min_delay: float = 1.0
    max_delay: float = 3.0

    def __init__(self):
        # One session is shared across all requests — more efficient
        self.session = create_session()

    # ── Override this in your subclass ──────────────────────────

    def parse(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Given a parsed HTML page, return a dict of the data you want.
        Must be implemented by each subclass.
        """
        raise NotImplementedError(
            "Your scraper must implement the parse() method."
        )

    # ── Shared logic (don't change these) ───────────────────────

    def get_text(self, soup: BeautifulSoup, selector) -> Optional[str]:
        """
        Find an element by CSS selector and return its text.
        selector can be a string OR a list of selectors to try in order.
        Returns None if nothing is found (instead of crashing).
        """
        # If given a list, try each selector until one works
        if isinstance(selector, list):
            for s in selector:
                element = soup.select_one(s)
                if element:
                    return element.get_text(strip=True)
            return None

        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None

    def fetch_page(self, url: str) -> BeautifulSoup:
        """
        Download a URL and return a parsed BeautifulSoup object.
        Raises an exception if the request fails (the caller handles it).
        """
        response = self.session.get(url, timeout=(5, 20))
        response.raise_for_status()     # raises on 4xx / 5xx errors
        response.encoding = "utf-8"
        return BeautifulSoup(response.text, "html.parser")

    def run(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Visit every URL, parse it, and return two lists:
            data      → successfully scraped items
            failures  → URLs that failed, with error details
        """
        # Remove duplicate URLs while keeping order
        unique_urls = list(dict.fromkeys(self.urls))

        data: List[Dict] = []
        failures: List[Dict] = []

        logger.info(f"Starting scrape — {len(unique_urls)} URLs")

        for url in unique_urls:
            try:
                soup = self.fetch_page(url)
                item = self.parse(soup, url)
                data.append(item)
                logger.info(f"✓ Scraped: {url}")

            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response else "unknown"
                logger.error(f"✗ HTTP {status}: {url}")
                failures.append({
                    "url":        url,
                    "error_type": "http_error",
                    "status":     status,
                    "msg":        str(exc),
                })

            except Exception as exc:
                logger.error(f"✗ Error on {url}: {exc}")
                failures.append({
                    "url":        url,
                    "error_type": "general_error",
                    "status":     None,
                    "msg":        str(exc),
                })

            # Polite delay between requests
            time.sleep(random.uniform(self.min_delay, self.max_delay))

        logger.info(f"Done — {len(data)} ok, {len(failures)} failed")
        return data, failures
