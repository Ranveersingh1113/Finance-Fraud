import { Header } from "@/components/Layout/Header";
import { AlertCard } from "@/components/Dashboard/AlertCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function Alerts() {
  const alerts = {
    all: [
      { type: "Fan-Out Pattern Detected", description: "Account 966 → 650+ accounts", amount: "$371M", timestamp: "2m ago", severity: "critical" as const },
      { type: "Circular Trading Identified", description: "Loop detected across 12 entities", amount: "$89M", timestamp: "15m ago", severity: "high" as const },
      { type: "Unusual Volume Spike", description: "Transaction volume 3x above baseline", timestamp: "45m ago", severity: "medium" as const },
      { type: "Layering Pattern Match", description: "Multiple orders at different prices", amount: "$12M", timestamp: "1h ago", severity: "high" as const },
      { type: "Suspicious Account Activity", description: "Rapid sequence of trades detected", timestamp: "2h ago", severity: "medium" as const },
    ],
    critical: [
      { type: "Fan-Out Pattern Detected", description: "Account 966 → 650+ accounts", amount: "$371M", timestamp: "2m ago", severity: "critical" as const },
    ],
    high: [
      { type: "Circular Trading Identified", description: "Loop detected across 12 entities", amount: "$89M", timestamp: "15m ago", severity: "high" as const },
      { type: "Layering Pattern Match", description: "Multiple orders at different prices", amount: "$12M", timestamp: "1h ago", severity: "high" as const },
    ],
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header title="Alerts" badge={alerts.all.length} />
      
      <main className="px-4 py-6 max-w-screen-xl mx-auto">
        <Tabs defaultValue="all" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="all">All ({alerts.all.length})</TabsTrigger>
            <TabsTrigger value="critical">Critical ({alerts.critical.length})</TabsTrigger>
            <TabsTrigger value="high">High ({alerts.high.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-3">
            {alerts.all.map((alert, i) => (
              <AlertCard key={i} {...alert} />
            ))}
          </TabsContent>

          <TabsContent value="critical" className="space-y-3">
            {alerts.critical.map((alert, i) => (
              <AlertCard key={i} {...alert} />
            ))}
          </TabsContent>

          <TabsContent value="high" className="space-y-3">
            {alerts.high.map((alert, i) => (
              <AlertCard key={i} {...alert} />
            ))}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
