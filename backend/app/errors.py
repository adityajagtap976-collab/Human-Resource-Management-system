from __future__ import annotations

import oracledb
from fastapi import HTTPException

# Oracle error codes worth translating into meaningful HTTP responses
# instead of a raw 500 with an ORA- stack trace.
_UNIQUE_VIOLATION = 1        # ORA-00001: unique constraint violated
_FK_PARENT_MISSING = 2291    # ORA-02291: integrity constraint violated - parent key not found
_FK_CHILD_EXISTS = 2292      # ORA-02292: integrity constraint violated - child record found


def raise_as_http(exc: oracledb.DatabaseError) -> None:
    (error_obj,) = exc.args
    code = getattr(error_obj, "code", None)

    if code == _UNIQUE_VIOLATION:
        raise HTTPException(status_code=409, detail="A record with that unique value already exists.")
    if code == _FK_PARENT_MISSING:
        raise HTTPException(status_code=400, detail="Referenced department_id does not exist.")
    if code == _FK_CHILD_EXISTS:
        raise HTTPException(status_code=409, detail="Cannot delete: employees still reference this department.")

    raise HTTPException(status_code=500, detail=f"Database error: {error_obj.message.strip()}")
