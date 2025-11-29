import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "@/lib/api";

function Login() {
  // COMMENTED OUT FOR COMMUNITY EDITION - Uncomment when enterprise edition is enabled
  // const [isAzureLoading, setIsAzureLoading] = useState(false)
  const [isGithubLoading, setIsGithubLoading] = useState(false);
  const [isAdminLoading, setIsAdminLoading] = useState(false);
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [adminError, setAdminError] = useState("");
  const navigate = useNavigate();

  // COMMENTED OUT FOR COMMUNITY EDITION - Uncomment when enterprise edition is enabled
  // const handleAzureSignIn = () => {
  //   setIsAzureLoading(true)
  //   // Redirect to backend Azure OAuth endpoint
  //   const backendUrl = import.meta.env.VITE_API_URL || window.location.origin
  //   window.location.href = `${backendUrl}/auth/login/azure`
  // }

  const handleGithubSignIn = () => {
    setIsGithubLoading(true);
    // Redirect to backend GitHub OAuth endpoint
    const backendUrl = import.meta.env.VITE_API_URL || window.location.origin;
    window.location.href = `${backendUrl}/auth/login/github`;
  };

  const handleAdminSignIn = async (e) => {
    e.preventDefault();
    setIsAdminLoading(true);
    setAdminError("");

    try {
      const response = await api.post("/api/auth/admin/login", {
        email: adminEmail,
        password: adminPassword,
      });

      // Both admin and regular users go to /dashboard
      // DashboardRouter will route them to the correct view based on role
      navigate("/dashboard");
    } catch (error) {
      setAdminError(
        error.response?.data?.detail || "Invalid email or password"
      );
    } finally {
      setIsAdminLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-[400px] space-y-8">
        {/* Logo */}
        <div className="flex justify-center">
          <div className="flex size-12 items-center justify-center rounded-lg bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500">
            <span className="text-2xl font-bold text-white">A</span>
          </div>
        </div>

        {/* Header */}
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">
            Sign in to Arka
          </h1>
          <p className="text-sm text-muted-foreground">
            Connect to your MCP servers securely
          </p>
        </div>

        {/* Admin Login Form */}
        <form onSubmit={handleAdminSignIn} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="admin@example.com"
              value={adminEmail}
              onChange={(e) => setAdminEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">Password</Label>
              <Button
                type="button"
                variant="link"
                className="h-auto p-0 text-xs"
                onClick={() => navigate("/forgot-password")}
              >
                Forgot password?
              </Button>
            </div>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={adminPassword}
              onChange={(e) => setAdminPassword(e.target.value)}
              required
            />
          </div>
          {adminError && <p className="text-sm text-red-500">{adminError}</p>}
          <Button type="submit" className="w-full" disabled={isAdminLoading}>
            {isAdminLoading ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" />
                Signing in...
              </>
            ) : (
              "Sign in"
            )}
          </Button>
        </form>

        {/* Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">
              Or continue with
            </span>
          </div>
        </div>

        {/* Social Login */}
        <div className="space-y-3">
          {/* Azure SSO - Enterprise Edition Only */}
          {/* COMMENTED OUT FOR COMMUNITY EDITION - Uncomment when enterprise edition is enabled */}
          {isEnterprise && (
            <Button
              type="button"
              className="w-full bg-blue-600 hover:bg-blue-700"
              onClick={handleAzureSignIn}
              disabled={isAzureLoading}
            >
              {isAzureLoading ? (
                <>
                  <Loader2 className="mr-2 size-4 animate-spin" />
                  Redirecting...
                </>
              ) : (
                <>
                  <svg
                    className="mr-2 size-5"
                    viewBox="0 0 23 23"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path d="M0 0h10.93v10.93H0V0z" fill="#f25022" />
                    <path d="M12.07 0H23v10.93H12.07V0z" fill="#7fba00" />
                    <path d="M0 12.07h10.93V23H0V12.07z" fill="#00a4ef" />
                    <path d="M12.07 12.07H23V23H12.07V12.07z" fill="#ffb900" />
                  </svg>
                  Sign in with Microsoft
                </>
              )}
            </Button>
          )}

          {/* GitHub OAuth - Available in All Editions */}
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={handleGithubSignIn}
            disabled={isGithubLoading}
          >
            {isGithubLoading ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" />
                Redirecting...
              </>
            ) : (
              <>
                <svg
                  className="mr-2 size-5"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
                Sign in with GitHub
              </>
            )}
          </Button>
        </div>

        {/* Footer */}
        <div className="text-center text-sm">
          <span className="text-muted-foreground">Enterprise MCP Gateway</span>
        </div>
      </div>
    </div>
  );
}

export default Login;
