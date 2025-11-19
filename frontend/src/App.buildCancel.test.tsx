import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from './App'

describe('App build cancel flow', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })
  afterEach(() => {
    jest.useRealTimers()
    // @ts-ignore
    delete global.fetch
  })

  it('starts a build and cancels it via the BuildQueue cancel action', async () => {
    const fakeId = 'deadbeef'
    // mock fetch to handle /build/run, /build/{id}, and /build/{id}/cancel
    // @ts-ignore
    global.fetch = jest.fn((url, opts) => {
      if (typeof url === 'string' && url.endsWith('/build/run')) {
        return Promise.resolve({ json: () => Promise.resolve({ build_id: fakeId }) })
      }
      if (typeof url === 'string' && url.includes('/build/') && url.endsWith('/cancel')) {
        return Promise.resolve({ ok: true })
      }
      // polling endpoint
      if (typeof url === 'string' && url.includes(`/build/${fakeId}`)) {
        return Promise.resolve({ json: () => Promise.resolve({ id: fakeId, status: 'running', log: '' }) })
      }
      return Promise.resolve({ json: () => Promise.resolve({}) })
    })

    render(<App />)

    // click the Build button
    const buildBtn = screen.getByRole('button', { name: /Build/i })
    fireEvent.click(buildBtn)

    // the badge showing count should appear
    await waitFor(() => expect(screen.getByLabelText('build-queue-count')).toBeInTheDocument())

  // find and click cancel button for the build (opens confirmation)
  const cancelBtn = await screen.findByLabelText(`cancel-build-${fakeId}`)
  fireEvent.click(cancelBtn)
  // confirm the cancel in modal
  const confirm = await screen.findByLabelText(`confirm-cancel-${fakeId}`)
  fireEvent.click(confirm)

  // assert fetch was called for cancel
  // @ts-ignore
  expect(global.fetch).toHaveBeenCalledWith(`/build/${fakeId}/cancel`, { method: 'POST' })

  // UI should reflect cancelling status immediately (optimistic update)
  await screen.findByText(/cancelling/i)
  })
})
