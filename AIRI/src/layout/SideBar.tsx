import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "../components/ui/button";
import {
  LayoutDashboard,
  FileText,
  Upload,
  BarChart3,
  LogOut,
} from "lucide-react";

export default function Sidebar({ handleLogout }: any) {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
    { name: "Upload JD", icon: FileText, path: "/dashboard/upload-jd" },
    { name: "Screen Resume", icon: Upload, path: "/dashboard/screen" },
    { name: "Results", icon: BarChart3, path: "/dashboard/results" },
  ];

  return (
    <aside className="w-72 h-screen sticky top-0 bg-slate-900 border-r border-slate-800 p-6 flex flex-col justify-between">
      <div>
        <div className="text-2xl font-semibold text-blue-500 mb-8">AIRI</div>

        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);

            return (
              <div
                key={item.name}
                onClick={() => navigate(item.path)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer
                ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-slate-400 hover:bg-slate-800"
                }`}
              >
                <Icon size={18} />
                {item.name}
              </div>
            );
          })}
        </nav>
      </div>

      <Button
        variant="ghost"
        onClick={handleLogout}
        className="justify-start gap-3 text-slate-400 hover:text-red-400"
      >
        <LogOut size={16} />
        Sign Out
      </Button>
    </aside>
  );
}
