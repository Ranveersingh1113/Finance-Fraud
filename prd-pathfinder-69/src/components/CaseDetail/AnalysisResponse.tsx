/**
 * Component to format and display analysis responses from the RAG engine
 */
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  FileText,
  Shield,
  Target,
  CheckSquare,
  Gavel,
  Clock,
  Network,
  ExternalLink,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";

interface AnalysisResponseProps {
  answer: string;
}

export function AnalysisResponse({ answer }: AnalysisResponseProps) {
  // Parse the structured response - handle both formatted and plain text
  const parseResponse = (text: string) => {
    // If text doesn't contain structured data, return plain text
    if (!text.includes('ACCOUNT PROFILE') && !text.includes('MONEY FLOW') && !text.includes('ACCOUNT ID:')) {
      return { plainText: text };
    }
    const sections: Record<string, any> = {
      accountProfile: null,
      transactionFlow: null,
      topOutgoing: [],
      topIncoming: [],
      fraudTypology: null,
      regulatoryViolations: [],
      requiredActions: [],
      complianceChecklist: [],
      casePrecedents: [],
      regulatoryContext: null,
      riskAssessment: null,
    };

    // Extract account profile (handle both "ACCOUNT PROFILE:" and "MONEY FLOW ANALYSIS:" formats)
    const accountMatch = text.match(/(?:ACCOUNT PROFILE|MONEY FLOW ANALYSIS)[\s\S]*?ACCOUNT PROFILE:([\s\S]*?)(?=TRANSACTION|REGULATORY|RISK|$)/i) ||
                       text.match(/ACCOUNT PROFILE:([\s\S]*?)(?=TRANSACTION|REGULATORY|RISK|$)/i);
    if (accountMatch) {
      const profileText = accountMatch[1];
      sections.accountProfile = {
        id: profileText.match(/Account ID:\s*(\d+)/i)?.[1],
        type: profileText.match(/Type:\s*(\w+)/i)?.[1],
        country: profileText.match(/Country:\s*(\w+)/i)?.[1],
        balance: profileText.match(/Balance:\s*([^\n]+)/i)?.[1],
        status: profileText.match(/Status:\s*([^\n]+)/i)?.[1],
        fraudFlag: profileText.match(/Fraud Flag:\s*(\w+)/i)?.[1],
      };
    }

    // Extract transaction flow
    const flowMatch = text.match(/TRANSACTION FLOW[^:]*:([\s\S]*?)(?=TOP OUTGOING|REGULATORY|RISK|$)/i);
    if (flowMatch) {
      const flowText = flowMatch[1];
      sections.transactionFlow = {
        accountsConnected: flowText.match(/Accounts Connected:\s*(\d+)/i)?.[1],
        outgoing: flowText.match(/Outgoing Transactions:\s*(\d+)/i)?.[1],
        incoming: flowText.match(/Incoming Transactions:\s*(\d+)/i)?.[1],
        totalSent: flowText.match(/Total Sent:\s*([^\n]+)/i)?.[1],
        totalReceived: flowText.match(/Total Received:\s*([^\n]+)/i)?.[1],
        netFlow: flowText.match(/Net Flow:\s*([^\n]+)/i)?.[1],
        patternType: flowText.match(/Pattern Type:\s*([^\n]+)/i)?.[1],
        patternDescription: flowText.match(/Pattern Description:\s*([^\n]+)/i)?.[1],
      };
    }

    // Extract top outgoing transactions
    const outgoingMatch = text.match(/TOP OUTGOING TRANSACTIONS:([\s\S]*?)(?=TOP INCOMING|REGULATORY|RISK|$)/i);
    if (outgoingMatch) {
      const outgoingText = outgoingMatch[1];
      const transactions = outgoingText.match(/\d+\.\s*Sent\s*([^\n→]+)\s*→\s*Account\s*(\d+)/g);
      if (transactions) {
        sections.topOutgoing = transactions.map((t) => {
          const match = t.match(/\d+\.\s*Sent\s*([^\n→]+)\s*→\s*Account\s*(\d+)/);
          return { amount: match?.[1]?.trim(), account: match?.[2] };
        });
      }
    }

    // Extract top incoming transactions
    const incomingMatch = text.match(/TOP INCOMING TRANSACTIONS:([\s\S]*?)(?=FRAUD TYPOLOGY|REGULATORY|RISK|$)/i);
    if (incomingMatch) {
      const incomingText = incomingMatch[1];
      const transactions = incomingText.match(/\d+\.\s*Received\s*([^\n←]+)\s*←\s*Account\s*(\d+)/g);
      if (transactions) {
        sections.topIncoming = transactions.map((t) => {
          const match = t.match(/\d+\.\s*Received\s*([^\n←]+)\s*←\s*Account\s*(\d+)/);
          return { amount: match?.[1]?.trim(), account: match?.[2] };
        });
      }
    }

    // Extract fraud typology
    const fraudMatch = text.match(/🔍 FRAUD TYPOLOGY & INTELLIGENCE:([\s\S]*?)(?=\*\*⚖️|REGULATORY|RISK|$)/i);
    if (fraudMatch) {
      const fraudText = fraudMatch[1];
      sections.fraudTypology = {
        fraudType: fraudText.match(/Fraud Type:\s*\*\*([^*]+)\*\*/i)?.[1]?.trim(),
        mlPhase: fraudText.match(/Money Laundering Phase:\s*\*\*([^*]+)\*\*/i)?.[1]?.trim(),
        priority: fraudText.match(/Investigation Priority:\s*\*\*([^*]+)\*\*/i)?.[1]?.trim(),
        indicators: fraudText.match(/Key Fraud Indicators:([\s\S]*?)(?=\*\*⚖️|REGULATORY|RISK|$)/i)?.[1]
          ?.split(/[•\n]/)
          .filter(Boolean)
          .map(i => i.trim()) || [],
      };
    }

    // Extract regulatory violations
    const violationsMatch = text.match(/⚖️ Regulatory Violations Identified:([\s\S]*?)(?=\*\*📋|RISK|$)/i);
    if (violationsMatch) {
      sections.regulatoryViolations = violationsMatch[1]
        .split(/[•\n]/)
        .filter(Boolean)
        .map(v => v.trim());
    }

    // Extract required actions
    const actionsMatch = text.match(/📋 REQUIRED ACTIONS[^:]*:([\s\S]*?)(?=\*\*✅|REGULATORY|RISK|$)/i);
    if (actionsMatch) {
      const actionsText = actionsMatch[1];
      const actionItems = actionsText.split(/[🔴🟠🟡]\s*\*\*/).filter(Boolean);
      sections.requiredActions = actionItems.map(item => {
        const actionMatch = item.match(/([^*]+)\*\*/);
        const deadlineMatch = item.match(/Deadline:\s*([^|]+)/i);
        const priorityMatch = item.match(/Priority:\s*(\w+)/i);
        return {
          action: actionMatch?.[1]?.trim(),
          deadline: deadlineMatch?.[1]?.trim(),
          priority: priorityMatch?.[1]?.trim(),
        };
      }).filter(a => a.action);
    }

    // Extract compliance checklist
    // IMPORTANT: Stop at REGULATORY CONTEXT section or separator to avoid capturing SEBI documents
    const complianceMatch = text.match(/✅ COMPLIANCE CHECKLIST:([\s\S]*?)(?=---|\*\*📚 REGULATORY CONTEXT|\*\*REGULATORY CONTEXT|📚 REGULATORY CONTEXT|RISK ASSESSMENT|$)/i);
    if (complianceMatch) {
      let checklistText = complianceMatch[1].trim();
      
      // CRITICAL: Remove any SEBI regulation document content that might have been captured
      // Remove patterns that indicate SEBI documents (numbered lists with relevance scores, etc.)
      checklistText = checklistText.replace(/\d+\.\s*\*\*[^*]+\*\*\s*\(Relevance:\s*\d+\.\d+%\)[\s\S]*?(?=\d+\.|$)/gi, '');
      checklistText = checklistText.replace(/\*\*Supporting SEBI Regulation Documents:\*\*[\s\S]*/gi, '');
      checklistText = checklistText.replace(/📚 REGULATORY CONTEXT[\s\S]*/gi, '');
      checklistText = checklistText.replace(/Supporting SEBI Regulation Documents:[\s\S]*/gi, '');
      checklistText = checklistText.replace(/---[\s\S]*/gi, ''); // Remove separator if captured
      
      sections.complianceChecklist = checklistText
        .split(/[☐\n]/)
        .filter(Boolean)
        .map(c => c.trim())
        .filter(c => {
          // Filter out items that look like SEBI document entries
          const isSebiDoc = /\(Relevance:\s*\d+\.\d+%\)/i.test(c) || 
                           /Supporting SEBI/i.test(c) ||
                           /SEBI Master Circular/i.test(c) ||
                           /SEBI.*Regulation.*Document/i.test(c) ||
                           /^\d+\.\s*\*\*/i.test(c); // Numbered list items with bold (likely SEBI docs)
          return c.length > 10 && !isSebiDoc;
        });
    }

    // Extract case precedents
    const precedentsMatch = text.match(/📚 SIMILAR SEBI ENFORCEMENT CASES[\s\S]*?Found \d+ enforcement cases[^\n]*\n([\s\S]*?)(?=\*\*REGULATORY|RISK|$)/i);
    if (precedentsMatch) {
      const precedentsText = precedentsMatch[1];
      const caseMatches = precedentsText.matchAll(/\d+\.\s*\*\*([^*]+)\*\*[\s\S]*?Violation:\s*([^\n]+)[\s\S]*?Outcome:\s*([^\n]+)/gi);
      for (const match of caseMatches) {
        sections.casePrecedents.push({
          name: match[1].trim(),
          violation: match[2].trim(),
          outcome: match[3].trim(),
        });
      }
    }

    // Extract regulatory context (put in collapsible)
    // IMPORTANT: Only extract SEBI documents, NOT fraud intelligence content (violations, actions, checklist)
    // Try multiple patterns to catch different formats, but exclude fraud intelligence sections
    const regulatoryMatch = text.match(/📚 REGULATORY CONTEXT & SEBI REGULATIONS:([\s\S]*?)(?=RISK ASSESSMENT|$)/i) ||
                           text.match(/\*\*📚 REGULATORY CONTEXT & SEBI REGULATIONS:\*\*([\s\S]*?)(?=RISK ASSESSMENT|$)/i) ||
                           text.match(/REGULATORY CONTEXT:([\s\S]*?)(?=RISK ASSESSMENT|$)/i) ||
                           text.match(/REGULATORY CONTEXT:([\s\S]*?)(?=\n\n|RISK|$)/i);
    
    if (regulatoryMatch) {
      let context = regulatoryMatch[1].trim();
      
      // CRITICAL: Remove any fraud intelligence content that might have been extracted
      // Remove violations, actions, and compliance checklist sections
      context = context.replace(/\*\*⚖️ Regulatory Violations Identified:\*\*[\s\S]*?(?=\*\*📋|\*\*✅|\*\*📚|RISK|$)/gi, '');
      context = context.replace(/\*\*📋 REQUIRED ACTIONS[^:]*:\*\*[\s\S]*?(?=\*\*✅|\*\*📚|RISK|$)/gi, '');
      context = context.replace(/\*\*✅ COMPLIANCE CHECKLIST:\*\*[\s\S]*?(?=\*\*📚|RISK|$)/gi, '');
      context = context.replace(/⚖️ Regulatory Violations Identified:[\s\S]*?(?=📋|✅|📚|RISK|$)/gi, '');
      context = context.replace(/📋 REQUIRED ACTIONS[^:]*:[\s\S]*?(?=✅|📚|RISK|$)/gi, '');
      context = context.replace(/✅ COMPLIANCE CHECKLIST:[\s\S]*?(?=📚|RISK|$)/gi, '');
      
      // Clean up unnecessary phrases
      context = context.replace(/\d+\s+similar\s+SEBI\s+enforcement\s+cases?\s+found/gi, '');
      context = context.replace(/Pattern matches SEBI violations with \d+% confidence/gi, '');
      context = context.replace(/Recommended Action:[^\n]+/gi, '');
      context = context.replace(/Enhanced monitoring and SAR filing/gi, '');
      context = context.trim();
      
      // Only include if there's substantial content and it's NOT just fraud intelligence
      if (context && context.length > 10 && 
          !context.match(/Regulatory Violations Identified|REQUIRED ACTIONS|COMPLIANCE CHECKLIST/i)) {
        sections.regulatoryContext = context;
      }
    }
    
    // Also check for SEBI regulations section at the start (for regulatory queries)
    // Try multiple patterns to catch the regulations section
    const sebiRegMatch = text.match(/SEBI REGULATIONS APPLICABLE TO ACCOUNT[\s\S]*?(?=ACCOUNT PROFILE|Account Context|REGULATORY CONTEXT|RISK ASSESSMENT|$)/i) ||
                         text.match(/## SEBI REGULATIONS[\s\S]*?(?=ACCOUNT PROFILE|Account Context|REGULATORY CONTEXT|RISK ASSESSMENT|$)/i) ||
                         text.match(/\*\*SEBI Regulations Applicable:\*\*[\s\S]*?(?=ACCOUNT PROFILE|Account Context|REGULATORY CONTEXT|RISK ASSESSMENT|$)/i);
    
    if (sebiRegMatch && !sections.regulatoryContext) {
      let regText = sebiRegMatch[0].trim();
      // Extract the regulations part - remove the header
      const regContent = regText
        .replace(/^## SEBI REGULATIONS[^\n]*\n/i, '')
        .replace(/^\*\*SEBI Regulations Applicable:\*\*\s*/i, '')
        .replace(/^SEBI REGULATIONS APPLICABLE TO ACCOUNT[^\n]*\n/i, '')
        .trim();
      if (regContent && regContent.length > 50) {
        sections.regulatoryContext = regContent;
      }
    }
    
    // If still no regulatory context but the query mentions regulations, extract from the beginning
    if (!sections.regulatoryContext && (text.includes('SEBI') || text.includes('regulation'))) {
      // Try to extract first few paragraphs as regulatory content
      const lines = text.split('\n');
      let regulatoryLines: string[] = [];
      let foundRegStart = false;
      for (const line of lines) {
        if (line.match(/SEBI|regulation|regulatory|compliance/i) && !foundRegStart) {
          foundRegStart = true;
        }
        if (foundRegStart && regulatoryLines.length < 20) {
          regulatoryLines.push(line);
          if (line.match(/ACCOUNT PROFILE|Account Context|REGULATORY CONTEXT|RISK/i)) {
            break;
          }
        }
      }
      if (regulatoryLines.length > 5) {
        sections.regulatoryContext = regulatoryLines.join('\n').trim();
      }
    }

    // Extract risk assessment
    const riskMatch = text.match(/RISK ASSESSMENT:([\s\S]*?)$/i);
    if (riskMatch) {
      const riskText = riskMatch[1];
      sections.riskAssessment = {
        level: riskText.match(/Risk Level:\s*([^\n(]+)/i)?.[1]?.trim(),
        score: riskText.match(/Score:\s*(\d+)/i)?.[1],
        factors: riskText.match(/Risk Factors:([\s\S]*?)(?=SAR Filing|$)/i)?.[1]?.trim(),
        sarFiling: riskText.match(/SAR Filing:\s*([^\n]+)/i)?.[1]?.trim(),
      };
    }

    return sections;
  };

  // Clean answer text - remove stats sections before parsing
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

  const navigate = useNavigate();
  const cleanedAnswer = cleanAnswer(answer);
  const sections = parseResponse(cleanedAnswer);
  
  // Extract account IDs for clickable links
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
  
  const accountIds = extractAccountIds(cleanedAnswer);
  const [expandedAccounts, setExpandedAccounts] = useState(false);
  
  // Process answer to make account IDs clickable
  const processAnswerWithLinks = (text: string): string => {
    let processed = text;
    accountIds.forEach(accountId => {
      const regex = new RegExp(`(Account\\s+)?${accountId}(?![\\d])`, 'gi');
      processed = processed.replace(regex, (match) => {
        if (match.includes('[') || match.includes(']')) return match;
        return `[${match}](/graph?account=${accountId})`;
      });
    });
    return processed;
  };
  
  const answerWithLinks = processAnswerWithLinks(cleanedAnswer);
  const hasPatternAnalysis = cleanedAnswer.includes("Cross-Domain Pattern Analysis");
  const patternSection = hasPatternAnalysis ? cleanedAnswer.split('---')[0] : '';
  const mainAnswer = hasPatternAnalysis ? cleanedAnswer.split('---').slice(1).join('---') : cleanedAnswer;

  // If plain text, display with markdown rendering
  if (sections.plainText) {
    return (
      <div className="space-y-4">
        {/* Pattern Analysis Section */}
        {hasPatternAnalysis && patternSection && (
          <Card className="p-4 bg-muted/50 border">
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
        
        <Card className="p-4">
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
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Account Profile */}
      {sections.accountProfile && (
        <Card className="p-4">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Account Profile
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {sections.accountProfile.id && (
              <div>
                <p className="text-xs text-muted-foreground">Account ID</p>
                <p className="font-medium">{sections.accountProfile.id}</p>
              </div>
            )}
            {sections.accountProfile.balance && (
              <div>
                <p className="text-xs text-muted-foreground">Balance</p>
                <p className="font-medium text-green-600">{sections.accountProfile.balance}</p>
              </div>
            )}
            {sections.accountProfile.status && (
              <div>
                <p className="text-xs text-muted-foreground">Status</p>
                <Badge
                  variant={sections.accountProfile.status === "SUSPICIOUS" ? "destructive" : "secondary"}
                >
                  {sections.accountProfile.status}
                </Badge>
              </div>
            )}
            {sections.accountProfile.fraudFlag === "YES" && (
              <div>
                <p className="text-xs text-muted-foreground">Fraud Flag</p>
                <Badge variant="destructive">Yes</Badge>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Transaction Flow */}
      {sections.transactionFlow && (
        <Card className="p-4">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Transaction Flow
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
            {sections.transactionFlow.accountsConnected && (
              <div>
                <p className="text-xs text-muted-foreground">Connected Accounts</p>
                <p className="font-medium text-lg">{sections.transactionFlow.accountsConnected}</p>
              </div>
            )}
            {sections.transactionFlow.outgoing && (
              <div>
                <p className="text-xs text-muted-foreground">Outgoing</p>
                <p className="font-medium">{sections.transactionFlow.outgoing}</p>
              </div>
            )}
            {sections.transactionFlow.incoming && (
              <div>
                <p className="text-xs text-muted-foreground">Incoming</p>
                <p className="font-medium">{sections.transactionFlow.incoming}</p>
              </div>
            )}
            {sections.transactionFlow.netFlow && (
              <div>
                <p className="text-xs text-muted-foreground">Net Flow</p>
                <p className={`font-medium ${
                  sections.transactionFlow.netFlow.includes("-") ? "text-red-600" : "text-green-600"
                }`}>
                  {sections.transactionFlow.netFlow}
                </p>
              </div>
            )}
          </div>
          {sections.transactionFlow.patternType && (
            <div className="mt-3">
              <Badge variant="outline" className="mr-2">
                {sections.transactionFlow.patternType}
              </Badge>
              {sections.transactionFlow.patternDescription && (
                <p className="text-sm text-muted-foreground mt-2">
                  {sections.transactionFlow.patternDescription}
                </p>
              )}
            </div>
          )}
        </Card>
      )}

      {/* Fraud Typology & Intelligence */}
      {sections.fraudTypology && (
        <Card className="p-4 border-l-4 border-l-red-500 bg-red-50/50 dark:bg-red-950/20">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <Target className="h-5 w-5 text-red-600" />
            Fraud Intelligence
          </h3>
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {sections.fraudTypology.fraudType && (
                <div>
                  <p className="text-xs text-muted-foreground">Fraud Type</p>
                  <p className="font-semibold text-red-600">{sections.fraudTypology.fraudType}</p>
                </div>
              )}
              {sections.fraudTypology.mlPhase && (
                <div>
                  <p className="text-xs text-muted-foreground">ML Phase</p>
                  <Badge variant="outline">{sections.fraudTypology.mlPhase}</Badge>
                </div>
              )}
              {sections.fraudTypology.priority && (
                <div>
                  <p className="text-xs text-muted-foreground">Investigation Priority</p>
                  <Badge 
                    variant={
                      sections.fraudTypology.priority === "CRITICAL" ? "destructive" : 
                      sections.fraudTypology.priority === "HIGH" ? "default" : "secondary"
                    }
                    className="font-bold"
                  >
                    {sections.fraudTypology.priority}
                  </Badge>
                </div>
              )}
            </div>
            {sections.fraudTypology.indicators && sections.fraudTypology.indicators.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">Key Fraud Indicators</p>
                <ul className="space-y-1">
                  {sections.fraudTypology.indicators.filter(i => i.length > 5).map((indicator, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <span className="text-red-500 mt-0.5">•</span>
                      <span>{indicator}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Regulatory Violations */}
      {sections.regulatoryViolations && sections.regulatoryViolations.length > 0 && (
        <Card className="p-4 border-l-4 border-l-orange-500 bg-orange-50/50 dark:bg-orange-950/20">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <Gavel className="h-5 w-5 text-orange-600" />
            Regulatory Violations Identified
          </h3>
          <ul className="space-y-2">
            {sections.regulatoryViolations.filter(v => v.length > 10).map((violation, i) => (
              <li key={i} className="text-sm flex items-start gap-2 p-2 bg-background rounded">
                <span className="text-orange-500 mt-0.5">•</span>
                <span>{violation}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Required Actions */}
      {sections.requiredActions && sections.requiredActions.length > 0 && (
        <Card className="p-4 border-l-4 border-l-blue-500 bg-blue-50/50 dark:bg-blue-950/20">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <Clock className="h-5 w-5 text-blue-600" />
            Required Actions (with Deadlines)
          </h3>
          <div className="space-y-3">
            {sections.requiredActions.map((action, i) => (
              <div key={i} className="p-3 bg-background rounded-lg border">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="font-medium">{action.action}</p>
                    <div className="flex items-center gap-3 mt-2 text-sm">
                      <span className="text-muted-foreground">
                        Deadline: <span className="font-semibold text-foreground">{action.deadline}</span>
                      </span>
                      {action.priority && (
                        <Badge 
                          size="sm"
                          variant={
                            action.priority === "CRITICAL" ? "destructive" : 
                            action.priority === "HIGH" ? "default" : "secondary"
                          }
                        >
                          {action.priority}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Compliance Checklist */}
      {sections.complianceChecklist && sections.complianceChecklist.length > 0 && (
        <Card className="p-4 border-l-4 border-l-green-500 bg-green-50/50 dark:bg-green-950/20">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <CheckSquare className="h-5 w-5 text-green-600" />
            Compliance Checklist
          </h3>
          <ul className="space-y-2">
            {sections.complianceChecklist.map((item, i) => (
              <li key={i} className="text-sm flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Case Precedents */}
      {sections.casePrecedents && sections.casePrecedents.length > 0 && (
        <Card className="p-4">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Similar SEBI Enforcement Cases
          </h3>
          <div className="space-y-3">
            {sections.casePrecedents.map((case_, i) => (
              <div key={i} className="p-3 bg-muted/50 rounded-lg">
                <p className="font-medium">{case_.name}</p>
                <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Violation</p>
                    <p>{case_.violation}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Outcome</p>
                    <p>{case_.outcome}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Top Transactions */}
      {(sections.topOutgoing.length > 0 || sections.topIncoming.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sections.topOutgoing.length > 0 && (
            <Card className="p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-red-500" />
                Top Outgoing
              </h3>
              <div className="space-y-2">
                {sections.topOutgoing.map((tx, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                    <div className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-red-500" />
                      <span className="text-sm font-medium">Account {tx.account}</span>
                    </div>
                    <span className="text-sm font-semibold text-red-600">{tx.amount}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {sections.topIncoming.length > 0 && (
            <Card className="p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                Top Incoming
              </h3>
              <div className="space-y-2">
                {sections.topIncoming.map((tx, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                    <div className="flex items-center gap-2">
                      <ArrowLeft className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium">Account {tx.account}</span>
                    </div>
                    <span className="text-sm font-semibold text-green-600">{tx.amount}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}

      {/* Risk Assessment */}
      {sections.riskAssessment && (
        <Card className="p-4">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            Risk Assessment
          </h3>
          {sections.riskAssessment.level && (
            <div className="mb-3">
              <p className="text-xs text-muted-foreground mb-1">Risk Level</p>
              <Badge
                variant={
                  sections.riskAssessment.level.includes("CRITICAL")
                    ? "destructive"
                    : sections.riskAssessment.level.includes("HIGH")
                    ? "default"
                    : "secondary"
                }
                className="text-lg px-3 py-1"
              >
                {sections.riskAssessment.level}
              </Badge>
              {sections.riskAssessment.score && (
                <span className="ml-2 text-sm text-muted-foreground">
                  (Score: {sections.riskAssessment.score}/100)
                </span>
              )}
            </div>
          )}
          {sections.riskAssessment.factors && (
            <div className="mb-3">
              <p className="text-xs text-muted-foreground mb-2">Risk Factors</p>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {sections.riskAssessment.factors.split(/[•\n]/).filter(Boolean).map((factor, i) => (
                  <li key={i} className="text-muted-foreground">{factor.trim()}</li>
                ))}
              </ul>
            </div>
          )}
          {sections.riskAssessment.sarFiling && (
            <div>
              <Badge variant="outline" className="font-semibold">
                SAR Filing: {sections.riskAssessment.sarFiling}
              </Badge>
            </div>
          )}
        </Card>
      )}

      {/* Regulatory Context - Always show for regulatory queries */}
      {(sections.regulatoryContext || 
        answer.includes('SEBI REGULATIONS') || 
        answer.includes('REGULATORY CONTEXT') ||
        answer.includes('SEBI regulations') ||
        answer.includes('regulation') && answer.includes('account')) && (
        <Accordion type="single" collapsible className="w-full" defaultValue="regulatory">
          <AccordionItem value="regulatory">
            <AccordionTrigger>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span>Regulatory Context & SEBI Regulations</span>
                {sections.regulatoryContext && (
                  <Badge variant="secondary" className="ml-2">
                    {sections.regulatoryContext.split('\n').filter(l => l.trim().match(/^\d+\./)).length || 'Details'}
                  </Badge>
                )}
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <Card className="p-4 bg-muted/50">
                {sections.regulatoryContext ? (
                  <div className="text-sm whitespace-pre-wrap space-y-3">
                    {/* Parse and format regulation documents */}
                    {sections.regulatoryContext.split(/\n(?=\d+\.|SEBI|Supporting|Similar|\*\*)/).map((section, idx) => {
                      if (section.trim()) {
                        return (
                          <div key={idx} className="pb-3 border-b last:border-0">
                            <p className="whitespace-pre-wrap">{section.trim()}</p>
                          </div>
                        );
                      }
                      return null;
                    })}
                  </div>
                ) : (
                  <div className="text-sm">
                    <p className="text-muted-foreground mb-2">
                      Regulatory information is included in the analysis above. Below is the full answer text:
                    </p>
                    <p className="whitespace-pre-wrap bg-background p-3 rounded border">
                      {answer.substring(0, 2000)}
                      {answer.length > 2000 ? '...' : ''}
                    </p>
                  </div>
                )}
              </Card>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}
    </div>
  );
}

