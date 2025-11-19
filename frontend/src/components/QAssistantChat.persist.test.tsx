import { render } from '@testing-library/react';
import { screen, fireEvent, waitFor } from '@testing-library/dom';
import '@testing-library/jest-dom';
import QAssistantChat from './QAssistantChat';

beforeEach(() => {
  // reset fetch mock
  (globalThis as any).fetch = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

test('rolls back optimistic approval on server error', async () => {
  // mock fetch to return error
  (globalThis as any).fetch.mockResolvedValueOnce({
    ok: false,
    json: async () => ({ status: 'error', message: 'boom' })
  });

  render(<QAssistantChat />);
  const approveBtn = screen.getByLabelText('Approve snapshot 1');
  fireEvent.click(approveBtn);

  // optimistic: should show Approved immediately
  const status = screen.getByLabelText('status-1');
  expect(status).toHaveTextContent(/Approved/i);

  // after server error, it should rollback to Pending and show error toast
  await waitFor(() => expect(screen.getByText(/Failed to persist approval/i)).toBeInTheDocument());
  expect(status).toHaveTextContent(/Pending/i);
});
