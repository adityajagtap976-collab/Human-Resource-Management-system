import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-1 flex-col items-start justify-center gap-6 px-6 py-20">
      <h1 className="text-3xl font-semibold">HR Management System</h1>
      <p className="text-black/60 dark:text-white/60">
        Employee &amp; Department management backed by Oracle 19c via a FastAPI service.
      </p>
      <div className="flex gap-4">
        <Link
          href="/departments"
          className="rounded bg-black px-5 py-2 text-sm text-white dark:bg-white dark:text-black"
        >
          Manage Departments
        </Link>
        <Link
          href="/employees"
          className="rounded border border-black/20 px-5 py-2 text-sm dark:border-white/20"
        >
          Manage Employees
        </Link>
      </div>
    </main>
  );
}
