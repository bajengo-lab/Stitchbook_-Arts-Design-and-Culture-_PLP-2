"""
Run this script once to verify that Stitchbook can connect to MySQL
and that the required tables (customers and orders) exist.
"""

import os
import sys
import traceback
from typing import Any, cast

from database.connection import get_connection


def main():
    """
    Tests the database connection and checks that both tables are present.
    """
    connection = get_connection()
    app_env = os.getenv("APP_ENV", "local").strip().lower()
    if app_env == "deployed":
        db_host = os.getenv("AIVEN_DB_HOST", "")
    else:
        db_host = os.getenv("LOCAL_DB_HOST", "localhost")

    if connection is None:
        sys.stderr.write(
            f"check_connection: could not connect (APP_ENV={app_env}, host={db_host})\n"
        )
        print(
            f"Connection test failed: Could not open a connection (mode: {app_env}, host: {db_host})."
        )
        return

    cursor = None
    try:
        cursor = connection.cursor()

        # Check which database and user are active
        cursor.execute("SELECT DATABASE(), CURRENT_USER()")
        row = cast(tuple[Any, ...], cursor.fetchone())
        current_db = row[0]
        current_user = row[1]

        # Check which tables exist in the database
        cursor.execute("SHOW TABLES")
        table_rows = cast(list[tuple[Any, ...]], cursor.fetchall())

        existing_tables = []
        for table_row in table_rows:
            existing_tables.append(table_row[0])

        if "customers" in existing_tables and "orders" in existing_tables:
            print(
                f"Connection successful! Mode: {app_env} | Host: {db_host}\n"
                f"Connected to database '{current_db}' as '{current_user}' "
                f"and found both tables ('customers', 'orders')."
            )
        else:
            sys.stderr.write(
                f"check_connection: tables missing in '{current_db}' (APP_ENV={app_env}). "
                f"Found: {existing_tables}\n"
            )
            print(
                f"Connected to '{current_db}' as '{current_user}' (mode: {app_env}), "
                f"but required tables are missing. Found tables: {existing_tables}. "
                f"Please run database/schema.sql."
            )

    except Exception:
        sys.stderr.write(traceback.format_exc())
        print("Connection test failed while checking the database tables.")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
