type Result = {
  name: string;
  score: number;
  skills_match: string[];
  experience: string;
  summary: string;
};

interface Props {
  results: Result[];
}

export default function ResultsTable({ results }: Props) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <table className="w-full text-left">
        <thead className="bg-slate-800 text-slate-300 text-sm">
          <tr>
            <th className="p-4">Candidate</th>
            <th className="p-4">Match Score</th>
            <th className="p-4">Skills Match</th>
            <th className="p-4">Experience</th>
            <th className="p-4">AI Summary</th>
          </tr>
        </thead>

        <tbody>
          {results.map((candidate, index) => (
            <tr
              key={index}
              className="border-t border-slate-800 hover:bg-slate-800/40"
            >
              <td className="p-4 font-medium">{candidate.name}</td>

              <td className="p-4">
                <span className="bg-blue-600 px-3 py-1 rounded text-sm">
                  {candidate.score}%
                </span>
              </td>

              <td className="p-4 text-sm text-slate-300">
                {candidate.skills_match?.join(", ")}
              </td>

              <td className="p-4 text-sm text-slate-300">
                {candidate.experience}
              </td>

              <td className="p-4 text-sm text-slate-400">
                {candidate.summary}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
