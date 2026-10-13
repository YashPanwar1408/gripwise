// GripWise Frontend — Typed API client
import type {
  ApiResponse,
  TokenResponse,
  Vehicle,
  TyrePosition,
  Inspection,
  ConsentRecord,
  MechanicFinding,
  ServiceRecord,
  MechanicProfile,
  LearningModuleSummary,
  LearningModuleDetail,
  QuizResult,
  MechanicBadge,
  CustomerReferral,
  SaathiDashboardStats,
  SaathiProgramInitiative,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: Record<string, string>
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string>),
  };

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  const json = (await res.json().catch(() => null)) as
    | (Partial<ApiResponse<T>> & { detail?: unknown; message?: unknown })
    | null;

  if (!res.ok || !json?.success) {
    const detail = json?.detail;
    const detailObject =
      detail !== null && typeof detail === "object" && !Array.isArray(detail)
        ? (detail as { code?: unknown; message?: unknown })
        : null;
    const validationMessage = Array.isArray(detail)
      ? detail
          .map((item) =>
            item && typeof item === "object" && "msg" in item && typeof item.msg === "string"
              ? item.msg
              : "Invalid request"
          )
          .join("; ")
      : undefined;

    throw new ApiError(
      json?.error?.code ??
        (typeof detailObject?.code === "string" ? detailObject.code : `HTTP_${res.status}`),
      json?.error?.message ??
        (typeof detail === "string" ? detail : undefined) ??
        (typeof detailObject?.message === "string" ? detailObject.message : undefined) ??
        validationMessage ??
        (typeof json?.message === "string" ? json.message : undefined) ??
        (res.statusText || "Request failed"),
      json?.error?.details
    );
  }
  return json.data as T;
}

// ── Auth ─────────────────────────────────────────────────────────

export const authApi = {
  register: (body: {
    display_name: string;
    email?: string;
    mobile?: string;
    password: string;
    role?: string;
    workshop_name?: string;
    workshop_city?: string;
  }) =>
    request<TokenResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  login: (credential: string, password: string) =>
    request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ credential, password }),
    }),

  refresh: (refresh_token: string) =>
    request<TokenResponse>("/api/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
    }),
};

// ── Vehicles ─────────────────────────────────────────────────────

export const vehiclesApi = {
  list: (token: string) =>
    request<{ vehicles: Vehicle[] }>("/api/vehicles", {}, token),

  create: (
    token: string,
    body: { make: string; model: string; year?: number; registration?: string; vehicle_type: string }
  ) =>
    request<Vehicle>("/api/vehicles", { method: "POST", body: JSON.stringify(body) }, token),

  addTyrePosition: (
    token: string,
    vehicleId: string,
    body: {
      position: string;
      brand?: string;
      model_name?: string;
      size_spec?: string;
      installed_at?: string;
      installed_km?: number;
    }
  ) =>
    request<TyrePosition>(
      `/api/vehicles/${vehicleId}/tyre-positions`,
      { method: "POST", body: JSON.stringify(body) },
      token
    ),
};

// ── Inspections ───────────────────────────────────────────────────

export const inspectionsApi = {
  submit: (token: string, tyrePositionId: string, image: File, odometerKm?: number) => {
    const form = new FormData();
    form.append("tyre_position_id", tyrePositionId);
    form.append("image", image);
    if (odometerKm !== undefined) form.append("odometer_km", String(odometerKm));
    return request<{ inspection_id: string; status: string; poll_url: string }>(
      "/api/inspections",
      { method: "POST", body: form },
      token
    );
  },

  get: (token: string, inspectionId: string) =>
    request<Inspection>(`/api/inspections/${inspectionId}`, {}, token),

  list: (token: string, tyrePositionId?: string) =>
    request<{ inspections: Inspection[] }>(
      `/api/inspections${tyrePositionId ? `?tyre_position_id=${tyrePositionId}` : ""}`,
      {},
      token
    ),
};

// ── Consent & Mechanic ────────────────────────────────────────────

export const consentApi = {
  list: (token: string) =>
    request<ConsentRecord[]>("/api/consent", {}, token),
  grant: (token: string, mechanic_id: string) =>
    request<ConsentRecord>("/api/consent", { method: "POST", body: JSON.stringify({ mechanic_id }) }, token),
  revoke: (token: string, consent_id: string) =>
    request<{ success: boolean }>(`/api/consent/${consent_id}`, { method: "DELETE" }, token),
};

export const mechanicApi = {
  getInspections: (token: string) =>
    request<{ inspections: Inspection[] }>("/api/mechanic/inspections", {}, token),
  getInspection: (token: string, inspectionId: string) =>
    request<Inspection>(`/api/mechanic/inspections/${inspectionId}`, {}, token),
  addFinding: (token: string, inspectionId: string, body: any) =>
    request<MechanicFinding>(`/api/mechanic/inspections/${inspectionId}/findings`, { method: "POST", body: JSON.stringify(body) }, token),
  addServiceRecord: (token: string, body: any) =>
    request<ServiceRecord>("/api/mechanic/service-records", { method: "POST", body: JSON.stringify(body) }, token),
};

// ── Mechanic Growth API ────────────────────────────────────────────

export const saathiApi = {
  getDashboard: (token: string) =>
    request<SaathiDashboardStats>("/api/saathi/dashboard", {}, token),

  getProfile: (token: string) =>
    request<MechanicProfile>("/api/saathi/profile", {}, token),

  updateProfile: (token: string, body: Partial<MechanicProfile>) =>
    request<MechanicProfile>("/api/saathi/profile", { method: "PUT", body: JSON.stringify(body) }, token),

  getModules: (token: string) =>
    request<{ modules: LearningModuleSummary[] }>("/api/saathi/learning/modules", {}, token),

  getModuleDetail: (token: string, moduleId: string) =>
    request<LearningModuleDetail>(`/api/saathi/learning/modules/${moduleId}`, {}, token),

  submitQuiz: (token: string, moduleId: string, answers: number[]) =>
    request<QuizResult>(
      `/api/saathi/learning/modules/${moduleId}/quiz`,
      { method: "POST", body: JSON.stringify({ answers }) },
      token
    ),

  getBadges: (token: string) =>
    request<{ badges: MechanicBadge[] }>("/api/saathi/badges", {}, token),

  getReferrals: (token: string) =>
    request<{ referrals: CustomerReferral[] }>("/api/saathi/referrals", {}, token),

  createReferral: (
    token: string,
    body: {
      customer_name_masked: string;
      customer_phone_masked?: string;
      vehicle_model: string;
      tyre_need: string;
      notes?: string;
      consent_confirmed?: boolean;
    }
  ) =>
    request<CustomerReferral>("/api/saathi/referrals", { method: "POST", body: JSON.stringify(body) }, token),

  updateReferral: (
    token: string,
    referralId: string,
    body: { status: string; notes?: string; service_record_id?: string }
  ) =>
    request<CustomerReferral>(
      `/api/saathi/referrals/${referralId}`,
      { method: "PATCH", body: JSON.stringify(body) },
      token
    ),

  getInitiatives: (token: string) =>
    request<{ case_study: string; program_disclaimer: string; initiatives: SaathiProgramInitiative[] }>(
      "/api/saathi/initiatives",
      {},
      token
    ),
};

export { ApiError };
