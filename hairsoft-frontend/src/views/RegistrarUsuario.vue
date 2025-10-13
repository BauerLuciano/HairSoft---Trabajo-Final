<template>
  <div class="form-container">
    <div class="form-card">
      <h1 class="form-title">Registrar Usuario</h1>
      <p class="form-subtitle">Completa los datos del usuario</p>

      <form @submit.prevent="crearUsuario" class="form-grid">

        <!-- Nombre -->
        <div class="input-group">
          <label class="input-label">Nombre: <span class="obligatorio">*</span></label>
          <input 
            id="nombre"
            type="text"
            v-model="form.nombre"
            class="input-field"
            placeholder="Ingrese el nombre"
            required
          />
        </div>

        <!-- Apellido -->
        <div class="input-group">
          <label class="input-label">Apellido: <span class="obligatorio">*</span></label>
          <input 
            type="text"
            v-model="form.apellido"
            class="input-field"
            placeholder="Ingrese el apellido"
            required
          />
        </div>

        <!-- DNI -->
        <div class="input-group">
          <label class="input-label">DNI: <span class="obligatorio">*</span></label>
          <input 
            type="text"
            v-model="form.dni"
            class="input-field"
            placeholder="Ingrese el número de documento"
            required
          />
        </div>

        <!-- Teléfono -->
        <div class="input-group">
          <label class="input-label">Teléfono:</label>
          <input 
            type="text"
            v-model="form.telefono"
            class="input-field"
            placeholder="Ingrese el teléfono"
          />
        </div>

        <!-- Correo -->
        <div class="input-group">
          <label class="input-label">Correo: <span class="obligatorio">*</span></label>
          <input 
            type="email"
            v-model="form.correo"
            class="input-field"
            placeholder="ejemplo@correo.com"
            required
          />
        </div>

        <!-- Contraseña -->
        <div class="input-group">
          <label class="input-label">Contraseña: <span class="obligatorio">*</span></label>
          <input 
            type="password"
            v-model="form.contrasena"
            class="input-field"
            placeholder="Ingrese una contraseña segura"
            required
          />
        </div>

        <!-- Rol -->
        <div class="input-group">
          <label class="input-label">Rol: <span class="obligatorio">*</span></label>
          <select v-model="form.rol" class="input-field" required>
            <option value="">Seleccionar rol</option>
            <option value="ADMIN">Administrador</option>
            <option value="REC">Recepcionista</option>
            <option value="PEL">Peluquero</option>
            <option value="CLI">Cliente</option>
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
        contrasena: '',
        rol: ''
      },
      usuarios: []
    };
  },
  async mounted() {
    try {
      const res = await fetch('http://localhost:8000/usuarios/');
      if (res.ok) {
        const data = await res.json();
        this.usuarios = data.usuarios;
      }
    } catch (error) {
      console.error('Error al cargar usuarios existentes:', error);
    }
  },
  methods: {
    async crearUsuario() {
      if (this.form.rol === 'ADMIN' && this.usuarios.some(u => u.rol === 'ADMIN')) {
        alert('Ya existe un Administrador. No se puede crear otro.');
        return;
      }

      try {
        const res = await fetch('http://localhost:8000/usuarios/nuevo/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });

        if (res.ok) {
          alert('Usuario registrado con éxito');
          this.form = { nombre: '', apellido: '', dni: '', telefono: '', correo: '', contrasena: '', rol: '' };
          this.$router.push('/usuarios');
        } else {
          const errorData = await res.json();
          alert('Error al registrar usuario: ' + (errorData.detail || JSON.stringify(errorData.errors)));
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
* {
  box-sizing: border-box;
}

/* CONTENEDOR PRINCIPAL */
.form-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0a;
  padding: 40px 20px;
}

.form-card {
  background: #1a1a1a;
  border-radius: 24px;
  padding: 48px;
  width: 100%;
  max-width: 900px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
}

/* TÍTULOS */
.form-title {
  color: #ffffff;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  text-align: center;
}

.form-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  text-align: center;
  margin-bottom: 40px;
}

/* GRID DEL FORMULARIO */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.full-width {
  grid-column: 1 / -1;
}

/* LABELS - ARRIBA DE LOS CAMPOS EN BLANCO BRILLANTE */
.input-label {
  display: block !important;      /* sigue en bloque */
  position: static !important;    /* elimina cualquier posición flotante/absoluta */
  margin-bottom: -16px;             /* espacio entre label y el input */
  color: #ffffff !important;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  padding: 0;
  line-height: 1.5;
  visibility: visible !important;
  opacity: 1 !important;
}


.obligatorio {
  color: #ff4b4b;
  font-weight: 700;
  margin-left: 3px;
}

/* CAMPOS - COMPLETAMENTE REDONDEADOS Y ELEGANTES */
.input-field {
  width: 100%;
  padding: 16px 22px;
  font-size: 15px;
  border: 2px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.input-field::placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.input-field:hover {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.08);
}

.input-field:focus {
  outline: none;
  border-color: #0099ff;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 4px rgba(0, 153, 255, 0.15), 0 4px 12px rgba(0, 153, 255, 0.2);
  transform: translateY(-1px);
}

/* Select - COMPLETAMENTE REDONDEADO */
select.input-field {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'%3E%3Cpath fill='rgba(255,255,255,0.7)' d='M8 11L3 6h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 18px center;
  border-radius: 70px;
  padding-right: 48px;
}

select.input-field option {
  background: #1a1a1a;
  color: #ffffff;
  padding: 12px;
}

/* BOTÓN - COMPLETAMENTE REDONDEADO Y ELEGANTE */
.submit-button {
  width: 100%;
  padding: 18px;
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #0099ff 0%, #0066cc 100%);
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(0, 153, 255, 0.35);
  margin-top: 8px;
  letter-spacing: 0.5px;
}

.submit-button:hover {
  background: linear-gradient(135deg, #00aaff 0%, #0077dd 100%);
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 153, 255, 0.45);
}

.submit-button:active {
  transform: translateY(0);
  box-shadow: 0 4px 16px rgba(0, 153, 255, 0.35);
}


/* RESPONSIVE */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .form-card {
    padding: 32px 24px;
  }

  .form-title {
    font-size: 28px;
  }
}
</style>