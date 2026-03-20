export const API_BASE = "http://127.0.0.1:8000";

export const uploadJD = async (data: any) => {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API_BASE}/jd`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error("JD upload failed");
  }

  return res.json();
};

export const getUserJDs = async () => {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API_BASE}/jd/user`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  console.log("GET /jd/user response status:", res.status);

  if (!res.ok) {
    throw new Error("Failed to fetch JDs");
  }

  return res.json();
};

export const screenResumes = async (requirement_id: string) => {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ requirement_id }),
  });

  if (!res.ok) {
    throw new Error("Screening failed");
  }

  return res.json();
};

export const uploadResumes = async (formData: FormData) => {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Resume upload failed");
  }

  return res.json();
};

export const getResults = async (requirementId: string) => {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API_BASE}/results/${requirementId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch results");
  }

  return res.json();
};
export const downloadResume = async (resumeId: string) => {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API_BASE}/resumes/resume/${resumeId}/download`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Download failed");
  }

  return res.blob();
};
