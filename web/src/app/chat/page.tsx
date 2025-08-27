'use client';

import { useState } from 'react';
import { DashboardHeader } from '@/components/dashboard/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Send, MessageSquare, FileText, Lightbulb } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{
    title: string;
    excerpt: string;
    billNumber?: string;
    relevanceScore: number;
  }>;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Simulate API call to RAG endpoint
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Based on the available government documents, here's what I found regarding "${input}":

The Infrastructure Investment and Jobs Act (H.R.3684) addresses many infrastructure-related queries by providing comprehensive funding for roads, bridges, broadband internet, and clean energy initiatives. This legislation represents a significant investment in America's infrastructure needs.

For social programs and climate-related questions, the Build Back Better Act (H.R.5376) contains provisions for expanded healthcare access, childcare support, and environmental protection measures.

This response is generated from analysis of relevant government documents in the database, using semantic search to find the most pertinent information.`,
        timestamp: new Date(),
        sources: [
          {
            title: 'Infrastructure Investment and Jobs Act',
            excerpt: 'This bill provides funding for infrastructure improvements including roads, bridges, broadband, and clean energy...',
            billNumber: 'H.R.3684',
            relevanceScore: 0.95
          },
          {
            title: 'Build Back Better Act',
            excerpt: 'A comprehensive social spending and climate change bill that aims to expand social programs...',
            billNumber: 'H.R.5376',
            relevanceScore: 0.87
          }
        ]
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    "What is the current status of infrastructure spending?",
    "Find information about healthcare policy changes",
    "Show me climate change legislation",
    "What are the latest defense authorization updates?"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <DashboardHeader />
      
      <main className="container mx-auto px-4 py-8 h-[calc(100vh-4rem)]">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100 mb-2">
              RAG Chat Interface
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Query government documents using AI-powered retrieval and generation
            </p>
          </div>

          <div className="flex-1 flex gap-6">
            {/* Chat Area */}
            <div className="flex-1 flex flex-col">
              <Card className="flex-1 flex flex-col">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <MessageSquare className="h-5 w-5 mr-2" />
                    Conversation
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col">
                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto mb-4 space-y-4">
                    {messages.length === 0 ? (
                      <div className="flex items-center justify-center h-full text-slate-500">
                        <div className="text-center">
                          <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                          <p className="mb-2">Start a conversation</p>
                          <p className="text-sm">Ask questions about government documents and legislation</p>
                        </div>
                      </div>
                    ) : (
                      messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-3xl p-4 rounded-lg ${
                              message.type === 'user'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-slate-100 dark:bg-slate-800'
                            }`}
                          >
                            <p className="whitespace-pre-wrap">{message.content}</p>
                            {message.sources && (
                              <div className="mt-4 pt-4 border-t border-slate-300 dark:border-slate-600">
                                <p className="text-sm font-medium mb-2 flex items-center">
                                  <FileText className="h-4 w-4 mr-1" />
                                  Sources
                                </p>
                                <div className="space-y-2">
                                  {message.sources.map((source, index) => (
                                    <div key={index} className="p-2 bg-white dark:bg-slate-900 rounded border">
                                      <div className="flex items-center justify-between mb-1">
                                        <h4 className="text-sm font-medium">{source.title}</h4>
                                        <Badge variant="outline" className="text-xs">
                                          {Math.round(source.relevanceScore * 100)}% match
                                        </Badge>
                                      </div>
                                      {source.billNumber && (
                                        <Badge variant="outline" className="text-xs mr-2">
                                          {source.billNumber}
                                        </Badge>
                                      )}
                                      <p className="text-xs text-slate-600 dark:text-slate-400">
                                        {source.excerpt}
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            <p className="text-xs opacity-70 mt-2">
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-lg">
                          <LoadingSpinner size="sm" />
                          <span className="ml-2 text-sm">AI is thinking...</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Input Area */}
                  <div className="flex items-end space-x-2">
                    <div className="flex-1">
                      <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about government documents, bills, policies..."
                        className="w-full p-3 border border-slate-300 rounded-lg resize-none focus:ring-2 focus:ring-primary focus:border-transparent"
                        rows={3}
                        disabled={isLoading}
                      />
                    </div>
                    <Button
                      onClick={handleSendMessage}
                      disabled={!input.trim() || isLoading}
                      className="h-[72px]"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="w-80 space-y-6">
              {/* Quick Questions */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Lightbulb className="h-5 w-5 mr-2" />
                    Quick Questions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {quickQuestions.map((question, index) => (
                      <button
                        key={index}
                        onClick={() => setInput(question)}
                        className="w-full text-left p-3 text-sm bg-slate-50 hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 rounded-lg transition-colors"
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Chat History */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Conversations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-sm text-slate-500">No previous conversations</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}