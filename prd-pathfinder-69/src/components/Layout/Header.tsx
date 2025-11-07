import { Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface HeaderProps {
  title: string;
  badge?: number;
}

export const Header = ({ title, badge }: HeaderProps) => {
  return (
    <header className="sticky top-0 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-40 border-b border-border">
      <div className="flex items-center justify-between h-14 px-4 max-w-screen-xl mx-auto">
        <div className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-primary" />
          <h1 className="text-lg font-bold text-foreground">{title}</h1>
        </div>
        {badge !== undefined && badge > 0 && (
          <Badge variant="destructive" className="h-6 min-w-6 rounded-full">
            {badge}
          </Badge>
        )}
      </div>
    </header>
  );
};
