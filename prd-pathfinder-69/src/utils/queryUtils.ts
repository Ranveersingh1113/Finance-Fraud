/**
 * Utility functions for query management
 */

const DELETED_QUERIES_STORAGE_KEY = "deleted_queries_by_case";

/**
 * Get deleted query IDs for a specific case from localStorage
 */
export function getDeletedQueryIds(caseId: string): Set<number> {
  try {
    const stored = localStorage.getItem(DELETED_QUERIES_STORAGE_KEY);
    if (stored) {
      const deletedByCase = JSON.parse(stored) as Record<string, number[]>;
      const deletedIds = deletedByCase[caseId] || [];
      return new Set(deletedIds);
    }
  } catch (e) {
    console.error("Failed to load deleted queries:", e);
  }
  return new Set();
}

/**
 * Calculate visible query count for a case
 * Takes backend query_count and subtracts deleted queries from localStorage
 */
export function getVisibleQueryCount(
  caseId: string,
  backendQueryCount: number,
  queries?: Array<{ id: number }>
): number {
  // If we have the queries array, filter them
  if (queries) {
    const deletedIds = getDeletedQueryIds(caseId);
    return queries.filter((q) => !deletedIds.has(q.id)).length;
  }
  
  // Otherwise, try to get deleted count from localStorage
  const deletedIds = getDeletedQueryIds(caseId);
  const deletedCount = deletedIds.size;
  
  // Subtract deleted count from backend count
  // But we need to be careful - if backend count is less than deleted count,
  // something is wrong, so just return backend count
  return Math.max(0, backendQueryCount - deletedCount);
}

