/**
 * Tests for profile API methods.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchMyProfile,
  updateMyProfile,
  updateMySkills,
  updateMyInterests,
} from "@/lib/api";
import { setToken } from "@/lib/auth";

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("Profile API Client", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorage.clear();
    setToken("mock-jwt-token");
  });

  it("fetchMyProfile should call GET /users/me with Bearer auth", async () => {
    const mockProfile = {
      id: "u123",
      email: "student@univ.edu",
      name: "Student Name",
      university: "MIT",
      degree: "B.Tech",
      branch: "Computer Science",
      graduation_year: 2026,
      current_year: 3,
      cgpa: 9.1,
      preferred_opportunity_types: ["internship"],
      preferred_work_modes: ["remote"],
      preferred_locations: ["Remote"],
      skills: [{ id: "s1", name: "Python", proficiency: "advanced" }],
      interests: [{ id: "i1", name: "AI/ML" }],
      is_admin: false,
      created_at: "2026-09-01T00:00:00Z",
      updated_at: "2026-09-01T00:00:00Z",
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: mockProfile, error: null }),
    });

    const profile = await fetchMyProfile();

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/users/me"),
      expect.objectContaining({
        headers: expect.any(Headers),
      })
    );
    expect(profile.university).toBe("MIT");
    expect(profile.skills?.length).toBe(1);
    expect(profile.skills?.[0].name).toBe("Python");
  });

  it("updateMyProfile should send PATCH with academic updates", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: { id: "u123", university: "Stanford", cgpa: 9.5 },
        error: null,
      }),
    });

    const updated = await updateMyProfile({
      university: "Stanford",
      cgpa: 9.5,
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/users/me"),
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ university: "Stanford", cgpa: 9.5 }),
      })
    );
    expect(updated.university).toBe("Stanford");
  });

  it("updateMySkills should send PUT /users/me/skills", async () => {
    const newSkills = [
      { name: "TypeScript", proficiency: "intermediate" },
      { name: "Go", proficiency: "beginner" },
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: [
          { id: "s1", name: "TypeScript", proficiency: "intermediate" },
          { id: "s2", name: "Go", proficiency: "beginner" },
        ],
        error: null,
      }),
    });

    const result = await updateMySkills(newSkills);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/users/me/skills"),
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({ skills: newSkills }),
      })
    );
    expect(result.length).toBe(2);
    expect(result[0].name).toBe("TypeScript");
  });

  it("updateMyInterests should send PUT /users/me/interests", async () => {
    const newInterests = [{ name: "Web Development" }];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: [{ id: "i1", name: "Web Development" }],
        error: null,
      }),
    });

    const result = await updateMyInterests(newInterests);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/users/me/interests"),
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({ interests: newInterests }),
      })
    );
    expect(result.length).toBe(1);
    expect(result[0].name).toBe("Web Development");
  });
});
