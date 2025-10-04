<template>
  <div class="form-container">
    <div class="form-card">
      <h1 class="form-title">Registrar Usuario</h1>
      <p class="form-subtitle">Completa los datos del usuario</p>

      <form @submit.prevent="crearUsuario" class="form-grid">
        <!-- Nombre -->
        <div class="input-group">
          <input 
            type="text"
            v-model="form.nombre"
            class="input-field"
            placeholder="Nombre (*)"
            required
          />
        </div>

        <!-- Apellido -->
        <div class="input-group">
          <input 
            type="text"
            v-model="form.apellido"
            class="input-field"
            placeholder="Apellido (*)"
            required
          />
        </div>

        <!-- DNI -->
        <div class="input-group">
          <input 
            type="text"
            v-model="form.dni"
            class="input-field"
            placeholder="DNI (*)"
            required
          />
        </div>

        <!-- Teléfono -->
        <div class="input-group">
          <input 
            type="text"
            v-model="form.telefono"
            class="input-field"
            placeholder="Teléfono"
          />
        </div>

        <!-- Correo -->
        <div class="input-group">
          <input 
            type="email"
            v-model="form.correo"
            class="input-field"
            placeholder="Correo (*)"
            required
          />
        </div>

        <!-- Rol -->
        <div class="input-group">
          <select v-model="form.rol" class="input-field" required>
            <option value="">Seleccionar rol (*)</option>
            <option value="admin">Admin</option>
            <option value="peluquero">Peluquero</option>
            <option value="cliente">Cliente</option>
          </select>
        </div>

        <!-- Botón Guardar -->
        <div class="input-group full-width">
          <button type="submit" class="submit-button">Guardar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        nombre: '',
        apellido: '',
        dni: '',
        telefono: '',
        correo: '',
        rol: ''
      }
    };
  },
  methods: {
    async crearUsuario() {
      try {
        const res = await fetch('http://localhost:8000/usuarios/api/usuarios/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });

        if (res.ok) {
          alert('Usuario registrado con éxito');
          this.form = { nombre: '', apellido: '', dni: '', telefono: '', correo: '', rol: '' };
          this.$router.push('/usuarios'); // opcional: volver a listado si tienes ruta
        } else {
          alert('Error al registrar usuario');
        }
      } catch (error) {
        console.error(error);
        alert('Error de conexión con el servidor');
      }
    }
  }
};
</script>

<style scoped>
/* Reset general */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;

  .input-group {
  position: relative; /* IMPORTANTE para que los íconos absolutos se posicionen respecto al input */
}

.input-field {
  width: 100%;
  padding: 18px 50px 18px 22px; /* Dejamos espacio a la derecha para los íconos */
  font-size: 16px;
  border-radius: 16px;
  border: 1.5px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.input-icon {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: white;
  font-size: 20px;
}

.input-icon.lupa {
  right: 40px; /* un poco a la izquierda del borde derecho */
}
}

.input-icon.agregar-cliente {
  right: 10px; /* pegado al borde derecho */
}

/* Contenedor principal - FONDO OSCURO */
.form-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 60px 20px;
  background: #0a0a0a;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  position: relative;
  overflow: hidden;
}

.form-container::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 153, 255, 0.15) 0%, transparent 70%);
  top: -200px;
  left: -200px;
  animation: float 20s ease-in-out infinite;
}

.form-container::after {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(138, 43, 226, 0.15) 0%, transparent 70%);
  bottom: -150px;
  right: -150px;
  animation: float 15s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

/* Tarjeta del formulario */
.form-card {
  background: rgba(20, 20, 20, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 32px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.8),
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
  padding: 70px 90px;
  width: 100%;
  max-width: 1100px;
  position: relative;
  overflow: visible;
  z-index: 10;
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent,
    #0099ff 25%,
    #00d4ff 50%,
    #0099ff 75%,
    transparent
  );
  animation: borderGlow 4s linear infinite;
}

@keyframes borderGlow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Título */
.form-title {
  text-align: center;
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 15px;
  line-height: 1.2;
  letter-spacing: -1px;
}

/* Subtítulo */
.form-subtitle {
  text-align: center;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 50px;
  line-height: 1.5;
  font-weight: 400;
}

/* Grid para inputs */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 40px;
}

.full-width {
  grid-column: span 2;
}

/* Grupo de input */
.input-group {
  position: relative;
}

/* Inputs y selects */
.input-field {
  width: 100%;
  padding: 18px 22px;
  font-size: 16px;
  border: 1.5px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-weight: 500;
}

.input-field:focus {
  outline: none;
  border-color: rgba(0, 153, 255, 0.6);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 153, 255, 0.2),
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.input-field::placeholder {
  color: rgba(255, 255, 255, 0.3);
  font-size: 15px;
  font-weight: 400;
}

/* Select específico */
select.input-field {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='rgba(255,255,255,0.5)' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 15px center;
  padding-right: 40px;
}

select.input-field option {
  background: #1a1a1a;
  color: white;
  padding: 10px;
}

/* Botón */
.submit-button {
  width: 100%;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #0099ff 0%, #8a2be2 100%);
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 52px;
  box-shadow: 0 8px 32px rgba(0, 153, 255, 0.4),
              inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
  letter-spacing: 0.5px;
}

.submit-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.submit-button:hover::before {
  left: 100%;
}

.submit-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 48px rgba(0, 153, 255, 0.6),
              0 0 60px rgba(138, 43, 226, 0.4);
}

.submit-button:active {
  transform: translateY(-1px);
}

/* Autocomplete de clientes */
.sugerencias-list {
  background: rgba(20, 20, 20, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  list-style: none;
  padding: 8px;
  margin: 8px 0 0 0;
  border-radius: 12px;
  max-height: 200px;
  overflow-y: auto;
  position: absolute;
  z-index: 1000;
  width: 100%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
}

.sugerencias-list li {
  padding: 10px 12px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 14px;
}

.sugerencias-list li:hover {
  background: rgba(0, 153, 255, 0.3);
  transform: translateX(4px);
}

/* Scrollbar personalizada */
.sugerencias-list::-webkit-scrollbar {
  width: 6px;
}

.sugerencias-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.sugerencias-list::-webkit-scrollbar-thumb {
  background: rgba(0, 153, 255, 0.5);
  border-radius: 10px;
}

/* Responsive */
@media (max-width: 768px) {
  .form-container {
    padding: 40px 16px;
  }
  
  .form-card {
    padding: 36px 28px;
    max-width: 100%;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .full-width {
    grid-column: span 1;
  }
  
  .form-title {
    font-size: 26px;
  }
}

@media (max-width: 480px) {
  .form-card {
    padding: 28px 20px;
    border-radius: 28px;
  }
  
  .form-title {
    font-size: 24px;
  }
  
  .form-subtitle {
    font-size: 14px;
  }
  
  .input-field {
    padding: 14px 16px;
    font-size: 16px;
  }
}
</style>
