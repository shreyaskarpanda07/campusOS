"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  fetchMyProfile,
  updateMyInterests,
  updateMyProfile,
  updateMySkills,
  ApiRequestError,
} from "@/lib/api";
import { getToken } from "@/lib/auth";
import { User, Skill, Interest } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { TagInput, TagItem } from "@/components/ui/TagInput";

const ALL_OPPORTUNITY_TYPES = [
  "internship",
  "hackathon",
  "competition",
  "fellowship",
  "scholarship",
];

const ALL_WORK_MODES = ["remote", "onsite", "hybrid"];

export default function ProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form states
  const [name, setName] = useState("");
  const [university, setUniversity] = useState("");
  const [degree, setDegree] = useState("");
  const [branch, setBranch] = useState("");
  const [graduationYear, setGraduationYear] = useState<string>("");
  const [currentYear, setCurrentYear] = useState<string>("");
  const [cgpa, setCgpa] = useState<string>("");

  const [oppTypes, setOppTypes] = useState<string[]>([]);
  const [workModes, setWorkModes] = useState<string[]>([]);
  const [locations, setLocations] = useState<TagItem[]>([]);

  const [skills, setSkills] = useState<TagItem[]>([]);
  const [interests, setInterests] = useState<TagItem[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    fetchMyProfile()
      .then((user: User) => {
        setName(user.name || "");
        setUniversity(user.university || "");
        setDegree(user.degree || "");
        setBranch(user.branch || "");
        setGraduationYear(user.graduation_year ? String(user.graduation_year) : "");
        setCurrentYear(user.current_year ? String(user.current_year) : "");
        setCgpa(user.cgpa !== null && user.cgpa !== undefined ? String(user.cgpa) : "");
        setOppTypes(user.preferred_opportunity_types || []);
        setWorkModes(user.preferred_work_modes || []);
        setLocations(
          (user.preferred_locations || []).map((loc) => ({ name: loc }))
        );
        setSkills(
          (user.skills || []).map((s: Skill) => ({
            name: s.name,
            proficiency: s.proficiency || "intermediate",
          }))
        );
        setInterests(
          (user.interests || []).map((i: Interest) => ({ name: i.name }))
        );
      })
      .catch((err) => {
        if (err instanceof ApiRequestError && err.status === 401) {
          router.push("/login");
        } else {
          setErrorMsg(err.message || "Failed to load profile.");
        }
      })
      .finally(() => setLoading(false));
  }, [router]);

  const toggleOppType = (type: string) => {
    setOppTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const toggleWorkMode = (mode: string) => {
    setWorkModes((prev) =>
      prev.includes(mode) ? prev.filter((m) => m !== mode) : [...prev, mode]
    );
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      // 1. Update basic academic info & preferences
      await updateMyProfile({
        name: name.trim() || undefined,
        university: university.trim() || undefined,
        degree: degree.trim() || undefined,
        branch: branch.trim() || undefined,
        graduation_year: graduationYear ? parseInt(graduationYear, 10) : undefined,
        current_year: currentYear ? parseInt(currentYear, 10) : undefined,
        cgpa: cgpa ? parseFloat(cgpa) : undefined,
        preferred_opportunity_types: oppTypes,
        preferred_work_modes: workModes,
        preferred_locations: locations.map((l) => l.name),
      });

      // 2. Sync skills
      await updateMySkills(
        skills.map((s) => ({
          name: s.name,
          proficiency: s.proficiency || null,
        }))
      );

      // 3. Sync interests
      await updateMyInterests(interests.map((i) => ({ name: i.name })));

      setSuccessMsg("Profile and preferences updated successfully!");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex items-center gap-3 text-gray-500 text-sm">
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-primary-600 border-t-transparent" />
          Loading your student profile…
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* ── Top Header ── */}
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-200">
          <div>
            <Link
              href="/"
              className="text-xs font-semibold text-primary-600 uppercase tracking-wider hover:underline"
            >
              &larr; Back to CampusOS
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 mt-1">
              Student Profile & Eligibility
            </h1>
            <p className="text-sm text-gray-500">
              CampusOS matches you with relevant opportunities based on your academic details and skills.
            </p>
          </div>
        </div>

        {/* ── Alerts ── */}
        {successMsg && (
          <div
            role="status"
            className="mb-6 rounded-lg bg-green-50 p-4 border border-green-200 text-sm text-green-700"
          >
            {successMsg}
          </div>
        )}
        {errorMsg && (
          <div
            role="alert"
            className="mb-6 rounded-lg bg-red-50 p-4 border border-red-200 text-sm text-red-700"
          >
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-8">
          {/* ── Section 1: Academic Background ── */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-5">
            <h2 className="text-base font-semibold text-gray-900 border-b border-gray-100 pb-2">
              Academic Background
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
                required
              />

              <Input
                label="University / College"
                value={university}
                onChange={(e) => setUniversity(e.target.value)}
                placeholder="e.g. Stanford, MIT, IIT Bombay"
              />

              <Input
                label="Degree"
                value={degree}
                onChange={(e) => setDegree(e.target.value)}
                placeholder="e.g. B.Tech, B.S., MBA"
              />

              <Input
                label="Branch / Discipline"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                placeholder="e.g. Computer Science, Mechanical"
              />

              <Input
                label="Current Year of Study"
                type="number"
                min="1"
                max="6"
                value={currentYear}
                onChange={(e) => setCurrentYear(e.target.value)}
                placeholder="e.g. 3"
              />

              <Input
                label="Graduation Year"
                type="number"
                min="2020"
                max="2035"
                value={graduationYear}
                onChange={(e) => setGraduationYear(e.target.value)}
                placeholder="e.g. 2026"
              />

              <Input
                label="CGPA / Percentage"
                type="number"
                step="0.01"
                min="0.00"
                max="10.00"
                value={cgpa}
                onChange={(e) => setCgpa(e.target.value)}
                placeholder="e.g. 8.75"
                helperText="Scale of 10.0"
              />
            </div>
          </div>

          {/* ── Section 2: Skills & Proficiency ── */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
            <div>
              <h2 className="text-base font-semibold text-gray-900">
                Skills & Technical Expertise
              </h2>
              <p className="text-xs text-gray-500">
                Add programming languages, frameworks, or tools with your current proficiency.
              </p>
            </div>

            <TagInput
              label="Add Skills"
              placeholder="e.g. Python, React, SQL, PyTorch..."
              tags={skills}
              onChange={setSkills}
              showProficiency={true}
            />
          </div>

          {/* ── Section 3: Interests & Preferred Roles ── */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
            <div>
              <h2 className="text-base font-semibold text-gray-900">
                Career Interests & Domains
              </h2>
              <p className="text-xs text-gray-500">
                Areas you want to explore (e.g. Artificial Intelligence, Quantitative Finance, Web3, Product).
              </p>
            </div>

            <TagInput
              label="Add Interests"
              placeholder="e.g. Machine Learning, Distributed Systems, FinTech..."
              tags={interests}
              onChange={setInterests}
            />
          </div>

          {/* ── Section 4: Opportunity & Work Preferences ── */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-5">
            <h2 className="text-base font-semibold text-gray-900 border-b border-gray-100 pb-2">
              Opportunity Preferences
            </h2>

            {/* Opportunity Types */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Opportunity Types
              </label>
              <div className="flex flex-wrap gap-2">
                {ALL_OPPORTUNITY_TYPES.map((type) => {
                  const active = oppTypes.includes(type);
                  return (
                    <button
                      key={type}
                      type="button"
                      onClick={() => toggleOppType(type)}
                      className={`capitalize px-3.5 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                        active
                          ? "bg-primary-600 text-white border-primary-600 shadow-sm"
                          : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                      }`}
                    >
                      {type}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Work Modes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Work Modes
              </label>
              <div className="flex flex-wrap gap-2">
                {ALL_WORK_MODES.map((mode) => {
                  const active = workModes.includes(mode);
                  return (
                    <button
                      key={mode}
                      type="button"
                      onClick={() => toggleWorkMode(mode)}
                      className={`capitalize px-3.5 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                        active
                          ? "bg-primary-600 text-white border-primary-600 shadow-sm"
                          : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                      }`}
                    >
                      {mode}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Preferred Locations */}
            <div>
              <TagInput
                label="Preferred Cities / Locations"
                placeholder="e.g. Bangalore, San Francisco, Remote..."
                tags={locations}
                onChange={setLocations}
              />
            </div>
          </div>

          {/* ── Submit Button ── */}
          <div className="flex justify-end gap-3 pt-2">
            <Link href="/">
              <Button type="button" variant="outline">
                Cancel
              </Button>
            </Link>
            <Button
              type="submit"
              variant="primary"
              isLoading={saving}
            >
              Save Profile
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
