"""
Reads database settings from .env and opens a database connection.

APP_ENV=local    -> uses the LOCAL_DB_* settings (MySQL on this computer)
APP_ENV=deployed -> uses the AIVEN_* settings (Aiven MySQL, over SSL)

If APP_ENV is missing, "local" is used.
"""

import os
import sys
import traceback

import mysql.connector
from dotenv import load_dotenv


def get_connection():
    """
    Loads environment variables from .env and returns an open MySQL connection.
    If anything fails, logs the problem to stderr and returns None.
    """
    app_env = "unknown"

    try:
        # Load settings from the .env file in the project root
        load_dotenv()

        app_env = os.getenv("APP_ENV", "local").strip().lower()

        if app_env == "local":
            db_host = os.getenv("LOCAL_DB_HOST", "localhost")
            db_port_text = os.getenv("LOCAL_DB_PORT", "3306")
            db_user = os.getenv("LOCAL_DB_USER", "stitchbook_user")
            db_password = os.getenv("LOCAL_DB_PASSWORD", "")
            db_name = os.getenv("LOCAL_DB_NAME", "stitchbook")

            # Convert the port string from .env into an integer
            db_port = int(db_port_text)

            # Open a connection to the local MySQL as the limited stitchbook_user
            connection = mysql.connector.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name,
            )
            return connection

        if app_env == "deployed":
            db_host = os.getenv("AIVEN_DB_HOST", "").strip()
            db_port_text = os.getenv("AIVEN_DB_PORT", "").strip()
            db_user = os.getenv("AIVEN_DB_USER", "").strip()
            db_password = os.getenv("AIVEN_DB_PASSWORD", "")
            db_name = os.getenv("AIVEN_DB_NAME", "").strip()
            ssl_ca_path = os.getenv("AIVEN_SSL_CA", "").strip()

            # Make sure every Aiven setting has a value
            missing_settings = []
            if db_host == "":
                missing_settings.append("AIVEN_DB_HOST")
            if db_port_text == "":
                missing_settings.append("AIVEN_DB_PORT")
            if db_user == "":
                missing_settings.append("AIVEN_DB_USER")
            if db_password == "":
                missing_settings.append("AIVEN_DB_PASSWORD")
            if db_name == "":
                missing_settings.append("AIVEN_DB_NAME")
            if ssl_ca_path == "":
                missing_settings.append("AIVEN_SSL_CA")

            if len(missing_settings) > 0:
                missing_text = ", ".join(missing_settings)
                sys.stderr.write(
                    "APP_ENV=deployed but these settings are empty in .env: "
                    + missing_text
                    + "\n"
                )
                print(
                    "Error: Aiven settings are missing in your .env file. Missing: "
                    + missing_text
                )
                return None

            # A relative certificate path (like certs/ca.pem) is read from the project folder
            if not os.path.isabs(ssl_ca_path):
                project_folder = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
                ssl_ca_path = os.path.join(project_folder, ssl_ca_path)

            if not os.path.isfile(ssl_ca_path):
                sys.stderr.write(
                    "APP_ENV=deployed but the SSL certificate file was not found: "
                    + ssl_ca_path
                    + "\n"
                )
                print(
                    "Error: The Aiven SSL certificate file was not found. Check AIVEN_SSL_CA in your .env file."
                )
                return None

            # Convert the port string from .env into an integer
            db_port = int(db_port_text)

            # Open a connection to Aiven over SSL using its CA certificate
            connection = mysql.connector.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name,
                ssl_ca=ssl_ca_path,
            )
            return connection

        # Any other APP_ENV value is a mistake in the .env file
        sys.stderr.write(
            'Invalid APP_ENV value: "' + app_env + '". Use "local" or "deployed".\n'
        )
        print('Error: APP_ENV in your .env file must be "local" or "deployed".')
        return None

    except Exception:
        # Log the full error and traceback to standard error so nothing is hidden
        sys.stderr.write(traceback.format_exc())
        print(
            f"Error: Could not connect to the database (APP_ENV={app_env}). "
            "Please check your .env settings and make sure the database is running."
        )
        return None
