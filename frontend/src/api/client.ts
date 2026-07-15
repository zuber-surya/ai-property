/**
 * The one place the frontend talks to the API. Grouped by domain (rules/frontend.md).
 * Errors come back as the envelope {error:{code,message}} (04-api-spec §1) — we
 * surface the human message, never a raw code.
 */
const BASE = 'http://127.0.0.1:8000/api/v1';

export class ApiError extends Error {
  constructor(public code: string, message: string) {
    super(message);
  }
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  });
  const body = res.status === 204 ? null : await res.json();
  if (!res.ok) {
    const e = body?.error ?? { code: 'ERROR', message: 'Something went wrong.' };
    throw new ApiError(e.code, e.message);
  }
  return body as T;
}
