import { API_BASE } from "./api";
import { authFetch } from "./authFetch";

export const candidateService = {
  searchByJD: async (jdText: string) => {
    const token = localStorage.getItem("access_token");

    const response = await authFetch("/your-backend-endpoint", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ jd_text: jdText }),
    });

    if (!response) {
      throw new Error("Authentication failed");
    }

    if (!response.ok) {
      throw new Error("Failed to fetch candidates");
    }

    return await response.json();
  },
};