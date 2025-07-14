import React from 'react';
import { createRoot } from 'react-dom/client';
import { AuthProvider } from '@/contexts/AuthContext';
import { AuthGuard } from '@/components/Auth';
import { Layout, PageHeader, Card, EmptyState } from '@/components/Layout';
import { useAnalytics } from '@/hooks/useAnalytics';
import './main.css';

function HomePage() {
  useAnalytics();

  const features = [
    {
      title: 'Document Search',
      description: 'Search across government documents with AI-powered semantic search',
      href: '/web/search.html',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
      color: 'bg-blue-500',
    },
    {
      title: 'RAG Interface',
      description: 'Query government documents using AI-powered retrieval and generation',
      href: '/web/rag_interface.html',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      color: 'bg-green-500',
    },
    {
      title: 'Document Viewer',
      description: 'Browse and analyze government documents with advanced search capabilities',
      href: '/web/data_viewer.html',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      color: 'bg-green-500',
    },
    {
      title: 'Entity Viewer',
      description: 'Explore entities and relationships in legislative documents',
      href: '/web/entity_viewer.html',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
      ),
      color: 'bg-purple-500',
    },
    {
      title: 'Script Runner',
      description: 'Execute data processing and analysis scripts in a controlled environment',
      href: '/web/script_runner.html',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
      ),
      color: 'bg-orange-500',
    },
    {
      title: 'Workspace',
      description: 'Collaborative environment for research and analysis projects',
      href: '/web/workspace.html',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
      ),
      color: 'bg-indigo-500',
    },
  ];

  const stats = [
    { label: 'Documents Processed', value: '10,247', change: '+12%' },
    { label: 'RAG Queries', value: '3,891', change: '+8%' },
    { label: 'Active Users', value: '156', change: '+5%' },
    { label: 'Entities Extracted', value: '47,293', change: '+15%' },
  ];

  return (
    <Layout title="OpenDiscourse - Enterprise Platform">
      <PageHeader
        title="Welcome to OpenDiscourse"
        subtitle="Enterprise-grade platform for government document analysis and retrieval"
      />

      <div className="p-6 space-y-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <Card key={index} className="text-center">
              <div className="space-y-2">
                <p className="text-2xl font-bold text-secondary-900">{stat.value}</p>
                <p className="text-sm text-secondary-600">{stat.label}</p>
                <p className="text-xs text-green-600 font-medium">{stat.change} this month</p>
              </div>
            </Card>
          ))}
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer group">
              <a href={feature.href} className="block">
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg ${feature.color} text-white`}>
                    {feature.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-secondary-900 group-hover:text-primary-600 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-secondary-600 mt-1">
                      {feature.description}
                    </p>
                  </div>
                </div>
                <div className="mt-4 flex items-center text-primary-600 text-sm font-medium">
                  <span>Launch Tool</span>
                  <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </a>
            </Card>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="Recent RAG Queries" subtitle="Latest questions and responses">
            <div className="space-y-4">
              {[
                { query: "What is the budget allocation for healthcare?", time: "2 minutes ago" },
                { query: "Find bills related to infrastructure spending", time: "15 minutes ago" },
                { query: "Committee assignments for education policy", time: "1 hour ago" },
              ].map((item, index) => (
                <div key={index} className="flex items-start justify-between py-2">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-secondary-900 line-clamp-1">
                      {item.query}
                    </p>
                    <p className="text-xs text-secondary-500 mt-1">{item.time}</p>
                  </div>
                  <button className="text-primary-600 hover:text-primary-700 text-sm font-medium ml-4">
                    View
                  </button>
                </div>
              ))}
            </div>
          </Card>

          <Card title="System Status" subtitle="Platform health and performance">
            <div className="space-y-4">
              {[
                { service: "RAG Service", status: "Operational", uptime: "99.9%" },
                { service: "Document Processor", status: "Operational", uptime: "99.7%" },
                { service: "Vector Database", status: "Operational", uptime: "99.8%" },
                { service: "API Gateway", status: "Operational", uptime: "99.9%" },
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium text-secondary-900">{item.service}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-green-600 font-medium">{item.status}</p>
                    <p className="text-xs text-secondary-500">{item.uptime} uptime</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card title="Quick Actions" subtitle="Common tasks and shortcuts">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="/web/document_upload.html" className="btn-primary inline-flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Upload Documents
            </a>
            <button className="btn-outline">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              View Analytics
            </button>
            <button className="btn-outline">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Settings
            </button>
          </div>
        </Card>
      </div>
    </Layout>
  );
}

function App() {
  return (
    <AuthProvider>
      <AuthGuard>
        <HomePage />
      </AuthGuard>
    </AuthProvider>
  );
}

// Mount the React app
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<App />);
} else {
  console.error('Root container not found');
}