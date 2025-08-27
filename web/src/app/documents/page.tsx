import { Metadata } from 'next';
import { Suspense } from 'react';
import { DashboardHeader } from '@/components/dashboard/header';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, Upload, Filter, Download } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Document Library',
  description: 'Browse and manage your political document collection with advanced search and filtering.',
};

// Mock data for demonstration
const mockDocuments = [
  {
    id: '1',
    title: 'Infrastructure Investment and Jobs Act',
    excerpt: 'This bill provides funding for infrastructure improvements including roads, bridges, broadband, and clean energy...',
    type: 'Bill',
    billNumber: 'H.R.3684',
    session: '117th Congress',
    date: '2021-11-15',
    tags: ['infrastructure', 'transportation', 'broadband'],
    status: 'Enacted'
  },
  {
    id: '2',
    title: 'Build Back Better Act',
    excerpt: 'A comprehensive social spending and climate change bill that aims to expand social programs and combat climate change...',
    type: 'Bill',
    billNumber: 'H.R.5376',
    session: '117th Congress',
    date: '2021-11-19',
    tags: ['climate', 'social programs', 'healthcare'],
    status: 'Introduced'
  },
  {
    id: '3',
    title: 'Defense Authorization Act 2024',
    excerpt: 'Annual defense spending authorization covering military operations, personnel, and equipment procurement...',
    type: 'Bill',
    billNumber: 'H.R.2670',
    session: '118th Congress',
    date: '2023-12-22',
    tags: ['defense', 'military', 'budget'],
    status: 'Enacted'
  }
];

export default function DocumentsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <DashboardHeader />
      
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
                Document Library
              </h1>
              <p className="text-slate-600 dark:text-slate-400">
                Browse and manage your political document collection
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload
              </Button>
            </div>
          </div>

          {/* Search Bar */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search documents by title, content, bill number, or keywords..."
                    className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
                <Button>
                  Search
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Documents Grid */}
          <Suspense fallback={<LoadingSpinner />}>
            <div className="grid gap-6">
              {mockDocuments.map((doc) => (
                <Card key={doc.id} className="hover:shadow-lg transition-all duration-200">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <CardTitle className="text-xl">{doc.title}</CardTitle>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{doc.type}</Badge>
                          <Badge variant="outline">{doc.billNumber}</Badge>
                          <Badge variant={doc.status === 'Enacted' ? 'default' : 'secondary'}>
                            {doc.status}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="ghost" size="sm">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-slate-600 dark:text-slate-400 mb-4">
                      {doc.excerpt}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm text-slate-500">
                        <span>{doc.session}</span>
                        <span>•</span>
                        <span>{new Date(doc.date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {doc.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                        <Button variant="outline" size="sm">
                          RAG Query
                        </Button>
                        <Button variant="outline" size="sm">
                          Analyze
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </Suspense>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Showing 3 of 247 documents
            </p>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" disabled>
                Previous
              </Button>
              <Button variant="outline" size="sm">
                Next
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}