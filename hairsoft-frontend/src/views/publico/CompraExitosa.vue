<template>
  <div class="success-container">
    <div class="card-success">
      <div class="icon-circle">
        <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </div>
      <h1>¡Gracias por tu compra!</h1>
      <p>Tu pago se procesó correctamente.</p>
      <p class="info-text">
        Estamos preparando tu pedido. Podés ver el estado en tu perfil.
      </p>
      
      <div class="actions">
        <router-link to="/client/dashboard" class="btn-primary">Ir a Mis Pedidos</router-link>
        <router-link to="/productos" class="btn-secondary">Seguir Comprando</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.success-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
  padding: 20px;
}
.card-success {
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  max-width: 500px;
  width: 100%;
}
.icon-circle {
  width: 80px;
  height: 80px;
  background: #2ecc71;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}
h1 { color: #2c3e50; margin-bottom: 10px; }
.info-text { color: #7f8c8d; margin-bottom: 30px; }
.actions { display: flex; gap: 15px; justify-content: center; }
.btn-primary, .btn-secondary {
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
}
.btn-primary { background: #2ecc71; color: white; }
.btn-secondary { background: #ecf0f1; color: #2c3e50; }
</style>