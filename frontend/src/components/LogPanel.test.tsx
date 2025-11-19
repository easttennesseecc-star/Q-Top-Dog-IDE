import React from 'react'
import { render } from '@testing-library/react'
import { screen } from '@testing-library/dom'
import LogPanel from './LogPanel'

describe('LogPanel', () => {
  it('renders no logs message', () => {
    render(<LogPanel lines={[]} />)
    expect(screen.getByText(/No logs yet/i)).toBeInTheDocument()
  })

  it('renders given log lines', () => {
    const lines = ['first line', 'second line']
    render(<LogPanel lines={lines} />)
    expect(screen.getByTestId('log-line-0').textContent).toBe('first line')
    expect(screen.getByTestId('log-line-1').textContent).toBe('second line')
  })
})
