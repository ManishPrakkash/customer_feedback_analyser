import os
from dotenv import load_dotenv
from typing import Optional

try:
	from psycopg_pool import ConnectionPool
except Exception:  # pragma: no cover
	ConnectionPool = None  # type: ignore

load_dotenv()

DB_URI = os.getenv("DB_URI")

# Create a connection pool only if a DB URI is configured and psycopg is available
if DB_URI and ConnectionPool is not None:
	db_pool: Optional[ConnectionPool] = ConnectionPool(DB_URI)  # type: ignore
else:
	db_pool = None  # type: ignore