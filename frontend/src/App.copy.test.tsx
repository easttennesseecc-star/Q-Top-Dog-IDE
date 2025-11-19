import React from 'react'
import { render } from '@testing-library/react'
import { screen, fireEvent, waitFor } from '@testing-library/dom'
import '@testing-library/jest-dom'
import App from './App'

describe('App copy build id toast', () => {
  afterEach(() => {
    // @ts-ignore
    delete global.fetch
  })

  it('shows a Copied toast when build id is copied', async () => {
    const fakeId = 'cafebabe'
    // mock fetch to handle /build/run and polling
    // @ts-ignore
    global.fetch = jest.fn((url, opts) => {
      if (typeof url === 'string' && url.endsWith('/build/run')) {
        return Promise.resolve({ json: () => Promise.resolve({ build_id: fakeId }) })
      }
      if (typeof url === 'string' && url.includes(`/build/${fakeId}`)) {
        return Promise.resolve({ json: () => Promise.resolve({ id: fakeId, status: 'running', log: '' }) })
      }
      return Promise.resolve({ json: () => Promise.resolve({}) })
    })

    // mock clipboard
    // @ts-ignore
    global.navigator = global.navigator || {}
    // @ts-ignore
    global.navigator.clipboard = { writeText: jest.fn().mockResolvedValue(undefined) }

    render(<App />)

    // click the Build button
    const buildBtn = screen.getByRole('button', { name: /Build/i })
    fireEvent.click(buildBtn)

    // wait for queue badge
    await waitFor(() => expect(screen.getByLabelText('build-queue-count')).toBeInTheDocument())

    // click the copy button
    const copyBtn = await screen.findByLabelText(`copy-buildid-${fakeId}`)
    fireEvent.click(copyBtn)

    // toast should appear with Copied
    await waitFor(() => expect(screen.getByText(new RegExp(`Copied ${fakeId.slice(0,6)}`))).toBeInTheDocument())
  })
})
