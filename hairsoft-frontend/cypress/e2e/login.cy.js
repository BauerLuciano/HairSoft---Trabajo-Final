describe('Login - Admin', () => {
  it('Debería loguearse como admin y ver SweetAlert de bienvenida', () => {
    cy.visit('/login')

    cy.get('input[placeholder="nombre@ejemplo.com"]').type('claudio@gmail.com')
    cy.get('input[placeholder="Ingresá tu contraseña"]').type('Claudio25')
    cy.get('button[type="submit"]').click()

    cy.get('.swal2-title', { timeout: 15000 }).should('contain', '¡Bienvenido!')
    cy.screenshot('01-login-bienvenido')

    cy.url({ timeout: 15000 }).should('include', '/dashboard')
    cy.screenshot('02-dashboard-admin')
  })
})
