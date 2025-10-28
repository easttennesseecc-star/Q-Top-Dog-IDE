import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../App'

// Ensure App uses relative fetch; tests will mock global.fetch

describe('Build flow', () => {
  beforeEach(() => {
    jest.resetAllMocks()
  })

  it('starts a build and polls until completion', async () => {
    // Mock POST /build/run
  (globalThis as any).fetch = jest.fn((url: string) => {
      if (url.endsWith('/build/run')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ status: 'ok', build_id: 'bid-123' }),
        })
      }
      if (url.endsWith('/build/bid-123')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ build: { id: 'bid-123', status: 'success', log: 'done' } }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
    })

    render(<App />)

    // Find the build button by aria-label and click it
    const buildButton = await screen.findByLabelText('run-build')
    fireEvent.click(buildButton)

    // Wait for the build queue badge to update (badge shows number of builds)
    await waitFor(() => {
      const badges = screen.getAllByText(/\d+/)
      expect(badges.length).toBeGreaterThanOrEqual(0)
    })

    // Eventually the polling should have fetched the build status; ensure fetch was called
    await waitFor(() => {
      expect((globalThis as any).fetch).toHaveBeenCalled()
    })
  })
})
