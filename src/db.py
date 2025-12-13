import os
from dataclasses import dataclass

import psycopg2
from psycopg2.extensions import connection as PgConnection
from dotenv import load_dotenv


@dataclass(frozen=True)
class PgConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str


def load_pg_config() -> PgConfig:
    """Load Postgres connection details from .env / environment variables."""
    load_dotenv()

    host = os.getenv("PGHOST", "localhost")
    port = int(os.getenv("PGPORT", "5432"))
    dbname = os.getenv("PGDATABASE", "marketing_engine")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD")

    if not password:
        raise RuntimeError(
            "Missing PGPASSWORD. Add PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD to your .env"
        )

    return PgConfig(host=host, port=port, dbname=dbname, user=user, password=password)


def get_conn() -> PgConnection:
    cfg = load_pg_config()
    return psycopg2.connect(
        host=cfg.host,
        port=cfg.port,
        dbname=cfg.dbname,
        user=cfg.user,
        password=cfg.password,
    )
