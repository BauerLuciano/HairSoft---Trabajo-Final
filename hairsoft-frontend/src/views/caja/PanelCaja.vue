<template>
  <div class="list-container">
    <div class="list-card">
      
      <div class="list-header">
        <div class="header-content">
          <h1><i class="ri-bank-card-line"></i> Caja Diaria</h1>
          <p>Control de ingresos, egresos y arqueo de caja.</p>
        </div>
        <div class="header-buttons">
          <button 
            class="action-button historial-btn" 
            style="width: auto; padding: 0 20px; height: 44px; border-radius: 12px;"
            @click="mostrarHistorial = !mostrarHistorial"
          >
            <i class="ri-history-line"></i> {{ mostrarHistorial ? 'Ver Caja Actual' : 'Historial de Cajas' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="loader-container">
        <i class="ri-loader-4-line animate-spin loader-icon"></i>
        <p>Cargando información...</p>
      </div>

      <div v-else>
        
        <div v-if="mostrarHistorial">
          <h2 style="margin-bottom: 20px; color: var(--text-primary);">Historial de Sesiones Anteriores</h2>

          <div class="filters-grid" style="grid-template-columns: 1fr 1fr 1fr auto; margin-bottom: 25px; align-items: end;">
            <div class="filter-group">
              <label>Usuario que cerró</label>
              <select v-model="filterUser" class="filter-select">
                <option value="">Todos los usuarios</option>
                <option v-for="user in uniqueUsers" :key="user" :value="user">
                  {{ user }}
                </option>
              </select>
            </div>

            <div class="filter-group">
              <label>Fecha desde</label>
              <input type="date" v-model="filterDateFrom" class="filter-input">
            </div>

            <div class="filter-group">
              <label>Fecha hasta</label>
              <input type="date" v-model="filterDateTo" class="filter-input">
            </div>

            <div>
              <button class="clear-filters-btn" @click="limpiarFiltros" style="height: 46px;">
                <i class="ri-eraser-line"></i> Limpiar
              </button>
            </div>
          </div>

          <div class="table-container">
            <table class="users-table">
              <thead>
                <tr>
                  <th>N° Sesión</th>
                  <th>Apertura</th>
                  <th>Cierre</th>
                  <th>Usuario Cierre</th>
                  <th class="text-right">Fondo Inicial (Efvo / MP)</th>
                  <th class="text-right">Físico Contado</th>
                  <th class="text-right">Mercado Pago</th>
                  <th class="text-right" style="color: var(--accent-color);">Total Final</th>
                  <th class="text-center">Estado</th>
                  <th class="text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredCajas.length === 0">
                  <td colspan="10" class="no-results">
                    <i class="ri-history-line no-results-icon" style="font-size: 2rem;"></i>
                    <p>No hay cajas que coincidan con los filtros.</p>
                  </td>
                </tr>
                <tr v-for="caja in paginatedCajas" :key="caja.id">
                  <td><strong>#{{ caja.id }}</strong></td>
                  <td>{{ formatearFechaCorta(caja.fecha_apertura) }}</td>
                  <td>{{ caja.fecha_cierre ? formatearFechaCorta(caja.fecha_cierre) : '-' }}</td>
                  <td>{{ caja.usuario_cierre_nombre || '-' }}</td>
                  <td class="text-right" style="color: var(--text-secondary);">
                    {{ formatearMoneda(caja.saldo_inicial_efectivo) }} / {{ formatearMoneda(caja.saldo_inicial_mp) }}
                  </td>
                  <td class="text-right"><strong>{{ formatearMoneda(caja.saldo_final_efectivo_real) }}</strong></td>
                  <td class="text-right">{{ formatearMoneda(caja.saldo_final_mp_real) }}</td>
                  <td class="text-right">
                    <strong :style="{ color: calcularTotalRealDeclarado(caja) < 0 ? '#ef4444' : 'var(--accent-color)' }">
                      {{ caja.esta_abierta ? '-' : formatearMoneda(calcularTotalRealDeclarado(caja)) }}
                    </strong>
                  </td>
                  <td class="text-center">
                    <span :class="caja.esta_abierta ? 'badge-estado estado-warning' : 'badge-estado estado-success'">
                      {{ caja.esta_abierta ? 'ABIERTA' : 'CERRADA' }}
                    </span>
                  </td>
                  <td class="text-center">
                    <button class="action-button edit" title="Ver Movimientos" @click="verDetalleCajaCerrada(caja)" style="margin: 0 auto;">
                      <i class="ri-eye-line"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination" v-if="totalPagesCajas > 1">
            <button :disabled="currentPageCajas === 1" @click="currentPageCajas--">
              <i class="ri-arrow-left-s-line"></i> Anterior
            </button>
            <span>Página {{ currentPageCajas }} de {{ totalPagesCajas }}</span>
            <button :disabled="currentPageCajas === totalPagesCajas" @click="currentPageCajas++">
              Siguiente <i class="ri-arrow-right-s-line"></i>
            </button>
          </div>
        </div>

        <div v-else>
          
          <div v-if="!sesionActual" class="caja-cerrada-wrapper">
            <div class="caja-cerrada-card">
              <div class="icono-bloqueo">
                <i class="ri-lock-2-line"></i>
              </div>
              <h2>Caja Cerrada</h2>
              <p>Para registrar cobros o pagos, necesitás iniciar una sesión de caja.</p>

              <div v-if="pendientesInfo && pendientesInfo.cantidad > 0" class="alerta-huerfanos">
                <i class="ri-notification-3-line"></i>
                <div class="alerta-content">
                  <strong>Cobros Web Pendientes</strong>

                  <p>
                    {{ pendientesInfo.cantidad === 1 
                      ? 'Ingresó 1 pago' 
                      : `Ingresaron ${pendientesInfo.cantidad} pagos` }} 
                    mientras la caja estaba cerrada.
                  </p>

                  <p>
                    <strong>Total: {{ formatearMoneda(pendientesInfo.total_dinero) }}</strong>
                  </p>

                </div>
              </div>

              <form @submit.prevent="abrirCaja" class="form-apertura">
                <div class="filter-group">
                  <label>Seleccionar Caja Física</label>
                  <select v-model="formApertura.caja" required class="filter-select">
                    <option value="" disabled>Seleccione una caja...</option>
                    <option v-for="c in cajasDisponibles" :key="c.id" :value="c.id">
                      {{ c.nombre }}
                    </option>
                  </select>
                </div>

                <div class="filter-group" style="margin-top: 15px;">
                  <label>Tipo de Fondo Inicial</label>
                  <select v-model="formApertura.tipoFondo" class="filter-select">
                    <option value="EFECTIVO">Solo Efectivo</option>
                    <option value="MERCADO_PAGO">Solo Mercado Pago</option>
                    <option value="AMBOS">Efectivo y Mercado Pago</option>
                  </select>
                </div>

                <div v-if="['EFECTIVO', 'AMBOS'].includes(formApertura.tipoFondo)" class="filter-group" style="margin-top: 15px;">
                  <label>Fondo de Caja (Efectivo Inicial)</label>
                  <div class="input-money-wrapper">
                    <span class="currency-symbol">$</span>
                    <input type="number" v-model="formApertura.saldo_inicial_efectivo" step="0.01" min="0" required class="filter-input input-money">
                  </div>
                </div>

                <div v-if="['MERCADO_PAGO', 'AMBOS'].includes(formApertura.tipoFondo)" class="filter-group" style="margin-top: 15px;">
                  <label>Fondo Inicial (Mercado Pago)</label>
                  <div class="input-money-wrapper">
                    <span class="currency-symbol">$</span>
                    <input type="number" v-model="formApertura.saldo_inicial_mp" step="0.01" min="0" required class="filter-input input-money">
                  </div>
                </div>

                <button type="submit" class="register-button btn-full" style="margin-top: 25px;">
                  <i class="ri-key-2-line"></i> INICIAR TURNO DE CAJA
                </button>
              </form>
            </div>
          </div>

          <div v-else>
            
            <div class="status-bar-caja">
              <div class="status-info">
                <span class="badge-estado estado-success" style="font-size: 0.85rem;"><i class="ri-lock-unlock-line"></i> ABIERTA</span>
                <span class="caja-nombre-txt">{{ sesionActual.caja_nombre }}</span>
                <span class="caja-usuario-txt">Por {{ sesionActual.usuario_apertura_nombre }} ({{ formatearFecha(sesionActual.fecha_apertura) }})</span>
              </div>
              <button @click="mostrarModalCierre = true" class="action-button delete btn-arqueo">
                <i class="ri-scales-3-line"></i> Cierre de caja
              </button>
            </div>

            <div v-if="balance">
              <div class="balance-card total-general" style="margin-bottom: 20px;">
                <div class="b-icon" style="background: var(--accent-color); color: white; width: 60px; height: 60px; font-size: 2rem;">
                  <i class="ri-safe-2-line"></i>
                </div>
                <div class="b-data">
                  <p style="font-size: 1rem;">TOTAL GENERAL CALCULADO</p>
                  <h3 style="font-size: 2.5rem; color: var(--accent-color);">{{ formatearMoneda(calcularTotalActual(balance)) }}</h3>
                </div>
              </div>

              <div class="balances-grid" style="grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));">
                <div class="balance-card">
                  <div class="b-icon"><i class="ri-wallet-3-line"></i></div>
                  <div class="b-data">
                    <p>Fondo Inicial</p>
                    <h3 style="font-size: 1.2rem;">{{ formatearMoneda(balance.saldo_inicial_efectivo) }}</h3>
                    <h3 style="font-size: 1.2rem;">{{ formatearMoneda(balance.saldo_inicial_mp) }}</h3>
                  </div>
                </div>
                <div class="balance-card highlight">
                  <div class="b-icon"><i class="ri-cash-line"></i></div>
                  <div class="b-data">
                    <p>Saldo (Efectivo)</p>
                    <h3>{{ formatearMoneda(balance.esperado_efectivo) }}</h3>
                  </div>
                </div>
                <div class="balance-card mp">
                  <div class="b-icon"><i class="ri-qr-scan-2-line"></i></div>
                  <div class="b-data">
                    <p>Saldo (Mercado Pago)</p>
                    <h3>{{ formatearMoneda(balance.esperado_mp) }}</h3>
                  </div>
                </div>
              </div>
            </div>

            <div class="movimientos-wrapper">
              <div class="list-header" style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: none;">
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.3rem;">Historial de Movimientos</h3>
                <button @click="mostrarModalGasto = true" class="register-button">
                  <i class="ri-add-line"></i> Movimiento Manual
                </button>
              </div>

              <div class="table-container">
                <table class="users-table table-fixed">
                  <thead>
                    <tr>
                      <th style="width: 10%;">Hora</th>
                      <th style="width: 10%;">Tipo</th>
                      <th style="width: 25%;">Concepto</th>
                      <th style="width: 15%;">Método</th>
                      <th style="width: 30%;">Descripción</th>
                      <th class="text-right" style="width: 10%;">Monto</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="movimientos.length === 0">
                      <td colspan="6" class="no-results">
                        <i class="ri-file-list-3-line no-results-icon" style="font-size: 2rem;"></i>
                        <p>No hay movimientos registrados en esta sesión.</p>
                      </td>
                    </tr>
                    <tr v-for="mov in paginatedMovs" :key="mov.id">
                      <td>{{ formatearHora(mov.fecha) }}</td>
                      <td>
                        <span :class="mov.tipo === 'INGRESO' ? 'badge-estado estado-success' : 'badge-estado estado-danger'">
                          {{ mov.tipo }}
                        </span>
                      </td>
                      <td><strong>{{ mov.concepto_display }}</strong></td>
                      <td>{{ mov.metodo_pago_display }}</td>
                      <td class="col-descripcion">{{ mov.descripcion || '-' }}</td>
                      <td class="text-right">
                        <strong :style="{ color: mov.tipo === 'INGRESO' ? '#10b981' : '#ef4444' }">
                          {{ mov.tipo === 'EGRESO' ? '-' : '+' }}{{ formatearMoneda(mov.monto) }}
                        </strong>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="pagination" v-if="totalPagesMovs > 1">
                <button :disabled="currentPageMovs === 1" @click="currentPageMovs--">
                  <i class="ri-arrow-left-s-line"></i> Anterior
                </button>
                <span>Página {{ currentPageMovs }} de {{ totalPagesMovs }}</span>
                <button :disabled="currentPageMovs === totalPagesMovs" @click="currentPageMovs++">
                  Siguiente <i class="ri-arrow-right-s-line"></i>
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>

    <div v-if="mostrarModalCierre" class="modal-overlay" @click.self="mostrarModalCierre = false">
      <div class="modal-content modal-cierre">
        <div class="historial-header">
          <h2>Arqueo de Caja</h2>
          <p>Declaración de dinero físico y digital contado.</p>
          <button class="modal-close" @click="mostrarModalCierre = false"><i class="ri-close-line"></i></button>
        </div>
        
        <div class="historial-body">
          <form @submit.prevent="cerrarCaja">
            
            <div class="alerta-cierre">
              <i class="ri-information-line"></i>
              <p>Verificá los valores cargados. Si coinciden con el sistema, la caja cerrará sin diferencias.</p>
            </div>

            <div class="resumen-esperado" v-if="balance">
              <h4>Según el sistema, deberías tener:</h4>
              <div class="resumen-grid" style="grid-template-columns: 1fr 1fr;">
                <div class="resumen-item">
                  <span style="color: #10b981;"><i class="ri-cash-line"></i> Efectivo:</span>
                  <strong>{{ formatearMoneda(balance.esperado_efectivo) }}</strong>
                </div>
                <div class="resumen-item">
                  <span style="color: #00a1f1;"><i class="ri-qr-scan-2-line"></i> Mercado Pago:</span>
                  <strong>{{ formatearMoneda(balance.esperado_mp) }}</strong>
                </div>
              </div>
            </div>

            <div class="filters-grid" style="grid-template-columns: 1fr;">
              <div class="filter-group">
                <label>Dinero en el Cajón (Efectivo):</label>
                <div class="input-money-wrapper">
                  <span class="currency-symbol">$</span>
                  <input type="number" v-model="formCierre.saldo_final_efectivo_real" step="0.01" min="0" required class="filter-input input-money">
                </div>
              </div>
              <div class="filter-group">
                <label>Dinero en Mercado Pago:</label>
                <div class="input-money-wrapper">
                  <span class="currency-symbol">$</span>
                  <input type="number" v-model="formCierre.saldo_final_mp_real" step="0.01" min="0" required class="filter-input input-money">
                </div>
              </div>

              <div class="filter-group" v-if="hayDiferencia">
                <label style="color: #ef4444; font-size: 0.85rem; display: flex; align-items: center; gap: 5px;">
                  <i class="ri-error-warning-line" style="font-size: 1.2rem;"></i> 
                  DIFERENCIA DE {{ (diferenciaCierre > 0 ? '+' : '') + formatearMoneda(diferenciaCierre) }} ({{ tipoDiferencia }}). INGRESE JUSTIFICACIÓN:
                </label>
                <textarea v-model="formCierre.observaciones" rows="3" class="filter-input" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.03);" placeholder="Obligatorio: justifique detalladamente el descuadre de caja..." required></textarea>
              </div>
            </div>
            
            <div style="display: flex; gap: 10px; margin-top: 25px;">
              <button type="button" @click="mostrarModalCierre = false" class="clear-filters-btn" style="flex: 1; justify-content: center;">Cancelar</button>
              <button type="submit" class="register-button" style="flex: 1; justify-content: center; background: #ef4444;">
                <i class="ri-lock-fill"></i> Confirmar Cierre
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="mostrarModalGasto" class="modal-overlay" @click.self="mostrarModalGasto = false">
      <div class="modal-content modal-cierre">
        <div class="historial-header">
          <h2>Nuevo Movimiento Manual</h2>
          <p>Registrar plata que entra o sale fuera del flujo automático.</p>
          <button class="modal-close" @click="mostrarModalGasto = false"><i class="ri-close-line"></i></button>
        </div>
        
        <div class="historial-body">
          <form @submit.prevent="registrarGastoManual">
            <div class="filters-grid" style="grid-template-columns: 1fr;">
              
              <div class="filter-group">
                <label>Tipo de Movimiento</label>
                <select v-model="formGasto.tipo" required class="filter-select custom-select">
                  <option value="EGRESO">Salida de Plata (Egreso)</option>
                  <option value="INGRESO">Entrada de Plata (Ingreso)</option>
                </select>
              </div>

              <div class="filter-group">
                <label>Categoría / Concepto</label>
                
                <select v-if="formGasto.tipo === 'EGRESO'" v-model="formGasto.concepto" required class="filter-select custom-select">
                  <option value="GASTO_OPERATIVO">Gasto Local </option>
                  <option value="RETIRO_SOCIO">Retiro de Dueño</option>
                  <option value="LIQUIDACION_SUELDO">Liquidación de Sueldos</option>
                  <option value="PAGO_PROVEEDOR">Pago a Proveedor</option>
                  <option value="OTROS">Otros / Ajuste</option>
                </select>

                <select v-else v-model="formGasto.concepto" required class="filter-select custom-select">
                  <option value="APORTE_SOCIO">Aporte del dueño</option>
                  <option value="COBRO_DEUDA">Cobro de Deuda</option>
                  <option value="OTROS">Otros / Ajuste</option>
                </select>
              </div>

              <div class="filter-group">
                <label>Medio de Pago</label>
                <select v-model="formGasto.metodo_pago" required class="filter-select custom-select">
                  <option value="EFECTIVO">Efectivo (Del Cajón)</option>
                  <option value="MERCADO_PAGO">Mercado Pago</option>
                </select>
              </div>

              <div class="filter-group">
                <label>Monto</label>
                <div class="input-money-wrapper">
                  <span class="currency-symbol">$</span>
                  <input type="number" v-model="formGasto.monto" step="0.01" min="1" required class="filter-input input-money">
                </div>
              </div>

              <div class="filter-group">
                <label>Descripción Breve</label>
                <input type="text" v-model="formGasto.descripcion" required class="filter-input" placeholder="Ej: Compra de café, aporte del dueño...">
              </div>

            </div>
            
            <div style="display: flex; gap: 10px; margin-top: 25px;">
              <button type="button" @click="mostrarModalGasto = false" class="clear-filters-btn" style="flex: 1; justify-content: center;">Cancelar</button>
              <button type="submit" class="register-button" style="flex: 1; justify-content: center;">Guardar Movimiento</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="mostrarModalDetalleHistorial" class="modal-overlay" @click.self="mostrarModalDetalleHistorial = false">
      <div class="modal-content modal-historial-amplio">
        <div class="historial-header">
          <h2>Movimientos - Sesión #{{ cajaSeleccionada?.id }}</h2>
          <div style="display: flex; justify-content: space-between; align-items: flex-end; width: 100%;">
             <div>
                <p style="margin:0;">
                  Caja: <strong>{{ cajaSeleccionada?.caja_nombre }}</strong> | 
                  Fecha: {{ formatearFechaCorta(cajaSeleccionada?.fecha_apertura) }}
                </p>
                <p style="margin:0; font-size: 0.9rem; color: var(--text-secondary);">
                  Fondo Inicial (Efvo/MP): <strong>{{ formatearMoneda(cajaSeleccionada?.saldo_inicial_efectivo) }} / {{ formatearMoneda(cajaSeleccionada?.saldo_inicial_mp) }}</strong>
                </p>
             </div>
             <div v-if="cajaSeleccionada?.diferencia_detalle !== 0" :style="{ color: cajaSeleccionada?.diferencia_detalle < 0 ? '#ef4444' : '#10b981', fontWeight: 'bold' }">
                Diferencia: {{ (cajaSeleccionada?.diferencia_detalle > 0 ? '+' : '') + formatearMoneda(cajaSeleccionada?.diferencia_detalle) }}
             </div>
          </div>
          <button class="modal-close" @click="mostrarModalDetalleHistorial = false"><i class="ri-close-line"></i></button>
        </div>
        
        <div class="historial-body">
          <div v-if="cajaSeleccionada?.observaciones" class="alerta-cierre" style="background: rgba(14, 165, 233, 0.05); border-left: 4px solid var(--accent-color); margin-bottom: 20px; display: flex; gap: 15px; padding: 15px; border-radius: 4px;">
              <i class="ri-chat-history-line" style="color: var(--accent-color); font-size: 1.5rem;"></i>
              <div>
                  <strong style="color: var(--text-primary); display: block; margin-bottom: 5px;">Justificación de la diferencia:</strong>
                  <p style="margin: 0; font-style: italic; color: var(--text-secondary);">"{{ cajaSeleccionada.observaciones }}"</p>
              </div>
          </div>

          <div v-if="cargandoMovimientosHistorial" style="text-align: center; padding: 40px;">
            <i class="ri-loader-4-line animate-spin loader-icon"></i>
            <p>Cargando movimientos...</p>
          </div>
          <div v-else>
            <div class="table-container">
              <table class="users-table table-fixed">
                <thead>
                  <tr>
                    <th style="width: 10%;">Hora</th>
                    <th style="width: 10%;">Tipo</th>
                    <th style="width: 25%;">Concepto</th>
                    <th style="width: 15%;">Método</th>
                    <th style="width: 30%;">Descripción</th>
                    <th class="text-right" style="width: 10%;">Monto</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="movimientosHistorial.length === 0">
                    <td colspan="6" class="no-results">No hay movimientos registrados.</td>
                  </tr>
                  <tr v-for="mov in paginatedModalMovs" :key="mov.id">
                    <td>{{ formatearHora(mov.fecha) }}</td>
                    <td>
                      <span :class="mov.tipo === 'INGRESO' ? 'badge-estado estado-success' : 'badge-estado estado-danger'">
                        {{ mov.tipo }}
                      </span>
                    </td>
                    <td><strong>{{ mov.concepto_display }}</strong></td>
                    <td>{{ mov.metodo_pago_display }}</td>
                    <td class="col-descripcion">{{ mov.descripcion || '-' }}</td>
                    <td class="text-right">
                      <strong :style="{ color: mov.tipo === 'INGRESO' ? '#10b981' : '#ef4444' }">
                        {{ mov.tipo === 'EGRESO' ? '-' : '+' }}{{ formatearMoneda(mov.monto) }}
                      </strong>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="pagination" v-if="totalPagesModalMovs > 1">
              <button :disabled="currentPageModalMovs === 1" @click="currentPageModalMovs--">
                <i class="ri-arrow-left-s-line"></i> Anterior
              </button>
              <span>Página {{ currentPageModalMovs }} de {{ totalPagesModalMovs }}</span>
              <button :disabled="currentPageModalMovs === totalPagesModalMovs" @click="currentPageModalMovs++">
                Siguiente <i class="ri-arrow-right-s-line"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import cajaService from '@/services/cajaService';
import Swal from 'sweetalert2';

const loading = ref(true);
const cajasDisponibles = ref([]);
const sesionActual = ref(null);
const balance = ref(null);
const movimientos = ref([]);
const pendientesInfo = ref(null);
const mostrarHistorial = ref(false);
const historialCajas = ref([]);
const mostrarModalCierre = ref(false);
const mostrarModalGasto = ref(false);
const mostrarModalDetalleHistorial = ref(false);
const cajaSeleccionada = ref(null);
const movimientosHistorial = ref([]);
const cargandoMovimientosHistorial = ref(false);

const formApertura = ref({ 
  caja: '', 
  tipoFondo: 'EFECTIVO', 
  saldo_inicial_efectivo: 0,
  saldo_inicial_mp: 0 
});
const formCierre = ref({ saldo_final_efectivo_real: 0, saldo_final_mp_real: 0, observaciones: '' });

// Asegurarnos que empiece limpio
const formGasto = ref({ tipo: 'EGRESO', concepto: 'GASTO_OPERATIVO', metodo_pago: 'EFECTIVO', monto: '', descripcion: '' });

watch(() => formGasto.value.tipo, (nuevoTipo) => {
  if (nuevoTipo === 'EGRESO') {
    formGasto.value.concepto = 'GASTO_OPERATIVO';
  } else {
    formGasto.value.concepto = 'APORTE_SOCIO';
  }
});

let pollingInterval = null;
const itemsPerPage = 9;

// ----- FILTROS -----
const filterUser = ref('');
const filterDateFrom = ref('');
const filterDateTo = ref('');

const uniqueUsers = computed(() => {
  const users = historialCajas.value
    .map(c => c.usuario_cierre_nombre)
    .filter(u => u && u.trim() !== '');
  return [...new Set(users)];
});

const filteredCajas = computed(() => {
  return historialCajas.value.filter(caja => {
    if (filterUser.value && caja.usuario_cierre_nombre !== filterUser.value) return false;

    if (filterDateFrom.value) {
      const fechaCaja = new Date(caja.fecha_apertura);
      fechaCaja.setHours(0, 0, 0, 0);
      const desde = new Date(filterDateFrom.value);
      desde.setHours(0, 0, 0, 0);
      if (fechaCaja < desde) return false;
    }

    if (filterDateTo.value) {
      const fechaCaja = new Date(caja.fecha_apertura);
      fechaCaja.setHours(0, 0, 0, 0);
      const hasta = new Date(filterDateTo.value);
      hasta.setHours(0, 0, 0, 0);
      if (fechaCaja > hasta) return false;
    }

    return true;
  });
});

// Paginación del historial
const currentPageCajas = ref(1);
const paginatedCajas = computed(() => {
  const start = (currentPageCajas.value - 1) * itemsPerPage;
  return filteredCajas.value.slice(start, start + itemsPerPage);
});
const totalPagesCajas = computed(() => Math.ceil(filteredCajas.value.length / itemsPerPage));

// Reiniciar página al cambiar filtros
watch([filterUser, filterDateFrom, filterDateTo], () => {
  currentPageCajas.value = 1;
});

const limpiarFiltros = () => {
  filterUser.value = '';
  filterDateFrom.value = '';
  filterDateTo.value = '';
  currentPageCajas.value = 1;
};

// ----- FIN FILTROS -----

const diferenciaCierre = computed(() => {
  if (!balance.value) return 0;
  const esperado = parseFloat(balance.value.esperado_efectivo) + parseFloat(balance.value.esperado_mp);
  const real = parseFloat(formCierre.value.saldo_final_efectivo_real || 0) + parseFloat(formCierre.value.saldo_final_mp_real || 0);
  
  return real - esperado; 
});

const hayDiferencia = computed(() => {
  return Math.abs(diferenciaCierre.value) > 0.01;
});

const tipoDiferencia = computed(() => {
  if (!balance.value) return '';
  const esperado = parseFloat(balance.value.esperado_efectivo) + parseFloat(balance.value.esperado_mp);

  if (diferenciaCierre.value < 0) {
      if (esperado < 0 && parseFloat(formCierre.value.saldo_final_efectivo_real || 0) === 0) {
          return 'FALTANTE: Fondos Insuficientes para cubrir deuda';
      }
      return 'FALTANTE';
  }
  return 'SOBRANTE';
});

const calcularTotalRealDeclarado = (caja) => {
  return parseFloat(caja.saldo_final_efectivo_real || 0) + parseFloat(caja.saldo_final_mp_real || 0);
};

const calcularTotalCaja = (caja) => {
  if (caja.esta_abierta) return 0;
  return parseFloat(caja.saldo_final_efectivo_real || 0) + parseFloat(caja.saldo_final_mp_real || 0);
};

const formatearMoneda = (valor) => {
  const n = parseFloat(valor || 0);
  const signo = n < 0 ? '-' : '';
  const formateado = Math.abs(n).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return `$ ${signo}${formateado}`;
};

// Paginación de movimientos actuales
const currentPageMovs = ref(1);
const paginatedMovs = computed(() => {
  const start = (currentPageMovs.value - 1) * itemsPerPage;
  return movimientos.value.slice(start, start + itemsPerPage);
});
const totalPagesMovs = computed(() => Math.ceil(movimientos.value.length / itemsPerPage));

// Paginación de movimientos del modal de historial
const currentPageModalMovs = ref(1);
const paginatedModalMovs = computed(() => {
  const start = (currentPageModalMovs.value - 1) * itemsPerPage;
  return movimientosHistorial.value.slice(start, start + itemsPerPage);
});
const totalPagesModalMovs = computed(() => Math.ceil(movimientosHistorial.value.length / itemsPerPage));

const inicializar = async () => {
  loading.value = true;
  try {
    try {
      const resSesion = await cajaService.getSesionActual();
      sesionActual.value = resSesion.data;
      await cargarDatosCajaAbierta(sesionActual.value.id);
      iniciarRadar();
    } catch (e) {
      if (e.response && e.response.status === 404) {
        sesionActual.value = null;
        await cargarDatosApertura();
      }
    }
    await cargarHistorial();
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const cargarDatosApertura = async () => {
  const [resCajas, resPendientes] = await Promise.all([
    cajaService.getCajas(),
    cajaService.getPendientes()
  ]);
  cajasDisponibles.value = resCajas.data.filter(c => c.activa);
  if (cajasDisponibles.value.length > 0) {
    formApertura.value.caja = cajasDisponibles.value[0].id;
  }
  pendientesInfo.value = resPendientes.data;
};

const cargarDatosCajaAbierta = async (sesionId) => {
  const [resBalance, resMovs] = await Promise.all([
    cajaService.getBalance(sesionId),
    cajaService.getMovimientos(sesionId)
  ]);
  balance.value = resBalance.data;
  movimientos.value = resMovs.data;
  currentPageMovs.value = 1; 
  
  formCierre.value.saldo_final_efectivo_real = Math.max(0, parseFloat(balance.value.esperado_efectivo));
  formCierre.value.saldo_final_mp_real = Math.max(0, parseFloat(balance.value.esperado_mp)); 
  formCierre.value.observaciones = ''; 
};

const checkNuevosMovimientos = async () => {
  if (!sesionActual.value || mostrarHistorial.value) return;
  try {
    const resMovs = await cajaService.getMovimientos(sesionActual.value.id);
    if (resMovs.data.length > movimientos.value.length) {
      movimientos.value = resMovs.data;
      const resBalance = await cajaService.getBalance(sesionActual.value.id);
      balance.value = resBalance.data;
      Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: `¡Nuevos pagos ingresados!`, showConfirmButton: false, timer: 3000 });
    }
  } catch (error) { console.error(error); }
};

const iniciarRadar = () => {
  if (pollingInterval) clearInterval(pollingInterval);
  pollingInterval = setInterval(checkNuevosMovimientos, 15000);
};

const detenerRadar = () => { if (pollingInterval) clearInterval(pollingInterval); };

const cargarHistorial = async () => {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch('http://localhost:8000/api/sesiones-caja/', {
      headers: { 'Authorization': `Token ${token}` }
    });
    const data = await res.json();
    historialCajas.value = data;
  } catch (e) { console.error(e); }
}

