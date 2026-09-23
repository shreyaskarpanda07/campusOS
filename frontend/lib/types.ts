/**
 * Shared TypeScript types used across the frontend.
 *
 * These types mirror the backend Pydantic schemas to keep
 * frontend/backend contracts in sync.
 */

export interface Skill {
  id: string;
  name: string;
  proficiency?: string | null;
}

export interface Interest {
  id: string;
  name: string;
}

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
  preferred_locations: string[];
  skills?: Skill[];
  interests?: Interest[];
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdate {
  name?: string;
  university?: string;
  degree?: string;
  branch?: string;
  graduation_year?: number;
  current_year?: number;
  cgpa?: number;
  preferred_opportunity_types?: string[];
  preferred_work_modes?: string[];
  preferred_locations?: string[];
}

/** Response received upon successful registration or login. */
export interface AuthResponseData {
  user: User;
  access_token: string;
  token_type: string;
}

/** Opportunity skill specification */
export interface OpportunitySkill {
  id: string;
  name: string;
  requirement_type: "required" | "preferred";
}

/** Source provenance representation */
export interface OpportunitySource {
  source_id: string;
  source_name: string;
  source_url?: string | null;
  fetched_at: string;
}

/** Deterministic Eligibility Evaluation result */
export interface EligibilityEvaluation {
  status: "eligible" | "ineligible" | "uncertain";
  reasons: string[];
  missing_data: string[];
}

/** Opportunity model */
export interface Opportunity {
  id: string;
  title: string;
  organization: string;
  type: string;
  description?: string | null;
  deadline?: string | null;
  start_date?: string | null;
  location?: string | null;
  work_mode?: string | null;
  minimum_cgpa?: number | null;
  eligibility: Record<string, any>;
  compensation?: string | null;
  application_url?: string | null;
  status: string;
  skills: OpportunitySkill[];
  sources?: OpportunitySource[];
  eligibility_evaluation?: EligibilityEvaluation | null;
  created_at: string;
  updated_at?: string;
}

export interface PaginationMeta {
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface OpportunityListResponse {
  items: Opportunity[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    pages: number;
  };
}

export interface OpportunityFilterParams {
  type?: string;
  work_mode?: string;
  location?: string;
  organization?: string;
  search?: string;
  status?: string;
  max_cgpa?: number;
  page?: number;
  per_page?: number;
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
