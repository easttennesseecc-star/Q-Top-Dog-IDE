
import { render } from '@testing-library/react';
import { screen } from '@testing-library/dom';
import '@testing-library/jest-dom';
import App from './App';

describe('App', () => {
  it('renders build health dashboard with all key statuses', () => {
    render(<App />);
    // Updated assertions to match current UI
  expect(screen.getByText(/Build Health:/i)).toBeInTheDocument();
  // The header includes quick status indicators labelled Build/Tests/AI — use aria-labels
  expect(screen.getAllByLabelText(/Build/i).length).toBeGreaterThan(0);
  expect(screen.getByLabelText(/Tests/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/AI/i)).toBeInTheDocument();
  });

  it('renders AI Assistant and new Workflow/Plugin Dock placeholders', () => {
    render(<App />);
  // The main assistant panel is titled 'Q Assistant' (may appear multiple times)
  const assistantEls = screen.getAllByText(/Q Assistant/i);
  expect(assistantEls.length).toBeGreaterThan(0);
  // Tab buttons are rendered inside the assistant header
  expect(screen.getByRole('button', { name: /Workflow/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Plugins/i })).toBeInTheDocument();
  });
});
