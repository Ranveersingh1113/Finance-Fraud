import { Header } from "@/components/Layout/Header";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Search, Clock, TrendingUp, Sparkles, Loader2, FileText, X, Network, ExternalLink } from "lucide-react";
import { useState, useEffect } from "react";
import { useUnifiedSearch } from "@/hooks/useSearch";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const STORAGE_KEY = "search_history";

interface SearchHistoryItem {
  query: string;
  timestamp: number;
}

export default function SearchPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [recentSearches, setRecentSearches] = useState<SearchHistoryItem[]>([]);
  const [expandedAccounts, setExpandedAccounts] = useState(false);
  
  const { mutate: search, data: searchResults, isPending, error } = useUnifiedSearch();

  // Load search history from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const history = JSON.parse(stored) as SearchHistoryItem[];
        setRecentSearches(history);
      } catch (e) {
        console.error("Failed to load search history:", e);
      }
    }
  }, []);

  // Save search to history
  const saveToHistory = (query: string) => {
    if (!query.trim()) return;
    
    const newItem: SearchHistoryItem = {
      query: query.trim(),
      timestamp: Date.now(),
    };

    setRecentSearches((prev) => {
      // Remove duplicates and add to beginning
      const filtered = prev.filter((item) => item.query !== newItem.query);
      const updated = [newItem, ...filtered].slice(0, 10); // Keep last 10
      
      // Save to localStorage
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  // Delete a search from history
  const deleteFromHistory = (query: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the card click
    
    setRecentSearches((prev) => {
      const updated = prev.filter((item) => item.query !== query);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  // Clear all search history
  const clearHistory = () => {
    setRecentSearches([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      setHasSearched(true);
      saveToHistory(searchQuery);
      search({
        query: searchQuery,
        n_results: 5,
        include_metadata: true,
      });
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header title="Intelligent Search" />
      
      <main className="px-4 py-6 max-w-screen-xl mx-auto space-y-6">
        {/* Search Input */}
        <div className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Ask about fraud patterns, regulations, or cases..."
              className="pl-10 pr-4 h-12 text-base"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button 
            onClick={handleSearch} 
            disabled={!searchQuery.trim() || isPending}
            className="w-full h-12 bg-gradient-primary"
          >
            {isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing with GraphRAG...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Intelligent Search
              </>
            )}
          </Button>
        </div>

        {/* Quick Filters */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          <Badge variant="outline" className="cursor-pointer hover:bg-primary hover:text-primary-foreground">
            All Sources
          </Badge>
          <Badge variant="outline" className="cursor-pointer hover:bg-primary hover:text-primary-foreground">
            SEBI Regulations
          </Badge>
          <Badge variant="outline" className="cursor-pointer hover:bg-primary hover:text-primary-foreground">
            Transactions
          </Badge>
          <Badge variant="outline" className="cursor-pointer hover:bg-primary hover:text-primary-foreground">
            Patterns
          </Badge>
        </div>

        {/* Recent Searches */}
        {recentSearches.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-semibold text-foreground">Recent Searches</h3>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearHistory}
                className="text-xs text-muted-foreground hover:text-destructive"
              >
                Clear All
              </Button>
            </div>
            <div className="space-y-2">
              {recentSearches.map((item, i) => (
                <Card
                  key={i}
                  className="p-3 cursor-pointer hover:shadow-md transition-shadow group relative"
                  onClick={() => setSearchQuery(item.query)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm text-foreground flex-1">{item.query}</p>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive"
                      onClick={(e) => deleteFromHistory(item.query, e)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                </Card>
              ))}
            </div>
          </section>
        )}

        {/* Error State */}
        {error && (
          <Card className="p-4 bg-destructive/10 border-destructive">
            <p className="text-sm text-destructive">{error.message}</p>
          </Card>
        )}

        {/* AI Answer */}
        {searchResults && hasSearched && (() => {
          // Clean answer text - remove stats sections
          const cleanAnswer = (text: string) => {
            if (!text) return text;
            
            // Remove "KNOWLEDGE GRAPH INTELLIGENCE:" section with stats
            let cleaned = text.replace(
              /\*\*KNOWLEDGE GRAPH INTELLIGENCE:\*\*[\s\S]*?(?=\*\*CROSS-DOMAIN|AI ANALYSIS|ACCOUNT PROFILE|$)/i,
              ''
            );
            
            // Remove "SEBI Regulatory Database:" stats
            cleaned = cleaned.replace(
              /SEBI Regulatory Database:[\s\S]*?violation types on record[\s\S]*?(?=\n\n|$)/i,
              ''
            );
            
            // Remove "Transaction Network Analysis:" stats
            cleaned = cleaned.replace(
              /Transaction Network Analysis:[\s\S]*?suspicious accounts flagged[\s\S]*?(?=\n\n|$)/i,
              ''
            );
            
            // Improve formatting for numbered lists (account lists)
            cleaned = cleaned.replace(/(\d+)\.\s+(Account \d+):/g, '$1. **$2**:');
            
            // Improve formatting for pattern descriptions
            cleaned = cleaned.replace(/\*\*CROSS-DOMAIN PATTERN ANALYSIS:\*\*/g, '## Cross-Domain Pattern Analysis');
            
            // Clean up multiple newlines
            cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
            
            return cleaned.trim();
          };

          const formattedAnswer = cleanAnswer(searchResults.answer);
          
          // Extract account IDs from the answer for clickable links
          const extractAccountIds = (text: string): string[] => {
            // Only match "Account" followed by a number, or numbers in account-specific contexts
            // Avoid matching years (2002, 2005), regulation numbers, etc.
            const patterns = [
              /Account\s+(\d{1,4})(?:\s|$|,|:|\.|;)/gi,  // "Account 123"
              /account\s+ID:\s*(\d{1,4})/gi,  // "Account ID: 123"
              /account\s+(\d{1,4})\s+(?:has|shows|displays|contains|with)/gi,  // "account 123 has"
              /(?:analyze|trace|show|find).*?account\s+(\d{1,4})/gi,  // "analyze account 123"
            ];
            
            const accounts = new Set<string>();
            patterns.forEach(pattern => {
              const matches = text.matchAll(pattern);
              for (const match of matches) {
                const accountId = match[1];
                // Filter out common false positives (years, regulation numbers)
                if (accountId && 
                    !['2002', '2005', '2019', '2020', '2021', '2022', '2023', '2024'].includes(accountId) &&
                    parseInt(accountId) > 0 && parseInt(accountId) < 10000) {
                  accounts.add(accountId);
                }
              }
            });
            
            return Array.from(accounts);
          };
          
          const accountIds = extractAccountIds(formattedAnswer);
          
          // Process answer to make account IDs clickable
          const processAnswerWithLinks = (text: string): string => {
            let processed = text;
            // Replace account mentions with markdown links
            accountIds.forEach(accountId => {
              const regex = new RegExp(`(Account\\s+)?${accountId}(?![\\d])`, 'gi');
              processed = processed.replace(regex, (match) => {
                // Don't replace if already in a link
                if (match.includes('[') || match.includes(']')) return match;
                return `[${match}](/graph?account=${accountId})`;
              });
            });
            return processed;
          };
          
          const answerWithLinks = processAnswerWithLinks(formattedAnswer);
          const hasPatternAnalysis = formattedAnswer.includes("Cross-Domain Pattern Analysis");
          const patternSection = hasPatternAnalysis ? formattedAnswer.split('---')[0] : '';
          const mainAnswer = hasPatternAnalysis ? formattedAnswer.split('---').slice(1).join('---') : formattedAnswer;

          return (
            <>
              <section>
                <Card className="p-6 mb-6 bg-gradient-to-br from-primary/5 to-primary/10">
                  <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="h-5 w-5 text-primary" />
                    <h3 className="text-base font-semibold text-foreground">AI Analysis</h3>
                    <Badge variant="secondary" className="ml-auto">
                      {(searchResults.confidence_score * 100).toFixed(0)}% confident
                    </Badge>
                  </div>
                  
                  {/* Cross-Domain Pattern Analysis Section */}
                  {hasPatternAnalysis && patternSection && (
                    <Card className="p-4 mb-4 bg-muted/50 border">
                      <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        Pattern Analysis
                      </h4>
                      <div className="text-sm text-muted-foreground">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            h2: ({node, ...props}) => <h2 className="text-base font-semibold mt-4 mb-2" {...props} />,
                            ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-1 ml-2" {...props} />,
                            li: ({node, ...props}) => <li className="text-foreground" {...props} />,
                            p: ({node, ...props}) => <p className="mb-2" {...props} />,
                            strong: ({node, ...props}) => <strong className="font-semibold text-foreground" {...props} />,
                          }}
                        >
                          {patternSection}
                        </ReactMarkdown>
                      </div>
                    </Card>
                  )}
                  
                  {/* Main Answer with Markdown Rendering */}
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        h2: ({node, ...props}) => <h2 className="text-base font-semibold mt-4 mb-2 text-foreground" {...props} />,
                        h3: ({node, ...props}) => <h3 className="text-sm font-semibold mt-3 mb-2 text-foreground" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-1 ml-4 mb-3" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal list-inside space-y-1 ml-4 mb-3" {...props} />,
                        li: ({node, ...props}) => <li className="text-foreground" {...props} />,
                        p: ({node, ...props}) => <p className="mb-3 leading-relaxed text-foreground" {...props} />,
                        strong: ({node, ...props}) => <strong className="font-semibold text-foreground" {...props} />,
                        a: ({node, href, children, ...props}) => {
                          if (href?.startsWith('/graph')) {
                            const accountId = href.split('account=')[1];
                            return (
                              <button
                                onClick={(e) => {
                                  e.preventDefault();
                                  navigate(href);
                                }}
                                className="text-primary hover:text-primary/80 underline font-medium inline-flex items-center gap-1"
                                {...props}
                              >
                                {children}
                                <ExternalLink className="h-3 w-3" />
                              </button>
                            );
                          }
                          return <a href={href} className="text-primary hover:underline" {...props}>{children}</a>;
                        },
                      }}
                    >
                      {mainAnswer}
                    </ReactMarkdown>
                  </div>
                  
                  {/* Quick Account Links */}
                  {accountIds.length > 0 && (
                    <div className="mt-4 pt-4 border-t">
                      <div className="flex items-center gap-2 mb-2">
                        <Network className="h-4 w-4 text-muted-foreground" />
                        <span className="text-xs font-medium text-muted-foreground">Quick Access:</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {accountIds.slice(0, expandedAccounts ? accountIds.length : 6).map((accountId) => (
                          <Button
                            key={accountId}
                            variant="outline"
                            size="sm"
                            className="h-7 text-xs"
                            onClick={() => navigate(`/graph?account=${accountId}`)}
                          >
                            Account {accountId}
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </Button>
                        ))}
                        {accountIds.length > 6 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs"
                            onClick={() => setExpandedAccounts(!expandedAccounts)}
                          >
                            {expandedAccounts ? 'Show Less' : `+${accountIds.length - 6} more`}
                          </Button>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground">
                    <span>⏱️ {searchResults.processing_time.toFixed(2)}s</span>
                    <span>📊 {searchResults.query_type.replace('_', ' ')}</span>
                    <span>🔍 {searchResults.evidence.length} sources</span>
                  </div>
                </Card>
              </section>

              {/* Evidence Sources - Collapsible */}
              {searchResults.evidence && searchResults.evidence.length > 0 && (
                <section>
                  <Accordion type="single" collapsible className="w-full">
                    <AccordionItem value="evidence">
                      <AccordionTrigger className="hover:no-underline">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-muted-foreground" />
                          <h3 className="text-base font-semibold text-foreground">
                            View Context & Evidence Used
                          </h3>
                          <Badge variant="secondary" className="ml-2">
                            {searchResults.evidence.length} sources
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-3 pt-2">
                          {searchResults.evidence.map((evidence, i) => (
                            <Card key={i} className="p-4 hover:shadow-lg transition-shadow">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center gap-2">
                                  <Badge variant="outline" className="font-mono">
                                    [{evidence.rank}]
                                  </Badge>
                                  <span className="text-sm font-semibold text-foreground">
                                    {evidence.source.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                  </span>
                                </div>
                                <div className="flex items-center gap-1">
                                  <TrendingUp className="h-4 w-4 text-success" />
                                  <span className="text-xs font-semibold text-success">
                                    {(evidence.score * 100).toFixed(0)}%
                                  </span>
                                </div>
                              </div>
                              <p className="text-sm text-muted-foreground leading-relaxed">
                                {evidence.document.substring(0, 300)}
                                {evidence.document.length > 300 && '...'}
                              </p>
                              {evidence.metadata && Object.keys(evidence.metadata).length > 0 && (
                                <div className="mt-2 pt-2 border-t text-xs text-muted-foreground">
                                  {evidence.metadata.title && (
                                    <p><strong>Title:</strong> {evidence.metadata.title}</p>
                                  )}
                                  {evidence.metadata.document_type && (
                                    <p><strong>Type:</strong> {evidence.metadata.document_type}</p>
                                  )}
                                </div>
                              )}
                            </Card>
                          ))}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </section>
              )}
            </>
          );
        })()}
      </main>
    </div>
  );
}
