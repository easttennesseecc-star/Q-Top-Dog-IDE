import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../App'

describe('Build UI (simple)', () => {
  beforeEach(() => {
    jest.resetAllMocks()
  })

  it('enqueues a build and opens the build panel', async () => {
    // Mock POST /build/run response
    (globalThis as any).fetch = jest.fn((url: string) => {
      if (url.endsWith('/build/run')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'ok', build_id: 'bid-quick' }) })
      }
      // Default: return an empty build object
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ build: { id: 'bid-quick', status: 'queued', log: '' } }) })
    })

    render(<App />)
    const btn = await screen.findByLabelText('run-build')
    fireEvent.click(btn)

  await waitFor(() => expect((globalThis as any).fetch).toHaveBeenCalled())
  // Build queue badge should appear
  await waitFor(() => expect(screen.getByLabelText('build-queue-count')).toBeInTheDocument())
  // Build panel should open
  await waitFor(() => expect(screen.getByText('Build Queue')).toBeInTheDocument())
  })
})
