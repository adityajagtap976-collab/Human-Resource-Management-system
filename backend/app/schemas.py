from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class DepartmentBase(BaseModel):
    department_name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)


class DepartmentOut(DepartmentBase):
    department_id: int


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    hire_date: Optional[date] = None
    job_title: Optional[str] = Field(None, max_length=80)
    salary: Optional[Decimal] = None
    department_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    hire_date: Optional[date] = None
    job_title: Optional[str] = Field(None, max_length=80)
    salary: Optional[Decimal] = None
    department_id: Optional[int] = None


class EmployeeOut(EmployeeBase):
    employee_id: int
