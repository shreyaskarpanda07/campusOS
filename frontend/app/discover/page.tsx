"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { fetchOpportunities, ApiRequestError } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Opportunity } from "@/lib/types";
import { OpportunityCard } from "@/components/features/OpportunityCard";

const CATEGORIES = [
  { label: "All Opportunities", value: "" },
  { label: "Internships", value: "internship" },
  { label: "Hackathons", value: "hackathon" },
  { label: "Competitions", value: "competition" },
  { label: "Fellowships", value: "fellowship" },
  { label: "Scholarships", value: "scholarship" },
];

const MODES = [
  { label: "All Modes", value: "" },
  { label: "Remote", value: "remote" },
  { label: "Hybrid", value: "hybrid" },
  { label: "Onsite", value: "onsite" },
];

export default function DiscoverPage() {
  const router = useRouter();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedMode, setSelectedMode] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const loadOpportunities = (targetPage = page) => {
    setLoading(true);
    setErrorMsg(null);

    fetchOpportunities({
      search: search.trim() || undefined,
      type: selectedCategory || undefined,
      work_mode: selectedMode || undefined,
      page: targetPage,
      per_page: 9,
    })
      .then((res) => {
        setOpportunities(res.items);
        setPage(res.pagination.page);
        setTotalPages(res.pagination.pages);
        setTotalCount(res.pagination.total);
      })
      .catch((err) => {
        if (err instanceof ApiRequestError && err.status === 401) {
          router.push("/login");
        } else {
          setErrorMsg(err.message || "Failed to load opportunities.");
        }
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }
    loadOpportunities(1);
  }, [selectedCategory, selectedMode, router]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadOpportunities(1);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* ── Top Bar ── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-gray-200 pb-5">
          <div>
            <Link
              href="/"
              className="text-xs font-semibold text-primary-600 uppercase tracking-wider hover:underline"
            >
              &larr; CampusOS Home
            </Link>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight mt-1">
              Discover Opportunities
            </h1>
            <p className="text-sm text-gray-500">
              Explore verified internships, hackathons, case challenges, and scholarships.
            </p>
          </div>

          <Link
            href="/profile"
            className="inline-flex items-center text-xs font-medium text-primary-700 bg-primary-50 hover:bg-primary-100 border border-primary-200 px-3.5 py-2 rounded-lg transition-colors"
          >
            My Profile & Eligibility &rarr;
          </Link>
        </div>

        {/* ── Search & Filter Controls ── */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm space-y-4">
          <form onSubmit={handleSearchSubmit} className="flex gap-2">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by role, company, or keyword (e.g. Google, Machine Learning, Case Challenge)..."
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
            <button
              type="submit"
              className="bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
            >
              Search
            </button>
          </form>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-gray-100">
            {/* Category tabs */}
            <div className="flex flex-wrap gap-1.5">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => {
                    setSelectedCategory(cat.value);
                  }}
                  className={`text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors ${
                    selectedCategory === cat.value
                      ? "bg-primary-600 text-white border-primary-600 shadow-sm"
                      : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Work Mode dropdown */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Mode:</span>
              <select
                value={selectedMode}
                onChange={(e) => {
                  setSelectedMode(e.target.value);
                }}
                className="text-xs font-medium rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-gray-700 focus:outline-none focus:border-primary-500"
              >
                {MODES.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* ── Status / Error ── */}
        {errorMsg && (
          <div
            role="alert"
            className="rounded-lg bg-red-50 p-4 border border-red-200 text-sm text-red-700"
          >
            {errorMsg}
          </div>
        )}

        {/* ── Results Info ── */}
        <div className="flex items-center justify-between text-xs text-gray-500 px-1">
          <span>
            Showing <strong className="text-gray-900">{opportunities.length}</strong> of{" "}
            <strong className="text-gray-900">{totalCount}</strong> opportunities
          </span>
        </div>

        {/* ── Grid or Empty State ── */}
        {loading ? (
          <div className="py-16 text-center text-gray-400 text-sm">
            <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-primary-600 border-t-transparent mb-2" />
            <p>Loading opportunities…</p>
          </div>
        ) : opportunities.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm">
            <div className="text-3xl mb-2">🔍</div>
            <h3 className="text-base font-semibold text-gray-900 mb-1">
              No matching opportunities found
            </h3>
            <p className="text-xs text-gray-500 max-w-sm mx-auto mb-4">
              Try adjusting your search query, removing specific filters, or resetting category selections.
            </p>
            <button
              onClick={() => {
                setSearch("");
                setSelectedCategory("");
                setSelectedMode("");
              }}
              className="text-xs font-medium text-primary-600 hover:text-primary-800 underline"
            >
              Reset all filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {opportunities.map((opp) => (
              <OpportunityCard key={opp.id} opportunity={opp} />
            ))}
          </div>
        )}

        {/* ── Pagination ── */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-3 pt-6">
            <button
              onClick={() => loadOpportunities(page - 1)}
              disabled={page <= 1}
              className="rounded-lg border border-gray-300 bg-white px-3.5 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              &larr; Previous
            </button>
            <span className="text-xs text-gray-600 font-medium">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => loadOpportunities(page + 1)}
              disabled={page >= totalPages}
              className="rounded-lg border border-gray-300 bg-white px-3.5 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next &rarr;
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
