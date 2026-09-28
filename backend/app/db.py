from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import oracledb

_pool: oracledb.ConnectionPool | None = None

# Hard upper bounds so a locked row / dead network can never hang a request.
_CALL_TIMEOUT_MS = int(os.environ.get("ORACLE_CALL_TIMEOUT_MS", "8000"))
_POOL_WAIT_MS = int(os.environ.get("ORACLE_POOL_WAIT_MS", "5000"))


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
            # Never wait forever for a free connection.
            getmode=oracledb.POOL_GETMODE_TIMEDWAIT,
            wait_timeout=_POOL_WAIT_MS,
            # Drop idle connections and ping stale ones before handing out.
            timeout=300,
            ping_interval=60,
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
    # Applies to every statement on this connection: a statement blocked on a
    # lock held by another (uncommitted) session raises DPY-4024 instead of
    # hanging indefinitely.
    conn.call_timeout = _CALL_TIMEOUT_MS
    try:
        yield conn
    finally:
        try:
            pool.release(conn)
        except oracledb.Error:
            # Connection was already broken by a timeout; the pool discards it.
            pass


def dict_rowfactory(cursor: oracledb.Cursor):
    columns = [col[0].lower() for col in cursor.description]

    def row_to_dict(*args):
        return dict(zip(columns, args))

    return row_to_dict
