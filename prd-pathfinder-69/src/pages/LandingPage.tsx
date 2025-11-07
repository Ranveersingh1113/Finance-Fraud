import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Shield, Activity, Sparkles, PlayCircle, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const floatingOrbs = [
  { size: 220, delay: 0, color: "from-indigo-500/40 to-purple-500/40", top: "-10%", left: "-5%" },
  { size: 260, delay: 4, color: "from-cyan-500/30 to-blue-500/30", top: "60%", left: "-15%" },
  { size: 200, delay: 8, color: "from-emerald-500/30 to-teal-500/30", top: "15%", left: "70%" },
];

const featureCards = [
  {
    icon: Shield,
    title: "Advanced Protection",
    description:
      "AI-assisted threat detection, rapid escalation workflows, and compliance-ready case packages in one unified workspace.",
  },
  {
    icon: Activity,
    title: "Real-Time Analytics",
    description:
      "Continuously ingest regulatory intelligence, trade logs, and banking telemetry to surface suspicious activity as it happens.",
  },
  {
    icon: Sparkles,
    title: "Augmented Investigations",
    description:
      "Explainable insights, dynamic graph exploration, and multi-domain knowledge fusion accelerate analyst conclusions.",
  },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [scrollY, setScrollY] = useState(0);
  const { isAuthenticated, isInitializing } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (!isInitializing && isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, isInitializing, navigate]);

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-hidden">
      <header className="relative isolate overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(76,29,149,0.25),_transparent_55%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(14,116,144,0.2),_transparent_60%)]" />

        {/* Floating Orbs */}
        {floatingOrbs.map((orb, index) => (
          <div
            key={index}
            className={cn(
              "pointer-events-none absolute rounded-full blur-3xl opacity-70",
              `bg-gradient-to-br ${orb.color}`
            )}
            style={{
              width: orb.size,
              height: orb.size,
              top: orb.top,
              left: orb.left,
              transform: `translateY(${Math.sin((scrollY / 120) + index) * 20}px)` ,
              animation: `float ${20 + index * 6}s ease-in-out ${orb.delay}s infinite` as const,
            }}
          />
        ))}

        <nav className="relative z-10 flex items-center justify-between px-6 lg:px-16 py-6">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 shadow-lg shadow-indigo-500/40 grid place-content-center">
              <span className="text-lg font-black">FF</span>
            </div>
            <div>
              <p className="text-sm uppercase tracking-widest text-indigo-200">Finance Fraud</p>
              <h1 className="text-lg font-semibold">Intelligence Platform</h1>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-3">
            <Button
              variant="secondary"
              className="bg-white text-slate-950 hover:bg-slate-200"
              onClick={() => navigate("/login")}
            >
              Sign in
            </Button>
          </div>
        </nav>

        <section className="relative z-10 px-6 lg:px-16 pt-16 pb-28">
          <div className="max-w-5xl mx-auto text-center space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-4 py-2 text-sm backdrop-blur">
              <Sparkles className="h-4 w-4 text-indigo-300" />
              <span className="text-indigo-100">Next-generation financial crime intelligence</span>
            </div>

            <h2 className="text-4xl sm:text-6xl lg:text-7xl font-black leading-tight tracking-tight">
              Illuminate hidden fraud patterns before they impact your institution.
            </h2>

            <p className="text-lg sm:text-xl text-white/70 max-w-3xl mx-auto">
              Our AI-native investigation workspace blends knowledge graphs, regulatory intelligence, and multi-modal analytics
              to accelerate decisions. Built with compliance in mind, trusted by the teams who can’t afford to miss anomalies.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Button
                size="lg"
                className="bg-gradient-to-r from-indigo-500 via-violet-500 to-pink-500 text-white shadow-xl shadow-indigo-500/40 hover:shadow-indigo-500/60"
                onClick={() => navigate("/login")}
              >
                Sign in to launch
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-white/40 text-white hover:bg-white/10"
                onClick={() => {
                  const videoSection = document.getElementById("demo-video");
                  videoSection?.scrollIntoView({ behavior: "smooth" });
                }}
              >
                Preview demo video
                <PlayCircle className="ml-2 h-5 w-5" />
              </Button>
            </div>
          </div>

          <div className="relative mt-20">
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/30 via-transparent to-purple-500/30 blur-3xl" />
            <div className="relative mx-auto max-w-5xl rounded-3xl border border-white/10 bg-white/5 p-1 shadow-2xl shadow-indigo-900/40 backdrop-blur">
              <div className="rounded-[26px] bg-slate-900 p-6 sm:p-10 grid gap-8 md:grid-cols-[1.2fr_1fr]">
                <div className="text-left space-y-6">
                  <p className="text-indigo-200 uppercase tracking-[0.25em] text-xs">Built for analysts</p>
                  <h3 className="text-2xl sm:text-3xl font-semibold">
                    A single command center for intelligence gathering, evidence curation, and case collaboration.
                  </h3>
                  <ul className="space-y-3 text-sm text-white/70">
                    <li className="flex items-start gap-3">
                      <span className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-400" />
                      Real-time ingestion from regulatory feeds, transaction networks, and market surveillance platforms.
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-400" />
                      Evidence-aware AI co-pilot that assembles Suspicious Activity Reports ready for compliance review.
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="mt-1 h-2.5 w-2.5 rounded-full bg-violet-400" />
                      Collaborative workspace with audit trails, investigation templates, and automated escalations.
                    </li>
                  </ul>
                </div>
                <div className="relative flex items-center justify-center">
                  <div className="absolute -inset-6 bg-gradient-to-tr from-indigo-500 via-purple-500 to-fuchsia-500 opacity-40 blur-2xl" />
                  <div className="relative aspect-[4/3] w-full overflow-hidden rounded-2xl border border-white/10 bg-slate-950/60 shadow-lg">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/40 via-transparent to-sky-500/30 animate-[pulse_6s_ease-in-out_infinite]" />
                    <div className="relative h-full w-full grid place-content-center gap-4 p-6">
                      <div className="grid grid-cols-3 gap-2">
                        {[...Array(9)].map((_, idx) => (
                          <div
                            key={idx}
                            className="h-16 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm animate-[pulse_5s_ease-in-out_infinite]"
                            style={{ animationDelay: `${idx * 0.2}s` }}
                          />
                        ))}
                      </div>
                      <p className="text-center text-xs uppercase tracking-[0.35em] text-white/60">
                        Intelligence Fabric
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </header>

      <main className="relative z-10 space-y-32 pb-24">
        <section className="px-6 lg:px-16">
          <div className="max-w-6xl mx-auto grid gap-8 md:grid-cols-3">
            {featureCards.map((feature, index) => (
              <div
                key={feature.title}
                className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur shadow-lg shadow-black/20 transition-transform duration-500 hover:-translate-y-2"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-white/0 via-white/10 to-white/0 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                <feature.icon className="h-12 w-12 text-indigo-300 mb-6" />
                <h4 className="text-2xl font-semibold mb-4">{feature.title}</h4>
                <p className="text-sm text-white/70 leading-relaxed">{feature.description}</p>
                <div className="mt-6 flex items-center gap-2 text-indigo-200 text-sm">
                  <span>Learn more</span>
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
                <div
                  className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"
                  style={{ animation: `grow ${4 + index}s ease-in-out ${index}s infinite alternate` }}
                />
              </div>
            ))}
          </div>
        </section>

        <section className="px-6 lg:px-16">
          <div className="max-w-6xl mx-auto grid gap-12 lg:grid-cols-[1.2fr_1fr] items-center">
            <div className="space-y-6">
              <p className="text-sm uppercase tracking-[0.3em] text-indigo-200">Regulatory grade evidence</p>
              <h3 className="text-3xl sm:text-4xl font-semibold">
                Bridge the gap between intelligence generation and regulator-ready documentation.
              </h3>
              <p className="text-white/70 leading-relaxed">
                Every insight includes provenance, score attribution, and evidence bundles to accelerate compliance review. Build
                institutional memory with reusable playbooks and automated reporting pipelines that keep auditors delighted.
              </p>
              <div className="grid gap-4 sm:grid-cols-2">
                {["Dynamic graph visualisation", "Intelligent query co-pilots", "Explainable scoring", "SAR automation"].map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-sm text-white/80">
                    {item}
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-8 bg-gradient-to-tr from-sky-500/30 via-indigo-500/20 to-purple-500/30 blur-3xl" />
              <div className="relative rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur shadow-xl">
                <div className="flex justify-between items-center mb-6">
                  <h4 className="text-lg font-semibold">Live Intelligence Feed</h4>
                  <span className="text-xs font-medium uppercase tracking-[0.3em] text-emerald-300">real-time</span>
                </div>
                <div className="space-y-4">
                  {["SEBI enforcement precedent match", "High-volume AMLSim anomaly", "Cross-market insider cluster detected"].map((alert, idx) => (
                    <div key={alert} className="rounded-2xl border border-white/10 bg-slate-900/80 p-4">
                      <p className="text-sm font-medium text-white/90">{alert}</p>
                      <p className="text-xs text-white/60 mt-1">{["Critical", "High", "Medium"][idx]}</p>
                      <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                        <div
                          className={cn(
                            "h-full rounded-full",
                            ["bg-red-500", "bg-orange-400", "bg-yellow-400"][idx]
                          )}
                          style={{ width: `${70 + idx * 8}%`, animation: `pulseBar 4s ease-in-out ${idx}s infinite alternate` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="demo-video" className="px-6 lg:px-16">
          <div className="max-w-5xl mx-auto text-center space-y-10">
            <div className="space-y-3">
              <p className="text-sm uppercase tracking-[0.3em] text-indigo-200">Platform in action</p>
              <h3 className="text-3xl font-semibold">Explore the Finance Fraud Intelligence Platform</h3>
              <p className="text-white/70 max-w-2xl mx-auto">
                Dive into a guided tour showcasing intelligent investigations, graph exploration, and automated SAR generation. The
                future of financial crime defense awaits.
              </p>
            </div>
            <div className="relative">
              <div className="absolute -inset-4 rounded-[3rem] bg-gradient-to-r from-indigo-500 via-purple-500 to-fuchsia-500 opacity-30 blur-2xl" />
              <div className="relative overflow-hidden rounded-[2.5rem] border border-white/15 bg-slate-900/70 shadow-2xl backdrop-blur">
                <video
                  className="aspect-video w-full"
                  controls
                  preload="metadata"
                  poster="https://images.pexels.com/photos/730547/pexels-photo-730547.jpeg?auto=compress&cs=tinysrgb&w=1200"
                >
                  <source src="/finance-fraud-demo.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="relative z-10 px-6 lg:px-16 py-12 border-t border-white/10 bg-slate-950/80 backdrop-blur">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6 text-sm text-white/60">
          <p>© {new Date().getFullYear()} Finance Fraud Intelligence Platform. All rights reserved.</p>
          <div className="flex gap-6">
            <Button variant="link" className="text-white/70 hover:text-white p-0" onClick={() => navigate("/login")}>
              Launch App
            </Button>
            <Button variant="link" className="text-white/70 hover:text-white p-0" onClick={() => navigate("/login")}>
              Meet the team
            </Button>
            <Button variant="link" className="text-white/70 hover:text-white p-0" onClick={() => navigate("/login")}>
              Active investigations
            </Button>
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(-10px); opacity: 0.75; }
          50% { transform: translateY(15px); opacity: 0.95; }
        }

        @keyframes grow {
          0% { transform: scaleX(0.3); opacity: 0.6; }
          100% { transform: scaleX(1); opacity: 1; }
        }

        @keyframes pulseBar {
          0% { filter: brightness(0.8); }
          100% { filter: brightness(1.2); }
        }
      `}</style>
    </div>
  );
}

