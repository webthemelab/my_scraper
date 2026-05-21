# db/connection.py
# ─────────────────────────────────────────────────────────────
# Reads database credentials from your .env file and returns
# a live PostgreSQL connection.
#
# Important:
#   • Credentials NEVER appear in this file — they come from .env
#   • If any required variable is missing, we raise a clear error
#     instead of crashing with a confusing message later
# ─────────────────────────────────────────────────────────────

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # reads your .env file into os.environ


def get_db_config() -> dict:
    """
    Read DB credentials from environment variables.
    Raises a clear EnvironmentError if anything is missing.
    """
    required = ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    missing = [key for key in required if not os.getenv(key)]

    if missing:
        raise EnvironmentError(
            f"Missing environment variables: {', '.join(missing)}\n"
            f"Copy .env.example to .env and fill in your values."
        )

    return {
        "host":     os.environ["PGHOST"],
        "database": os.environ["PGDATABASE"],
        "user":     os.environ["PGUSER"],
        "password": os.environ["PGPASSWORD"],
        "port":     os.environ.get("PGPORT", "5432"),
        # "prefer"  = use SSL if available (good for local dev)
        # "require" = always use SSL (use this for remote/production DBs)
        "sslmode":  os.environ.get("PGSSLMODE", "prefer"),
    }


def get_connection():
    """
    Open and return a PostgreSQL connection.

    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    """
    config = get_db_config()
    return psycopg2.connect(**config)
