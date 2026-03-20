import { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent } from "../components/ui/card";
import { Label } from "../components/ui/label";
import { useNavigate } from "react-router-dom";

type LoginPageProps = {
  onLogin: (user: any) => void;
};

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [form, setForm] = useState({
    username: "",
    password: "",
    confirmPassword: "",
  });

  const [isSignup, setIsSignup] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate("/dashboard");
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!form.username || !form.password) {
      setError("All fields are required");
      return;
    }

    if (isSignup && form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      if (isSignup) {
        const response = await fetch("http://127.0.0.1:8000/users/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: form.username,
            password: form.password,
          }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || "Signup failed");
        }

        setIsSignup(false);
        setForm({ username: "", password: "", confirmPassword: "" });
        setError("Account created successfully. Please login.");
        return;
      }

      const formData = new URLSearchParams();
      formData.append("username", form.username);
      formData.append("password", form.password);

      const loginResponse = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!loginResponse.ok) {
        throw new Error("Invalid credentials");
      }

      const data = await loginResponse.json();

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      const tokenPayload = JSON.parse(atob(data.access_token.split(".")[1]));
      const userId = tokenPayload.user_id;

      const userResponse = await fetch(`http://127.0.0.1:8000/users/${userId}`);

      if (!userResponse.ok) {
        throw new Error("Failed to fetch user details");
      }

      const user = await userResponse.json();

      localStorage.setItem("user", JSON.stringify(user));

      onLogin(user);

      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#060a12]">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.08)_1px,transparent_1px)] bg-[size:60px_60px]" />

      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-violet-600/10 to-transparent blur-3xl" />

      <Card className="relative w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 shadow-2xl rounded-2xl">
        <CardContent className="p-8 space-y-6">
          <div className="text-center space-y-2">
            <div className="mx-auto w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg">
              <span className="text-white text-xl font-bold">AIRI</span>
            </div>

            <h1 className="text-2xl font-bold text-white">VCTI</h1>
            <p className="text-xs tracking-widest uppercase text-blue-400">
              AI Recruitment Intelligence
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label className="text-xs uppercase tracking-widest text-slate-400">
                Username
              </Label>
              <Input
                className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 focus:border-blue-500"
                placeholder="Enter username"
                value={form.username}
                onChange={(e) =>
                  setForm((p) => ({ ...p, username: e.target.value }))
                }
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs uppercase tracking-widest text-slate-400">
                Password
              </Label>
              <Input
                type="password"
                className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 focus:border-blue-500"
                placeholder="Enter password"
                value={form.password}
                onChange={(e) =>
                  setForm((p) => ({ ...p, password: e.target.value }))
                }
              />
            </div>

            {isSignup && (
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-widest text-slate-400">
                  Confirm Password
                </Label>
                <Input
                  type="password"
                  className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 focus:border-blue-500"
                  placeholder="Confirm password"
                  value={form.confirmPassword}
                  onChange={(e) =>
                    setForm((p) => ({
                      ...p,
                      confirmPassword: e.target.value,
                    }))
                  }
                />
              </div>
            )}

            {error && (
              <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-md px-3 py-2">
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-500 to-violet-600 hover:opacity-90 text-white font-medium"
            >
              {loading
                ? isSignup
                  ? "Creating Account..."
                  : "Authenticating..."
                : isSignup
                  ? "Create Account →"
                  : "Log In →"}
            </Button>
          </form>

          <div className="text-center text-sm text-slate-400">
            {isSignup ? "Already have an account?" : "Don't have an account?"}
            <button
              type="button"
              onClick={() => {
                setIsSignup(!isSignup);
                setError("");
              }}
              className="ml-2 text-blue-400 hover:underline"
            >
              {isSignup ? "Sign In" : "Sign Up"}
            </button>
          </div>

          <p className="text-center text-[11px] text-slate-500 mt-4">
            © 2026 VCTI · Secure Recruitment Platform
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
