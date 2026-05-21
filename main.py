# main.py
# ─────────────────────────────────────────────────────────────
# Entry point — run this file to start the scraper:
#
#     python main.py
#
# What it does, step by step:
#   1. Make sure the database tables exist
#   2. Run the Minimo scraper
#   3. Save results to JSON, CSV, and XML files
#   4. Save results to PostgreSQL (upsert — no duplicates)
#   5. Log any failed URLs to the database and to a JSON file
#   6. Print a summary at the end
#
# Exit codes:
#   0 = everything worked
#   1 = some URLs failed or the database save failed
# ─────────────────────────────────────────────────────────────

import sys

from scrapers.minimo_scraper import MinimoScraper
from db.queries import ensure_tables_exist, save_profiles, save_failed_urls
from exports.exporter import save_json, save_csv, save_xml, save_failures
from utils.logger import logger


def main():
    logger.info("=" * 50)
    logger.info("Scraper starting")
    logger.info("=" * 50)

    # ── Step 1: Make sure database tables exist ──────────────
    try:
        ensure_tables_exist()
    except Exception as e:
        logger.error(f"Could not connect to database: {e}")
        logger.error("Check your .env file and make sure PostgreSQL is running.")
        sys.exit(1)

    # ── Step 2: Run the scraper ──────────────────────────────
    scraper = MinimoScraper()
    data, failures = scraper.run()

    # ── Step 3: Save to flat files ───────────────────────────
    if data:
        save_json(data)
        save_csv(data)
        save_xml(data)

    if failures:
        save_failures(failures)

    # ── Step 4: Save to PostgreSQL ───────────────────────────
    db_ok = True
    try:
        save_profiles(data)
        save_failed_urls(failures)
    except Exception as e:
        logger.error(f"Database save failed: {e}")
        db_ok = False

    # ── Step 5: Print summary ────────────────────────────────
    logger.info("=" * 50)
    logger.info(f"Scraped successfully : {len(data)}")
    logger.info(f"Failed               : {len(failures)}")
    logger.info(f"Database save        : {'OK' if db_ok else 'FAILED'}")
    logger.info("=" * 50)

    # Exit with code 1 if anything went wrong
    # (useful for cron jobs and CI systems that check exit codes)
    if failures or not db_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
