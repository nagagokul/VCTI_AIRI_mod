import { useEffect, useState } from "react";
import { Card, CardContent } from "../components/ui/card";

export default function Dashboard() {
  const [username, setUsername] = useState("");

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      const user = JSON.parse(storedUser);
      setUsername(user.username);
    }
  }, []);

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">
          Welcome back, {username}
        </h1>
        <p className="text-slate-400 mt-2">
          Here’s an overview of your AI recruitment activity.
        </p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {[
          { label: "Total JDs", value: "4" },
          { label: "Resumes Uploaded", value: "26" },
          { label: "Screenings Completed", value: "4" },
          { label: "Last Activity", value: "2 hrs ago" },
        ].map((stat) => (
          <Card key={stat.label} className="bg-slate-900 border-slate-800">
            <CardContent className="p-6">
              <p className="text-sm text-slate-400">{stat.label}</p>
              <h2 className="text-2xl font-semibold mt-2">{stat.value}</h2>
            </CardContent>
          </Card>
        ))}
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">
          Recent Screening Activity
        </h2>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-6 space-y-4 text-sm">
            <div className="flex justify-between text-slate-400">
              <span>Frontend Developer</span>
              <span>12 Resumes</span>
              <span className="text-green-400">Completed</span>
              <span>Today</span>
            </div>

            <div className="flex justify-between text-slate-400">
              <span>Backend Engineer</span>
              <span>8 Resumes</span>
              <span className="text-green-400">Completed</span>
              <span>Yesterday</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">System Status</h2>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-6 space-y-2 text-sm">
            <p>
              🤖 AI Engine: <span className="text-green-400">Active</span>
            </p>
            <p>
              🔗 Backend: <span className="text-green-400">Connected</span>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
