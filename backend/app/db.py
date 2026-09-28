from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import oracledb

_pool: oracledb.ConnectionPool | None = None


class DatabaseUnavailable(Exception):
    """Raised when the Oracle pool cannot be created or a connection cannot be
    acquired (wrong DSN/credentials, listener down, missing .env, ...).
    main.py turns it into a JSON 503 that still carries CORS headers."""


def _get_pool() -> oracledb.ConnectionPool:
    global _pool
    if _pool is not None:
        return _pool

    user = os.environ.get("ORACLE_USER")
    password = os.environ.get("ORACLE_PASSWORD")
    dsn = os.environ.get("ORACLE_DSN")

    if not user or not password or not dsn:
        raise DatabaseUnavailable(
            "Missing Oracle settings. Set ORACLE_USER, ORACLE_PASSWORD and "
            "ORACLE_DSN in backend/.env (see backend/.env.example)."
        )

    try:
        _pool = oracledb.create_pool(
            user=user,
            password=password,
            dsn=dsn,
            min=int(os.environ.get("ORACLE_POOL_MIN", "1")),
            max=int(os.environ.get("ORACLE_POOL_MAX", "4")),
            increment=1,
        )
    except oracledb.Error as exc:
        raise DatabaseUnavailable(
            f"Cannot connect to Oracle ({str(exc).splitlines()[0]}). "
            "Check ORACLE_DSN/ORACLE_USER/ORACLE_PASSWORD and that the listener is running."
        ) from exc
    return _pool


@contextmanager
def get_connection() -> Iterator[oracledb.Connection]:
    pool = _get_pool()
    try:
        conn = pool.acquire()
    except oracledb.Error as exc:
        raise DatabaseUnavailable(
            f"Cannot connect to Oracle ({str(exc).splitlines()[0]}). "
            "Check ORACLE_DSN/ORACLE_USER/ORACLE_PASSWORD and that the listener is running."
        ) from exc
    try:
        yield conn
    finally:
        pool.release(conn)


def dict_rowfactory(cursor: oracledb.Cursor):
    columns = [col[0].lower() for col in cursor.description]

    def row_to_dict(*args):
        return dict(zip(columns, args))

    return row_to_dict
