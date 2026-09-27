from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


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


class EmployeeOut(EmployeeBase):
    employee_id: int
