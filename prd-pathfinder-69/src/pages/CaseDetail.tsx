import { Header } from "@/components/Layout/Header";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import {
  ArrowLeft,
  FileText,
  Search,
  Loader2,
  AlertCircle,
  Calendar,
  User,
  Tag,
  TrendingUp,
  Sparkles,
  Network,
  X,
  Trash2,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { useCase, useAnalyzeCase, useGenerateSAR, useSARReports } from "@/hooks/useCases";
import { useState, useEffect } from "react";
import { AnalysisResponse } from "@/components/CaseDetail/AnalysisResponse";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const DELETED_QUERIES_STORAGE_KEY = "deleted_queries_by_case";

export default function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [analysisQuery, setAnalysisQuery] = useState("");
  const [deletedQueryIds, setDeletedQueryIds] = useState<Set<number>>(new Set());

  const { data: caseData, isLoading, error } = useCase(caseId);
  const { mutate: analyzeCase, isPending: isAnalyzing } = useAnalyzeCase();
  const [sarDialogOpen, setSarDialogOpen] = useState(false);
  const { data: sarReports } = useSARReports(caseId);
  const generateSARMutation = useGenerateSAR();
  const { mutate: generateSAR, isPending: isGeneratingSAR } = generateSARMutation;

  // Load deleted query IDs from localStorage on mount
  useEffect(() => {
    if (caseId) {
      try {
        const stored = localStorage.getItem(DELETED_QUERIES_STORAGE_KEY);
        if (stored) {
          const deletedByCase = JSON.parse(stored) as Record<string, number[]>;
          const deletedIds = deletedByCase[caseId] || [];
          setDeletedQueryIds(new Set(deletedIds));
        }
      } catch (e) {
        console.error("Failed to load deleted queries:", e);
      }
    }
  }, [caseId]);

  // Save deleted query IDs to localStorage
  const saveDeletedQueries = (caseId: string, deletedIds: Set<number>) => {
    try {
      const stored = localStorage.getItem(DELETED_QUERIES_STORAGE_KEY);
      const deletedByCase = stored ? (JSON.parse(stored) as Record<string, number[]>) : {};
      deletedByCase[caseId] = Array.from(deletedIds);
      localStorage.setItem(DELETED_QUERIES_STORAGE_KEY, JSON.stringify(deletedByCase));
    } catch (e) {
      console.error("Failed to save deleted queries:", e);
    }
  };

  // Filter out deleted queries using query IDs
  const visibleQueries = caseData?.queries?.filter((query) => !deletedQueryIds.has(query.id)) || [];

  // Delete a query (persistent via localStorage)
  const handleDeleteQuery = (queryId: number) => {
    const updated = new Set([...deletedQueryIds, queryId]);
    setDeletedQueryIds(updated);
    if (caseId) {
      saveDeletedQueries(caseId, updated);
    }
  };
  
  // Open dialog when SAR is generated
  useEffect(() => {
    if (generateSARMutation.isSuccess && !sarDialogOpen) {
      setSarDialogOpen(true);
    }
  }, [generateSARMutation.isSuccess, sarDialogOpen]);

  const handleAnalyze = () => {
    if (analysisQuery.trim() && caseId) {
      analyzeCase({
        caseId,
        query: analysisQuery,
      });
      setAnalysisQuery("");
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "bg-red-500";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-green-500";
      default:
        return "bg-gray-500";
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case "critical":
        return "🔴 Critical";
      case "high":
        return "🟠 High";
      case "medium":
        return "🟡 Medium";
      case "low":
        return "🟢 Low";
      default:
        return priority;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-blue-500";
      case "under_review":
        return "bg-purple-500";
      case "closed":
        return "bg-gray-500";
      case "archived":
        return "bg-gray-400";
      default:
        return "bg-gray-500";
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background pb-20">
        <Header title="Case Details" />
        <main className="px-4 py-6 max-w-screen-xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
          </div>
        </main>
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="min-h-screen bg-background pb-20">
        <Header title="Case Details" />
        <main className="px-4 py-6 max-w-screen-xl mx-auto">
          <Button
            variant="ghost"
            onClick={() => navigate("/cases")}
            className="mb-6"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Cases
          </Button>
          <Card className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">Case Not Found</h2>
            <p className="text-muted-foreground mb-4">
              The case you're looking for doesn't exist or has been deleted.
            </p>
            <Button onClick={() => navigate("/cases")}>
              Return to Cases
            </Button>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header title="Case Details" />

      <main className="px-4 py-6 max-w-screen-xl mx-auto space-y-6">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => navigate("/cases")}
          className="mb-2"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Cases
        </Button>

        {/* Case Header */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <h1 className="text-2xl font-bold text-foreground">
                  {caseData.case_id}
                </h1>
                <Badge className={`${getPriorityColor(caseData.priority)} text-white`}>
                  {getPriorityLabel(caseData.priority)}
                </Badge>
                <Badge className={`${getStatusColor(caseData.status)} text-white`}>
                  {caseData.status.replace("_", " ")}
                </Badge>
              </div>
              <p className="text-muted-foreground text-sm">
                {caseData.description}
              </p>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Case Metadata */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Analyst</p>
                <p className="text-sm font-medium">{caseData.analyst}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Created</p>
                <p className="text-sm font-medium">
                  {new Date(caseData.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Updated</p>
                <p className="text-sm font-medium">
                  {new Date(caseData.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Queries</p>
                <p className="text-sm font-medium">{visibleQueries.length}</p>
              </div>
            </div>
          </div>

          {/* Tags */}
          {caseData.tags && caseData.tags.length > 0 && (
            <>
              <Separator className="my-4" />
              <div className="flex items-center gap-2 flex-wrap">
                <Tag className="h-4 w-4 text-muted-foreground" />
                {caseData.tags.map((tag, index) => (
                  <Badge key={index} variant="outline">
                    {tag}
                  </Badge>
                ))}
              </div>
            </>
          )}
        </Card>

        {/* Analysis Section */}
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-bold">AI Analysis</h2>
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            Ask questions about this case using the GraphRAG engine
          </p>
          <div className="space-y-3">
            <Textarea
              placeholder="E.g., What SEBI regulations apply to this case? Find similar transaction patterns..."
              value={analysisQuery}
              onChange={(e) => setAnalysisQuery(e.target.value)}
              rows={3}
              className="resize-none"
            />
            <Button
              onClick={handleAnalyze}
              disabled={!analysisQuery.trim() || isAnalyzing}
              className="w-full bg-gradient-primary"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing with GraphRAG...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Run Analysis
                </>
              )}
            </Button>
          </div>
        </Card>

        {/* Query History */}
        {caseData?.queries && caseData.queries.length > 0 && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-bold">Query History</h2>
                <Badge variant="secondary" className="ml-2">
                  {visibleQueries.length}
                </Badge>
              </div>
            </div>
            {visibleQueries.length > 0 ? (
              <div className="space-y-4">
                {caseData.queries.map((query) => {
                  if (deletedQueryIds.has(query.id)) return null;
                  
                  return (
                    <Card key={query.id} className="p-4 bg-muted/50 group relative">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-foreground">
                            {query.query}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary" className="ml-2">
                            {(query.confidence_score * 100).toFixed(0)}%
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0 hover:bg-destructive/10 hover:text-destructive"
                            onClick={() => handleDeleteQuery(query.id)}
                            title="Delete query"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      
                      {/* Use formatted response component */}
                      <AnalysisResponse answer={query.answer ?? ""} />
                      
                      <Separator className="my-3" />
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>📊 {query.query_type.replace("_", " ")}</span>
                        <span>⏱️ {query.processing_time.toFixed(2)}s</span>
                        <span>
                          {new Date(query.timestamp).toLocaleString()}
                        </span>
                      </div>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                All queries have been deleted
              </p>
            )}
          </Card>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <Dialog open={sarDialogOpen} onOpenChange={setSarDialogOpen}>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                size="lg"
                onClick={() => {
                  if (caseId && !sarDialogOpen && !sarReports?.reports?.[0]) {
                    generateSAR(caseId);
                  } else {
                    setSarDialogOpen(true);
                  }
                }}
                disabled={isGeneratingSAR}
              >
                {isGeneratingSAR ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <FileText className="h-5 w-5 mr-2" />
                    Generate SAR
                  </>
                )}
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Suspicious Activity Report (SAR)</DialogTitle>
                <DialogDescription>
                  Generated SAR for {caseData?.case_id}
                </DialogDescription>
              </DialogHeader>
              <div className="mt-4">
                {isGeneratingSAR ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : sarReports?.reports?.[0]?.report_content ? (
                  <div className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-lg">
                    {sarReports.reports[0].report_content}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No SAR report available. Click Generate SAR to create one.</p>
                )}
              </div>
            </DialogContent>
          </Dialog>
          <Button
            variant="outline"
            size="lg"
            onClick={() => {
              // Extract account number from the most recent query response
              let accountId = null;
              if (caseData.queries && caseData.queries.length > 0) {
                // Try to find account ID in the answer (more specific patterns)
                for (const query of caseData.queries) {
                  const match = query.answer.match(/Account\s*ID:\s*(\d+)/i) ||
                               query.answer.match(/account_(\d+)/i);
                  if (match) {
                    accountId = match[1];
                    break;
                  }
                }
              }
              if (accountId) {
                navigate(`/graph?account=${accountId}`);
              } else {
                // Fallback: show graph for case
                navigate(`/graph?case=${caseId}`);
              }
            }}
          >
            <Network className="h-5 w-5 mr-2" />
            View Graph
          </Button>
        </div>
      </main>
    </div>
  );
}

