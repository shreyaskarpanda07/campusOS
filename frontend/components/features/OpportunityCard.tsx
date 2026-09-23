"use client";

import React from "react";
import Link from "next/link";
import { Opportunity } from "@/lib/types";

interface OpportunityCardProps {
  opportunity: Opportunity;
}

export const OpportunityCard: React.FC<OpportunityCardProps> = ({ opportunity }) => {
  const typeColors: Record<string, string> = {
    internship: "bg-blue-50 text-blue-700 border-blue-200",
    hackathon: "bg-purple-50 text-purple-700 border-purple-200",
    competition: "bg-amber-50 text-amber-700 border-amber-200",
    fellowship: "bg-emerald-50 text-emerald-700 border-emerald-200",
    scholarship: "bg-indigo-50 text-indigo-700 border-indigo-200",
  };

  const badgeColor =
    typeColors[opportunity.type.toLowerCase()] ||
    "bg-gray-50 text-gray-700 border-gray-200";

  // Calculate days to deadline
  let deadlineText: string | null = null;
  if (opportunity.deadline) {
    const today = new Date();
    const d = new Date(opportunity.deadline);
    const diffDays = Math.ceil((d.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    if (diffDays < 0) {
      deadlineText = "Deadline passed";
    } else if (diffDays === 0) {
      deadlineText = "Deadline today!";
    } else if (diffDays === 1) {
      deadlineText = "Deadline tomorrow";
    } else {
      deadlineText = `Deadline: in ${diffDays} days`;
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
      <div>
        {/* ── Type & Urgency Bar ── */}
        <div className="flex items-center justify-between gap-2 mb-2">
          <span
            className={`capitalize px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeColor}`}
          >
            {opportunity.type}
          </span>

          {deadlineText && (
            <span className="text-xs font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
              {deadlineText}
            </span>
          )}
        </div>

        {/* ── Title & Organization ── */}
        <h3 className="text-base font-bold text-gray-900 line-clamp-2">
          {opportunity.title}
        </h3>
        <p className="text-sm font-medium text-primary-700 mb-2">
          {opportunity.organization}
        </p>

        {/* ── Metadata: Location & Mode ── */}
        <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 mb-3">
          {opportunity.work_mode && (
            <span className="capitalize flex items-center gap-1">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-gray-400" />
              {opportunity.work_mode}
            </span>
          )}
          {opportunity.location && (
            <span className="flex items-center gap-1">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-gray-400" />
              {opportunity.location}
            </span>
          )}
          {opportunity.minimum_cgpa && (
            <span className="flex items-center gap-1 font-medium text-gray-700">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-primary-400" />
              Min CGPA: {opportunity.minimum_cgpa}
            </span>
          )}
        </div>

        {/* ── Description Snippet ── */}
        {opportunity.description && (
          <p className="text-xs text-gray-600 line-clamp-3 mb-4">
            {opportunity.description}
          </p>
        )}

        {/* ── Skills Required ── */}
        {opportunity.skills && opportunity.skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {opportunity.skills.slice(0, 4).map((s) => (
              <span
                key={s.id}
                className="bg-gray-100 text-gray-700 text-[11px] font-medium px-2 py-0.5 rounded"
              >
                {s.name}
              </span>
            ))}
            {opportunity.skills.length > 4 && (
              <span className="text-[11px] text-gray-400 px-1 py-0.5">
                +{opportunity.skills.length - 4} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* ── Card Footer ── */}
      <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
        {opportunity.compensation ? (
          <span className="text-xs font-semibold text-emerald-700">
            {opportunity.compensation}
          </span>
        ) : (
          <span className="text-xs text-gray-400">Unspecified comp</span>
        )}

        <div className="flex gap-2">
          <Link
            href={`/opportunities/${opportunity.id}`}
            className="text-xs font-medium text-primary-600 hover:text-primary-800 px-2.5 py-1.5 rounded border border-primary-200 hover:bg-primary-50 transition-colors"
          >
            Details
          </Link>
          {opportunity.application_url && (
            <a
              href={opportunity.application_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-medium text-white bg-primary-600 hover:bg-primary-700 px-2.5 py-1.5 rounded transition-colors"
            >
              Apply &rarr;
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
