describe('Reserva de Turno - Camino Feliz (Cliente)', () => {
  it('Debería completar la reserva como cliente y ver historial', () => {
    cy.visit('/login')

    cy.get('input[placeholder="nombre@ejemplo.com"]').type('lucianobauer13@gmail.com')
    cy.get('input[placeholder="Ingresá tu contraseña"]').type('Luciano25')
    cy.get('button[type="submit"]').click()

    cy.get('.swal2-title', { timeout: 15000 }).should('contain', '¡Bienvenido!')
    cy.screenshot('05a-login-cliente-exitoso')

    cy.url({ timeout: 15000 }).should('include', '/dashboard')
    cy.screenshot('05b-dashboard-cliente')

    cy.visit('/turnos/crear-web')
    cy.contains('Reservar Turno Online', { timeout: 15000 }).should('be.visible')
    cy.screenshot('05c-crear-web-cargado')

    cy.get('[data-cy^="cat-"]', { timeout: 10000 }).first().click()
    cy.wait(500)

    cy.get('[data-cy^="serv-"]', { timeout: 10000 }).first().click()
    cy.wait(500)

    cy.get('[data-cy^="pel-"]', { timeout: 10000 }).first().click()
    cy.wait(500)

    cy.get('.day-btn:not(.day-disabled)', { timeout: 10000 }).first().click()
    cy.wait(1500)

    cy.get('[data-cy^="hora-"]', { timeout: 10000 }).first().click()
    cy.wait(500)

    cy.get('[data-cy="pago-total"]', { timeout: 5000 }).click()
    cy.wait(500)

    cy.intercept('POST', 'http://localhost:8000/api/turnos/crear/', {
      statusCode: 201,
      body: { status: 'ok', turno_id: 999, mp_data: null }
    }).as('crearTurno')

    cy.get('[data-cy="btn-confirmar"]', { timeout: 10000 }).click()

    cy.wait('@crearTurno', { timeout: 15000 })
    cy.url({ timeout: 15000 }).should('include', '/cliente/historial')
    cy.screenshot('05d-historial-turno-creado')
  })
})
