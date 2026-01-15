describe('Módulo de Autenticación - HairSoft', () => {
  
  beforeEach(() => {
    cy.visit('/login') 
  })

  it('CP-UI-001: Debería mostrar error de SweetAlert con credenciales falsas', () => {
    cy.get('input[placeholder="nombre@ejemplo.com"]').type('error@test.com')
    cy.get('input[placeholder="Ingresá tu contraseña"]').type('123456')
    cy.get('button[type="submit"]').click()

    cy.get('.swal2-popup', { timeout: 10000 }).should('be.visible')
    cy.get('.swal2-title').should('contain', 'Error')
  })

  it('CP-UI-002: Login exitoso como Administrador (Claudio) y redirección', () => {
    cy.get('input[placeholder="nombre@ejemplo.com"]').type('claudio@gmail.com')
    cy.get('input[placeholder="Ingresá tu contraseña"]').type('Claudio25')
    cy.get('button[type="submit"]').click()

    cy.get('.swal2-title', { timeout: 10000 }).should('contain', '¡Bienvenido!')
    cy.url({ timeout: 5000 }).should('include', '/dashboard')
    cy.contains(/Dashboard|Panel de Control|Resumen/i).should('be.visible')
  })

  it('CP-UI-003: Login exitoso como Cliente (Luciano) y ruta específica', () => {
    // Credenciales de Luciano
    cy.get('input[placeholder="nombre@ejemplo.com"]').type('lucianobauer13@gmail.com')
    cy.get('input[placeholder="Ingresá tu contraseña"]').type('123456')
    cy.get('button[type="submit"]').click()

    cy.get('.swal2-title', { timeout: 10000 }).should('contain', '¡Bienvenido!')

    // Verificamos que el router te mandó a la zona de clientes
    cy.url({ timeout: 5000 }).should('include', '/cliente/dashboard')
    
    // Verificamos que se vea algo propio del cliente (Mis Turnos, Reservar, etc.)
    cy.contains(/Mis Turnos|Reservar|Panel|Cliente/i).should('be.visible')
  })

  it('CP-UI-004: Validación visual del campo contraseña (Ojo)', () => {
    cy.get('input[placeholder="Ingresá tu contraseña"]').as('passInput').type('Prueba123')
    cy.get('@passInput').should('have.attr', 'type', 'password')
    cy.get('.toggle-btn').click()
    cy.get('@passInput').should('have.attr', 'type', 'text')
  })
})