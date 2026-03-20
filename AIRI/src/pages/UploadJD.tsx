import { uploadJD } from "../services/api";
import JDInput from "../components/JDInput";

export default function UploadJD() {
  const handleUploadJD = async (data: any) => {
    try {
      // data now already contains requirement_id and correctly named fields
      const response = await uploadJD(data);

      console.log("JD Saved:", response);
      alert("Job Description uploaded successfully!");
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload JD");
    }
  };

  return (
    <div className="p-6 text-white">
      <h1 className="text-2xl font-semibold mb-6">Add New Job Description</h1>

      <JDInput onSubmit={handleUploadJD} />
    </div>
  );
}
