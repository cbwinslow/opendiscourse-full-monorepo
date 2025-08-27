const { render, screen } = require('@testing-library/react');
const Ingestion = require('../ingestion').default;

describe('Ingestion Page', () => {
  it('renders ingestion status and trigger button', () => {
    render(<Ingestion />);
    expect(screen.getByText('Document Ingestion')).toBeInTheDocument();
    expect(screen.getByText('govinfo.gov:')).toBeInTheDocument();
    expect(screen.getByText('Trigger Ingestion')).toBeInTheDocument();
  });
});
