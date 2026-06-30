const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(body.detail || `Request failed with status ${response.status}`, response.status);
  }
  return response.json();
}

export function shortenUrl({ url, customAlias, expiresAt }) {
  return request("/shorten", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url,
      custom_alias: customAlias || null,
      expires_at: expiresAt || null,
    }),
  });
}

export function getUrlStats(shortCode) {
  return request(`/api/urls/${shortCode}/stats`);
}

export { ApiError, API_BASE_URL };
