import { useState } from "react";

interface Props {
  onSubmit: (data: any) => void;
}

export default function JDInput({ onSubmit }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [skills, setSkills] = useState("");
  const [experience, setExperience] = useState("");

  const handleSubmit = () => {
    if (!title || !description) return;

    const jdData = {
      requirement_id: `REQ-${Date.now()}`,
      job_title: title,
      job_description: description,
      experience_level: experience,
      required_skills: skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean),
    };

    onSubmit(jdData);

    setTitle("");
    setDescription("");
    setSkills("");
    setExperience("");
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
      <h2 className="text-lg font-semibold text-white">
        Upload Job Description
      </h2>

      <div>
        <label className="block text-sm mb-1 text-slate-300">Job Title</label>
        <input
          type="text"
          className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white"
          placeholder="Frontend Developer"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm mb-1 text-slate-300">
          Job Description
        </label>
        <textarea
          className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white min-h-[120px]"
          placeholder="Paste job description..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm mb-1 text-slate-300">
          Required Skills
        </label>
        <input
          type="text"
          className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white"
          placeholder="React, Node.js, PostgreSQL"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm mb-1 text-slate-300">
          Minimum Experience (years)
        </label>
        <input
          type="number"
          className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white"
          placeholder="3"
          value={experience}
          onChange={(e) => setExperience(e.target.value)}
        />
      </div>

      <button
        onClick={handleSubmit}
        className="bg-blue-600 hover:bg-blue-700 px-5 py-2 rounded text-white"
        disabled={!title || !description}
      >
        Save Job Description
      </button>
    </div>
  );
}
