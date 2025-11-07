import { Header } from "@/components/Layout/Header";
import { CaseCard } from "@/components/Dashboard/CaseCard";
import { Button } from "@/components/ui/button";
import { Plus, Filter, Loader2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCases, useCreateCase } from "@/hooks/useCases";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getVisibleQueryCount } from "@/utils/queryUtils";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function Cases() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("active");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newCase, setNewCase] = useState({
    description: "",
    priority: "medium" as "critical" | "high" | "medium" | "low",
    tags: "",
  });

  // Fetch cases based on active tab
  const { data: activeCases, isLoading: loadingActive } = useCases("active");
  const { data: reviewCases, isLoading: loadingReview } = useCases("under_review");
  const { data: closedCases, isLoading: loadingClosed } = useCases("closed");
  const { mutate: createCase, isPending: creatingCase } = useCreateCase();

  const handleCreateCase = () => {
    // Generate case ID in format: CASE_YYYYMMDD_NNN
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
    const timeStr = now.getTime().toString().slice(-3); // Last 3 digits of timestamp
    const caseId = `CASE_${dateStr}_${timeStr}`;
    
    createCase(
      {
        case_id: caseId,
        description: newCase.description,
        priority: newCase.priority,
        analyst: "Sarah Johnson", // Default analyst from profile
        tags: newCase.tags.split(",").map((t) => t.trim()).filter(Boolean),
      },
      {
        onSuccess: () => {
          setDialogOpen(false);
          setNewCase({ description: "", priority: "medium", tags: "" });
        },
      }
    );
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const renderCasesList = (cases: any, isLoading: boolean) => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      );
    }

    if (!cases?.cases || cases.cases.length === 0) {
      return (
        <div className="text-center py-12 text-muted-foreground">
          <p>No cases found in this category.</p>
          <Button
            variant="link"
            onClick={() => setDialogOpen(true)}
            className="mt-2"
          >
            Create your first case
          </Button>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {cases.cases.map((caseItem: any) => {
          const visibleQueryCount = getVisibleQueryCount(
            caseItem.case_id,
            caseItem.query_count || 0
          );
          return (
            <CaseCard
              key={caseItem.case_id}
              id={caseItem.case_id}
              title={caseItem.description.substring(0, 50) + (caseItem.description.length > 50 ? "..." : "")}
              priority={caseItem.priority}
              lastUpdate={formatTimestamp(caseItem.updated_at)}
              queryCount={visibleQueryCount}
              onClick={() => navigate(`/cases/${caseItem.case_id}`)}
            />
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header title="Cases" />
      
      <main className="px-4 py-6 max-w-screen-xl mx-auto">
        {/* Action Bar */}
        <div className="flex gap-2 mb-6">
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex-1 bg-gradient-primary" size="lg">
                <Plus className="h-5 w-5 mr-2" />
                New Case
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Create New Case</DialogTitle>
                <DialogDescription>
                  Start a new fraud investigation case. Add details to help track your analysis.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe the case..."
                    value={newCase.description}
                    onChange={(e) =>
                      setNewCase({ ...newCase, description: e.target.value })
                    }
                    rows={3}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={newCase.priority}
                    onValueChange={(value: any) =>
                      setNewCase({ ...newCase, priority: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="critical">🔴 Critical</SelectItem>
                      <SelectItem value="high">🟠 High</SelectItem>
                      <SelectItem value="medium">🟡 Medium</SelectItem>
                      <SelectItem value="low">🟢 Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="tags">Tags (comma-separated)</Label>
                  <Input
                    id="tags"
                    placeholder="e.g., insider-trading, market-manipulation"
                    value={newCase.tags}
                    onChange={(e) =>
                      setNewCase({ ...newCase, tags: e.target.value })
                    }
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                  disabled={creatingCase}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  onClick={handleCreateCase}
                  disabled={!newCase.description || creatingCase}
                >
                  {creatingCase ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Case"
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Button variant="outline" size="lg">
            <Filter className="h-5 w-5" />
          </Button>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="active">
              Active ({activeCases?.count || 0})
            </TabsTrigger>
            <TabsTrigger value="review">
              Review ({reviewCases?.count || 0})
            </TabsTrigger>
            <TabsTrigger value="closed">
              Closed ({closedCases?.count || 0})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="active">
            {renderCasesList(activeCases, loadingActive)}
          </TabsContent>

          <TabsContent value="review">
            {renderCasesList(reviewCases, loadingReview)}
          </TabsContent>

          <TabsContent value="closed">
            {renderCasesList(closedCases, loadingClosed)}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
