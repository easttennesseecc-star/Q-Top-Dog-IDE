import React from 'react'
import { render, act } from '@testing-library/react'
import { screen, waitFor } from '@testing-library/dom'
import { useState } from 'react'
import { useBuildPoll } from './useBuildPoll'

function TestComp({ bid, onChunk }: { bid: string; onChunk?: (c: string) => void }) {
  const [b, setB] = useState<any>(null)
  useBuildPoll(bid, setB, (chunk) => {
    if (onChunk) onChunk(chunk)
  })
  return (
    <div>
      <div data-testid="status">{b ? b.status : 'none'}</div>
      <pre data-testid="log">{b ? b.log : ''}</pre>
    </div>
  )
}

describe('useBuildPoll', () => {
  beforeEach(() => {
    jest.useFakeTimers()
    jest.resetAllMocks()
  })
  afterEach(() => {
    jest.useRealTimers()
  })

  it('polls and updates running -> success', async () => {
    // prepare fetch to return running, running, success
    (globalThis as any).fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ build: { id: 'b1', status: 'running', log: 'l1' } }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ build: { id: 'b1', status: 'running', log: 'l1\nline2' } }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ build: { id: 'b1', status: 'success', log: 'done' } }) })

  const chunks: string[] = []
  const onChunk = (c: string) => chunks.push(c)
  render(<TestComp bid="b1" onChunk={onChunk} />)

    // initial immediate poll executed by the hook
    await waitFor(() => expect((globalThis as any).fetch).toHaveBeenCalled())
    // first update should be running
    await waitFor(() => expect(screen.getByTestId('status').textContent).toBe('running'))

    // advance timers to trigger next poll
    await act(async () => {
      jest.advanceTimersByTime(1000)
      // allow promises to resolve
      await Promise.resolve()
    })
    await waitFor(() => expect(screen.getByTestId('status').textContent).toBe('running'))

    // advance again to success
    await act(async () => {
      jest.advanceTimersByTime(1000)
      await Promise.resolve()
    })

    await waitFor(() => expect(screen.getByTestId('status').textContent).toBe('success'))
    expect(screen.getByTestId('log').textContent).toContain('done')
    // onChunk should have been called with incremental updates; final chunk includes 'done'
    expect(chunks.join('')).toContain('done')
  })

  it('polls and updates running -> failed', async () => {
    (globalThis as any).fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ build: { id: 'b2', status: 'running', log: 'working' } }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ build: { id: 'b2', status: 'running', log: 'still' } }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ build: { id: 'b2', status: 'failed', log: 'err' } }) })

  const chunks: string[] = []
  const onChunk = (c: string) => chunks.push(c)
  render(<TestComp bid="b2" onChunk={onChunk} />)
    await waitFor(() => expect((globalThis as any).fetch).toHaveBeenCalled())
    await waitFor(() => expect(screen.getByTestId('status').textContent).toBe('running'))

    await act(async () => { jest.advanceTimersByTime(1000); await Promise.resolve() })
    await act(async () => { jest.advanceTimersByTime(1000); await Promise.resolve() })

    await waitFor(() => expect(screen.getByTestId('status').textContent).toBe('failed'))
    expect(screen.getByTestId('log').textContent).toContain('err')
    expect(chunks.join('')).toContain('err')
  })
})