const abrirCaja = async () => {
  try {
    const payload = {
      caja: formApertura.value.caja,
      saldo_inicial_efectivo: ['EFECTIVO', 'AMBOS'].includes(formApertura.value.tipoFondo) ? formApertura.value.saldo_inicial_efectivo : 0,
      saldo_inicial_mp: ['MERCADO_PAGO', 'AMBOS'].includes(formApertura.value.tipoFondo) ? formApertura.value.saldo_inicial_mp : 0,
    };

    await cajaService.abrirCaja(payload);
    inicializar(); 
  } catch (error) { Swal.fire('Error', 'No se pudo abrir', 'error'); }
};

const cerrarCaja = async () => {
  if (hayDiferencia.value && !formCierre.value.observaciones.trim()) {
      Swal.fire({ icon: 'warning', title: 'Justificación Requerida', text: `Debe justificar la diferencia de ${formatearMoneda(Math.abs(diferenciaCierre.value))} (${tipoDiferencia.value})` });
      return;
  }
  Swal.fire({
      title: '¿Cerrar caja?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, cerrar'
  }).then(async (result) => {
      if (result.isConfirmed) {
          try {
            await cajaService.cerrarCaja(sesionActual.value.id, formCierre.value);
            detenerRadar();
            mostrarModalCierre.value = false;
            inicializar();
          } catch (error) { Swal.fire('Error', 'Error al cerrar', 'error'); }
      }
  });
};

