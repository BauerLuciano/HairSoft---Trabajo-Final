describe('Página Principal', () => {
  it('Debería cargar el home correctamente', () => {
    cy.visit('/')
    cy.url().should('include', '/web/home')
    cy.get('.hero-title', { timeout: 15000 }).should('exist')
  })
})
