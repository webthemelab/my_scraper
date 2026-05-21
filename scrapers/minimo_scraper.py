# scrapers/minimo_scraper.py
# ─────────────────────────────────────────────────────────────
# Scraper for minimodel.jp profiles.
#
# This file only does TWO things:
#   1. Lists the URLs to visit
#   2. Defines how to read data from one page
#
# All the hard work (retry, delay, error handling, logging)
# is handled automatically by BaseScraper.
# ─────────────────────────────────────────────────────────────

from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


# CSS selectors — if the website changes its HTML, update these
# SELECTORS = {
#     "salon_name":   "[class*='__salonName']",
#     "salon_kana":   "[class*='__salonNameKana']",
#     "staff_name":   [
#         "h1[class*='__artistName'] > span",  # try this first
#         "[class*='__artistName']",            # fallback if first not found
#     ],
#     "rating":       "[class*='__value']",
#     "location":     "[class*='__locationText']",
#     "updated_date": "time",
# }
SELECTORS = {
    "salon_name": [
        "span[class*='__salonName']",
        "[class*='__salonName']",
    ],

    "salon_kana": [
        "span[class*='__salonNameKana']",
        "[class*='__salonNameKana']",
    ],

    "staff_name": [
        "a[class*='__artistName']",
        "h1[class*='__artistNameArea'] a[href*='/r/']",
        "[class*='__artistName']",
    ],

    "rating": [
        "span[class*='__value']",
        "[class*='__ratingStar'] [class*='__value']",
    ],

    "location": [
        "span[class*='__locationText']",
        "[class*='__locationText']",
    ],

    "updated_date": [
        "time[datetime]",
        "time",
    ],
}

# Required fields — if any are missing, the row is skipped with an error
REQUIRED_FIELDS = ["page_url", "salon_name", "staff_name"]


class MinimoScraper(BaseScraper):
    """
    Scrapes staff profile pages from minimodel.jp.

    To add more URLs, just add them to the list below.
    To scrape a different website, create a new file like this one.
    """

    urls = [
        "https://minimodel.jp/r/af51gWH",
        "https://minimodel.jp/r/Hwek6aD",
        "https://minimodel.jp/r/ei8HT1b",
        "https://minimodel.jp/r/eGn8fpC",
        "https://minimodel.jp/r/s9y11uv",
        "https://minimodel.jp/r/IOOCAXj",
        "https://minimodel.jp/r/Go7wY1Q",
        "https://minimodel.jp/r/2b51bWB",
        "https://minimodel.jp/r/qGY13rj",
        "https://minimodel.jp/r/lGtQ1Sd",
        "https://minimodel.jp/r/gLb3Jcm",
        "https://minimodel.jp/r/hGODr6k",
    ]

    def parse(self, soup: BeautifulSoup, url: str) -> dict:
        """
        Read data from one profile page.
        Returns a dict with all the fields we want to save.
        """
        item = {
            "page_url":     url,
            "salon_name":   self.get_text(soup, SELECTORS["salon_name"]),
            "salon_kana":   self.get_text(soup, SELECTORS["salon_kana"]),
            "staff_name":   self.get_text(soup, SELECTORS["staff_name"]),
            "rating":       self.get_text(soup, SELECTORS["rating"]),
            "location":     self.get_text(soup, SELECTORS["location"]),
            "updated_date": self.get_text(soup, SELECTORS["updated_date"]),
        }

        # Check that the important fields are not empty
        missing = [f for f in REQUIRED_FIELDS if not item.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return item