const registrarGastoManual = async () => {
  // 🔥 VALIDACIÓN DE FONDOS INSUFICIENTES (solo si es EGRESO)
  if (formGasto.value.tipo === 'EGRESO') {
      const montoEgreso = parseFloat(formGasto.value.monto);
      let saldoDisponible = 0;
      let metodoNombre = '';

      if (formGasto.value.metodo_pago === 'EFECTIVO') {
          saldoDisponible = parseFloat(balance.value.esperado_efectivo);
          metodoNombre = 'Efectivo';
      } else if (formGasto.value.metodo_pago === 'MERCADO_PAGO') {
          saldoDisponible = parseFloat(balance.value.esperado_mp);
          metodoNombre = 'Mercado Pago';
      }

      if (montoEgreso > saldoDisponible) {
          Swal.fire({
              icon: 'error',
              title: 'Fondos Insuficientes',
              html: `Estás intentando registrar un egreso de <b>${formatearMoneda(montoEgreso)}</b>, pero el saldo actual en <b>${metodoNombre}</b> es de solo <b>${formatearMoneda(saldoDisponible)}</b>.<br><br>Si se agregó dinero adicional a la caja, registrá primero un <i>Ingreso Manual</i> por la diferencia.`,
              confirmButtonColor: '#ef4444',
              confirmButtonText: 'Entendido'
          });
          return; // Detiene la ejecución, no envía el gasto
      }
  }

  try {
    await cajaService.crearMovimientoManual(formGasto.value);
    mostrarModalGasto.value = false;
    formGasto.value = { tipo: 'EGRESO', concepto: 'GASTO_OPERATIVO', metodo_pago: 'EFECTIVO', monto: '', descripcion: '' };
    cargarDatosCajaAbierta(sesionActual.value.id);
  } catch (error) { Swal.fire('Error', 'Error al registrar', 'error'); }
};

