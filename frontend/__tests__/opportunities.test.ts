/**
 * Tests for Opportunity API methods.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchOpportunities, fetchOpportunityDetail, ApiRequestError } from "@/lib/api";
import { setToken } from "@/lib/auth";

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("Opportunities API Client", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorage.clear();
    setToken("mock-jwt-token");
  });

  it("fetchOpportunities should send correct query parameters and return paginated list", async () => {
    const mockListResponse = {
      items: [
        {
          id: "opp-1",
          title: "SWE Intern",
          organization: "Google",
          type: "internship",
          work_mode: "hybrid",
          status: "active",
          skills: [{ id: "s1", name: "Python", requirement_type: "required" }],
          eligibility: {},
          created_at: "2026-09-22T00:00:00Z",
        },
      ],
      pagination: {
        total: 1,
        page: 1,
        per_page: 20,
        pages: 1,
      },
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: mockListResponse, error: null }),
    });

    const res = await fetchOpportunities({
      type: "internship",
      work_mode: "hybrid",
      search: "Google",
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/opportunities?type=internship&work_mode=hybrid&search=Google"),
      expect.any(Object)
    );
    expect(res.items.length).toBe(1);
    expect(res.items[0].title).toBe("SWE Intern");
    expect(res.pagination.total).toBe(1);
  });

  it("fetchOpportunityDetail should fetch by ID and return detail object", async () => {
    const mockDetail = {
      id: "opp-999",
      title: "Deloitte Challenge",
      organization: "Deloitte",
      type: "competition",
      status: "active",
      skills: [],
      sources: [
        {
          source_id: "src-1",
          source_name: "Unstop",
          source_url: "https://unstop.com",
          fetched_at: "2026-09-22T00:00:00Z",
        },
      ],
      eligibility: { eligible_years: [2026] },
      created_at: "2026-09-22T00:00:00Z",
      updated_at: "2026-09-22T00:00:00Z",
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: mockDetail, error: null }),
    });

    const result = await fetchOpportunityDetail("opp-999");

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/opportunities/opp-999"),
      expect.any(Object)
    );
    expect(result.organization).toBe("Deloitte");
    expect(result.sources?.length).toBe(1);
  });

  it("fetchOpportunityDetail should throw ApiRequestError on 404", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({
        data: null,
        error: { code: "OPPORTUNITY_NOT_FOUND", message: "Not found" },
      }),
    });

    await expect(fetchOpportunityDetail("non-existent-id")).rejects.toThrow(
      ApiRequestError
    );
  });
});
