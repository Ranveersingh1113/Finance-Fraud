import { Header } from "@/components/Layout/Header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { ArrowLeft, Network, Loader2, ZoomIn, ZoomOut, Maximize, X, DollarSign, ArrowRightLeft, Info } from "lucide-react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useState, useCallback, useEffect, useMemo } from "react";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MiniMap,
  Panel,
  MarkerType,
  ConnectionMode,
  useReactFlow,
} from "reactflow";
import dagre from "dagre";
import "reactflow/dist/style.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";
const API_KEY = import.meta.env.VITE_API_KEY || "dev-api-key";

interface GraphNode {
  id: string;
  label: string;
  type: string;
  color: string;
  size: number;
  is_center: boolean;
  data: {
    balance: number;
    country: string;
    business_type: string;
    is_suspicious: boolean;
    is_fraud: boolean;
  };
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  width: number;
  type: string;
  data: {
    amount: number;
    transaction_type: string;
    timestamp: number;
  };
}

interface GraphData {
  center_account: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    total_nodes: number;
    total_edges: number;
    hops: number;
    account_nodes: number;
    suspicious_nodes: number;
    fraud_nodes: number;
  };
}

interface GraphResponse {
  success: boolean;
  account_id: string;
  graph: GraphData;
  timestamp: string;
}

async function fetchAccountGraph(accountId: string, hops: number = 2): Promise<GraphResponse> {
  const response = await fetch(
    `${API_BASE_URL}/graph/account/${accountId}?hops=${hops}&max_nodes=200`,
    {
      headers: {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch graph data");
  }

  return response.json();
}

// Layout graph using dagre for better visualization
function getLayoutedElements(nodes: Node[], edges: Edge[], direction: string = "LR", nodeCount: number = 0) {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  // Adjust layout parameters based on graph size
  const isLargeGraph = nodeCount > 50;
  const nodesep = isLargeGraph ? 30 : 50;
  const ranksep = isLargeGraph ? 60 : 100;
  
  dagreGraph.setGraph({ 
    rankdir: direction,
    nodesep: nodesep,
    ranksep: ranksep,
    edgesep: 10,
    ranker: 'tight-tree', // Better for large graphs
  });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { 
      width: node.width || 120, 
      height: node.height || 60 
    });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  return {
    nodes: nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      return {
        ...node,
        position: {
          x: nodeWithPosition.x - (node.width || 120) / 2,
          y: nodeWithPosition.y - (node.height || 60) / 2,
        },
      };
    }),
    edges,
  };
}

// Convert backend nodes to ReactFlow nodes
function convertToReactFlowNodes(graphNodes: GraphNode[], centerAccountId?: string): Node[] {
  return graphNodes.map((node) => ({
    id: node.id,
    type: "default",
    position: { x: 0, y: 0 }, // Will be set by layout
    width: node.size * 2 + 20,
    height: node.size * 2 + 20,
    data: {
      label: (
        <div className="text-center">
          <div className="font-semibold text-xs">{node.label}</div>
          {node.data.balance > 0 && (
            <div className="text-[10px] text-muted-foreground">
              ${(node.data.balance / 1000).toFixed(0)}K
            </div>
          )}
        </div>
      ),
      originalNode: node, // Store original node data for click handler
    },
    style: {
      background: node.color,
      color: "#fff",
      border: node.is_center ? "3px solid #fbbf24" : "2px solid #fff",
      borderRadius: "8px",
      padding: "8px",
      width: node.size * 2 + 20,
      height: node.size * 2 + 20,
      fontSize: "10px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: node.is_center
        ? "0 0 20px rgba(251, 191, 36, 0.6)"
        : "0 2px 8px rgba(0, 0, 0, 0.15)",
      cursor: "pointer",
    },
  }));
}

