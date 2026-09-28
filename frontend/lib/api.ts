const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export type Department = {
  department_id: number;
  department_name: string;
  location: string | null;
};

export type DepartmentInput = {
  department_name: string;
  location?: string | null;
};

export type Employee = {
  employee_id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  hire_date: string | null;
  job_title: string | null;
  salary: number | null;
  department_id: number | null;
};

export type EmployeeInput = {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  hire_date?: string | null;
  job_title?: string | null;
  salary?: number | null;
  department_id?: number | null;
};

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// FastAPI sends a string for our own errors, but a list of {loc, msg} objects
// for validation (422) errors. Turn both into one readable sentence.
function formatDetail(d: unknown): string | undefined {
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((e: { loc?: (string | number)[]; msg?: string }) => {
        const field = e.loc?.filter((p) => p !== "body").join(" ");
        return field ? `${field}: ${e.msg}` : (e.msg ?? "Invalid value");
      })
      .join("; ");
  }
  return undefined;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      0,
      `Cannot reach the API at ${API_BASE}. Is the backend running? (try ${API_BASE}/health)`,
    );
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = formatDetail(body.detail) ?? detail;
    } catch {
      // response had no JSON body — fall back to statusText
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const departmentsApi = {
  list: () => request<Department[]>("/departments"),
  get: (id: number) => request<Department>(`/departments/${id}`),
  create: (data: DepartmentInput) =>
    request<Department>("/departments", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<DepartmentInput>) =>
    request<Department>(`/departments/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  remove: (id: number) =>
    request<void>(`/departments/${id}`, { method: "DELETE" }),
};

export const employeesApi = {
  list: (departmentId?: number) =>
    request<Employee[]>(
      departmentId ? `/employees?department_id=${departmentId}` : "/employees",
    ),
  get: (id: number) => request<Employee>(`/employees/${id}`),
  create: (data: EmployeeInput) =>
    request<Employee>("/employees", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<EmployeeInput>) =>
    request<Employee>(`/employees/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  remove: (id: number) =>
    request<void>(`/employees/${id}`, { method: "DELETE" }),
};

export { ApiError };
