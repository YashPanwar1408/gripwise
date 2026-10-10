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
  created_at: string;
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