const verDetalleCajaCerrada = async (caja) => {
  cajaSeleccionada.value = caja;
  mostrarModalDetalleHistorial.value = true;
  cargandoMovimientosHistorial.value = true;
  try {
    const res = await cajaService.getMovimientos(caja.id);
    movimientosHistorial.value = res.data;
  } catch (error) { console.error(error); } finally { cargandoMovimientosHistorial.value = false; }
};

const calcularTotalActual = (bal) => {
  if (!bal) return 0;
  return parseFloat(bal.esperado_efectivo) + parseFloat(bal.esperado_mp);
};

const formatearFecha = (f) => f ? new Date(f).toLocaleString('es-AR') : '';
const formatearFechaCorta = (f) => f ? new Date(f).toLocaleDateString('es-AR') : '';
const formatearHora = (f) => f ? new Date(f).toLocaleTimeString('es-AR', {hour:'2-digit', minute:'2-digit'}) : '';

onMounted(() => inicializar());
onUnmounted(() => detenerRadar());
</script>

<style scoped>
/* HEREDANDO LOS ESTILOS DEL SISTEMA */
.list-container { padding: 32px; max-width: 1600px; margin: 0 auto; min-height: 100vh; font-family: 'Inter', sans-serif; }
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; transition: all 0.4s ease; border: 1px solid var(--border-color); }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); border-radius: 24px 24px 0 0; }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; flex-wrap: wrap; gap: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; letter-spacing: 0.5px; }

