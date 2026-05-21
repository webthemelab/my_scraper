# db/queries.py
# ─────────────────────────────────────────────────────────────
# All database read/write operations live here.
# The rest of the code just calls these functions — it never
# writes raw SQL anywhere else.
#
# Key concept — UPSERT (INSERT ... ON CONFLICT ... DO UPDATE):
#   • If this URL is new → insert a fresh row
#   • If this URL already exists → update it with the latest data
#   • This means running the scraper twice never creates duplicates
# ─────────────────────────────────────────────────────────────

from typing import List, Dict
from db.connection import get_connection
from utils.logger import logger


# ── SQL statements ────────────────────────────────────────────

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS minimo_profiles (
    page_url     TEXT PRIMARY KEY,
    salon_name   TEXT,
    salon_kana   TEXT,
    staff_name   TEXT,
    rating       TEXT,
    location     TEXT,
    updated_date TEXT,
    saved_at     TIMESTAMPTZ DEFAULT NOW()
);
"""
# page_url is PRIMARY KEY → PostgreSQL will never store the same URL twice.
# saved_at records exactly when we scraped each row.

UPSERT_SQL = """
    INSERT INTO minimo_profiles (
        page_url, salon_name, salon_kana, staff_name,
        rating, location, updated_date
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (page_url) DO UPDATE SET
        salon_name   = EXCLUDED.salon_name,
        salon_kana   = EXCLUDED.salon_kana,
        staff_name   = EXCLUDED.staff_name,
        rating       = EXCLUDED.rating,
        location     = EXCLUDED.location,
        updated_date = EXCLUDED.updated_date,
        saved_at     = NOW();
"""

CREATE_FAILED_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS failed_urls (
    id         SERIAL PRIMARY KEY,
    url        TEXT NOT NULL,
    error_type TEXT,
    status     TEXT,
    message    TEXT,
    failed_at  TIMESTAMPTZ DEFAULT NOW()
);
"""

INSERT_FAILED_SQL = """
    INSERT INTO failed_urls (url, error_type, status, message)
    VALUES (%s, %s, %s, %s);
"""


# ── Public functions ──────────────────────────────────────────

def ensure_tables_exist():
    """
    Create the tables if they don't exist yet.
    Safe to run every time — CREATE TABLE IF NOT EXISTS does nothing
    if the table is already there.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            cur.execute(CREATE_FAILED_TABLE_SQL)
    logger.debug("Tables verified / created.")


def save_profiles(data: List[Dict]):
    """
    Save (or update) a list of scraped profile dicts to PostgreSQL.
    Uses UPSERT so running this twice never creates duplicates.
    """
    if not data:
        logger.warning("save_profiles called with empty data — nothing to save.")
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            for item in data:
                cur.execute(UPSERT_SQL, (
                    item["page_url"],
                    item.get("salon_name"),
                    item.get("salon_kana"),
                    item.get("staff_name"),
                    item.get("rating"),
                    item.get("location"),
                    item.get("updated_date"),
                ))

    logger.info(f"Saved {len(data)} profiles to database.")


def save_failed_urls(failures: List[Dict]):
    """
    Log each failed URL to the failed_urls table so you can
    investigate and retry them later.
    """
    if not failures:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            for f in failures:
                cur.execute(INSERT_FAILED_SQL, (
                    f.get("url"),
                    f.get("error_type"),
                    str(f.get("status", "")),
                    f.get("msg"),
                ))

    logger.info(f"Logged {len(failures)} failed URLs to database.")
