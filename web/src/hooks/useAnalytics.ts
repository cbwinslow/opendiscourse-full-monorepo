import { useEffect } from 'react';
import { apiClient } from '@/utils/api';

export function useAnalytics() {
  const trackEvent = (event: string, metadata?: Record<string, any>) => {
    apiClient.analytics().track(event, metadata);
  };

  const trackPageView = () => {
    trackEvent('page_view', {
      path: window.location.pathname,
      referrer: document.referrer,
    });
  };

  useEffect(() => {
    trackPageView();
  }, []);

  return {
    trackEvent,
    trackPageView,
  };
}