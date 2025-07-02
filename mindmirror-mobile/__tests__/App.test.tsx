describe('App', () => {
  it('can be imported without errors', () => {
    expect(() => {
      require('../src/App')
    }).not.toThrow()
  })
}) 