/**
 * TypeScript type definitions for API responses
 */

// Query & Search Types
export interface QueryRequest {
  query: string;
  n_results?: number;
  include_metadata?: boolean;
}

export interface Evidence {
  rank: number;
  score: number;
  document: string;
  source: string;
  metadata: Record<string, any>;
}

export interface QueryResponse {
  query: string;
  answer: string;
  confidence_score: number;
  query_type: string;
  processing_time: number;
  evidence: Evidence[];
  metadata: {
    model_used: string;
    graphs_loaded: boolean;
    pattern_cache_used: boolean;
    cross_domain_matches: number;
    sebi_entities_found: number;
    amlsim_patterns_found: number;
  };
}

// Case Types
export interface Case {
  case_id: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  analyst: string;
  status: 'active' | 'under_review' | 'closed' | 'archived';
  tags: string[];
  created_at: string;
  updated_at: string;
  queries?: Query[];
  query_count?: number;
}

export interface CreateCaseRequest {
  case_id?: string; // Optional - will be auto-generated if not provided
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  analyst?: string; // Optional - defaults to current user
  tags?: string[];
}

export interface CaseResponse {
  case_id: string;
  status: string;
  created_at: string;
  message: string;
}

export interface Query {
  id: number;
  case_id: string;
  query: string;
  answer: string;
  confidence_score: number;
  query_type: string;
  processing_time: number;
  timestamp: string;
}

// SAR Types
export interface SARReport {
  id: number;
  case_id: string;
  report_content: string;
  generated_at: string;
  analyst: string;
  status: 'draft' | 'submitted' | 'approved';
}

export interface SARResponse {
  case_id: string;
  sar_id: number;
  report_content: string;
  confidence: number;
  generated_at: string;
  status: string;
}

// Statistics Types
export interface SystemStats {
  system_status: string;
  rag_engine_stats: {
    total_documents: number;
    sebi_document_count: number;
    transaction_count: number;
    case_statistics: {
      total_cases: number;
      active_cases: number;
      closed_cases: number;
      total_queries: number;
        queries_today?: number;
      average_queries_per_case: number;
      priority_breakdown: {
        critical: number;
        high: number;
        medium: number;
        low: number;
      };
    };
  };
  timestamp: string;
}

// Health Check Types
export interface HealthResponse {
  status: string;
  version: string;
  models_available: {
    ollama_llama: boolean;
    bge_reranker: boolean;
    embedding_model: string;
    claude_3_5_haiku: boolean;
  };
  database_stats: {
    total_documents: number;
  };
}

// User Types
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar_url?: string | null;
  department?: string | null;
  joined_date?: string | null;
}

