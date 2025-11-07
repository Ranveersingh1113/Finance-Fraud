import { Card } from "@/components/ui/card";
import { AlertTriangle, TrendingUp, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface AlertCardProps {
  type: string;
  description: string;
  amount?: string;
  timestamp: string;
  severity: "critical" | "high" | "medium";
}

export const AlertCard = ({ type, description, amount, timestamp, severity }: AlertCardProps) => {
  const severityColors = {
    critical: "text-critical border-critical/20 bg-critical/5",
    high: "text-warning border-warning/20 bg-warning/5",
    medium: "text-primary border-primary/20 bg-primary/5",
  };

  return (
    <Card className={cn("p-4 border-l-4", severityColors[severity])}>
      <div className="flex items-start gap-3">
        <div className={cn(
          "p-2 rounded-lg",
          severity === "critical" && "bg-critical/10",
          severity === "high" && "bg-warning/10",
          severity === "medium" && "bg-primary/10"
        )}>
          <AlertTriangle className={cn(
            "h-5 w-5",
            severity === "critical" && "text-critical",
            severity === "high" && "text-warning",
            severity === "medium" && "text-primary"
          )} />
        </div>
        
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-foreground mb-1">{type}</h4>
          <p className="text-sm text-muted-foreground mb-2">{description}</p>
          
          {amount && (
            <div className="flex items-center gap-1 text-sm font-semibold text-critical mb-2">
              <TrendingUp className="h-4 w-4" />
              <span>{amount} flagged</span>
            </div>
          )}
          
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{timestamp}</span>
          </div>
        </div>
      </div>
    </Card>
  );
};
