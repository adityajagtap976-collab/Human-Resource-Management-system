from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import oracledb

_pool: oracledb.ConnectionPool | None = None


def _get_pool() -> oracledb.ConnectionPool:
    global _pool
    if _pool is not None:
        return _pool

    user = os.environ.get("ORACLE_USER")
    password = os.environ.get("ORACLE_PASSWORD")
    dsn = os.environ.get("ORACLE_DSN")

    if not user or not password or not dsn:
        raise RuntimeError(
            "Missing Oracle connection settings. Set ORACLE_USER, "
            "ORACLE_PASSWORD and ORACLE_DSN (see backend/.env.example)."
        )

    _pool = oracledb.create_pool(
        user=user,
        password=password,
        dsn=dsn,
        min=int(os.environ.get("ORACLE_POOL_MIN", "1")),
        max=int(os.environ.get("ORACLE_POOL_MAX", "4")),
        increment=1,
    )
    return _pool


@contextmanager
def get_connection() -> Iterator[oracledb.Connection]:
    pool = _get_pool()
    conn = pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)


def dict_rowfactory(cursor: oracledb.Cursor):
    columns = [col[0].lower() for col in cursor.description]

    def row_to_dict(*args):
        return dict(zip(columns, args))

    return row_to_dict
