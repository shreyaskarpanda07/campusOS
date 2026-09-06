/**
 * Tests for frontend authentication utilities and API methods.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { registerUser, loginUser, logoutUser, ApiRequestError } from "@/lib/api";
import {
  getToken,
  setToken,
  removeToken,
  getStoredUser,
  setStoredUser,
  clearAuth,
} from "@/lib/auth";

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("Auth Storage Helpers", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("should store and retrieve token", () => {
    expect(getToken()).toBeNull();
    setToken("test-jwt-token");
    expect(getToken()).toBe("test-jwt-token");
    removeToken();
    expect(getToken()).toBeNull();
  });

  it("should store and retrieve user profile", () => {
    expect(getStoredUser()).toBeNull();
    const sampleUser = {
      id: "user-123",
      email: "test@campus.edu",
      name: "Test Student",
      university: "MIT",
      degree: "B.Tech",
      branch: "CS",
      graduation_year: 2026,
      current_year: 3,
      cgpa: 9.2,
      preferred_opportunity_types: ["internship"],
      preferred_work_modes: ["remote"],
      is_admin: false,
      created_at: "2026-09-07T00:00:00Z",
      updated_at: "2026-09-07T00:00:00Z",
    };

    setStoredUser(sampleUser);
    expect(getStoredUser()).toEqual(sampleUser);

    clearAuth();
    expect(getStoredUser()).toBeNull();
    expect(getToken()).toBeNull();
  });
});

describe("Auth API Client", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorage.clear();
  });

  it("registerUser should POST to /auth/register and return payload", async () => {
    const mockUser = {
      id: "u1",
      email: "new@campus.edu",
      name: "New Student",
    };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: {
          user: mockUser,
          access_token: "jwt-123",
          token_type: "bearer",
        },
        error: null,
      }),
    });

    const res = await registerUser({
      email: "new@campus.edu",
      password: "password123",
      name: "New Student",
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/auth/register"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          email: "new@campus.edu",
          password: "password123",
          name: "New Student",
        }),
      })
    );

    expect(res.user.email).toBe("new@campus.edu");
    expect(res.access_token).toBe("jwt-123");
  });

  it("loginUser should POST to /auth/login and handle 401 error", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({
        data: null,
        error: {
          code: "INVALID_CREDENTIALS",
          message: "Invalid email or password.",
        },
      }),
    });

    await expect(
      loginUser({ email: "bad@campus.edu", password: "wrong" })
    ).rejects.toThrowError("Invalid email or password.");
  });

  it("logoutUser should send Authorization header when token exists", async () => {
    setToken("my-token");
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: { message: "Logged out" },
        error: null,
      }),
    });

    await logoutUser();

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/auth/logout"),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Authorization: "Bearer my-token",
        }),
      })
    );
  });
});
