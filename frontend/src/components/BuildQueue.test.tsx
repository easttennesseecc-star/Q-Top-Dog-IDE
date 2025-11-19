import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import BuildQueue from './BuildQueue'

describe('BuildQueue', () => {
  it('renders empty state and close button', () => {
    const onClose = jest.fn()
    render(<BuildQueue builds={[]} logsMap={{}} onClose={onClose} />)
    expect(screen.getByText('Build Queue')).toBeInTheDocument()
    fireEvent.click(screen.getByLabelText('close-build-panel'))
    expect(onClose).toHaveBeenCalled()
  })

  it('renders builds and allows select', () => {
    const onClose = jest.fn()
    const onSelect = jest.fn()
    const builds = [{ id: 'abc123', status: 'running', log: 'line1\nline2' }]
    render(<BuildQueue builds={builds} logsMap={{}} onClose={onClose} onSelect={onSelect} />)
    expect(screen.getByText(/Build abc123/i)).toBeInTheDocument()
    fireEvent.click(screen.getByLabelText('select-build-abc123'))
    expect(onSelect).toHaveBeenCalledWith('abc123')
  })

  it('copies build id to clipboard when copy clicked', () => {
    const onClose = jest.fn()
    const builds = [{ id: 'abc123', status: 'running', log: 'line1\nline2' }]
    // mock clipboard
    // @ts-ignore
    global.navigator = global.navigator || {}
    // @ts-ignore
    global.navigator.clipboard = { writeText: jest.fn().mockResolvedValue(undefined) }
    render(<BuildQueue builds={builds} logsMap={{}} onClose={onClose} />)
    fireEvent.click(screen.getByLabelText('copy-buildid-abc123'))
    // @ts-ignore
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('abc123')
  })

  it('sends cancel request when cancel clicked', async () => {
    const onClose = jest.fn()
    const builds = [{ id: 'abc123', status: 'running', log: 'line1\nline2' }]
    // mock fetch
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true })
    render(<BuildQueue builds={builds} logsMap={{}} onClose={onClose} />)
    fireEvent.click(screen.getByLabelText('cancel-build-abc123'))
    // modal should appear, confirm cancel
    fireEvent.click(await screen.findByLabelText('confirm-cancel-abc123'))
    // ensure fetch called with expected cancel endpoint
    // @ts-ignore
    expect(fetch).toHaveBeenCalledWith('/build/abc123/cancel', { method: 'POST' })
  })
})
