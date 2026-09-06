"use client";

import { useEffect, useState } from "react";
import { fetchHealth, type HealthData } from "@/lib/api";

/**
 * Landing page — shows the CampusOS branding and backend connection status.
 *
 * This page confirms that:
 * 1. The Next.js frontend is running.
 * 2. The frontend can reach the FastAPI backend.
 * 3. The backend can reach PostgreSQL.
 */
export default function HomePage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealth()
      .then((res) => {
        setHealth(res.data);
        setError(null);
      })
      .catch((err) => {
        setError(err.message || "Could not reach backend");
        setHealth(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      {/* ── Branding ──────────────────────────────────────────── */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold tracking-tight text-primary-700 mb-3">
          CampusOS
        </h1>
        <p className="text-lg text-gray-600 max-w-md">
          Personalized opportunity intelligence for university students.
        </p>
      </div>

      {/* ── Connection Status Card ────────────────────────────── */}
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white shadow-sm p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-4">
          System Status
        </h2>

        {loading && (
          <div className="flex items-center gap-2 text-gray-500">
            <span className="inline-block h-3 w-3 animate-pulse rounded-full bg-gray-300" />
            Checking backend connection…
          </div>
        )}

        {error && (
          <div className="space-y-2">
            <StatusRow label="Backend" status="error" value="Unreachable" />
            <p className="text-sm text-red-600 mt-2">{error}</p>
            <p className="text-xs text-gray-500 mt-1">
              Make sure the backend is running on{" "}
              <code className="bg-gray-100 px-1 rounded">
                http://localhost:8000
              </code>
            </p>
          </div>
        )}

        {health && (
          <div className="space-y-3">
            <StatusRow
              label="Backend"
              status="ok"
              value={`v${health.version}`}
            />
            <StatusRow
              label="Database"
              status={health.database === "connected" ? "ok" : "error"}
              value={health.database}
            />
            <StatusRow label="Frontend" status="ok" value="Running" />
          </div>
        )}
      </div>

      {/* ── Footer hint ───────────────────────────────────────── */}
      <p className="mt-8 text-sm text-gray-400">
        Phase 1 — Foundation scaffold
      </p>
    </main>
  );
}

/** Small status indicator row. */
function StatusRow({
  label,
  status,
  value,
}: {
  label: string;
  status: "ok" | "error";
  value: string;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-700">{label}</span>
      <span className="flex items-center gap-2 text-sm">
        <span
          className={`inline-block h-2.5 w-2.5 rounded-full ${
            status === "ok" ? "bg-green-500" : "bg-red-500"
          }`}
        />
        <span className={status === "ok" ? "text-green-700" : "text-red-600"}>
          {value}
        </span>
      </span>
    </div>
  );
}
