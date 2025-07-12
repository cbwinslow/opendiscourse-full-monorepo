import { fireEvent, render, screen } from '@testing-library/react';
import Entities from '../entities';

describe('Entities Page', () => {
  it('renders entity list and details', () => {
    render(<Entities />);
    expect(screen.getByText('Entities')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Jane Doe'));
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('Type: Politician')).toBeInTheDocument();
  });
});
