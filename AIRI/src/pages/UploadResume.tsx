import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUserJDs, uploadResumes, type ResumeUploadResponse } from "../services/api";
import ResumeUpload from "../components/ResumeUpload";

type JobDescriptionOption = {
  requirement_id: string;
  job_title?: string;
};

const emptySummary: ResumeUploadResponse = {
  uploaded: [],
  updated: [],
  duplicates: [],
  screening_refreshed_for: [],
  screening_results: [],
};

export default function UploadResume() {
  const [jds, setJds] = useState<JobDescriptionOption[]>([]);
  const [selectedJD, setSelectedJD] = useState<JobDescriptionOption | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [uploadSummary, setUploadSummary] = useState<ResumeUploadResponse>(emptySummary);

  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    const fetchJDs = async () => {
      try {
        const data = await getUserJDs();
        setJds(Array.isArray(data) ? data : data.data || []);
      } catch (error) {
        console.error("Failed to load JDs", error);
        setErrorMessage("Unable to load your job descriptions right now.");
      }
    };

    if (user?.id || user?.user_id) {
      fetchJDs();
    }
  }, [user?.id, user?.user_id]);

  const screeningCount = useMemo(
    () => uploadSummary.screening_results.length,
    [uploadSummary.screening_results],
  );

  const handleUpload = async () => {
    if (!selectedJD) {
      setErrorMessage("Please select a Job Description first.");
      return;
    }

    if (files.length === 0) {
      setErrorMessage("Please upload at least one resume.");
      return;
    }

    const requirementId = selectedJD.requirement_id;
    const formData = new FormData();
    formData.append("requirement_id", requirementId);

    files.forEach((file) => {
      formData.append("resumes", file);
    });

    try {
      setLoading(true);
      setErrorMessage("");
      const response = await uploadResumes(formData);
      setUploadSummary(response);
      setFiles([]);

      if (response.uploaded.length === 0 && response.updated.length === 0) {
        setErrorMessage("All selected resumes were rejected as duplicates.");
        return;
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setErrorMessage("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 text-white space-y-4">
      <div>
        <h1 className="text-2xl mb-2">Upload Resumes</h1>
        <p className="text-sm text-slate-400">
          Duplicate resumes are rejected automatically. Updated resumes replace the existing candidate profile and refresh screening for the selected job.
        </p>
      </div>

      <div className="mb-4">
        <label className="block mb-2 text-sm text-slate-400">
          Select Job Description
        </label>

        <select
          className="bg-slate-900 border border-slate-700 rounded p-2 w-full"
          value={selectedJD?.requirement_id || ""}
          onChange={(e) => {
            const jd = jds.find((item) => item.requirement_id === e.target.value) || null;
            setSelectedJD(jd);
          }}
        >
          <option value="">-- choose --</option>

          {jds.map((jd) => (
            <option key={jd.requirement_id} value={jd.requirement_id}>
              {jd.job_title || `JD ${jd.requirement_id}`}
            </option>
          ))}
        </select>
      </div>

      <ResumeUpload files={files} setFiles={setFiles} />

      {errorMessage && (
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {errorMessage}
        </div>
      )}

      {(uploadSummary.uploaded.length > 0 || uploadSummary.updated.length > 0 || uploadSummary.duplicates.length > 0) && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 space-y-3">
          <h2 className="text-lg font-semibold">Latest Upload Summary</h2>

          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-lg bg-slate-800 p-3">
              <div className="text-sm text-slate-400">Created</div>
              <div className="text-2xl font-semibold text-emerald-400">{uploadSummary.uploaded.length}</div>
            </div>
            <div className="rounded-lg bg-slate-800 p-3">
              <div className="text-sm text-slate-400">Updated</div>
              <div className="text-2xl font-semibold text-amber-400">{uploadSummary.updated.length}</div>
            </div>
            <div className="rounded-lg bg-slate-800 p-3">
              <div className="text-sm text-slate-400">Rejected Duplicates</div>
              <div className="text-2xl font-semibold text-rose-400">{uploadSummary.duplicates.length}</div>
            </div>
          </div>

          <div className="text-sm text-slate-400">
            Screening refreshed for {uploadSummary.screening_refreshed_for.length} candidate(s); {screeningCount} result(s) were regenerated for this job.
          </div>

          {(uploadSummary.uploaded.length > 0 || uploadSummary.updated.length > 0) && selectedJD && (
            <button
              type="button"
              onClick={() => navigate(`/dashboard/results/${selectedJD.requirement_id}`)}
              className="inline-flex rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
            >
              View refreshed results
            </button>
          )}

          {uploadSummary.duplicates.length > 0 && (
            <div>
              <div className="mb-2 text-sm font-medium text-slate-200">Rejected files</div>
              <ul className="space-y-2 text-sm text-slate-300">
                {uploadSummary.duplicates.map((duplicate) => (
                  <li key={`${duplicate.file_name}-${duplicate.existing_resume_id || "none"}`} className="rounded-md border border-slate-800 px-3 py-2">
                    <span className="font-medium text-white">{duplicate.file_name}</span>
                    <span className="text-slate-400"> — {duplicate.message} (similarity {Math.round(duplicate.similarity * 100)}%)</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <button
        onClick={handleUpload}
        className="bg-green-600 px-4 py-2 rounded"
        disabled={loading}
      >
        {loading ? "Processing..." : "Upload & Refresh Screening"}
      </button>
    </div>
  );
}
