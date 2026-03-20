import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AppLayout from "./layout/AppLayout";
import ProtectedRoute from "./ProtectedRoute";
import { useState, useEffect } from "react";
import UploadJD from "./pages/UploadJD";
import Screen from "./pages/UploadResume";
import Results from "./pages/Results";

function App() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  return (
    <Routes>
      <Route path="/" element={<Login onLogin={setUser} />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute user={user}>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="upload-jd" element={<UploadJD />} />
        <Route path="screen" element={<Screen />} />
        <Route path="results/" element={<Results />} />
        <Route path="results/:requirementId" element={<Results />} />
      </Route>

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