.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px; font-size: 0.95rem; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); display: flex; align-items: center; gap: 8px; }
.register-button:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); background: linear-gradient(135deg, #0284c7, #0369a1); }
.btn-full { width: 100%; justify-content: center; padding: 16px; font-size: 1.1rem; }

.action-button { padding: 8px; border: none; border-radius: 10px; font-size: 0.8rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; width: 36px; height: 36px; }
.action-button.historial-btn { background: var(--bg-tertiary); border: 1px solid #0ea5e9; color: #0ea5e9; gap: 8px; font-size: 0.9rem;}
.action-button.historial-btn:hover { background: #f0f9ff; border-color: #0284c7; color: #0284c7; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3); }

.action-button.edit { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); }
.action-button.edit:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.action-button.delete { background: var(--bg-tertiary); border: 1px solid var(--error-color); color: var(--error-color); cursor: pointer; font-weight: bold;}
.action-button.delete:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4); border-color: var(--error-color); }

/* UTILIDADES GLOBALES */
.loader-container { text-align: center; padding: 60px; color: var(--text-secondary); font-size: 1.2rem; }
.loader-icon { font-size: 3rem; color: #0ea5e9; margin-bottom: 15px; }
.animate-spin { animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.text-right { text-align: right !important; }
.text-center { text-align: center !important; }

/* BADGES */
.badge-estado { padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; display: inline-block; letter-spacing: 0.5px; }
.estado-success { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.5); }
.estado-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.5); }
.estado-warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.5); }

