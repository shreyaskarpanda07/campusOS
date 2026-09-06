/**
 * Shared TypeScript types used across the frontend.
 *
 * These types mirror the backend Pydantic schemas to keep
 * frontend/backend contracts in sync.
 */

/** User profile model. */
export interface User {
  id: string;
  email: string;
  name: string;
  university: string | null;
  degree: string | null;
  branch: string | null;
  graduation_year: number | null;
  current_year: number | null;
  cgpa: number | null;
  preferred_opportunity_types: string[];
  preferred_work_modes: string[];
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

/** Response received upon successful registration or login. */
export interface AuthResponseData {
  user: User;
  access_token: string;
  token_type: string;
}

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
