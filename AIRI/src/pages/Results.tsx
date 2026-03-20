import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getResults } from "../services/api";
import ResultsTable from "../components/ResultTable";

type ResultRow = {
  name: string;
  score: number;
  skills_match: string[];
  experience: string;
  summary: string;
};

export default function Results() {
  const { requirementId } = useParams();
  const [results, setResults] = useState<ResultRow[]>([]);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getResults(requirementId!);

        const formatted = data.results.map((result: any) => ({
          name: result.candidate_name || "Unnamed Candidate",
          score: result.score,
          skills_match: result.skills_match || [],
          experience: result.experience != null ? `${result.experience} years` : "N/A",
          summary: result.summary || "AI summary not available",
        }));

        setResults(formatted);
      } catch (error) {
        console.error("Failed to fetch results", error);
      }
    };

    if (requirementId) {
      fetchResults();
    }
  }, [requirementId]);

  return (
    <div className="p-6 text-white">
      <h1 className="text-2xl mb-4">Screening Results</h1>

      <ResultsTable results={results} />
    </div>
  );
}