/* TABLAS Y CHAU SCROLL HORIZONTAL */
.table-container { 
  border-radius: 16px; 
  border: 1px solid var(--border-color); 
  background: var(--bg-primary); 
  width: 100%; 
  overflow-x: auto; 
  -webkit-overflow-scrolling: touch; 
}
.users-table { 
  width: 100%; 
  min-width: 800px; 
  border-collapse: collapse; 
}
.table-fixed { table-layout: fixed; } 
.users-table th { background: var(--bg-tertiary); color: var(--text-secondary); padding: 16px 15px; text-align: left; font-weight: 800; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; border-bottom: 2px solid var(--border-color); }
.users-table td { padding: 14px 15px; border-bottom: 1px solid var(--border-color); color: var(--text-primary); font-size: 0.95rem; vertical-align: middle; }
.users-table tr:hover { background: var(--hover-bg); }
.col-descripcion { white-space: normal; word-break: break-word; }
.no-results { text-align: center; padding: 60px !important; color: var(--text-secondary); }

/* PANTALLA CAJA CERRADA */
.caja-cerrada-wrapper { display: flex; justify-content: center; padding: 40px 0; }
.caja-cerrada-card { background: var(--bg-primary); padding: 40px; border-radius: 20px; text-align: center; max-width: 500px; width: 100%; border: 1px solid var(--border-color); box-shadow: var(--shadow-md); }
.icono-bloqueo i { font-size: 5rem; color: #ef4444; opacity: 0.8; }
.caja-cerrada-card h2 { color: var(--text-primary); font-size: 1.8rem; margin: 10px 0; }
.caja-cerrada-card p { color: var(--text-secondary); margin-bottom: 30px; }

/* ALERTA HUERFANOS */
.alerta-huerfanos { background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; border-radius: 12px; padding: 20px; display: flex; gap: 15px; text-align: left; margin-bottom: 30px; align-items: flex-start; }
.alerta-huerfanos i { font-size: 1.5rem; color: #f59e0b; }
.alerta-content strong { display: block; color: #b45309; font-size: 1.1rem; margin-bottom: 5px; }
.alerta-content p { margin: 0; color: #92400e; font-size: 0.95rem; line-height: 1.4; }

/* FORMULARIOS Y FILTROS */
.filters-grid { display: grid; gap: 15px; }
.filter-group { text-align: left; display: flex; flex-direction: column; }
.filter-group label { font-weight: 700; margin-bottom: 8px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }

.filter-input, .filter-select { 
  padding: 12px 14px; 
  border: 2px solid var(--border-color); 
  border-radius: 10px; 
  background: var(--bg-primary); 
  color: var(--text-primary); 
  transition: all 0.3s; 
  font-size: 1rem; 
  width: 100%; 
  box-sizing: border-box;
}
.filter-select option {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.filter-input:focus, .filter-select:focus { outline: none; border-color: #0ea5e9; box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2); }
.clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 18px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: all 0.3s ease; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.8px; display: flex; align-items: center; gap: 6px; }
.clear-filters-btn:hover { background: var(--hover-bg); border-color: var(--text-secondary); }

/* INPUT CON SÍMBOLO $ */
.input-money-wrapper { position: relative; display: flex; align-items: center; }
.currency-symbol { position: absolute; left: 15px; color: var(--text-secondary); font-weight: bold; font-size: 1.1rem; pointer-events: none; }
.input-money { padding-left: 35px; font-weight: bold; font-size: 1.1rem; }

/* CAJA ABIERTA DASHBOARD */
.status-bar-caja { background: var(--bg-primary); padding: 20px 25px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border: 1px solid var(--border-color); }
.status-info { display: flex; align-items: center; gap: 15px; flex-wrap: wrap; }
.caja-nombre-txt { font-size: 1.2rem; font-weight: 900; color: var(--text-primary); }
.caja-usuario-txt { color: var(--text-secondary); font-size: 0.9rem; }
.btn-arqueo { padding: 10px 20px; border-radius: 10px; width: auto; font-size: 0.9rem; }

/* CARDS DE SALDOS */
.balances-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 40px; }
.balance-card { background: var(--bg-primary); padding: 25px; border-radius: 16px; border: 1px solid var(--border-color); display: flex; align-items: center; gap: 20px; transition: transform 0.3s; }
.balance-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.b-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 1.5rem; background: var(--bg-tertiary); color: var(--text-secondary); }
.b-data p { margin: 0 0 5px 0; color: var(--text-secondary); font-size: 0.85rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
.b-data h3 { margin: 0; color: var(--text-primary); font-size: 1.8rem; font-weight: 900; }

.balance-card.total-general { border: 2px solid var(--accent-color); background: rgba(14, 165, 233, 0.05); justify-content: flex-start;}
.balance-card.highlight .b-icon { background: #10b981; color: white; } 
.balance-card.mp .b-icon { background: #00a1f1; color: white; }
.balance-card.transfer .b-icon { background: #8b5cf6; color: white; }

/* RESUMEN ESPERADO EN EL MODAL DE CIERRE */
.resumen-esperado { background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 18px; margin-bottom: 25px; }
.resumen-esperado h4 { margin: 0 0 15px 0; color: var(--text-primary); font-size: 1rem; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;}
.resumen-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
.resumen-item { display: flex; flex-direction: column; gap: 5px; background: var(--bg-primary); padding: 12px; border-radius: 8px; border: 1px solid var(--border-color);}
.resumen-item span { font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; display: flex; align-items: center; gap: 5px;}
.resumen-item strong { font-size: 1.3rem; color: var(--text-primary); font-weight: 900; }

/* MODALES MEJORADOS */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.88); backdrop-filter: blur(5px); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeIn 0.2s ease; }
.modal-cierre { max-width: 600px !important; width: 90%; }
.modal-historial-amplio { max-width: 1100px !important; width: 95%; max-height: 90vh; display: flex; flex-direction: column; }
.historial-header { padding: 25px 30px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary); border-radius: 16px 16px 0 0; position: relative;}
.historial-header h2 { margin: 0 0 5px 0; color: var(--text-primary); font-size: 1.5rem; font-weight: 800; }
.historial-header p { margin: 0; color: var(--text-secondary); font-size: 1rem; }
.historial-body { padding: 30px; background: var(--bg-primary); border-radius: 0 0 16px 16px; flex: 1; overflow-y: auto;}

.modal-close { position: absolute; top: 20px; right: 20px; background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-secondary); border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; z-index: 10; }
.modal-close:hover { background: var(--error-color); color: white; border-color: var(--error-color); transform: rotate(90deg); }

.alerta-cierre { background: rgba(14, 165, 233, 0.1); border-left: 4px solid #0ea5e9; padding: 15px; margin-bottom: 20px; border-radius: 0 8px 8px 0; display: flex; gap: 12px; }
.alerta-cierre i { color: #0ea5e9; font-size: 1.5rem; }
.alerta-cierre p { margin: 0; color: var(--text-primary); font-size: 0.9rem; line-height: 1.5; }

/* PAGINACIÓN */
.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 25px; }
.pagination button { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 10px 20px; border-radius: 12px; cursor: pointer; font-weight: 800; transition: all 0.3s ease; font-size: 0.85rem; display: flex; align-items: center; gap: 8px; }
.pagination button:hover:not(:disabled) { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.pagination span { font-weight: bold; color: var(--text-secondary); }

/* Ajuste para columna de fondo inicial (opcional) */
.users-table td:nth-child(5) {
  white-space: normal;
  word-break: break-word;
  min-width: 140px;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

@media (max-width: 768px) {
  .list-card { padding: 20px; }
  .status-bar-caja { flex-direction: column; align-items: stretch; gap: 15px; }
  .btn-arqueo { width: 100%; }
}
</style>