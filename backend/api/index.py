"""
Entrypoint for deploying the backend AS a Vercel Python Function
(Option B in README.md). Vercel looks for a top-level `app` ASGI
object in api/index.py.

Read the README before you use this path: every cold start pays the
full Oracle connection cost, and Vercel's function timeout will cut
off slow Oracle handshakes on cheaper plans. Option A (a normal
always-on host running `uvicorn app.main:app`) is the one to use for
anything beyond a demo.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

