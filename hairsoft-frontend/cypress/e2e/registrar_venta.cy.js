describe('Registrar Venta', () => {
  it('Debería registrar una venta exitosamente', () => {
    cy.visit('/login')

    cy.get('input[placeholder="nombre@ejemplo.com"]').type('claudio@gmail.com')
    cy.get('input[placeholder="Ingresá tu contraseña"]').type('Claudio25')
    cy.get('button[type="submit"]').click()

    cy.get('.swal2-title', { timeout: 15000 }).should('contain', '¡Bienvenido!')
    cy.screenshot('05a-login-exitoso')

    cy.url({ timeout: 15000 }).should('include', '/dashboard')
    cy.screenshot('05b-dashboard-admin')

    cy.intercept('GET', 'http://127.0.0.1:8000/api/estado-caja/', {
      body: { abierta: true }
    })

    cy.visit('/ventas/crear')
    cy.contains('Nueva Venta', { timeout: 15000 }).should('be.visible')
    cy.screenshot('05c-venta-cargada')

    cy.get('.producto-item:not(.producto-sin-stock)', { timeout: 10000 }).first().within(() => {
      cy.get('.input-cantidad').clear({ force: true }).type('1')
      cy.get('.btn-agregar').click({ force: true })
    })
    cy.screenshot('05d-producto-agregado')

    cy.intercept('POST', 'http://127.0.0.1:8000/api/ventas/registrar/', {
      statusCode: 201,
      body: { id: 999, total: 1500.0 }
    }).as('registrarVenta')

    cy.get('.btn-confirmar', { timeout: 10000 }).click()

    cy.wait('@registrarVenta', { timeout: 15000 })

    cy.get('.swal2-title', { timeout: 10000 }).should('contain', '¡Venta Registrada Exitosamente!')
    cy.screenshot('05e-venta-exitosa')

    cy.get('.swal2-cancel', { timeout: 5000 }).click()

    cy.url({ timeout: 10000 }).should('include', '/ventas')
    cy.screenshot('05f-listado-ventas')
  })
})
