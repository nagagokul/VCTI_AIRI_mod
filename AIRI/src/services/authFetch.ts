const API_BASE = "http://127.0.0.1:8000";

export const authFetch = async (url: string, options: any = {}) => {
  let accessToken = localStorage.getItem("access_token");

  let response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${accessToken}`,
    },
  });

  // If token expired
  if (response.status === 401) {
    const refreshToken = localStorage.getItem("refresh_token");

    if (!refreshToken) {
      window.location.href = "/";
      return;
    }

    // Call refresh endpoint
    const refreshResponse = await fetch(`${API_BASE}/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    if (!refreshResponse.ok) {
      localStorage.clear();
      window.location.href = "/";
      return;
    }

    const refreshData = await refreshResponse.json();
    localStorage.setItem("access_token", refreshData.access_token);

    // Retry original request
    response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${refreshData.access_token}`,
      },
    });
  }

  return response;
};