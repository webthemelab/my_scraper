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
        "div[class*='__salonAddress']",
        "[class*='__salonAddress']",
        "span[class*='__locationText']",
        "[class*='__locationText']",
    ],
    "updated_date": [
        "time[datetime]",
        "time",
    ],
}

REQUIRED_FIELDS = ["page_url", "salon_name", "staff_name"]


class MinimoScraper(BaseScraper):
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

    def clean_location(self, location):
        if not location:
            return None

        return (
            location
            .replace("(地図)", "")
            .replace("地図", "")
            .strip()
        )

    def parse(self, soup: BeautifulSoup, url: str) -> dict:
        location = self.get_text(soup, SELECTORS["location"])

        item = {
            "page_url": url,
            "salon_name": self.get_text(soup, SELECTORS["salon_name"]),
            "salon_kana": self.get_text(soup, SELECTORS["salon_kana"]),
            "staff_name": self.get_text(soup, SELECTORS["staff_name"]),
            "rating": self.get_text(soup, SELECTORS["rating"]),
            "location": self.clean_location(location),
            "updated_date": self.get_text(soup, SELECTORS["updated_date"]),
        }

        missing = [f for f in REQUIRED_FIELDS if not item.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return item


        