from __future__ import annotations

import oracledb
from fastapi import APIRouter, HTTPException

from .. import crud
from ..errors import raise_as_http
from ..schemas import DepartmentCreate, DepartmentOut, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentOut])
def list_departments():
    return crud.list_departments()


@router.get("/{department_id}", response_model=DepartmentOut)
def get_department(department_id: int):
    dept = crud.get_department(department_id)
    if dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.post("", response_model=DepartmentOut, status_code=201)
def create_department(payload: DepartmentCreate):
    try:
        return crud.create_department(payload.department_name, payload.location)
    except oracledb.DatabaseError as exc:
        raise_as_http(exc)


@router.put("/{department_id}", response_model=DepartmentOut)
def update_department(department_id: int, payload: DepartmentUpdate):
    fields = payload.model_dump(exclude_unset=True)
    try:
        updated = crud.update_department(department_id, fields)
    except oracledb.DatabaseError as exc:
        raise_as_http(exc)
    if updated is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return updated


@router.delete("/{department_id}", status_code=204)
def delete_department(department_id: int):
    try:
        deleted = crud.delete_department(department_id)
    except oracledb.DatabaseError as exc:
        raise_as_http(exc)
    if not deleted:
        raise HTTPException(status_code=404, detail="Department not found")
