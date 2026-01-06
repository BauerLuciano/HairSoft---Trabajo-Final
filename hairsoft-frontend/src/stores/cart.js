import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: JSON.parse(localStorage.getItem('cart_items')) || [], // Recupera del almacenamiento local
    isCartOpen: false // Para abrir/cerrar el carrito lateral
  }),

  getters: {
    cantidadTotal: (state) => state.items.reduce((acc, item) => acc + item.cantidad, 0),
    
    precioTotal: (state) => state.items.reduce((acc, item) => acc + (item.precio * item.cantidad), 0),
    
    estaEnCarrito: (state) => (productoId) => {
      return state.items.find(item => item.id === productoId)
    }
  },

  actions: {
    agregarProducto(producto) {
      const existente = this.items.find(item => item.id === producto.id);
      
      if (existente) {
        // Si ya existe, chequeamos que no supere el stock real (asumiendo que producto trae stock_actual)
        if (existente.cantidad < producto.stock_actual) {
            existente.cantidad++;
        } else {
            alert("¡No hay más stock disponible de este producto!");
            return; // Salimos
        }
      } else {
        // Si es nuevo, lo agregamos con cantidad 1
        this.items.push({
          id: producto.id,
          nombre: producto.nombre,
          precio: parseFloat(producto.precio), // Aseguramos que sea número
          imagen: producto.imagen, // Si tenés foto
          stock_max: producto.stock_actual,
          cantidad: 1
        });
      }
      this.guardarEnLocalStorage();
      this.isCartOpen = true; // Abrimos el carrito para mostrar que se agregó
    },

    removerProducto(productoId) {
      this.items = this.items.filter(item => item.id !== productoId);
      this.guardarEnLocalStorage();
    },

    actualizarCantidad(productoId, cantidad) {
      const item = this.items.find(item => item.id === productoId);
      if (item) {
        if (cantidad > 0 && cantidad <= item.stock_max) {
            item.cantidad = cantidad;
            this.guardarEnLocalStorage();
        } else if (cantidad <= 0) {
            this.removerProducto(productoId);
        } else {
            alert(`Solo hay ${item.stock_max} unidades disponibles.`);
            item.cantidad = item.stock_max; // Lo forzamos al máximo posible
        }
      }
    },

    limpiarCarrito() {
      this.items = [];
      this.guardarEnLocalStorage();
    },

    toggleCart() {
      this.isCartOpen = !this.isCartOpen;
    },

    guardarEnLocalStorage() {
      localStorage.setItem('cart_items', JSON.stringify(this.items));
    }
  }
})