from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

import oracledb

from .db import DatabaseUnavailable, get_connection
from .routers import departments, employees

log = logging.getLogger("hrms")

app = FastAPI(
    title="HRMS API",
    description="Employee & Department CRUD backed by Oracle",
    version="1.0.0",
)

# --------------------------------------------------------------------- errors
# WHY THIS EXISTS: Starlette's 500 handler sits OUTSIDE CORSMiddleware, so any
# unhandled exception returns a response with no Access-Control-Allow-Origin
# header. The browser then reports "blocked by CORS policy" and hides the real
# error. Handlers for specific exception classes below run INSIDE CORSMiddleware,
# and the catch-all middleware is registered BEFORE CORS so it is inside it too.


@app.exception_handler(DatabaseUnavailable)
async def _db_unavailable(_: Request, exc: DatabaseUnavailable):
    log.error("Database unavailable: %s", exc)
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(oracledb.Error)
async def _oracle_error(_: Request, exc: oracledb.Error):
    log.exception("Unhandled Oracle error")
    first_line = str(exc).splitlines()[0]
    return JSONResponse(
        status_code=500, content={"detail": f"Database error: {first_line}"}
    )


@app.middleware("http")
async def _catch_all(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        log.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


# ------------------------------------------------------------------------ CORS
# Added AFTER the middleware above so it is the outermost layer.
# The frontend uses no cookies, so credentials are off (also makes "*" legal).
_DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
allowed_origins = [
    o.strip().rstrip("/")
    for o in os.environ.get("FRONTEND_ORIGIN", _DEFAULT_ORIGINS).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departments.router)
app.include_router(employees.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    """Proves the Oracle connection works. Open this first when the UI fails."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM dual")
        cur.fetchone()
    return {"status": "ok", "database": "reachable"}
