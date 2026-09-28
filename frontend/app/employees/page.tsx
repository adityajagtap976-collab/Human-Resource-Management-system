"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ApiError,
  Department,
  Employee,
  EmployeeInput,
  departmentsApi,
  employeesApi,
} from "@/lib/api";

const emptyForm: EmployeeInput = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  job_title: "",
  salary: undefined,
  department_id: undefined,
};

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<EmployeeInput>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const departmentName = useMemo(() => {
    const map = new Map(departments.map((d) => [d.department_id, d.department_name]));
    return (id: number | null) => (id !== null && map.has(id) ? map.get(id) : "—");
  }, [departments]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [emps, depts] = await Promise.all([employeesApi.list(), departmentsApi.list()]);
      setEmployees(emps);
      setDepartments(depts);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- standard fetch-on-mount; load() only setStates after the fetch resolves
    load();
  }, []);

  function startEdit(emp: Employee) {
    setEditingId(emp.employee_id);
    setForm({
      first_name: emp.first_name,
      last_name: emp.last_name,
      email: emp.email,
      phone: emp.phone ?? "",
      job_title: emp.job_title ?? "",
      salary: emp.salary ?? undefined,
      department_id: emp.department_id ?? undefined,
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const payload: EmployeeInput = {
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        phone: form.phone?.trim() || null,
        job_title: form.job_title?.trim() || null,
        salary: form.salary === undefined || Number.isNaN(form.salary) ? null : Number(form.salary),
        department_id: form.department_id ? Number(form.department_id) : null,
      };
      if (editingId !== null) {
        await employeesApi.update(editingId, payload);
      } else {
        await employeesApi.create(payload);
      }
      cancelEdit();
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this employee?")) return;
    setError(null);
    try {
      await employeesApi.remove(id);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed.");
    }
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Employees</h1>
        <Link href="/" className="text-sm underline underline-offset-4">
          &larr; Back
        </Link>
      </div>

      {error && (
        <p className="mb-4 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <form onSubmit={handleSubmit} className="mb-8 grid grid-cols-2 gap-3 rounded border border-black/10 p-4 sm:grid-cols-3">
        <Field label="First name">
          <input required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="input" />
        </Field>
        <Field label="Last name">
          <input required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="input" />
        </Field>
        <Field label="Email">
          <input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input" />
        </Field>
        <Field label="Phone">
          <input value={form.phone ?? ""} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="input" />
        </Field>
        <Field label="Job title">
          <input value={form.job_title ?? ""} onChange={(e) => setForm({ ...form, job_title: e.target.value })} className="input" />
        </Field>
        <Field label="Salary">
          <input
            type="number"
            step="0.01"
            value={form.salary ?? ""}
            onChange={(e) => setForm({ ...form, salary: e.target.value === "" ? undefined : Number(e.target.value) })}
            className="input"
          />
        </Field>
        <Field label="Department">
          <select
            value={form.department_id ?? ""}
            onChange={(e) => setForm({ ...form, department_id: e.target.value === "" ? undefined : Number(e.target.value) })}
            className="input"
          >
            <option value="">— none —</option>
            {departments.map((d) => (
              <option key={d.department_id} value={d.department_id}>
                {d.department_name}
              </option>
            ))}
          </select>
        </Field>

        <div className="col-span-full flex items-center gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="rounded bg-black px-4 py-1.5 text-sm text-white disabled:opacity-50 dark:bg-white dark:text-black"
          >
            {editingId !== null ? "Save changes" : "Add employee"}
          </button>
          {editingId !== null && (
            <button type="button" onClick={cancelEdit} className="text-sm underline underline-offset-4">
              Cancel
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <p className="text-sm text-black/60 dark:text-white/60">Loading…</p>
      ) : employees.length === 0 ? (
        <p className="text-sm text-black/60 dark:text-white/60">No employees yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-black/10 text-left">
                <th className="py-2 pr-2">#</th>
                <th className="py-2 pr-2">Name</th>
                <th className="py-2 pr-2">Email</th>
                <th className="py-2 pr-2">Job title</th>
                <th className="py-2 pr-2">Salary</th>
                <th className="py-2 pr-2">Department</th>
                <th className="py-2 pr-2"></th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp, i) => (
                <tr key={emp.employee_id} className="border-b border-black/5">
                  <td className="py-2 pr-2">{i + 1}</td>
                  <td className="py-2 pr-2">
                    {emp.first_name} {emp.last_name}
                  </td>
                  <td className="py-2 pr-2">{emp.email}</td>
                  <td className="py-2 pr-2">{emp.job_title ?? "—"}</td>
                  <td className="py-2 pr-2">{emp.salary ?? "—"}</td>
                  <td className="py-2 pr-2">{departmentName(emp.department_id)}</td>
                  <td className="py-2 pr-2 text-right whitespace-nowrap">
                    <button onClick={() => startEdit(emp)} className="mr-3 underline underline-offset-4">
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(emp.employee_id)}
                      className="text-red-600 underline underline-offset-4"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1 text-xs font-medium">
      {label}
      {children}
    </label>
  );
}