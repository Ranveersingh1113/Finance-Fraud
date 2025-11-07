import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

interface CaseCardProps {
  id: string;
  title: string;
  priority: "critical" | "high" | "medium" | "low";
  lastUpdate: string;
  queryCount: number;
  onClick?: () => void;
}

const priorityConfig = {
  critical: { color: "bg-critical text-critical-foreground", label: "Critical", dot: "bg-critical" },
  high: { color: "bg-priority-high text-white", label: "High", dot: "bg-priority-high" },
  medium: { color: "bg-priority-medium text-white", label: "Medium", dot: "bg-priority-medium" },
  low: { color: "bg-muted text-muted-foreground", label: "Low", dot: "bg-priority-low" },
};

export const CaseCard = ({ id, title, priority, lastUpdate, queryCount, onClick }: CaseCardProps) => {
  const config = priorityConfig[priority];

  return (
    <Card
      className="p-4 hover:shadow-lg transition-all cursor-pointer border-l-4"
      style={{ borderLeftColor: `hsl(var(--priority-${priority === "critical" ? "high" : priority}))` }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className={cn("w-2 h-2 rounded-full animate-pulse", config.dot)} />
          <span className="text-xs font-bold text-muted-foreground">{id}</span>
        </div>
        <Badge className={cn("text-xs", config.color)}>{config.label}</Badge>
      </div>
      
      <h3 className="font-semibold text-foreground mb-3">{title}</h3>
      
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          <span>{lastUpdate}</span>
        </div>
        <div className="flex items-center gap-1">
          <MessageSquare className="h-3 w-3" />
          <span>{queryCount} queries</span>
        </div>
      </div>
    </Card>
  );
};
