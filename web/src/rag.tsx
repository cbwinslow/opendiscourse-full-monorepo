import React from 'react';
import { createRoot } from 'react-dom/client';
import { AuthProvider } from '@/contexts/AuthContext';
import { RAGInterface } from '@/components/RAGInterface';
import './main.css';

function App() {
  return (
    <AuthProvider>
      <RAGInterface />
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