// Convert backend edges to ReactFlow edges
function convertToReactFlowEdges(graphEdges: GraphEdge[]): Edge[] {
  return graphEdges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    labelStyle: { fontSize: "10px", fill: "#64748b" },
    labelBgStyle: { fill: "#fff", fillOpacity: 0.8 },
    animated: edge.data.amount > 50000, // Animate large transactions
    style: {
      strokeWidth: Math.max(1, edge.width / 2),
      stroke: edge.data.amount > 100000 ? "#dc2626" : "#94a3b8",
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: edge.data.amount > 100000 ? "#dc2626" : "#94a3b8",
    },
  }));
}

export default function GraphView() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const accountIdParam = searchParams.get("account");
  const caseId = searchParams.get("case");
  const [hops, setHops] = useState(2);
  
  // Clean account ID for display (remove account_ prefix if present)
  const accountId = accountIdParam?.replace(/^account_/i, '') || accountIdParam || '';

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [graphStatus, setGraphStatus] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showDetailsPanel, setShowDetailsPanel] = useState(false);
  const [graphData, setGraphData] = useState<GraphData | null>(null);

  // Check graph status on mount
  useEffect(() => {
    if (accountIdParam) {
      fetch(`${API_BASE_URL}/graph/status`, {
        headers: {
          "X-API-Key": API_KEY,
          "Content-Type": "application/json",
        },
      })
        .then((res) => res.json())
        .then((status) => setGraphStatus(status))
        .catch((err) => console.error("Failed to fetch graph status:", err));
    }
  }, [accountIdParam]);

  const { data, isLoading, error } = useQuery<GraphResponse>({
    queryKey: ["account-graph", accountIdParam, hops],
    queryFn: () => fetchAccountGraph(accountIdParam || "", hops),
    enabled: !!accountIdParam,
    onSuccess: (data) => {
      console.log("Graph data received:", data);
      if (data?.graph) {
        console.log("Graph nodes:", data.graph.nodes?.length, "Graph edges:", data.graph.edges?.length);
        const reactFlowNodes = convertToReactFlowNodes(data.graph.nodes || [], data.account_id);
        const reactFlowEdges = convertToReactFlowEdges(data.graph.edges || []);
        
        // Apply dagre layout for better visualization
        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          reactFlowNodes,
          reactFlowEdges,
          hops > 1 ? "LR" : "TB", // Use horizontal layout for multi-hop graphs
          reactFlowNodes.length
        );
        
        console.log("ReactFlow nodes:", layoutedNodes.length, "ReactFlow edges:", layoutedEdges.length);
        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
        setGraphData(data.graph); // Store graph data for node details
      } else {
        console.warn("No graph data in response:", data);
      }
    },
  });

  // Handle data updates (fallback if onSuccess doesn't fire or data changes)
  useEffect(() => {
    if (data?.graph && !isLoading && !error) {
      console.log("useEffect: Processing graph data", data.graph);
      if (data.graph.nodes && data.graph.nodes.length > 0) {
        const reactFlowNodes = convertToReactFlowNodes(data.graph.nodes, data.account_id);
        const reactFlowEdges = convertToReactFlowEdges(data.graph.edges || []);
        
        // Apply dagre layout
        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          reactFlowNodes,
          reactFlowEdges,
          hops > 1 ? "LR" : "TB",
          reactFlowNodes.length
        );
        
        console.log("useEffect: Setting nodes/edges", layoutedNodes.length, layoutedEdges.length);
        // Only update if we have nodes to avoid clearing existing graph
        if (layoutedNodes.length > 0) {
          setNodes(layoutedNodes);
          setEdges(layoutedEdges);
          if (data?.graph) {
            setGraphData(data.graph);
          }
        }
      }
    }
  }, [data, isLoading, error, hops]);

  // Handle node click
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    const originalNode = node.data.originalNode as GraphNode;
    if (originalNode) {
      setSelectedNode(originalNode);
      setShowDetailsPanel(true);
    }
  }, []);

  // Get connected accounts and transactions for selected node
  const connectedData = useMemo(() => {
    if (!selectedNode || !graphData) return null;
    
    const nodeId = selectedNode.id;
    const connectedAccounts: GraphNode[] = [];
    const outgoingTransactions: GraphEdge[] = [];
    const incomingTransactions: GraphEdge[] = [];
    
    // Find connected accounts and transactions
    graphData.edges.forEach((edge) => {
      if (edge.source === nodeId) {
        outgoingTransactions.push(edge);
        // Find target account
        const targetAccount = graphData.nodes.find(n => n.id === edge.target);
        if (targetAccount) {
          connectedAccounts.push(targetAccount);
        }
      } else if (edge.target === nodeId) {
        incomingTransactions.push(edge);
        // Find source account
        const sourceAccount = graphData.nodes.find(n => n.id === edge.source);
        if (sourceAccount) {
          connectedAccounts.push(sourceAccount);
        }
      }
    });
    
    // Remove duplicates
    const uniqueAccounts = Array.from(
      new Map(connectedAccounts.map(acc => [acc.id, acc])).values()
    );
    
    return {
      connectedAccounts: uniqueAccounts,
      outgoingTransactions,
      incomingTransactions,
      totalOutgoing: outgoingTransactions.reduce((sum, t) => sum + (t.data.amount || 0), 0),
      totalIncoming: incomingTransactions.reduce((sum, t) => sum + (t.data.amount || 0), 0),
    };
  }, [selectedNode, graphData]);

  if (!accountId) {
    return (
      <div className="min-h-screen bg-background pb-20">
        <Header title="Transaction Graph" />
        <main className="px-4 py-6 max-w-screen-xl mx-auto">
          <Card className="p-6">
            <p className="text-center text-muted-foreground">
              No account ID provided. Please go back and try again.
            </p>
            <Button onClick={() => navigate(-1)} className="mt-4 mx-auto block">
              Go Back
            </Button>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header title="Transaction Graph" />
      <main className="px-4 py-6 max-w-screen-xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>

          <div className="flex items-center gap-3">
            {/* Hop controls */}
            <div className="flex items-center gap-1">
              <span className="text-xs text-muted-foreground mr-1">Hops:</span>
              {[1,2,3].map((h) => (
                <Button
                  key={h}
                  variant={hops === h ? "default" : "outline"}
                  size="sm"
                  onClick={() => setHops(h)}
                >
                  {h}
                </Button>
              ))}
            </div>

            {data?.graph.stats && (
              <div className="flex gap-2">
                <Badge variant="outline">
                  {data.graph.stats.total_nodes} Nodes
                </Badge>
                <Badge variant="outline">
                  {data.graph.stats.total_edges} Transactions
                </Badge>
                {data.graph.stats.suspicious_nodes > 0 && (
                  <Badge variant="destructive">
                    {data.graph.stats.suspicious_nodes} Suspicious
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Network className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-2xl font-bold">Transaction Network Graph</h1>
              <p className="text-sm text-muted-foreground">
                Account: {accountId} • {hops}-hop neighborhood
              </p>
            </div>
          </div>

          {isLoading && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                <p className="text-muted-foreground">Loading transaction graph...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center space-y-4 max-w-2xl">
                <p className="text-red-500 font-semibold mb-2 text-lg">Failed to load graph</p>
                <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-left">
                  <p className="text-sm text-foreground mb-2 font-medium">Error Details:</p>
                  <p className="text-sm text-muted-foreground">
                    {error instanceof Error ? error.message : "Unknown error"}
                  </p>
                </div>
                
                {/* Graph Status Diagnostics */}
                {graphStatus && (
                  <div className="bg-muted/50 border rounded-lg p-4 text-left mt-4">
                    <p className="text-sm font-medium mb-2">Graph Status:</p>
                    <div className="space-y-1 text-xs">
                      <p>AMLSim Graph Loaded: {graphStatus.amlsim_graph?.graph_loaded ? "✓ Yes" : "✗ No"}</p>
                      <p>Total Nodes: {graphStatus.amlsim_graph?.node_count || 0}</p>
                      <p>Total Edges: {graphStatus.amlsim_graph?.edge_count || 0}</p>
                      {graphStatus.amlsim_graph?.sample_accounts && graphStatus.amlsim_graph.sample_accounts.length > 0 && (
                        <div className="mt-2">
                          <p className="font-medium">Available Accounts (sample):</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {graphStatus.amlsim_graph.sample_accounts.map((acc: string) => (
                              <Badge 
                                key={acc} 
                                variant="outline" 
                                className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                                onClick={() => navigate(`/graph?account=${acc}`)}
                              >
                                {acc}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                <div className="text-sm text-muted-foreground space-y-2">
                  <p className="font-medium">Common Solutions:</p>
                  <ul className="list-disc list-inside space-y-1 text-left max-w-md mx-auto">
                    <li>Ensure the AMLSim graph is built: <code className="bg-muted px-1 rounded">python build_amlsim_graph.py</code></li>
                    <li>Restart the API server after building the graph</li>
                    <li>Check that account {accountId} exists in the transaction data</li>
                    <li>Try a different account ID from the list above</li>
                  </ul>
                </div>
                <div className="flex gap-2 justify-center mt-4">
                  <Button variant="outline" onClick={() => navigate(-1)}>
                    Go Back
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => window.location.reload()}
                  >
                    Retry
                  </Button>
                </div>
              </div>
            </div>
          )}

          {!isLoading && !error && nodes.length > 0 && (
            <div className="relative" style={{ height: "600px" }}>
              <div style={{ height: "600px" }} className="border rounded-lg">
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  onNodesChange={onNodesChange}
                  onEdgesChange={onEdgesChange}
                  onNodeClick={onNodeClick}
                  fitView
                  attributionPosition="bottom-right"
                  connectionMode={ConnectionMode.Strict}
                  minZoom={0.1}
                  maxZoom={2}
                >
                <Background />
                <Controls />
                <MiniMap
                  nodeColor={(node) => {
                    const style = node.style as any;
                    return style?.background || "#3b82f6";
                  }}
                  maskColor="rgba(0, 0, 0, 0.1)"
                  style={{
                    background: "#f8fafc",
                  }}
                />
                <Panel position="top-right" className="bg-white/90 p-3 rounded-lg shadow-lg">
                  <div className="text-xs space-y-2">
                    <div className="font-semibold text-gray-700 mb-2">Legend</div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-[#ef4444]" />
                      <span>Center Account</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-[#dc2626]" />
                      <span>Fraud</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-[#f59e0b]" />
                      <span>Suspicious</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-[#10b981]" />
                      <span>Normal</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-[#8b5cf6]" />
                      <span>Customer</span>
                    </div>
                  </div>
                </Panel>
              </ReactFlow>
              </div>
            </div>
          )}

          {!isLoading && !error && data && data.graph && (data.graph.nodes?.length === 0 || nodes.length === 0) && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center space-y-4">
                <p className="text-muted-foreground font-medium">
                  No graph data available for account {accountId}
                </p>
                <div className="bg-muted/50 border rounded-lg p-4 text-left mt-4 max-w-md mx-auto">
                  <p className="text-sm font-medium mb-2">Response Details:</p>
                  <div className="space-y-1 text-xs text-muted-foreground">
                    <p>Backend returned: {data.graph.nodes?.length || 0} nodes, {data.graph.edges?.length || 0} edges</p>
                    <p>ReactFlow converted: {nodes.length} nodes, {edges.length} edges</p>
                    {data.graph.stats && (
                      <>
                        <p>Total nodes in stats: {data.graph.stats.total_nodes}</p>
                        <p>Total edges in stats: {data.graph.stats.total_edges}</p>
                      </>
                    )}
                  </div>
                </div>
                <div className="text-sm text-muted-foreground space-y-2">
                  <p>Possible reasons:</p>
                  <ul className="list-disc list-inside space-y-1 text-left max-w-md mx-auto">
                    <li>Account {accountId} doesn't exist in the transaction graph</li>
                    <li>Account has no connections within {hops} hop(s)</li>
                    <li>Try increasing the number of hops using the controls above</li>
                    <li>Check browser console for conversion errors</li>
                  </ul>
                </div>
                <div className="flex gap-2 justify-center mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setHops(Math.min(3, hops + 1))}
                    disabled={hops >= 3}
                  >
                    Increase Hops
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => navigate(-1)}>
                    Go Back
                  </Button>
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* Node Details Sheet */}
        <Sheet open={showDetailsPanel} onOpenChange={setShowDetailsPanel}>
          <SheetContent className="w-full sm:max-w-2xl overflow-y-auto">
            <SheetHeader>
              <SheetTitle>Account Details</SheetTitle>
              <SheetDescription>
                View connected accounts, transactions, and account information
              </SheetDescription>
            </SheetHeader>
            
            {selectedNode && (
              <div className="mt-6 space-y-6">
                {/* Account Info */}
                <Card className="p-4">
                  <div className="flex items-center gap-3 mb-4">
                    <div 
                      className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold"
                      style={{ backgroundColor: selectedNode.color }}
                    >
                      {selectedNode.label}
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{selectedNode.id.replace('account_', 'Account ').replace('customer_', 'Customer ')}</h3>
                      <p className="text-sm text-muted-foreground">Type: {selectedNode.type}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    {selectedNode.data.balance > 0 && (
                      <div>
                        <p className="text-xs text-muted-foreground">Balance</p>
                        <p className="font-semibold">${selectedNode.data.balance.toLocaleString()}</p>
                      </div>
                    )}
                    {selectedNode.data.country && (
                      <div>
                        <p className="text-xs text-muted-foreground">Country</p>
                        <p className="font-semibold">{selectedNode.data.country}</p>
                      </div>
                    )}
                    {selectedNode.data.business_type && (
                      <div>
                        <p className="text-xs text-muted-foreground">Business Type</p>
                        <p className="font-semibold">{selectedNode.data.business_type}</p>
                      </div>
                    )}
                    <div>
                      <p className="text-xs text-muted-foreground">Status</p>
                      <div className="flex gap-2 mt-1">
                        {selectedNode.data.is_fraud && (
                          <Badge variant="destructive">Fraud</Badge>
                        )}
                        {selectedNode.data.is_suspicious && (
                          <Badge variant="outline" className="border-orange-500 text-orange-500">Suspicious</Badge>
                        )}
                        {!selectedNode.data.is_fraud && !selectedNode.data.is_suspicious && (
                          <Badge variant="outline" className="border-green-500 text-green-500">Normal</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Transaction Summary */}
                {connectedData && (
                  <>
                    <Card className="p-4">
                      <h4 className="font-semibold mb-4 flex items-center gap-2">
                        <ArrowRightLeft className="h-4 w-4" />
                        Transaction Summary
                      </h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <p className="text-xs text-muted-foreground">Outgoing</p>
                          <p className="text-lg font-semibold text-red-600">
                            ${connectedData.totalOutgoing.toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {connectedData.outgoingTransactions.length} transactions
                          </p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-xs text-muted-foreground">Incoming</p>
                          <p className="text-lg font-semibold text-green-600">
                            ${connectedData.totalIncoming.toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {connectedData.incomingTransactions.length} transactions
                          </p>
                        </div>
                      </div>
                    </Card>

                    {/* Connected Accounts */}
                    <Card className="p-4">
                      <h4 className="font-semibold mb-4 flex items-center gap-2">
                        <Network className="h-4 w-4" />
                        Connected Accounts ({connectedData.connectedAccounts.length})
                      </h4>
                      <ScrollArea className="h-64">
                        <div className="space-y-2">
                          {connectedData.connectedAccounts.map((account) => (
                            <div
                              key={account.id}
                              className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                            >
                              <div className="flex items-center gap-3">
                                <div
                                  className="w-8 h-8 rounded flex items-center justify-center text-white text-xs font-bold"
                                  style={{ backgroundColor: account.color }}
                                >
                                  {account.label}
                                </div>
                                <div>
                                  <p className="font-medium text-sm">{account.id.replace('account_', 'Account ')}</p>
                                  <p className="text-xs text-muted-foreground">{account.type}</p>
                                </div>
                              </div>
                              <div className="flex gap-2">
                                {account.data.is_fraud && (
                                  <Badge variant="destructive" className="text-xs">Fraud</Badge>
                                )}
                                {account.data.is_suspicious && (
                                  <Badge variant="outline" className="text-xs border-orange-500 text-orange-500">Suspicious</Badge>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </Card>

                    {/* Transactions */}
                    <Card className="p-4">
                      <h4 className="font-semibold mb-4 flex items-center gap-2">
                        <DollarSign className="h-4 w-4" />
                        Transactions ({connectedData.outgoingTransactions.length + connectedData.incomingTransactions.length})
                      </h4>
                      <ScrollArea className="h-64">
                        <div className="space-y-2">
                          {/* Outgoing */}
                          {connectedData.outgoingTransactions.map((txn, idx) => {
                            const targetAccount = graphData?.nodes.find(n => n.id === txn.target);
                            return (
                              <div key={`out-${idx}`} className="p-3 border rounded-lg bg-red-50/50 dark:bg-red-950/20">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <ArrowRightLeft className="h-4 w-4 text-red-600" />
                                    <span className="text-sm font-medium">To: {txn.target.replace('account_', 'Account ')}</span>
                                  </div>
                                  <span className="font-semibold text-red-600">
                                    ${txn.data.amount.toLocaleString()}
                                  </span>
                                </div>
                                {txn.data.transaction_type && (
                                  <p className="text-xs text-muted-foreground mt-1">
                                    Type: {txn.data.transaction_type}
                                  </p>
                                )}
                              </div>
                            );
                          })}
                          
                          {/* Incoming */}
                          {connectedData.incomingTransactions.map((txn, idx) => {
                            const sourceAccount = graphData?.nodes.find(n => n.id === txn.source);
                            return (
                              <div key={`in-${idx}`} className="p-3 border rounded-lg bg-green-50/50 dark:bg-green-950/20">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <ArrowRightLeft className="h-4 w-4 text-green-600 rotate-180" />
                                    <span className="text-sm font-medium">From: {txn.source.replace('account_', 'Account ')}</span>
                                  </div>
                                  <span className="font-semibold text-green-600">
                                    ${txn.data.amount.toLocaleString()}
                                  </span>
                                </div>
                                {txn.data.transaction_type && (
                                  <p className="text-xs text-muted-foreground mt-1">
                                    Type: {txn.data.transaction_type}
                                  </p>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </ScrollArea>
                    </Card>

                    {/* Legend */}
                    <Card className="p-4">
                      <h4 className="font-semibold mb-4 flex items-center gap-2">
                        <Info className="h-4 w-4" />
                        Legend
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded bg-[#ef4444]" />
                          <span>Center Account</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded bg-[#dc2626]" />
                          <span>Fraud Account</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded bg-[#f59e0b]" />
                          <span>Suspicious Account</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded bg-[#10b981]" />
                          <span>Normal Account</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded bg-[#8b5cf6]" />
                          <span>Customer Node</span>
                        </div>
                        <Separator className="my-2" />
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-0.5 bg-red-600" />
                          <span>High-value transaction (&gt;$100K)</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-0.5 bg-gray-400" />
                          <span>Normal transaction</span>
                        </div>
                      </div>
                    </Card>
                  </>
                )}
              </div>
            )}
          </SheetContent>
        </Sheet>
      </main>
    </div>
  );
}
