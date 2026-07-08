const API_BASE = "http://localhost:8000";

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

const api = {
  users: () => apiGet("/users"),
  user: (id) => apiGet(`/users/${id}`),
  posts: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v != null))
    ).toString();
    return apiGet(`/posts${qs ? `?${qs}` : ""}`);
  },
  post: (id) => apiGet(`/posts/${id}`),
};
