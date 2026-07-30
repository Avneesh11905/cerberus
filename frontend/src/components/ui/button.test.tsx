import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './button'

describe('Button component', () => {
  it('renders correctly with children', () => {
    render(<Button>Click me</Button>)
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeInTheDocument()
  })

  it('handles click events', () => {
    let clicked = false
    render(<Button onClick={() => (clicked = true)}>Click me</Button>)

    const button = screen.getByRole('button', { name: /click me/i })
    fireEvent.click(button)

    expect(clicked).toBe(true)
  })

  it('can be disabled', () => {
    render(<Button disabled>Click me</Button>)
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeDisabled()
  })
})
