# Human Resource Management System

Employee & Department CRUD. Oracle 19c for storage, FastAPI for the backend,
Next.js for the frontend.

**Status: functionally complete, DB-untested.** I verified the FastAPI app
imports cleanly, every route wires up, and the SQL is parametrized and
syntactically valid Oracle. I have **not** run it against a live Oracle
instance — I had no reachable Oracle DB from the build environment. Run
`schema.sql`, point the backend at your real instance, and smoke-test CRUD
before you trust this in front of anyone.

## Repo layout

```
backend/            FastAPI app (Python), Oracle 19c access via python-oracledb
  app/
    main.py         FastAPI app, CORS, router registration
    db.py           Connection pool (thin mode, no Oracle Client install needed)
    schemas.py      Pydantic request/response models
    crud.py         Raw parametrized SQL — no ORM
    errors.py       Maps ORA- error codes to sane HTTP responses
    routers/
      departments.py
      employees.py
  api/index.py      Entrypoint if you deploy the backend AS a Vercel Function
  schema.sql        DDL for both tables + seed rows
  requirements.txt
  .env.example
frontend/           Next.js 16 (App Router) + Tailwind v4
  app/
    page.tsx              Landing page
    departments/page.tsx  Department CRUD UI
    employees/page.tsx    Employee CRUD UI
  lib/api.ts             Typed fetch client for the backend
  .env.local.example
```

## Why the stack choice needs a caveat

Oracle 19c + Vercel serverless is not a natural fit. Vercel functions are
stateless and short-lived; there is no long-running process to keep an
Oracle connection pool warm. `python-oracledb`'s thin mode means you don't
need Oracle Instant Client installed (that part works fine anywhere,
including serverless) — but it doesn't remove the cost of a fresh
connection handshake on every cold start. Two real deployment options,
pick based on what you're actually optimizing for:

**Option A — recommended: run the backend as a normal always-on service.**
Deploy `backend/` to Render, Railway, Fly.io, a VM, or Oracle Cloud itself,
running `uvicorn app.main:app`. The connection pool stays warm across
requests like it's supposed to. Deploy `frontend/` to Vercel, pointing
`NEXT_PUBLIC_API_URL` at that backend's URL. This is the boring, correct
answer for anything beyond a demo.

**Option B — backend also on Vercel, as a Python Function.**
`backend/api/index.py` + `backend/vercel.json` are set up for this. Deploy
the `backend/` folder as its own Vercel project (Python runtime, ASGI
entrypoint auto-detected). Expect slower cold-start latency on every
Oracle round trip, and check Vercel's function timeout against how long
your Oracle handshake actually takes on a cheap plan — it can lose.
Vercel's "Services" feature can host both frontend and backend Python
function under one project/domain if you want a single deploy; check
current Vercel docs for exact monorepo config since this is a newer,
still-evolving feature.

## Database setup

1. Get an Oracle 19c instance reachable from wherever the backend runs
   (on-prem, a VM, or Oracle Cloud — if it's Autonomous DB with a wallet,
   you'll need mTLS config; python-oracledb thin mode supports wallets but
   the connection string format is different from a plain easy-connect
   string — see python-oracledb's `oracledb.connect(..., config_dir=...,
   wallet_location=...)` docs before assuming `.env.example`'s DSN format
   works as-is).
2. Run `backend/schema.sql` against it (SQL*Plus, SQLcl, or any Oracle
   client). It's idempotent — safe to re-run.
3. Create an app-level DB user with grants scoped to just these two
   tables. Don't run the API as SYS/SYSTEM.

## Backend — local dev

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then fill in ORACLE_USER / ORACLE_PASSWORD / ORACLE_DSN
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for interactive Swagger UI — that alone
will tell you fast whether your Oracle connection is actually working,
since `/departments` will either return data or throw a connection error.

Requested version was Python 3.14.7; `.python-version` is pinned to 3.14.
The code has no 3.14-specific syntax, so 3.12+ works identically if 3.14.7
isn't available in your environment — don't block yourself on an exact
patch version.

## Frontend — local dev

```bash
cd frontend
npm install
cp .env.local.example .env.local   # points at http://localhost:8000 by default
npm run dev
```

Visit `http://localhost:3000`.

Note: `npm run build` requires network access to `fonts.googleapis.com`
(the scaffold uses `next/font/google`). That's fine on Vercel; it will
fail in a network-locked sandbox. If you ever need a fully offline build,
swap `Geist`/`Geist_Mono` in `app/layout.tsx` for `next/font/local` or
system fonts.

## Deploying

**Frontend (Vercel):** import the repo, set root directory to `frontend`,
set `NEXT_PUBLIC_API_URL` to your backend's public URL, deploy.

**Backend (Option A hosts):** set `ORACLE_USER`, `ORACLE_PASSWORD`,
`ORACLE_DSN`, `FRONTEND_ORIGIN` (your Vercel frontend URL, comma-separated
if more than one) as environment variables on the host, run
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

**Backend (Option B, Vercel Python Function):** import `backend/` as a
separate Vercel project. Set the same env vars in that project's settings.
Vercel auto-detects the FastAPI app via `api/index.py`.

## What's actually tested vs. what isn't

Tested in the build sandbox (no live Oracle available there):
- Backend imports cleanly, all 10 CRUD routes + `/health` register (verified via `python -m py_compile` + a live import with fake Oracle env vars)
- Every SQL statement is parametrized (no string-built queries)
- Frontend type-checks clean (`tsc --noEmit`) and lints clean (`eslint`)

Not tested, because nothing in this sandbox could reach an Oracle instance:
- An actual round-trip INSERT/SELECT/UPDATE/DELETE against real Oracle 19c
- The `RETURNING ... INTO` bind-variable pattern in `crud.py` against your
  specific Oracle version/driver combo — this is standard python-oracledb
  usage, but "standard usage" and "works against your DB" are not the same
  claim until you've run it
- The full `next build` (blocked by sandbox network policy on Google
  Fonts, not by the app code — `tsc` passing is the real signal here)
- CORS in a real cross-origin deployment (only validated the middleware
  wiring, not an actual browser round trip)

Run the local dev steps above end-to-end against your real Oracle
instance before you consider this done. "Compiles" and "the routes exist"
is not the same bar as "CRUD actually works."
