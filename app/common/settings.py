from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = int(os.environ["LOG_LEVEL"])

# database
READ_DB_USER = os.environ["READ_DB_USER"]
READ_DB_PASS = os.environ["READ_DB_PASS"]
READ_DB_HOST = os.environ["READ_DB_HOST"]
READ_DB_PORT = int(os.environ["READ_DB_PORT"])
READ_DB_NAME = os.environ["READ_DB_NAME"]

WRITE_DB_USER = os.environ["WRITE_DB_USER"]
WRITE_DB_PASS = os.environ["WRITE_DB_PASS"]
WRITE_DB_HOST = os.environ["WRITE_DB_HOST"]
WRITE_DB_PORT = int(os.environ["WRITE_DB_PORT"])
WRITE_DB_NAME = os.environ["WRITE_DB_NAME"]

# redis
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])

# 0 keeps every daily point; N deletes the points of active players older than N days.
PROFILE_HISTORY_RETENTION_DAYS = int(os.environ.get("PROFILE_HISTORY_RETENTION_DAYS", "0"))

APP_ENV = os.environ["APP_ENV"]
APP_COMPONENT = os.environ["APP_COMPONENT"]
APP_HOST = os.environ["APP_HOST"]
APP_PORT = int(os.environ["APP_PORT"])
