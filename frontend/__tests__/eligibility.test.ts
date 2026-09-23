/**
 * Tests for OpportunityCard Eligibility Badges and Evaluation Display.
 */

import { describe, it, expect } from "vitest";
import React from "react";
import { render, screen } from "@testing-library/react";
import { OpportunityCard } from "@/components/features/OpportunityCard";
import { Opportunity } from "@/lib/types";

const baseOpp: Opportunity = {
  id: "opp-1",
  title: "Software Engineer Intern",
  organization: "Stripe",
  type: "internship",
  status: "active",
  skills: [],
  eligibility: {},
  created_at: "2026-09-23T00:00:00Z",
};

describe("OpportunityCard Eligibility Badge Rendering", () => {
  it("renders '✓ Eligible' badge when status is eligible", () => {
    const opp: Opportunity = {
      ...baseOpp,
      eligibility_evaluation: {
        status: "eligible",
        reasons: ["Meets CGPA requirement (9.0 >= 7.5)"],
        missing_data: [],
      },
    };

    render(<OpportunityCard opportunity={opp} />);
    expect(screen.getByText("✓ Eligible")).toBeDefined();
  });

  it("renders '✕ Ineligible' badge when status is ineligible", () => {
    const opp: Opportunity = {
      ...baseOpp,
      eligibility_evaluation: {
        status: "ineligible",
        reasons: ["CGPA below minimum requirement"],
        missing_data: [],
      },
    };

    render(<OpportunityCard opportunity={opp} />);
    expect(screen.getByText("✕ Ineligible")).toBeDefined();
  });

  it("renders '? Needs Info' badge when status is uncertain", () => {
    const opp: Opportunity = {
      ...baseOpp,
      eligibility_evaluation: {
        status: "uncertain",
        reasons: ["CGPA missing in student profile"],
        missing_data: ["CGPA not specified in student profile"],
      },
    };

    render(<OpportunityCard opportunity={opp} />);
    expect(screen.getByText("? Needs Info")).toBeDefined();
  });
});
