import React, { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingState } from './LoadingComponents';

interface LayoutProps {
  children: ReactNode;
  title?: string;
  showSidebar?: boolean;
}

export function Layout({ children, title, showSidebar = true }: LayoutProps) {
  const { isLoading } = useAuth();

  React.useEffect(() => {
    if (title) {
      document.title = `${title} - OpenDiscourse`;
    }
  }, [title]);

  return (
    <div className="min-h-screen bg-secondary-50 flex">
      {showSidebar && <Sidebar />}
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <LoadingState isLoading={isLoading} error={null}>
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </LoadingState>
      </div>
    </div>
  );
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className="bg-white border-b border-secondary-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-secondary-900">{title}</h1>
          {subtitle && (
            <p className="mt-1 text-sm text-secondary-600">{subtitle}</p>
          )}
        </div>
        {actions && (
          <div className="flex items-center space-x-3">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
}

export function Card({ children, className = '', title, subtitle, actions }: CardProps) {
  return (
    <div className={`card ${className}`}>
      {(title || subtitle || actions) && (
        <div className="flex items-start justify-between mb-4 pb-4 border-b border-secondary-200">
          <div>
            {title && <h3 className="text-lg font-medium text-secondary-900">{title}</h3>}
            {subtitle && <p className="mt-1 text-sm text-secondary-600">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center space-x-2">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
}

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      {icon && (
        <div className="mx-auto h-12 w-12 text-secondary-400 mb-4">
          {icon}
        </div>
      )}
      <h3 className="mt-2 text-sm font-medium text-secondary-900">{title}</h3>
      {description && (
        <p className="mt-1 text-sm text-secondary-500">{description}</p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}