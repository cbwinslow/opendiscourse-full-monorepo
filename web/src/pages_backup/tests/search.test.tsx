const { fireEvent, render, screen } = require('@testing-library/react');
import Search from '../search';

describe('Search Page', () => {
  it('renders search input and results', () => {
    render(<Search />);
    expect(screen.getByPlaceholderText('Search for people, committees, or documents...')).toBeInTheDocument();
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
  });

  it('filters results based on query', () => {
    render(<Search />);
    const input = screen.getByPlaceholderText('Search for people, committees, or documents...');
    fireEvent.change(input, { target: { value: 'finance' } });
    fireEvent.click(screen.getByText('Search'));
    expect(screen.getByText('Committee on Finance')).toBeInTheDocument();
    expect(screen.queryByText('Jane Doe')).not.toBeInTheDocument();
  });
});
