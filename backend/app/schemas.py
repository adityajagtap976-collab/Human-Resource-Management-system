from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator


def _coerce_date(v):
    if isinstance(v, datetime):
        return v.date()
    return v


class DepartmentBase(BaseModel):
    department_name: str = Field(..., min_length=1, max_length=100)
    location: str | None = Field(None, max_length=100)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    department_name: str | None = Field(None, min_length=1, max_length=100)
    location: str | None = Field(None, max_length=100)


class DepartmentOut(DepartmentBase):
    department_id: int


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    hire_date: date | None = None
    job_title: str | None = Field(None, max_length=80)
    salary: Decimal | None = None
    department_id: int | None = None

    @field_validator("hire_date", mode="before")
    @classmethod
    def _normalize_hire_date(cls, v):
        return _coerce_date(v)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    hire_date: date | None = None
    job_title: str | None = Field(None, max_length=80)
    salary: Decimal | None = None
    department_id: int | None = None

    @field_validator("hire_date", mode="before")
    @classmethod
    def _normalize_hire_date(cls, v):
        return _coerce_date(v)


class EmployeeOut(EmployeeBase):
    employee_id: int
