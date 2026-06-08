const { defineConfig } = require("cypress");

module.exports = defineConfig({
  chromeWebSecurity: false,
  e2e: {
    baseUrl: 'http://localhost:5173',
    // 🚨 ACÁ ESTÁ EL TRUCO: Le decimos que busque SOLO en tu carpeta e2e
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    // 🚨 Le prohibimos expresamente que muestre los ejemplos de Cypress
    excludeSpecPattern: ['**/1-getting-started/**', '**/2-advanced-examples/**'],
    supportFile: false
  },
});