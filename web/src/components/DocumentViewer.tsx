import React, { useState, useEffect } from 'react';
import { Document, SearchResult } from '@/types';
import { apiClient } from '@/utils/api';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useAnalytics } from '@/hooks/useAnalytics';
import { Card, Layout, PageHeader, EmptyState } from '@/components/Layout';
import { LoadingSpinner, LoadingState } from '@/components/LoadingComponents';

export function DocumentViewer() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loadingState, { setLoading, setError, reset }] = useLoadingState();
  const { trackEvent } = useAnalytics();

  const documentsPerPage = 20;

  useEffect(() => {
    fetchDocuments();
  }, [currentPage]);

  const fetchDocuments = async () => {
    setLoading(true);
    reset();

    try {
      const response = await apiClient.getDocuments(currentPage, documentsPerPage);
      
      if (response.success && response.data) {
        setDocuments(response.data.documents || []);
        setTotalCount(response.data.totalCount || 0);
        trackEvent('documents_loaded', { page: currentPage, count: response.data.documents?.length || 0 });
      } else {
        throw new Error(response.error?.message || 'Failed to fetch documents');
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setError(error instanceof Error ? error.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      fetchDocuments();
      return;
    }

    setLoading(true);
    reset();
    setCurrentPage(1);

    try {
      const response = await apiClient.searchDocuments(searchQuery.trim(), {
        maxResults: documentsPerPage,
      });
      
      if (response.success && response.data) {
        setDocuments(response.data.documents || []);
        setTotalCount(response.data.totalCount || 0);
        trackEvent('documents_searched', { query: searchQuery, results: response.data.documents?.length || 0 });
      } else {
        throw new Error(response.error?.message || 'Search failed');
      }
    } catch (error) {
      console.error('Search failed:', error);
      setError(error instanceof Error ? error.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentSelect = async (document: Document) => {
    setSelectedDocument(document);
    trackEvent('document_selected', { documentId: document.id, source: document.metadata.source });
  };

  const formatDocumentType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const totalPages = Math.ceil(totalCount / documentsPerPage);

  return (
    <Layout title="Document Viewer">
      <PageHeader
        title="Document Viewer"
        subtitle="Browse and search government documents and legislative data"
        actions={
          <div className="flex items-center space-x-3">
            <button className="btn-outline">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z" />
              </svg>
              Filters
            </button>
            <button className="btn-primary">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Upload
            </button>
          </div>
        }
      />

      <div className="flex h-full">
        {/* Document List Panel */}
        <div className="w-1/2 border-r border-secondary-200 flex flex-col">
          {/* Search Bar */}
          <div className="p-6 border-b border-secondary-200">
            <form onSubmit={handleSearch} className="flex space-x-3">
              <div className="flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search documents by title, content, or metadata..."
                  className="input"
                />
              </div>
              <button type="submit" className="btn-primary">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </form>
          </div>

          {/* Document List */}
          <div className="flex-1 overflow-y-auto">
            <LoadingState isLoading={loadingState.isLoading} error={loadingState.error}>
              {documents.length === 0 ? (
                <div className="p-6">
                  <EmptyState
                    icon={
                      <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    }
                    title="No documents found"
                    description={searchQuery ? "Try adjusting your search terms" : "Start by uploading documents or adjusting filters"}
                    action={
                      <button className="btn-primary">
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        Upload Documents
                      </button>
                    }
                  />
                </div>
              ) : (
                <div className="divide-y divide-secondary-200">
                  {documents.map((document) => (
                    <div
                      key={document.id}
                      onClick={() => handleDocumentSelect(document)}
                      className={`p-4 cursor-pointer hover:bg-secondary-50 transition-colors ${
                        selectedDocument?.id === document.id ? 'bg-primary-50 border-r-2 border-primary-600' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium text-secondary-900 truncate">
                            {document.title}
                          </h3>
                          <div className="mt-1 flex items-center space-x-2 text-xs text-secondary-500">
                            <span className="bg-secondary-100 px-2 py-1 rounded">
                              {formatDocumentType(document.metadata.documentType)}
                            </span>
                            {document.metadata.billNumber && (
                              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                {document.metadata.billNumber}
                              </span>
                            )}
                          </div>
                          <p className="mt-1 text-xs text-secondary-600 line-clamp-2">
                            {document.content.substring(0, 150)}...
                          </p>
                        </div>
                        <div className="ml-3 text-xs text-secondary-500">
                          {formatDate(document.updatedAt)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </LoadingState>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="p-4 border-t border-secondary-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-secondary-700">
                  Showing {(currentPage - 1) * documentsPerPage + 1} to {Math.min(currentPage * documentsPerPage, totalCount)} of {totalCount} documents
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    className="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-secondary-700">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Document Detail Panel */}
        <div className="w-1/2 flex flex-col">
          {selectedDocument ? (
            <DocumentDetail document={selectedDocument} />
          ) : (
            <div className="flex-1 flex items-center justify-center p-8">
              <EmptyState
                icon={
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                }
                title="Select a document"
                description="Choose a document from the list to view its details and content"
              />
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

interface DocumentDetailProps {
  document: Document;
}

function DocumentDetail({ document }: DocumentDetailProps) {
  const formatDocumentType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Document Header */}
      <div className="p-6 border-b border-secondary-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-secondary-900 mb-2">
              {document.title}
            </h2>
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="bg-secondary-100 text-secondary-800 px-3 py-1 rounded-full text-sm">
                {formatDocumentType(document.metadata.documentType)}
              </span>
              {document.metadata.billNumber && (
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                  Bill {document.metadata.billNumber}
                </span>
              )}
              {document.metadata.congressSession && (
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                  {document.metadata.congressSession}
                </span>
              )}
              {document.metadata.committee && (
                <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                  {document.metadata.committee}
                </span>
              )}
            </div>
            <div className="text-sm text-secondary-600">
              <p><strong>Source:</strong> {document.metadata.source}</p>
              <p><strong>Created:</strong> {formatDate(document.createdAt)}</p>
              <p><strong>Updated:</strong> {formatDate(document.updatedAt)}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 ml-4">
            <button className="btn-outline">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy
            </button>
            <button className="btn-outline">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Document Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="prose prose-sm max-w-none">
          <div className="whitespace-pre-wrap text-secondary-800 leading-relaxed">
            {document.content}
          </div>
        </div>
      </div>
    </div>
  );
}