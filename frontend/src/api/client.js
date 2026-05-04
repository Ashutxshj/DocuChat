const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const DEFAULT_USER_ID = import.meta.env.VITE_DEFAULT_USER_ID || "demo-user";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": DEFAULT_USER_ID,
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || "Request failed");
  }

  return response.json();
}

export const api = {
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      headers: {
        "X-User-Id": DEFAULT_USER_ID,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || "Upload failed");
    }

    return response.json();
  },

  processDocument: (payload) =>
    request("/process", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getDocumentStatus: (docId) => request(`/documents/${docId}`),

  sendMessage: (payload) =>
    request("/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getHistory: (sessionId) => request(`/history?session_id=${encodeURIComponent(sessionId)}`),
};
