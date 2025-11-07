import { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";

interface QuickActionProps {
  icon: LucideIcon;
  label: string;
  onClick: () => void;
}

export const QuickAction = ({ icon: Icon, label, onClick }: QuickActionProps) => {
  return (
    <Card
      className="p-4 flex flex-col items-center justify-center gap-2 hover:shadow-md transition-all cursor-pointer hover:scale-105 active:scale-95"
      onClick={onClick}
    >
      <div className="bg-primary/10 p-3 rounded-full">
        <Icon className="h-6 w-6 text-primary" />
      </div>
      <span className="text-sm font-medium text-foreground text-center">{label}</span>
    </Card>
  );
};
