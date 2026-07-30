import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from './auth'

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      accessToken: null,
      csrfToken: null,
      user: null,
      unverifiedEmail: null,
      verifiedEmail: null,
    })
  })

  it('should initialize with null state', () => {
    const state = useAuthStore.getState()
    expect(state.accessToken).toBeNull()
    expect(state.csrfToken).toBeNull()
    expect(state.user).toBeNull()
  })

  it('should set auth tokens and user', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      name: 'Test User',
      role: 'ADMIN',
      is_active: true,
      is_verified: true,
    }

    useAuthStore.getState().setAuth('access-token', 'csrf-token', mockUser)

    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('access-token')
    expect(state.csrfToken).toBe('csrf-token')
    expect(state.user).toEqual(mockUser)
  })

  it('should clear state on logout', () => {
    useAuthStore.setState({
      accessToken: 'access',
      csrfToken: 'csrf',
      user: {
        id: '123',
        email: 'test@example.com',
        role: 'USER',
        is_active: true,
        is_verified: true,
      },
    })

    useAuthStore.getState().logout()

    const state = useAuthStore.getState()
    expect(state.accessToken).toBeNull()
    expect(state.csrfToken).toBeNull()
    expect(state.user).toBeNull()
  })
})
