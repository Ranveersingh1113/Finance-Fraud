import { Header } from "@/components/Layout/Header";
import { StatCard } from "@/components/Dashboard/StatCard";
import { CaseCard } from "@/components/Dashboard/CaseCard";
import { AlertCard } from "@/components/Dashboard/AlertCard";
import { QuickAction } from "@/components/Dashboard/QuickAction";
import { Folder, Bell, Search as SearchIcon, TrendingUp, FileText, Network, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { useSystemStats } from "@/hooks/useStats";
import { useCases } from "@/hooks/useCases";
import { getVisibleQueryCount } from "@/utils/queryUtils";
import { useQueries } from "@tanstack/react-query";
import { casesApi } from "@/services/api";

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: stats, isLoading: statsLoading, error: statsError } = useSystemStats();
  const { data: casesData, isLoading: casesLoading, error: casesError } = useCases('active');
  const { data: allCasesData } = useCases(); // Fetch all cases for total query count

  // Get active cases
  const activeCases = casesData?.cases || [];
  const priorityCases = activeCases.slice(0, 3);
  const allCases = allCasesData?.cases || [];
  
  // Fetch full case details for priority cases to get accurate query counts
  const priorityCaseQueries = useQueries({
    queries: priorityCases.length > 0
      ? priorityCases.map((caseItem) => ({
          queryKey: ['case', caseItem.case_id],
          queryFn: () => casesApi.getById(caseItem.case_id),
          enabled: !!caseItem.case_id,
          staleTime: 30000,
        }))
      : [],
  });
  
  // Fetch all cases with queries to calculate total visible query count
  const allCaseQueries = useQueries({
    queries: allCases.length > 0
      ? allCases.map((caseItem) => ({
          queryKey: ['case', caseItem.case_id],
          queryFn: () => casesApi.getById(caseItem.case_id),
          enabled: !!caseItem.case_id,
          staleTime: 30000,
        }))
      : [],
  });
  
  // Create a map of case_id to case data with queries
  const casesWithQueries = new Map(
    priorityCaseQueries
      .map((query) => query.data)
      .filter(Boolean)
      .map((caseData) => [caseData.case_id, caseData])
  );
  
  // Calculate total visible query count across all cases
  const totalVisibleQueries = allCaseQueries
    .map((query) => query.data)
    .filter(Boolean)
    .reduce((total, caseData) => {
      const visibleCount = getVisibleQueryCount(
        caseData.case_id,
        caseData.query_count || 0,
        caseData.queries
      );
      return total + visibleCount;
    }, 0);
  
  const caseStats = stats?.rag_engine_stats?.case_statistics;
  
  // Check if backend is down
  const isBackendDown = statsError || casesError;

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header title="Fraud Intelligence" badge={3} />
      
      <main className="px-4 py-6 max-w-screen-xl mx-auto space-y-6">
        {/* Backend Connection Warning */}
        {isBackendDown && (
          <div className="bg-destructive/10 border border-destructive rounded-lg p-4">
            <h3 className="font-semibold text-destructive mb-2">⚠️ Backend Connection Issue</h3>
            <p className="text-sm text-muted-foreground mb-3">
              Cannot connect to backend API. Some features may not work.
            </p>
            <details className="text-xs text-muted-foreground">
              <summary className="cursor-pointer font-medium mb-2">How to fix:</summary>
              <ol className="list-decimal list-inside space-y-1 ml-2">
                <li>Make sure backend API server is running</li>
                <li>Check .env file has correct VITE_API_BASE_URL</li>
                <li>Run: python start_api.py</li>
              </ol>
            </details>
          </div>
        )}
      
        {/* Greeting */}
        <div>
          <h2 className="text-2xl font-bold text-foreground">Good morning, Sarah 👋</h2>
          <p className="text-sm text-muted-foreground">Monday, November 3, 2025</p>
        </div>

        {/* KPI Stats */}
        <section>
          <h3 className="text-lg font-bold text-foreground mb-4">📊 Today's KPIs</h3>
          {statsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              <StatCard 
                title="Cases" 
                value={caseStats?.total_cases?.toString() || "0"}
                change={`${caseStats?.active_cases || 0} active`}
                icon={Folder} 
                trend="up" 
              />
              <StatCard 
                title="Alerts" 
                value={caseStats?.priority_breakdown?.critical?.toString() || "0"}
                change="Critical" 
                icon={Bell} 
                trend="up" 
              />
              <StatCard 
                title="Queries" 
                value={
                  allCases.length > 0 && 
                  allCaseQueries.length > 0 && 
                  allCaseQueries.every((q) => !q.isLoading && q.data)
                    ? totalVisibleQueries.toString()
                    : (caseStats?.total_queries?.toString() || "0")
                }
                change="Total queries"
                icon={SearchIcon} 
                trend="up" 
              />
              <StatCard 
                title="Closed" 
                value={caseStats?.closed_cases?.toString() || "0"}
                change="Completed" 
                icon={TrendingUp} 
                trend="neutral" 
              />
            </div>
          )}
        </section>

        {/* Quick Actions */}
        <section>
          <h3 className="text-lg font-bold text-foreground mb-4">⚡ Quick Actions</h3>
          <div className="grid grid-cols-3 gap-3">
            <QuickAction
              icon={FileText}
              label="New Case"
              onClick={() => navigate("/cases")}
            />
            <QuickAction
              icon={SearchIcon}
              label="Quick Search"
              onClick={() => navigate("/search")}
            />
            <QuickAction
              icon={Network}
              label="Graph View"
              onClick={() => navigate("/cases")}
            />
          </div>
        </section>

        {/* Priority Cases */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-foreground">🔥 Priority Cases</h3>
            <Button variant="ghost" size="sm" onClick={() => navigate("/cases")}>
              View All
            </Button>
          </div>
          {casesLoading || (priorityCaseQueries.length > 0 && priorityCaseQueries.some((q) => q.isLoading)) ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : activeCases.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No active cases yet. Create your first case!
            </div>
          ) : (
            <div className="space-y-3">
              {priorityCases.map((caseItem) => {
                // Get full case data with queries if available
                const fullCaseData = casesWithQueries.get(caseItem.case_id);
                const visibleQueryCount = fullCaseData
                  ? getVisibleQueryCount(
                      caseItem.case_id,
                      caseItem.query_count || 0,
                      fullCaseData.queries
                    )
                  : getVisibleQueryCount(
                      caseItem.case_id,
                      caseItem.query_count || 0
                    );
                return (
                  <CaseCard
                    key={caseItem.case_id}
                    id={caseItem.case_id}
                    title={caseItem.description.substring(0, 50)}
                    priority={caseItem.priority}
                    lastUpdate={new Date(caseItem.updated_at).toLocaleString()}
                    queryCount={visibleQueryCount}
                    onClick={() => navigate(`/cases/${caseItem.case_id}`)}
                  />
                );
              })}
            </div>
          )}
        </section>

        {/* Recent Alerts */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-foreground">🚨 Recent Alerts</h3>
            <Button variant="ghost" size="sm" onClick={() => navigate("/alerts")}>
              View All
            </Button>
          </div>
          <div className="space-y-3">
            <AlertCard
              type="Fan-Out Pattern Detected"
              description="Account 966 → 650+ accounts"
              amount="$371M"
              timestamp="2m ago"
              severity="critical"
            />
            <AlertCard
              type="Circular Trading Identified"
              description="Loop detected across 12 entities"
              amount="$89M"
              timestamp="15m ago"
              severity="high"
            />
            <AlertCard
              type="Unusual Volume Spike"
              description="Transaction volume 3x above baseline"
              timestamp="45m ago"
              severity="medium"
            />
          </div>
        </section>

        {/* Performance Metrics */}
        <section className="pb-4">
          <h3 className="text-lg font-bold text-foreground mb-4">📈 This Week</h3>
          <div className="bg-card rounded-lg border border-border p-6 shadow-md">
            <div className="flex items-end justify-between h-32 gap-2">
              {[40, 65, 55, 80, 70, 90, 75].map((height, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-2">
                  <div
                    className="w-full bg-gradient-primary rounded-t"
                    style={{ height: `${height}%` }}
                  />
                  <span className="text-xs text-muted-foreground">
                    {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
