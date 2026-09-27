from __future__ import annotations

import oracledb
from fastapi import APIRouter, HTTPException, Query

from .. import crud
from ..errors import raise_as_http
from ..schemas import EmployeeCreate, EmployeeOut, EmployeeUpdate

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
def list_employees(department_id: int | None = Query(default=None)):
    return crud.list_employees(department_id)


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int):
    emp = crud.get_employee(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(payload: EmployeeCreate):
    data = payload.model_dump(exclude_unset=True)
    try:
        return crud.create_employee(data)
    except oracledb.DatabaseError as exc:
        raise_as_http(exc)


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, payload: EmployeeUpdate):
    fields = payload.model_dump(exclude_unset=True)
    try:
        updated = crud.update_employee(employee_id, fields)
    except oracledb.DatabaseError as exc:
        raise_as_http(exc)
    if updated is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int):
    try:
        deleted = crud.delete_employee(employee_id)
    except oracledb.DatabaseError as exc:
        raise_as_http(exc)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
