import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadResumes, screenResumes, getUserJDs } from "../services/api";
import ResumeUpload from "../components/ResumeUpload";

export default function UploadResume() {
  const [jds, setJds] = useState<any[]>([]);
  const [selectedJD, setSelectedJD] = useState<any>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    const fetchJDs = async () => {
      try {
        const data = await getUserJDs(user.id);
        setJds(Array.isArray(data) ? data : data.data || []);
      } catch (err) {
        console.error("Failed to load JDs", err);
      }
    };

    if (user?.id) {
      fetchJDs();
    }
  }, []);

  const handleUpload = async () => {
    if (!selectedJD) {
      alert("Please select a Job Description first");
      return;
    }

    if (files.length === 0) {
      alert("Please upload at least one resume");
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

      await uploadResumes(formData);
      await screenResumes(requirementId);

      alert("Resumes uploaded and screening started");

      navigate(`/dashboard/results/${requirementId}`);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 text-white">
      <h1 className="text-2xl mb-4">Upload Resumes</h1>

      <div className="mb-4">
        <label className="block mb-2 text-sm text-slate-400">
          Select Job Description
        </label>

        <select
          className="bg-slate-900 border border-slate-700 rounded p-2 w-full"
          value={selectedJD?.requirement_id || ""}
          onChange={(e) => {
            const jd = jds.find((j) => j.requirement_id === e.target.value);
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

      <button
        onClick={handleUpload}
        className="bg-green-600 px-4 py-2 mt-4 rounded"
        disabled={loading}
      >
        {loading ? "Processing..." : "Upload & Screen"}
      </button>
    </div>
  );
}
