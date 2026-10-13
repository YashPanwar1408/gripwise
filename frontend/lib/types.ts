// GripWise Frontend — API client types
// These mirror the backend Pydantic schemas exactly.

export type UserRole = "RIDER" | "MECHANIC" | "ADMIN";
export type VehicleType = "MOTORCYCLE" | "SCOOTER" | "BICYCLE" | "OTHER";
export type TyrePositionEnum = "FRONT" | "REAR" | "FRONT_LEFT" | "FRONT_RIGHT" | "REAR_LEFT" | "REAR_RIGHT";
export type ConfidenceTier =
  | "HIGH_CONFIDENCE"
  | "MEDIUM_CONFIDENCE"
  | "LOW_CONFIDENCE"
  | "NOT_AVAILABLE";
export type InspectionStatus = "PENDING" | "PROCESSING" | "COMPLETE" | "FAILED";
export type RecommendedAction =
  | "ok"
  | "monitor"
  | "inspect_soon"
  | "replace_urgently"
  | "seek_mechanic_now"
  | "analysis_failed";

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: { code: string; message: string; details?: Record<string, string> } | null;
}

export interface TokenResponse {
  user_id: string;
  role: UserRole;
  display_name: string;
  access_token: string;
  refresh_token: string;
}

export interface TyrePosition {
  tyre_position_id: string;
  vehicle_id: string;
  position: TyrePositionEnum;
  brand: string | null;
  model_name: string | null;
  size_spec: string | null;
  installed_at: string | null;
  installed_km: number | null;
  created_at: string;
}

export interface Vehicle {
  vehicle_id: string;
  make: string;
  model: string;
  year: number | null;
  registration: string | null;
  vehicle_type: VehicleType;
  tyre_positions: TyrePosition[];
  created_at: string;
}

export interface InspectionObservation {
  field: string;
  value: number | boolean | string | null;
  confidence: ConfidenceTier;
  explanation: string;
  caveat: string | null;
}

export interface Inspection {
  inspection_id: string;
  tyre_position_id: string;
  status: InspectionStatus;
  created_at: string;
  completed_at: string | null;
  inference_provider: string | null;
  model_version: string | null;
  image_quality: { status: string; issues: string[] };
  recommended_action: RecommendedAction | null;
  recommended_action_explanation: string | null;
  observations: InspectionObservation[];
  inference_ms: number | null;
  mechanic_verified?: boolean;
}

export interface ConsentRecord {
  id: string;
  rider_id: string;
  mechanic_id: string;
  granted_at: string;
  revoked_at: string | null;
  mechanic_name?: string | null;
  workshop_name?: string | null;
  rider_name?: string | null;
}

export interface MechanicFinding {
  id: string;
  inspection_id: string;
  mechanic_id: string;
  tread_depth_mm: number | null;
  pressure_psi: number | null;
  puncture_count: number | null;
  notes: string | null;
  created_at: string;
}

export interface ServiceRecord {
  id: string;
  tyre_position_id: string;
  mechanic_id: string;
  service_type: string;
  service_date: string;
  odometer_km: number | null;
  cost_amount: number | null;
  notes: string | null;
  created_at: string;
}

// ── Mechanic Growth Types ──────────────────────────────────────────

export interface MechanicProfile {
  user_id: string;
  display_name: string;
  workshop_name: string | null;
  workshop_city: string | null;
  years_experience: number | null;
  specialization: string | null;
  workshop_address: string | null;
  phone: string | null;
  bio: string | null;
  certifications?: string[] | null;
  completion_percent: number;
  completion_checklist: Record<string, boolean>;
}

export interface QuizQuestion {
  id: number;
  prompt: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface LearningModuleSummary {
  id: string;
  module_code: string;
  title: string;
  category: string;
  estimated_minutes: number;
  summary: string;
  points_reward: number;
  technical_source: string;
  completed: boolean;
  score_percent?: number | null;
  completed_at?: string | null;
}

export interface LearningModuleDetail extends LearningModuleSummary {
  content_markdown: string;
  quiz_questions: QuizQuestion[];
}

export interface QuizQuestionFeedback {
  question_id: number;
  selected_index: number;
  correct_index: number;
  is_correct: boolean;
  explanation: string;
}

export interface QuizResult {
  module_id: string;
  score_percent: number;
  passed: boolean;
  points_awarded: number;
  total_points: number;
  tier: string;
  newly_earned_badges: string[];
  feedback: QuizQuestionFeedback[];
}

export interface MechanicBadge {
  id: string;
  title: string;
  description: string;
  criteria_description: string;
  icon_name: string;
  category: string;
  points_threshold?: number | null;
  earned: boolean;
  earned_at?: string | null;
}

export interface CustomerReferral {
  id: string;
  mechanic_id: string;
  customer_name_masked: string;
  customer_phone_masked?: string | null;
  vehicle_model: string;
  tyre_need: string;
  status: "PENDING" | "CONTACTED" | "SERVICE_COMPLETED" | "EXPIRED";
  consent_confirmed: boolean;
  service_record_id?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScoringRule {
  activity: string;
  points: number;
  description: string;
  ethical_safeguard: string;
}

export interface SaathiDashboardStats {
  mechanic_id: string;
  display_name: string;
  workshop_name: string | null;
  workshop_city: string | null;
  profile_completeness_percent: number;
  total_points: number;
  tier: string;
  next_tier?: string | null;
  points_to_next_tier: number;
  completed_modules_count: number;
  total_modules_count: number;
  verified_findings_count: number;
  recorded_services_count: number;
  total_referrals_count: number;
  completed_referrals_count: number;
  badges_earned_count: number;
  total_badges_count: number;
  earned_badges: MechanicBadge[];
  all_badges: MechanicBadge[];
  scoring_rules: ScoringRule[];
  case_study_context: {
    program_name: string;
    challenge: string;
    purpose: string;
    disclaimer: string;
  };
}

export interface SaathiProgramInitiative {
  id: string;
  title: string;
  category: string;
  description: string;
  eligibility_level: string;
  status: string;
  tool_specs?: Record<string, string> | null;
}
