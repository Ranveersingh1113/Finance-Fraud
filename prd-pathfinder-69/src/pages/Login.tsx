import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import type { Location } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AlertCircle, ShieldCheck } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [apiKey, setApiKey] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as { from?: Location })?.from?.pathname || "/dashboard";

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [from, isAuthenticated, navigate]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(apiKey.trim());
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err?.message || "Unable to authenticate. Please verify your API key.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(129,140,248,0.15),_transparent_55%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(14,165,233,0.15),_transparent_60%)]" />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-6xl flex-col lg:flex-row">
        <section className="flex-1 px-8 py-16 lg:px-16 flex flex-col justify-center space-y-10">
          <div>
            <div className="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-5 py-2 text-sm text-indigo-200">
              <ShieldCheck className="h-4 w-4" />
              Verified access required
            </div>
            <h1 className="mt-6 text-4xl sm:text-5xl font-bold leading-tight">
              Securely sign in to the Finance Fraud Intelligence Platform.
            </h1>
            <p className="mt-4 text-base text-white/70 max-w-xl">
              Provide your analyst API credential to unlock investigative tooling, live intelligence, and regulatory documentation
              workflows.
            </p>
          </div>
          <ul className="grid gap-4 text-sm text-white/70">
            <li className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald-400" /> Banking-grade encryption for every request.</li>
            <li className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-sky-400" /> Full audit log of analyst access and actions.</li>
            <li className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-violet-400" /> Granular revocation to keep investigations contained.</li>
          </ul>
        </section>

        <section className="flex-1 px-8 py-16 lg:px-16 lg:py-24">
          <div className="mx-auto max-w-md rounded-3xl border border-white/10 bg-white/10 backdrop-blur-xl p-8 shadow-2xl">
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="space-y-2 text-left">
                <Label htmlFor="apiKey" className="text-sm uppercase tracking-[0.3em] text-white/60">
                  Analyst API Key
                </Label>
                <Input
                  id="apiKey"
                  value={apiKey}
                  onChange={(event) => setApiKey(event.target.value)}
                  placeholder="Enter your secure key"
                  className="bg-slate-950/60 border-white/20 text-white placeholder:text-white/30"
                  required
                />
                <p className="text-xs text-white/50">
                  Key owners are audited. Contact the platform administrator if you need access.
                </p>
              </div>

              {error && (
                <div className="flex items-start gap-3 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
                  <AlertCircle className="mt-0.5 h-4 w-4" />
                  <span>{error}</span>
                </div>
              )}

              <Button
                type="submit"
                size="lg"
                className="w-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Verifying access..." : "Sign in securely"}
              </Button>

              <p className="text-xs text-white/50 text-center">
                By signing in you acknowledge monitoring and agree to the acceptable use policy.
              </p>
            </form>
          </div>
        </section>
      </div>
    </div>
  );
}

