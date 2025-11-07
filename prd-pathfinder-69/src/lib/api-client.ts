/**
 * API Client for Finance Fraud Detection Backend
 * Handles all HTTP requests with authentication and error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
const DEFAULT_API_KEY = import.meta.env.VITE_API_KEY || '';
const STORAGE_KEY = 'finance_fraud_api_key';

const getStorage = () => {
  if (typeof window === 'undefined') return null;
  return window.sessionStorage;
};
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '120000', 10);

export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}

class ApiClient {
  private baseUrl: string;
  private apiKey: string;
  private timeout: number;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.timeout = API_TIMEOUT;

    this.apiKey = DEFAULT_API_KEY;

    if (typeof window !== 'undefined') {
      const storage = getStorage();
      const storedKey = storage?.getItem(STORAGE_KEY) ?? null;
      if (storedKey) {
        this.apiKey = storedKey;
      } else if (window.localStorage) {
        const legacyKey = window.localStorage.getItem(STORAGE_KEY);
        if (legacyKey) {
          this.apiKey = legacyKey;
          storage?.setItem(STORAGE_KEY, legacyKey);
          window.localStorage.removeItem(STORAGE_KEY);
        }
      }
    }
  }

  setApiKey(key: string | null) {
    this.apiKey = key ?? '';
  }

  getApiKey() {
    return this.apiKey;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey,
          'ngrok-skip-browser-warning': 'true',
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
          message: errorData.detail || errorData.message || 'API request failed',
          status: response.status,
          detail: errorData.detail,
        } as ApiError;
      }

      // Handle empty responses (e.g. 204) or non-JSON payloads gracefully
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        return await response.json();
      }

      if (response.status === 204 || response.status === 205) {
        return undefined as T;
      }

      const text = await response.text();
      throw {
        message: 'Unexpected response format from API.',
        status: response.status,
        detail: text?.slice(0, 500),
      } as ApiError;
    } catch (error: any) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw {
          message: 'Request timeout. Please try again.',
          status: 408,
        } as ApiError;
      }

      if (error.message === 'Failed to fetch') {
        throw {
          message: 'Cannot connect to backend. Please ensure the API server is running.',
          status: 0,
        } as ApiError;
      }

      throw error;
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();

export const updateApiClientKey = (key: string | null) => {
  apiClient.setApiKey(key);
  if (typeof window !== 'undefined') {
    const storage = getStorage();
    if (!storage) return;
    if (key) {
      storage.setItem(STORAGE_KEY, key);
    } else {
      storage.removeItem(STORAGE_KEY);
    }
    if (window.localStorage) {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }
};

export const getCurrentApiClientKey = () => apiClient.getApiKey();

