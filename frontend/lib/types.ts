/**
 * Shared TypeScript types used across the frontend.
 *
 * These types mirror the backend Pydantic schemas to keep
 * frontend/backend contracts in sync.
 */

/** Opportunity types supported by the platform. */
export type OpportunityType =
  | "internship"
  | "hackathon"
  | "competition"
  | "fellowship"
  | "scholarship"
  | "other";

/** Work mode options. */
export type WorkMode = "remote" | "onsite" | "hybrid";

/** Application tracking statuses (FR-08). */
export type ApplicationStatus =
  | "saved"
  | "applied"
  | "assessment"
  | "interview"
  | "offer"
  | "rejected"
  | "withdrawn";

/** Eligibility determination result. */
export type EligibilityStatus = "eligible" | "ineligible" | "uncertain";
