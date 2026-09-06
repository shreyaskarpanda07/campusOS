/**
 * Tests for the API client module.
 *
 * Verifies that fetchHealth correctly calls the backend
 * and handles both success and error responses.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchHealth } from "@/lib/api";

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("fetchHealth", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("should return health data on success", async () => {
    const mockResponse = {
      data: {
        status: "healthy",
        database: "connected",
        version: "0.1.0",
      },
      error: null,
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await fetchHealth();

    expect(result.data?.status).toBe("healthy");
    expect(result.data?.database).toBe("connected");
    expect(result.data?.version).toBe("0.1.0");
    expect(result.error).toBeNull();
  });

  it("should throw on non-OK response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    await expect(fetchHealth()).rejects.toThrow("Health check failed: 500");
  });

  it("should call the correct URL", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: null, error: null }),
    });

    await fetchHealth();

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/health"),
      expect.objectContaining({ cache: "no-store" })
    );
  });
});
