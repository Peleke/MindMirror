describe('Authentication', () => {
  it('can import auth context without errors', () => {
    expect(() => {
      require('../src/features/auth/context/AuthContext')
    }).not.toThrow()
  })

  it('can import auth hook without errors', () => {
    expect(() => {
      require('../src/features/auth/hooks/useAuthState')
    }).not.toThrow()
  })
}) 