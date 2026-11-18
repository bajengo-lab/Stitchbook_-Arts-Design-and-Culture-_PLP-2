"""Check the database connection and required Stitchbook tables."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stitchbook.db import get_connection


def main() -> int:
    conn = get_connection()
    if conn is None:
        print("FAILED: could not connect. Check your .env file and certificate.")
        return 1

    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result is None or result[0] != 1:
            raise RuntimeError("SELECT 1 did not return 1.")

        cursor.execute("SHOW TABLES")
        tables = [row[0].lower() for row in cursor.fetchall()]

        missing = [t for t in ("customers", "orders") if t not in tables]
        if missing:
            print(f"Connected, but missing tables: {', '.join(missing)}")
            return 1

        print("Connection OK, tables found: customers, orders")
        return 0
    except Exception as e:
        print(f"FAILED while checking the database: {e}")
        return 1
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())