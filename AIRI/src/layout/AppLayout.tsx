import { Outlet } from "react-router-dom";
import Sidebar from "./SideBar";

export default function AppLayout() {
  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/";
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar handleLogout={handleLogout} />

      <main className="flex-1 p-10 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
