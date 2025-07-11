import { render, screen } from '@testing-library/react';
import Ingestion from '../ingestion';

describe('Ingestion Page', () => {
  it('renders ingestion status and trigger button', () => {
    render(<Ingestion />);
    expect(screen.getByText('Document Ingestion')).toBeInTheDocument();
    expect(screen.getByText('govinfo.gov:')).toBeInTheDocument();
    expect(screen.getByText('Trigger Ingestion')).toBeInTheDocument();
  });
});
