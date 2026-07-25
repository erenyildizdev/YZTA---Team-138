const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000/api";

const ACCESS_TOKEN_KEY = "fikirlab_access_token";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string | null): void {
  if (token) localStorage.setItem(ACCESS_TOKEN_KEY, token);
  else localStorage.removeItem(ACCESS_TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (response.status === 204) return undefined as T;

  const text = await response.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!response.ok) {
    let message: string | null = null;

    if (body && typeof body === "object") {
      const anyBody = body as Record<string, unknown>;
      if ("detail" in anyBody || "message" in anyBody) {
        message = String(anyBody.detail ?? anyBody.message);
      } else {
        const fieldErrors = Object.entries(anyBody)
          .map(([field, value]) => (Array.isArray(value) ? `${field}: ${value.join(" ")}` : null))
          .filter((part): part is string => Boolean(part));
        if (fieldErrors.length) message = fieldErrors.join(" ");
      }
    } else if (typeof body === "string" && body) {
      message = body;
    }

    throw new ApiError(message ?? `İstek başarısız oldu (${response.status}).`, response.status);
  }

  return body as T;
}

export interface AuthUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface RegisterResponse {
  message: string;
  user: AuthUser;
}

export function register(payload: RegisterPayload): Promise<RegisterResponse> {
  return request<RegisterResponse>("/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface ValidationRoadmapPhase {
  week?: number;
  phase?: number;
  title?: string;
  [section: string]: unknown;
}

export interface ValidationRoadmapData {
  roadmap_type?: string;
  idea_title?: string;
  phases: ValidationRoadmapPhase[];
}

export interface ValidationRoadmapResponse {
  id: number;
  idea: number;
  roadmap_data: ValidationRoadmapData;
  created_at: string;
}

export function getValidationRoadmap(ideaId: number): Promise<ValidationRoadmapResponse> {
  return request<ValidationRoadmapResponse>(`/ideas/${ideaId}/roadmap/`);
}

export function generateValidationRoadmap(ideaId: number): Promise<ValidationRoadmapResponse> {
  return request<ValidationRoadmapResponse>(`/ideas/${ideaId}/generate-roadmap/`, {
    method: "POST",
  });
}

export interface IdeaPayload {
  title: string;
  description: string;
  target_audience: string;
  problem: string;
  solution: string;
  sector: string;
}

export interface IdeaResponse extends IdeaPayload {
  id: number;
  created_at: string;
}

export function createIdea(payload: IdeaPayload): Promise<IdeaResponse> {
  return request<IdeaResponse>("/ideas/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
