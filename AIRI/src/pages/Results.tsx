import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getResults } from "../services/api";
import ResultsTable from "../components/ResultTable";

export default function Results() {
  const { requirementId } = useParams();
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getResults(requirementId!);

        const formatted = data.results.map((r: any) => {
          let extractedName = "";

          if (r.resume_name) {
            extractedName = r.resume_name
              .split("_")[1]
              ?.replace(".pdf", "")
              .replace(/_/g, " ");
          }

          return {
            name: r.candidate_name || extractedName,
            score: r.score,
            skills_match: r.skills_match,
            experience: r.experience,
            // summary: "AI summary not available"
          };
        });

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
