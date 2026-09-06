/**
 * API client for communicating with the CampusOS backend.
 *
 * All backend calls go through this module so the base URL
 * is configured in one place.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

/**
 * Health check response shape from GET /api/health.
 */
export interface HealthData {
  status: string;
  database: string;
  version: string;
}

export interface ApiResponse<T> {
  data: T | null;
  error: { code: string; message: string } | null;
}

/**
 * Fetch backend health status.
 *
 * @returns The health data including DB connectivity and version.
 * @throws Error if the backend is unreachable.
 */
export async function fetchHealth(): Promise<ApiResponse<HealthData>> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  return response.json();
}
