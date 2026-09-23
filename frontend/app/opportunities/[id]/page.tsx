"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { fetchOpportunityDetail, ApiRequestError } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Opportunity } from "@/lib/types";

export default function OpportunityDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [opp, setOpp] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    if (!id) return;

    fetchOpportunityDetail(id)
      .then((data) => setOpp(data))
      .catch((err) => {
        if (err instanceof ApiRequestError && err.status === 401) {
          router.push("/login");
        } else {
          setErrorMsg(err.message || "Failed to load opportunity.");
        }
      })
      .finally(() => setLoading(false));
  }, [id, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex items-center gap-3 text-gray-500 text-sm">
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-primary-600 border-t-transparent" />
          Loading opportunity details…
        </div>
      </div>
    );
  }

  if (errorMsg || !opp) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white p-6 rounded-xl border border-gray-200 text-center shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-2">
            Opportunity Not Found
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            {errorMsg || "This opportunity may have expired or does not exist."}
          </p>
          <Link
            href="/discover"
            className="text-xs font-semibold text-primary-600 hover:underline"
          >
            &larr; Back to Discover
          </Link>
        </div>
      </div>
    );
  }

  const requiredSkills = (opp.skills || []).filter(
    (s) => s.requirement_type === "required"
  );
  const preferredSkills = (opp.skills || []).filter(
    (s) => s.requirement_type === "preferred"
  );

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* ── Back Navigation ── */}
        <Link
          href="/discover"
          className="inline-flex items-center text-xs font-semibold text-primary-600 uppercase tracking-wider hover:underline"
        >
          &larr; Back to Discover
        </Link>

        {/* ── Header Card ── */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <span className="capitalize px-3 py-1 rounded-full text-xs font-semibold border bg-primary-50 text-primary-700 border-primary-200">
                {opp.type}
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 mt-2">
                {opp.title}
              </h1>
              <p className="text-base font-semibold text-primary-700 mt-1">
                {opp.organization}
              </p>
            </div>

            {opp.application_url && (
              <a
                href={opp.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center bg-primary-600 hover:bg-primary-700 text-white font-medium text-sm px-6 py-3 rounded-lg shadow-sm transition-colors text-center"
              >
                Apply Now &rarr;
              </a>
            )}
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 mt-6 border-t border-gray-100 text-xs text-gray-600">
            <div>
              <span className="block text-gray-400">Deadline</span>
              <span className="font-semibold text-gray-900">
                {opp.deadline ? opp.deadline : "Rolling / Open"}
              </span>
            </div>
            <div>
              <span className="block text-gray-400">Work Mode</span>
              <span className="font-semibold text-gray-900 capitalize">
                {opp.work_mode || "Not specified"}
              </span>
            </div>
            <div>
              <span className="block text-gray-400">Location</span>
              <span className="font-semibold text-gray-900">
                {opp.location || "Remote / Unspecified"}
              </span>
            </div>
            <div>
              <span className="block text-gray-400">Compensation</span>
              <span className="font-semibold text-emerald-700">
                {opp.compensation || "Unspecified"}
              </span>
            </div>
          </div>
        </div>

        {/* ── Main Details Grid ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column (2/3): Description & Skills */}
          <div className="md:col-span-2 space-y-6">
            {/* Description */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-3">
              <h2 className="text-base font-bold text-gray-900">
                Opportunity Overview
              </h2>
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                {opp.description || "No detailed description provided."}
              </p>
            </div>

            {/* Skills Requirements */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
              <h2 className="text-base font-bold text-gray-900">
                Skills & Technologies
              </h2>

              {requiredSkills.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                    Required Skills
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {requiredSkills.map((s) => (
                      <span
                        key={s.id}
                        className="bg-primary-50 text-primary-800 border border-primary-200 text-xs font-medium px-3 py-1 rounded-full"
                      >
                        {s.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {preferredSkills.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                    Preferred / Nice-to-Have
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {preferredSkills.map((s) => (
                      <span
                        key={s.id}
                        className="bg-gray-100 text-gray-700 text-xs font-medium px-3 py-1 rounded-full"
                      >
                        {s.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {opp.skills.length === 0 && (
                <p className="text-xs text-gray-500">
                  No specific skill constraints listed. Open to all backgrounds.
                </p>
              )}
            </div>
          </div>

          {/* Right Column (1/3): Academic Eligibility & Source Provenance */}
          <div className="space-y-6">
            {/* Academic Eligibility */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
              <h2 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-2">
                Eligibility Criteria
              </h2>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-gray-400 block">Minimum CGPA:</span>
                  <span className="font-semibold text-gray-800">
                    {opp.minimum_cgpa ? `${opp.minimum_cgpa} / 10.0` : "No minimum CGPA required"}
                  </span>
                </div>

                {opp.eligibility?.eligible_years && (
                  <div>
                    <span className="text-gray-400 block">Eligible Graduation Years:</span>
                    <span className="font-semibold text-gray-800">
                      {opp.eligibility.eligible_years.join(", ")}
                    </span>
                  </div>
                )}

                {opp.eligibility?.eligible_branches && (
                  <div>
                    <span className="text-gray-400 block">Eligible Disciplines:</span>
                    <span className="font-semibold text-gray-800">
                      {opp.eligibility.eligible_branches.join(", ")}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Source Provenance (PRD Requirement) */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                Source Provenance
              </h2>

              {opp.sources && opp.sources.length > 0 ? (
                opp.sources.map((src, i) => (
                  <div key={i} className="text-xs space-y-1">
                    <p className="font-semibold text-gray-900">
                      {src.source_name}
                    </p>
                    {src.source_url && (
                      <a
                        href={src.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:underline break-all block"
                      >
                        {src.source_url}
                      </a>
                    )}
                    <span className="text-[11px] text-gray-400 block">
                      Indexed on {new Date(src.fetched_at).toLocaleDateString()}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-gray-500">
                  Direct official posting.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
