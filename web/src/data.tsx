import React from 'react';
import { createRoot } from 'react-dom/client';
import { AuthProvider } from '@/contexts/AuthContext';
import { AuthGuard } from '@/components/Auth';
import { DocumentViewer } from '@/components/DocumentViewer';
import './main.css';

function App() {
  return (
    <AuthProvider>
      <AuthGuard>
        <DocumentViewer />
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