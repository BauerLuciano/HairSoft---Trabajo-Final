<template>
  <div>
    <h2>Lista de Clientes</h2>
    <ul>
      <li v-for="cliente in clientes" :key="cliente.id">
        {{ cliente.nombre }} {{ cliente.apellido }} - {{ cliente.correo }}
      </li>
    </ul>
  </div>
</template>

<script>
import { obtenerClientes } from '../usuariosService';

export default {
  name: 'ClientesList',
  data() {
    return {
      clientes: [],
    };
  },
  async created() {
    this.clientes = await obtenerClientes();
  },
};
</script>
