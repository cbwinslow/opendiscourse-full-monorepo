export interface User {
  id: string;
  username: string;
  email?: string;
  role: 'admin' | 'user' | 'analyst';
  lastLogin?: Date;
}

export interface Document {
  id: string;
  title: string;
  content: string;
  metadata: DocumentMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export interface DocumentMetadata {
  source: string;
  documentType: 'bill' | 'committee_document' | 'legislative' | 'regulation';
  billNumber?: string;
  congressSession?: string;
  committee?: string;
  tags?: string[];
}

export interface RAGQuery {
  query: string;
  maxResults?: number;
  threshold?: number;
  filters?: Record<string, any>;
}

export interface RAGResult {
  answer: string;
  sourceDocuments: Document[];
  query: string;
  timestamp: Date;
  confidenceScore?: number;
}

export interface SearchResult {
  documents: Document[];
  totalCount: number;
  query: string;
  filters?: Record<string, any>;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  requestId?: string;
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  progress?: number;
}

export interface NavigationItem {
  id: string;
  label: string;
  href: string;
  icon?: string;
  children?: NavigationItem[];
}

export interface ThemeConfig {
  colorScheme: 'light' | 'dark' | 'auto';
  primaryColor: string;
  fontSize: 'small' | 'medium' | 'large';
}

export interface AnalyticsEvent {
  event: string;
  path: string;
  timestamp: Date;
  userId?: string;
  metadata?: Record<string, any>;
}