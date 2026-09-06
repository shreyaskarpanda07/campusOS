"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchHealth, logoutUser, type HealthData } from "@/lib/api";
import { clearAuth, getStoredUser } from "@/lib/auth";
import { User } from "@/lib/types";
import { Button } from "@/components/ui/Button";

/**
 * Landing page — shows CampusOS branding, auth actions, and backend connection status.
 */
export default function HomePage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    // Check client-side stored user
    setCurrentUser(getStoredUser());

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

  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch {
      // Clean up local auth even if network fails
    } finally {
      clearAuth();
      setCurrentUser(null);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-50">
      {/* ── Branding ──────────────────────────────────────────── */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-extrabold tracking-tight text-primary-700 mb-3">
          CampusOS
        </h1>
        <p className="text-lg text-gray-600 max-w-md mx-auto">
          Personalized opportunity intelligence for university students.
        </p>
      </div>

      {/* ── User Auth State / Action Bar ──────────────────────── */}
      <div className="mb-8 w-full max-w-md bg-white border border-gray-200 rounded-xl p-5 shadow-sm text-center">
        {currentUser ? (
          <div>
            <p className="text-sm text-gray-600 mb-1">Signed in as</p>
            <p className="text-base font-semibold text-gray-900 mb-4">
              {currentUser.name} ({currentUser.email})
            </p>
            <div className="flex justify-center gap-3">
              <Button
                variant="outline"
                onClick={handleLogout}
              >
                Sign Out
              </Button>
            </div>
          </div>
        ) : (
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Get personalized opportunities matched to your degree and skills.
            </p>
            <div className="flex justify-center gap-3">
              <Link href="/login">
                <Button variant="outline">Sign In</Button>
              </Link>
              <Link href="/signup">
                <Button variant="primary">Create Account</Button>
              </Link>
            </div>
          </div>
        )}
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
        CampusOS — Phase 2 Authentication Ready
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
