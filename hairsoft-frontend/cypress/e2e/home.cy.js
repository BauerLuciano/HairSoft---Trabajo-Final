describe('Página Principal', () => {
  it('Debería cargar el home correctamente', () => {
    cy.visit('/')
    cy.contains('HairSoft').should('be.visible')
  })
})