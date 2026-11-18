"""Database connection (reads .env, Aiven SSL). Owner: Mohammed."""
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Return a database connection, or None if it fails."""
    mode = os.getenv("DB_MODE", "aiven").lower()

    try:
        settings = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "connection_timeout": 10,
        }

        # Aiven requires SSL. Local MySQL usually does not.
        if mode == "aiven":
            ca_path = os.getenv("DB_SSL_CA")
            if not ca_path or not os.path.exists(ca_path):
                print("Certificate file not found. Check DB_SSL_CA in your .env file.")
                return None
            settings["ssl_ca"] = ca_path

        return mysql.connector.connect(**settings)

    except ValueError:
        print("DB_PORT in your .env file must be a number.")
    except mysql.connector.Error as e:
        print(f"Could not connect to the database: {e}")
    return None