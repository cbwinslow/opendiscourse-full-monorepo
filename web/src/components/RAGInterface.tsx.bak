import React, { useState, useRef, useEffect } from 'react';
import { RAGResult, Document } from '@/types';
import { apiClient } from '@/utils/api';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useAnalytics } from '@/hooks/useAnalytics';
import { Card, Layout, PageHeader } from '@/components/Layout';
import { LoadingSpinner, ProgressBar } from '@/components/LoadingComponents';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Document[];
}

export function RAGInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentQuery, setCurrentQuery] = useState('');
  const [loadingState, { setLoading, setError, reset }] = useLoadingState();
  const { trackEvent } = useAnalytics();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentQuery.trim() || loadingState.isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: currentQuery.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentQuery('');
    setLoading(true);
    reset();

    trackEvent('rag_query_submitted', { query_length: currentQuery.length });

    try {
      const response = await apiClient.ragQuery(currentQuery.trim());
      
      if (response.success && response.data) {
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          type: 'assistant',
          content: response.data.answer || 'I apologize, but I couldn\'t generate a response.',
          timestamp: new Date(),
          sources: response.data.source_documents || [],
        };

        setMessages(prev => [...prev, assistantMessage]);
        trackEvent('rag_query_completed', { 
          sources_count: assistantMessage.sources?.length || 0,
          response_length: assistantMessage.content.length 
        });
      } else {
        throw new Error(response.error?.message || 'Failed to get response');
      }
    } catch (error) {
      console.error('RAG query failed:', error);
      setError(error instanceof Error ? error.message : 'Query failed');
      trackEvent('rag_query_failed', { error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    trackEvent('rag_conversation_cleared');
  };

  const exampleQueries = [
    "What is the main purpose of this legislation?",
    "Summarize the key provisions of recent bills",
    "What committees are involved in healthcare legislation?",
    "Find documents related to budget appropriations",
  ];

  return (
    <Layout title="RAG Interface">
      <PageHeader
        title="RAG Interface"
        subtitle="Query government documents using AI-powered retrieval and generation"
        actions={
          <button
            onClick={clearConversation}
            className="btn-outline"
            disabled={messages.length === 0}
          >
            Clear Conversation
          </button>
        }
      />

      <div className="flex-1 flex flex-col h-full">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <Card className="max-w-2xl mx-auto">
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-secondary-900 mb-2">
                  Start a conversation
                </h3>
                <p className="text-secondary-600 mb-6">
                  Ask questions about government documents and legislation. Try one of these examples:
                </p>
                <div className="grid gap-2">
                  {exampleQueries.map((query, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentQuery(query)}
                      className="text-left p-3 bg-secondary-50 hover:bg-secondary-100 rounded-lg transition-colors text-sm text-secondary-700"
                    >
                      "{query}"
                    </button>
                  ))}
                </div>
              </div>
            </Card>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {loadingState.isLoading && (
                <div className="flex items-center justify-center py-4">
                  <LoadingSpinner className="mr-2" />
                  <span className="text-secondary-600">Generating response...</span>
                </div>
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-secondary-200 bg-white p-6">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-4">
              <div className="flex-1">
                <textarea
                  ref={inputRef}
                  value={currentQuery}
                  onChange={(e) => setCurrentQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a question about government documents..."
                  className="input resize-none"
                  rows={3}
                  disabled={loadingState.isLoading}
                />
                {loadingState.error && (
                  <p className="mt-2 text-sm text-red-600">{loadingState.error}</p>
                )}
              </div>
              <button
                type="submit"
                disabled={!currentQuery.trim() || loadingState.isLoading}
                className="btn-primary h-fit"
              >
                {loadingState.isLoading ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}

interface MessageBubbleProps {
  message: Message;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.type === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-3xl ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-lg p-4 ${
            isUser
              ? 'bg-primary-600 text-white'
              : 'bg-white border border-secondary-200'
          }`}
        >
          <div className="prose prose-sm max-w-none">
            <p className={isUser ? 'text-white' : 'text-secondary-900'}>
              {message.content}
            </p>
          </div>
          
          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-4 border-t border-secondary-200">
              <p className="text-xs font-medium text-secondary-600 mb-2">
                Sources ({message.sources.length}):
              </p>
              <div className="space-y-2">
                {message.sources.slice(0, 3).map((source, index) => (
                  <div key={index} className="text-xs bg-secondary-50 rounded p-2">
                    <p className="font-medium text-secondary-700">
                      {source.metadata?.source || 'Unknown Source'}
                    </p>
                    <p className="text-secondary-600 mt-1 line-clamp-2">
                      {source.content.substring(0, 150)}...
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <div className={`mt-1 text-xs text-secondary-500 ${isUser ? 'text-right' : 'text-left'}`}>
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}