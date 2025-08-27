import React, { useState } from 'react';
import { Layout, PageHeader, Card } from '@/components/Layout';
import { DocumentUpload } from '@/components/DocumentUpload';

export function UploadPage() {
  const [uploadStats, setUploadStats] = useState({
    totalUploaded: 0,
    successfulUploads: 0,
    failedUploads: 0,
    totalSize: 0
  });

  const handleUpload = (files: File[]) => {
    const totalSize = files.reduce((sum, file) => sum + file.size, 0);
    setUploadStats(prev => ({
      ...prev,
      totalUploaded: prev.totalUploaded + files.length,
      totalSize: prev.totalSize + totalSize
    }));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Layout title="Document Upload - OpenDiscourse">
      <PageHeader
        title="Document Upload"
        subtitle="Upload documents for ingestion into the RAG system"
      />

      <div className="p-6 space-y-6">
        {/* Upload Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="text-center">
            <div className="space-y-2">
              <p className="text-2xl font-bold text-secondary-900">{uploadStats.totalUploaded}</p>
              <p className="text-sm text-secondary-600">Total Uploaded</p>
            </div>
          </Card>
          <Card className="text-center">
            <div className="space-y-2">
              <p className="text-2xl font-bold text-green-600">{uploadStats.successfulUploads}</p>
              <p className="text-sm text-secondary-600">Successful</p>
            </div>
          </Card>
          <Card className="text-center">
            <div className="space-y-2">
              <p className="text-2xl font-bold text-red-600">{uploadStats.failedUploads}</p>
              <p className="text-sm text-secondary-600">Failed</p>
            </div>
          </Card>
          <Card className="text-center">
            <div className="space-y-2">
              <p className="text-2xl font-bold text-blue-600">{formatFileSize(uploadStats.totalSize)}</p>
              <p className="text-sm text-secondary-600">Total Size</p>
            </div>
          </Card>
        </div>

        {/* Upload Interface */}
        <Card title="Upload Documents" subtitle="Drag and drop files or click to select">
          <DocumentUpload
            onUpload={handleUpload}
            maxFiles={20}
            maxSize={50 * 1024 * 1024} // 50MB
            acceptedTypes={['.pdf', '.docx', '.txt', '.md', '.html', '.json']}
          />
        </Card>

        {/* Upload Guidelines */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="Supported File Types" subtitle="File formats accepted by the system">
            <div className="space-y-3">
              {[
                { type: 'PDF', description: 'Portable Document Format (.pdf)', icon: '📄' },
                { type: 'Word', description: 'Microsoft Word (.docx)', icon: '📝' },
                { type: 'Text', description: 'Plain text files (.txt)', icon: '📃' },
                { type: 'Markdown', description: 'Markdown documents (.md)', icon: '📋' },
                { type: 'HTML', description: 'Web pages (.html)', icon: '🌐' },
                { type: 'JSON', description: 'Structured data (.json)', icon: '⚙️' },
              ].map((fileType, index) => (
                <div key={index} className="flex items-center space-x-3 p-2">
                  <span className="text-lg">{fileType.icon}</span>
                  <div>
                    <p className="font-medium text-secondary-900">{fileType.type}</p>
                    <p className="text-sm text-secondary-600">{fileType.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Upload Guidelines" subtitle="Best practices for document upload">
            <div className="space-y-4">
              <div className="space-y-2">
                <h4 className="font-medium text-secondary-900">File Size Limits</h4>
                <ul className="text-sm text-secondary-600 space-y-1">
                  <li>• Maximum file size: 50MB per file</li>
                  <li>• Recommended: Under 10MB for faster processing</li>
                  <li>• Batch upload: Up to 20 files at once</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium text-secondary-900">Document Quality</h4>
                <ul className="text-sm text-secondary-600 space-y-1">
                  <li>• Ensure text is machine-readable (not scanned images)</li>
                  <li>• Use clear, descriptive filenames</li>
                  <li>• Include relevant metadata when possible</li>
                </ul>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium text-secondary-900">Processing Time</h4>
                <ul className="text-sm text-secondary-600 space-y-1">
                  <li>• Small files (< 1MB): 10-30 seconds</li>
                  <li>• Medium files (1-10MB): 1-5 minutes</li>
                  <li>• Large files (10-50MB): 5-15 minutes</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Uploads */}
        <Card title="Processing Queue" subtitle="Documents currently being processed">
          <div className="space-y-3">
            {[
              { name: "budget_report_2024.pdf", status: "Processing", progress: 75 },
              { name: "committee_minutes.docx", status: "Queued", progress: 0 },
              { name: "legislation_draft.txt", status: "Completed", progress: 100 },
            ].map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-secondary-900">{item.name}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      item.status === 'Completed' ? 'bg-green-100 text-green-800' :
                      item.status === 'Processing' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {item.status}
                    </span>
                    {item.status === 'Processing' && (
                      <div className="flex-1 bg-secondary-200 rounded-full h-1.5 max-w-24">
                        <div
                          className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${item.progress}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
                <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View
                </button>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </Layout>
  );
}

export default UploadPage;
