from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Matches the NUMBER(10,2) column: non-negative, at most 10 digits, 2 decimals.
Salary = Annotated[Decimal, Field(ge=0, lt=10**8, max_digits=10, decimal_places=2)]


def _reject_null(v):
    if v is None:
        raise ValueError("cannot be null")
    return v


def _coerce_date(v):
    if isinstance(v, datetime):
        return v.date()
    return v


class DepartmentBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    department_name: str = Field(..., min_length=1, max_length=100)
    location: str | None = Field(None, max_length=100)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    department_name: str | None = Field(None, min_length=1, max_length=100)
    location: str | None = Field(None, max_length=100)

    _no_null = field_validator("department_name")(_reject_null)


class DepartmentOut(DepartmentBase):
    department_id: int


class EmployeeBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    hire_date: date | None = None
    job_title: str | None = Field(None, max_length=80)
    salary: Salary | None = None
    department_id: int | None = None

    @field_validator("hire_date", mode="before")
    @classmethod
    def _normalize_hire_date(cls, v):
        return _coerce_date(v)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    hire_date: date | None = None
    job_title: str | None = Field(None, max_length=80)
    salary: Salary | None = None
    department_id: int | None = None

    _no_null = field_validator("first_name", "last_name", "email", "hire_date")(
        _reject_null
    )

    @field_validator("hire_date", mode="before")
    @classmethod
    def _normalize_hire_date(cls, v):
        return _coerce_date(v)


class EmployeeOut(EmployeeBase):
    employee_id: int
