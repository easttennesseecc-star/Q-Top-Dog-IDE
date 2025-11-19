import { render } from '@testing-library/react';
import { screen, fireEvent, waitFor } from '@testing-library/dom';
import '@testing-library/jest-dom';
import QAssistantChat from './QAssistantChat';

beforeEach(() => {
  // mock fetch to succeed for these tests
  (globalThis as any).fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({ status: 'ok' }) });
});

describe('QAssistantChat snapshot actions', () => {
  it('approves a snapshot optimistically and shows a toast', async () => {
    render(<QAssistantChat />);
    const approveBtn = screen.getByLabelText('Approve snapshot 1');
    fireEvent.click(approveBtn);
    // status badge should update immediately
    const status = screen.getByLabelText('status-1');
    expect(status).toHaveTextContent(/Approved/i);
    // toast should appear (persisted)
    await waitFor(() => expect(screen.getByText(/approved and persisted/i)).toBeInTheDocument());
  });

  it('requests change for a snapshot and shows a toast', async () => {
    render(<QAssistantChat />);
    const reqBtn = screen.getByLabelText('Request change for snapshot 2');
    fireEvent.click(reqBtn);
    const status = screen.getByLabelText('status-2');
    expect(status).toHaveTextContent(/Change requested/i);
    await waitFor(() => expect(screen.getByText(/Change requested for snapshot 2/i)).toBeInTheDocument());
  });
});
