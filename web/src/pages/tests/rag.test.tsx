const { render, screen } = require('@testing-library/react');
import RAGReports from '../rag';

describe('RAG Reports Page', () => {
  it('renders RAG reports and run button', () => {
    render(<RAGReports />);
    expect(screen.getByText('RAG Reports')).toBeInTheDocument();
    expect(screen.getByText('Run Selected Report')).toBeInTheDocument();
  });
});
