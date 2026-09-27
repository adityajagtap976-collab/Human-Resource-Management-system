"""
Oracle 19c connectivity via python-oracledb in THIN mode.

Thin mode means no Oracle Instant Client install is required — pure Python,
which is what makes this deployable on a serverless host at all. It does
NOT mean connections are free: every cold start on a serverless platform
re-authenticates against the DB, which is the real cost you're paying for
choosing Oracle + serverless. This module keeps a pool at module scope so
that at least *warm* invocations (same container reused) skip that cost.

Required environment variables:
    ORACLE_USER      - schema/user to connect as
    ORACLE_PASSWORD  - password for that user
    ORACLE_DSN       - easy-connect string, e.g. "host:1521/service_name"
                        or a full descriptor / wallet alias if you're on
                        Oracle Cloud Autonomous DB (see README for wallet notes)
Optional:
    ORACLE_POOL_MIN  - default 1
    ORACLE_POOL_MAX  - default 4
"""

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

    if not all([user, password, dsn]):
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
