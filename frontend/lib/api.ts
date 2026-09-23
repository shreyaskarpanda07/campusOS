/**
 * API client for communicating with the CampusOS backend.
 *
 * All backend calls go through this module so the base URL
 * is configured in one place.
 */

import { getToken } from "./auth";
import { AuthResponseData, Interest, Skill, User, UserProfileUpdate } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

/** Health check response shape from GET /api/health. */
export interface HealthData {
  status: string;
  database: string;
  version: string;
}

export interface ApiError {
  code: string;
  message: string;
}

export interface ApiResponse<T> {
  data: T | null;
  error: ApiError | null;
}

/** Custom error class carrying the backend error code and message. */
export class ApiRequestError extends Error {
  code: string;
  status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.code = code;
    this.status = status;
  }
}

/**
 * Helper to process backend fetch responses and unpack standard ApiResponse wrappers.
 */
async function handleResponse<T>(res: Response): Promise<T> {
  const json: ApiResponse<T> = await res.json().catch(() => ({
    data: null,
    error: { code: "PARSING_ERROR", message: "Failed to parse response JSON." },
  }));

  if (!res.ok || json.error) {
    const errCode = json.error?.code || `HTTP_${res.status}`;
    const errMsg = json.error?.message || `Request failed with status ${res.status}`;
    throw new ApiRequestError(errCode, errMsg, res.status);
  }

  return json.data as T;
}

/**
 * Fetch backend health status.
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

/**
 * Register a new user account.
 */
export async function registerUser(payload: {
  email: string;
  password: string;
  name: string;
}): Promise<AuthResponseData> {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return handleResponse<AuthResponseData>(res);
}

/**
 * Authenticate existing user.
 */
export async function loginUser(payload: {
  email: string;
  password: string;
}): Promise<AuthResponseData> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return handleResponse<AuthResponseData>(res);
}

/**
 * Invalidate active session / notify backend.
 */
export async function logoutUser(): Promise<{ message: string }> {
  const token = getToken();
  const res = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  return handleResponse<{ message: string }>(res);
}

/**
 * Authenticated fetch helper for subsequent protected API calls.
 */
export async function authFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  return handleResponse<T>(res);
}

/**
 * Fetch full profile of current authenticated student.
 */
export async function fetchMyProfile(): Promise<User> {
  return authFetch<User>("/users/me");
}

/**
 * Update academic background and preferences.
 */
export async function updateMyProfile(
  payload: UserProfileUpdate
): Promise<User> {
  return authFetch<User>("/users/me", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

/**
 * Synchronize skills list with proficiency.
 */
export async function updateMySkills(
  skills: { name: string; proficiency?: string | null }[]
): Promise<Skill[]> {
  return authFetch<Skill[]>("/users/me/skills", {
    method: "PUT",
    body: JSON.stringify({ skills }),
  });
}

/**
 * Synchronize career/opportunity interests.
 */
export async function updateMyInterests(
  interests: { name: string }[]
): Promise<Interest[]> {
  return authFetch<Interest[]>("/users/me/interests", {
    method: "PUT",
    body: JSON.stringify({ interests }),
  });
}

/**
 * Search and filter opportunities feed.
 */
export async function fetchOpportunities(
  params: import("./types").OpportunityFilterParams = {}
): Promise<import("./types").OpportunityListResponse> {
  const searchParams = new URLSearchParams();
  if (params.type) searchParams.set("type", params.type);
  if (params.work_mode) searchParams.set("work_mode", params.work_mode);
  if (params.location) searchParams.set("location", params.location);
  if (params.organization) searchParams.set("organization", params.organization);
  if (params.search) searchParams.set("search", params.search);
  if (params.status) searchParams.set("status", params.status);
  if (params.max_cgpa !== undefined && params.max_cgpa !== null) {
    searchParams.set("max_cgpa", String(params.max_cgpa));
  }
  if (params.page) searchParams.set("page", String(params.page));
  if (params.per_page) searchParams.set("per_page", String(params.per_page));

  const queryStr = searchParams.toString();
  const endpoint = `/opportunities${queryStr ? `?${queryStr}` : ""}`;
  return authFetch<import("./types").OpportunityListResponse>(endpoint);
}

/**
 * Fetch full opportunity details by ID.
 */
export async function fetchOpportunityDetail(
  id: string
): Promise<import("./types").Opportunity> {
  return authFetch<import("./types").Opportunity>(`/opportunities/${id}`);
}
