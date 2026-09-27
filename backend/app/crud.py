from __future__ import annotations

from typing import Any

from .db import dict_rowfactory, get_connection

# ---------------------------------------------------------------- helpers


def _fetch_one(cursor) -> dict | None:
    return cursor.fetchone()


def _fetch_all(cursor) -> list[dict]:
    return cursor.fetchall()


# ------------------------------------------------------------- departments


def list_departments() -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT department_id, department_name, location "
            "FROM departments ORDER BY department_id"
        )
        cur.rowfactory = dict_rowfactory(cur)
        return _fetch_all(cur)


def get_department(department_id: int) -> dict | None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT department_id, department_name, location "
            "FROM departments WHERE department_id = :id",
            id=department_id,
        )
        cur.rowfactory = dict_rowfactory(cur)
        return _fetch_one(cur)


def create_department(department_name: str, location: str | None) -> dict:
    with get_connection() as conn:
        cur = conn.cursor()
        new_id_var = cur.var(int)
        cur.execute(
            """
            INSERT INTO departments (department_name, location)
            VALUES (:name, :location)
            RETURNING department_id INTO :new_id
            """,
            name=department_name,
            location=location,
            new_id=new_id_var,
        )
        conn.commit()
        new_id = new_id_var.getvalue()[0]
        return {
            "department_id": new_id,
            "department_name": department_name,
            "location": location,
        }


def update_department(department_id: int, fields: dict[str, Any]) -> dict | None:
    if not fields:
        return get_department(department_id)

    set_clause = ", ".join(f"{col} = :{col}" for col in fields)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE departments SET {set_clause} WHERE department_id = :dept_id",
            dept_id=department_id,
            **fields,
        )
        if cur.rowcount == 0:
            conn.rollback()
            return None
        conn.commit()
    return get_department(department_id)


def delete_department(department_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM departments WHERE department_id = :id", id=department_id
        )
        deleted = cur.rowcount > 0
        conn.commit()
        return deleted


# --------------------------------------------------------------- employees

_EMPLOYEE_COLUMNS = (
    "employee_id, first_name, last_name, email, phone, "
    "hire_date, job_title, salary, department_id"
)


def list_employees(department_id: int | None = None) -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor()
        if department_id is not None:
            cur.execute(
                f"SELECT {_EMPLOYEE_COLUMNS} FROM employees "
                "WHERE department_id = :dept_id ORDER BY employee_id",
                dept_id=department_id,
            )
        else:
            cur.execute(
                f"SELECT {_EMPLOYEE_COLUMNS} FROM employees ORDER BY employee_id"
            )
        cur.rowfactory = dict_rowfactory(cur)
        return _fetch_all(cur)


def get_employee(employee_id: int) -> dict | None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT {_EMPLOYEE_COLUMNS} FROM employees WHERE employee_id = :id",
            id=employee_id,
        )
        cur.rowfactory = dict_rowfactory(cur)
        return _fetch_one(cur)


def create_employee(data: dict[str, Any]) -> dict:
    columns = list(data.keys())
    placeholders = ", ".join(f":{c}" for c in columns)
    col_list = ", ".join(columns)

    with get_connection() as conn:
        cur = conn.cursor()
        new_id_var = cur.var(int)
        cur.execute(
            f"""
            INSERT INTO employees ({col_list})
            VALUES ({placeholders})
            RETURNING employee_id INTO :new_id
            """,
            new_id=new_id_var,
            **data,
        )
        conn.commit()
        new_id = new_id_var.getvalue()[0]
    return get_employee(new_id)  # type: ignore[return-value]


def update_employee(employee_id: int, fields: dict[str, Any]) -> dict | None:
    if not fields:
        return get_employee(employee_id)

    set_clause = ", ".join(f"{col} = :{col}" for col in fields)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE employees SET {set_clause} WHERE employee_id = :emp_id",
            emp_id=employee_id,
            **fields,
        )
        if cur.rowcount == 0:
            conn.rollback()
            return None
        conn.commit()
    return get_employee(employee_id)


def delete_employee(employee_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM employees WHERE employee_id = :id", id=employee_id)
        deleted = cur.rowcount > 0
        conn.commit()
        return deleted
