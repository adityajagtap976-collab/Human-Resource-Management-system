"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ApiError,
  Department,
  DepartmentInput,
  departmentsApi,
} from "@/lib/api";

const emptyForm: DepartmentInput = { department_name: "", location: "" };

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<DepartmentInput>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setDepartments(await departmentsApi.list());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load departments.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- standard fetch-on-mount; load() only setStates after the fetch resolves
    load();
  }, []);

  function startEdit(dept: Department) {
    setEditingId(dept.department_id);
    setForm({ department_name: dept.department_name, location: dept.location ?? "" });
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
      const payload: DepartmentInput = {
        department_name: form.department_name.trim(),
        location: form.location?.trim() || null,
      };
      if (editingId !== null) {
        await departmentsApi.update(editingId, payload);
      } else {
        await departmentsApi.create(payload);
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
    if (!confirm("Delete this department? This is only allowed if no employees belong to it.")) {
      return;
    }
    setError(null);
    try {
      await departmentsApi.remove(id);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed.");
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Departments</h1>
        <Link href="/" className="text-sm underline underline-offset-4">
          &larr; Back
        </Link>
      </div>

      {error && (
        <p className="mb-4 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <form onSubmit={handleSubmit} className="mb-8 flex flex-wrap items-end gap-3 rounded border border-black/10 p-4">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium" htmlFor="department_name">
            Department name
          </label>
          <input
            id="department_name"
            required
            value={form.department_name}
            onChange={(e) => setForm({ ...form, department_name: e.target.value })}
            className="rounded border border-black/20 px-2 py-1 text-sm"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium" htmlFor="location">
            Location
          </label>
          <input
            id="location"
            value={form.location ?? ""}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
            className="rounded border border-black/20 px-2 py-1 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-black px-4 py-1.5 text-sm text-white disabled:opacity-50 dark:bg-white dark:text-black"
        >
          {editingId !== null ? "Save changes" : "Add department"}
        </button>
        {editingId !== null && (
          <button type="button" onClick={cancelEdit} className="text-sm underline underline-offset-4">
            Cancel
          </button>
        )}
      </form>

      {loading ? (
        <p className="text-sm text-black/60 dark:text-white/60">Loading…</p>
      ) : departments.length === 0 ? (
        <p className="text-sm text-black/60 dark:text-white/60">No departments yet.</p>
      ) : (
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-black/10 text-left">
              <th className="py-2 pr-2">#</th>
              <th className="py-2 pr-2">Name</th>
              <th className="py-2 pr-2">Location</th>
              <th className="py-2 pr-2"></th>
            </tr>
          </thead>
          <tbody>
            {departments.map((dept, i) => (
              <tr key={dept.department_id} className="border-b border-black/5">
                <td className="py-2 pr-2">{i + 1}</td>
                <td className="py-2 pr-2">{dept.department_name}</td>
                <td className="py-2 pr-2">{dept.location ?? "—"}</td>
                <td className="py-2 pr-2 text-right">
                  <button onClick={() => startEdit(dept)} className="mr-3 underline underline-offset-4">
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(dept.department_id)}
                    className="text-red-600 underline underline-offset-4"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}