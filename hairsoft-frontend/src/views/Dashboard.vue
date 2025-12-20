<template>
  <div class="dashboard-wrapper">
    
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">Dashboard - Reporte Comercial</h1>
        <p class="dashboard-subtitle">Análisis integral de ventas y servicios</p>
      </div>
      
      <div class="header-right">
        <div class="period-selector">
          <button 
            v-for="p in periods" 
            :key="p.value"
            :class="{ active: selectedPeriod === p.value && !customDateRange }"
            @click="selectPeriod(p.value)"
          >
            <i :class="p.icon"></i>
            {{ p.label }}
          </button>
          <button 
            :class="{ active: customDateRange }"
            @click="toggleCustomRange"
          >
            <i class="fas fa-calendar-alt"></i>
            Personalizado
          </button>
        </div>

        <div class="period-display">
          <i class="fas fa-calendar-check"></i>
          <span>{{ getPeriodDisplay }}</span>
        </div>

        <button @click="generatePDF" class="pdf-btn" :disabled="loading">
          <i class="fas fa-file-pdf"></i>
          Exportar Reporte Completo
        </button>
      </div>
    </header>

    <div v-if="customDateRange" class="custom-date-panel">
      <div class="custom-date-content">
        <div class="date-inputs">
          <div class="date-input-group">
            <label>
              <i class="fas fa-calendar-day"></i>
              Fecha Desde
            </label>
            <input 
              type="date" 
              v-model="dateFrom" 
              :max="dateTo || today"
              class="date-input-custom"
            />
          </div>
          <div class="date-input-group">
            <label>
              <i class="fas fa-calendar-day"></i>
              Fecha Hasta
            </label>
            <input 
              type="date" 
              v-model="dateTo" 
              :min="dateFrom"
              :max="today"
              class="date-input-custom"
            />
          </div>
          <button @click="applyCustomRange" class="apply-btn" :disabled="!dateFrom || !dateTo">
            <i class="fas fa-check"></i>
            Aplicar
          </button>
        </div>
        <div class="date-range-info" v-if="dateFrom && dateTo">
          <i class="fas fa-info-circle"></i>
          Mostrando datos desde <strong>{{ formatDateLong(dateFrom) }}</strong> hasta <strong>{{ formatDateLong(dateTo) }}</strong>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state-container">
      <div class="loader"></div>
      <p class="loading-text">Generando reporte...</p>
    </div>

    <div v-else-if="error" class="state-container error">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Error de Conexión</h3>
        <p>{{ error }}</p>
        <button @click="fetchDashboardData" class="retry-btn">
          <i class="fas fa-redo"></i>
          Reintentar
        </button>
      </div>
    </div>

    <main v-else class="dashboard-content fade-in" ref="dashboardContent">

      <div class="kpi-grid">
        
        <div class="kpi-card income">
          <div class="kpi-header-card">
            <div class="kpi-icon"><i class="fas fa-dollar-sign"></i></div>
          </div>
          <div class="kpi-data">
            <span class="label">Ingresos Totales</span>
            <span class="value">${{ formatNumber(dashboardData.ingresosTotales) }}</span>
            <span class="subtitle">Facturación del período</span>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none">
              <polyline points="0,18 20,15 40,10 60,12 80,6 100,4" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
        </div>

        <div class="kpi-card service">
          <div class="kpi-header-card">
            <div class="kpi-icon"><i class="fas fa-cut"></i></div>
          </div>
          <div class="kpi-data">
            <span class="label">Servicios Completados</span>
            <span class="value">{{ dashboardData.serviciosRealizados }}</span>
            <span class="subtitle">Turnos atendidos</span>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none">
              <polyline points="0,20 20,16 40,18 60,13 80,10 100,8" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
        </div>

        <div class="kpi-card product">
          <div class="kpi-header-card">
            <div class="kpi-icon"><i class="fas fa-shopping-bag"></i></div>
          </div>
          <div class="kpi-data">
            <span class="label">Productos Vendidos</span>
            <span class="value">{{ dashboardData.productosVendidos }}</span>
            <span class="subtitle">Unidades despachadas</span>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none">
              <polyline points="0,14 20,12 40,9 60,11 80,5 100,3" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
        </div>

        <div class="kpi-card clients">
          <div class="kpi-header-card">
            <div class="kpi-icon"><i class="fas fa-users"></i></div>
          </div>
          <div class="kpi-data">
            <span class="label">Clientes Atendidos</span>
            <span class="value">{{ dashboardData.clientesAtendidos || calcularClientes() }}</span>
            <span class="subtitle">Personas atendidas</span>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none">
              <polyline points="0,16 20,14 40,12 60,15 80,10 100,8" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
        </div>

      </div>

      <div class="section-card chart-section">
        <div class="section-header">
          <h3>
            <i class="fas fa-chart-line"></i> 
            Evolución de Ingresos Diarios
          </h3>
          <div class="chart-info">
            <span class="chart-legend">
              <i class="fas fa-circle" style="color: #ef4444"></i>
              Ingresos por día
            </span>
          </div>
        </div>
        <div class="chart-body">
          <div v-if="dashboardData.ventasPorDia.length" class="trading-chart-container">
            
            <svg class="chart-grid" :viewBox="`0 0 ${chartWidth} ${chartHeight}`">
              <g v-for="i in 5" :key="`ref-${i}`">
                <line 
                  :x1="60" :y1="(chartHeight / 5) * i"
                  :x2="chartWidth - 20" :y2="(chartHeight / 5) * i"
                  stroke="#475569" stroke-width="1" stroke-dasharray="5,5" opacity="0.6"/>
                <text 
                  :x="10" 
                  :y="(chartHeight / 5) * i + 5"
                  fill="#94a3b8"
                  font-size="11"
                  font-weight="600"
                  font-family="system-ui, -apple-system, sans-serif"
                >
                  ${{ formatNumberShort(Math.round((getMaxValue() / 5) * (5 - i))) }}
                </text>
              </g>
            </svg>

            <svg class="chart-svg" :viewBox="`0 0 ${chartWidth} ${chartHeight}`">
              <defs>
                <linearGradient id="areaGradientRed" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#ef4444;stop-opacity:0.35" />
                  <stop offset="50%" style="stop-color:#f87171;stop-opacity:0.15" />
                  <stop offset="100%" style="stop-color:#fca5a5;stop-opacity:0.05" />
                </linearGradient>
                
                <filter id="glowRed">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>

              <path :d="getAreaPath()" fill="url(#areaGradientRed)" class="chart-area"/>

              <path 
                :d="getLinePath()" 
                fill="none" 
                stroke="#ef4444" 
                stroke-width="4" 
                stroke-linecap="round"
                stroke-linejoin="round"
                opacity="0.25"
                filter="blur(6px)"
              />

              <path 
                :d="getLinePath()" 
                fill="none" 
                stroke="#ef4444" 
                stroke-width="3" 
                stroke-linecap="round"
                stroke-linejoin="round"
                class="chart-line-red"
                filter="url(#glowRed)"
              />

              <line 
                :x1="padding" 
                :y1="getYPosition(calculateAverageDaily())"
                :x2="chartWidth - padding" 
                :y2="getYPosition(calculateAverageDaily())"
                stroke="#10b981"
                stroke-width="2"
                stroke-dasharray="8,4"
                opacity="0.5"
              />

              <g v-for="(monto, i) in dashboardData.ventasPorDia" :key="`point-${i}`">
                <circle 
                  v-if="monto === Math.max(...dashboardData.ventasPorDia)"
                  :cx="getXPosition(i)" 
                  :cy="getYPosition(monto)"
                  r="9"
                  fill="#dc2626"
                  stroke="#ffffff"
                  stroke-width="3"
                  class="peak-point"
                />
                
                <circle 
                  :cx="getXPosition(i)" 
                  :cy="getYPosition(monto)"
                  r="12"
                  fill="#ef4444"
                  opacity="0.15"
                  class="point-glow"
                  :class="{ active: hoveredPoint === i }"
                />
                <circle 
                  :cx="getXPosition(i)" 
                  :cy="getYPosition(monto)"
                  r="6"
                  fill="#0f172a"
                  stroke="#ef4444"
                  stroke-width="3"
                  class="chart-point-red"
                  :class="{ active: hoveredPoint === i }"
                  @mouseenter="showTooltip(i, monto, $event)"
                  @mouseleave="hideTooltip"
                />
                <circle 
                  :cx="getXPosition(i)" 
                  :cy="getYPosition(monto)"
                  r="2"
                  fill="#fca5a5"
                  class="point-center"
                  :class="{ active: hoveredPoint === i }"
                />
              </g>
            </svg>

            <div class="chart-labels">
              <span 
                v-for="(label, i) in dashboardData.labelsDias" 
                :key="`label-${i}`"
                class="day-label"
                :class="{ active: hoveredPoint === i, peak: dashboardData.ventasPorDia[i] === Math.max(...dashboardData.ventasPorDia) }"
                :style="{ left: getXPositionPercent(i) + '%' }"
              >
                {{ label }}
                <span v-if="dashboardData.ventasPorDia[i] === Math.max(...dashboardData.ventasPorDia)" class="peak-badge">
                  <i class="fas fa-fire"></i>
                </span>
              </span>
            </div>

            <Transition name="tooltip">
              <div 
                v-if="tooltip.visible" 
                class="chart-tooltip"
                :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
              >
                <div class="tooltip-header">
                  <i class="fas fa-calendar-day"></i>
                  {{ tooltip.date }}
                  <span v-if="tooltip.value === Math.max(...dashboardData.ventasPorDia)" class="tooltip-badge">
                    <i class="fas fa-crown"></i> DÍA PICO
                  </span>
                </div>
                <div class="tooltip-body">
                  <div class="tooltip-value">${{ formatNumber(tooltip.value) }}</div>
                  <div class="tooltip-label">Ingresos del día</div>
                  <div class="tooltip-comparison" :class="getComparisonClass(tooltip.value)">
                    <i :class="getComparisonIcon(tooltip.value)"></i>
                    {{ getComparisonText(tooltip.value) }}
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <div v-else class="no-data">
            <i class="fas fa-chart-line"></i>
            <p>No hay ventas registradas en este período</p>
          </div>
        </div>
      </div>

      <div class="section-card distribution-card">
        <div class="section-header">
          <h3><i class="fas fa-chart-pie"></i> Distribución de Actividad</h3>
          <span class="subtitle-header">Proporción entre servicios y productos</span>
        </div>
        <div class="distribution-body">
          <div class="distribution-chart-container">
            <svg width="240" height="240" viewBox="0 0 200 200">
              <defs>
                <linearGradient id="pieGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#1d4ed8;stop-opacity:1" />
                </linearGradient>
                <linearGradient id="pieGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#047857;stop-opacity:1" />
                </linearGradient>
                <filter id="pieShadow">
                  <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.3"/>
                </filter>
              </defs>
              
              <circle cx="100" cy="100" r="85" fill="transparent" stroke="#334155" stroke-width="2" opacity="0.3"/>
              
              <path 
                :d="getPiePath(0, getServicePercentage())" 
                fill="url(#pieGradient2)"
                class="pie-sector"
                filter="url(#pieShadow)"
              />
              
              <path 
                :d="getPiePath(getServicePercentage(), 100)" 
                fill="url(#pieGradient1)"
                class="pie-sector"
                filter="url(#pieShadow)"
              />
              
              <circle cx="100" cy="100" r="45" fill="#1e293b"/>
              
              <text x="100" y="92" text-anchor="middle" fill="#f1f5f9" font-size="20" font-weight="800">
                {{ getTotalTransactions() }}
              </text>
              <text x="100" y="112" text-anchor="middle" fill="#94a3b8" font-size="13" font-weight="600">
                TOTAL
              </text>
            </svg>
          </div>
          <div class="distribution-legend">
            <div class="legend-item">
              <div class="legend-color service"></div>
              <div class="legend-content">
                <span class="legend-label">Servicios</span>
                <span class="legend-value">{{ dashboardData.serviciosRealizados }} turnos</span>
                <span class="legend-percentage">{{ getServicePercentage().toFixed(1) }}%</span>
              </div>
            </div>
            <div class="legend-item">
              <div class="legend-color product"></div>
              <div class="legend-content">
                <span class="legend-label">Productos</span>
                <span class="legend-value">{{ dashboardData.productosVendidos }} unidades</span>
                <span class="legend-percentage">{{ getProductPercentage().toFixed(1) }}%</span>
              </div>
            </div>
            <div class="distribution-insight">
              <i class="fas fa-lightbulb"></i>
              <span v-if="getServicePercentage() > getProductPercentage()">
                Los servicios dominan la actividad con un <strong>{{ (getServicePercentage() - getProductPercentage()).toFixed(1) }}%</strong> de diferencia
              </span>
              <span v-else-if="getProductPercentage() > getServicePercentage()">
                Los productos dominan la actividad con un <strong>{{ (getProductPercentage() - getServicePercentage()).toFixed(1) }}%</strong> de diferencia
              </span>
              <span v-else>
                Balance perfecto entre servicios y productos
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="top-section">
        <h3 class="section-title"><i class="fas fa-trophy"></i> Análisis de Desempeño</h3>
        <p class="section-subtitle">Top performers del período seleccionado</p>
        
        <div class="top-grid">
          
          <div class="section-card top-card">
            <div class="section-header">
              <h3><i class="fas fa-star"></i> Servicios Más Solicitados</h3>
              <span class="total-count">Total: {{ getTotalServices() }}</span>
            </div>
            <div class="list-body">
              <div class="list-item" v-for="(s, i) in dashboardData.serviciosTop" :key="i">
                <div class="rank" :class="getRankClass(i)">
                  <i v-if="i === 0" class="fas fa-crown"></i>
                  <span v-else>{{ i + 1 }}</span>
                </div>
                <div class="item-content">
                  <div class="item-header">
                    <div class="item-name">{{ s.nombre }}</div>
                    <div class="item-percentage">{{ getItemPercentage(s.cantidad, dashboardData.serviciosTop) }}%</div>
                  </div>
                  <div class="item-progress">
                    <div class="progress-bar">
                      <div 
                        class="progress-fill service" 
                        :style="{ width: getPercentage(s.cantidad, dashboardData.serviciosTop) + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
                <div class="item-count">{{ s.cantidad }} turnos</div>
              </div>
              <div v-if="!dashboardData.serviciosTop.length" class="no-data-text">
                <i class="fas fa-inbox"></i>
                Sin servicios registrados
              </div>
            </div>
          </div>

          <div class="section-card top-card">
            <div class="section-header">
              <h3><i class="fas fa-fire"></i> Productos Más Vendidos</h3>
              <span class="total-count">Total: {{ dashboardData.productosVendidos }} unidades</span>
            </div>
            <div class="list-body">
              <div class="list-item" v-for="(p, i) in dashboardData.productosTop" :key="i">
                <div class="rank" :class="getRankClass(i)">
                  <i v-if="i === 0" class="fas fa-crown"></i>
                  <span v-else>{{ i + 1 }}</span>
                </div>
                <div class="item-content">
                  <div class="item-header">
                    <div class="item-name">{{ p.nombre }}</div>
                    <div class="item-percentage">{{ getItemPercentage(p.cantidad, dashboardData.productosTop) }}%</div>
                  </div>
                  <div class="item-progress">
                    <div class="progress-bar">
                      <div 
                        class="progress-fill product" 
                        :style="{ width: getPercentage(p.cantidad, dashboardData.productosTop) + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
                <div class="item-count">{{ p.cantidad }} u.</div>
              </div>
              <div v-if="!dashboardData.productosTop.length" class="no-data-text">
                <i class="fas fa-inbox"></i>
                Sin productos vendidos
              </div>
            </div>
          </div>

        </div>
      </div>

      <div class="stats-grid">
        
        <div class="section-card stat-card">
          <div class="section-header">
            <h3><i class="fas fa-box-open"></i> Estado de Inventario</h3>
          </div>
          <div class="stat-body">
            <div class="stat-item">
              <div class="stat-label">Productos en stock bajo</div>
              <div class="stat-value" :class="{ 'warning': dashboardData.stockBajoCount > 0 }">
                {{ dashboardData.stockBajoCount }}
              </div>
            </div>
            <button 
              v-if="dashboardData.stockBajoCount > 0" 
              @click="irAInventario" 
              class="action-btn full-width"
            >
              <i class="fas fa-boxes"></i>
              Revisar Inventario Crítico
            </button>
          </div>
        </div>

        <div class="section-card stat-card insights-card">
          <div class="section-header">
            <h3><i class="fas fa-lightbulb"></i> Información del período</h3>
          </div>
          <div class="insights-body">
            <div class="insight-item" v-if="dashboardData.serviciosTop.length > 0">
              <i class="fas fa-medal"></i>
              <div class="insight-content">
                <strong>Servicio estrella:</strong> {{ dashboardData.serviciosTop[0]?.nombre }}
              </div>
            </div>
            <div class="insight-item" v-if="dashboardData.productosTop.length > 0">
              <i class="fas fa-shopping-bag"></i>
              <div class="insight-content">
                <strong>Producto top:</strong> {{ dashboardData.productosTop[0]?.nombre }}
              </div>
            </div>
            <div class="insight-item">
              <i class="fas fa-chart-line"></i>
              <div class="insight-content">
                <strong>Mejor día:</strong> {{ getPeakDay() }} (${{ formatNumber(Math.max(...dashboardData.ventasPorDia)) }})
              </div>
            </div>
          </div>
        </div>

      </div>

    </main>

    <div id="print-template" style="display: none;">
      <div class="pdf-page">
        <div class="pdf-header">
          <h1 class="pdf-title">HAIRSOFT</h1>
          <h2 class="pdf-subtitle">Los Últimos Serán Los Primeros</h2>
          <div class="pdf-divider"></div>
          <h3 class="pdf-report-title">Reporte de Gestión</h3>
          <p class="pdf-period">{{ getPeriodDisplay }}</p>
        </div>

        <div class="pdf-kpis">
          <div class="pdf-kpi">
            <div class="pdf-kpi-label">Ingresos</div>
            <div class="pdf-kpi-value">${{ formatNumber(dashboardData.ingresosTotales) }}</div>
          </div>
          <div class="pdf-kpi">
            <div class="pdf-kpi-label">Servicios</div>
            <div class="pdf-kpi-value">{{ dashboardData.serviciosRealizados }}</div>
          </div>
          <div class="pdf-kpi">
            <div class="pdf-kpi-label">Productos</div>
            <div class="pdf-kpi-value">{{ dashboardData.productosVendidos }}</div>
          </div>
          <div class="pdf-kpi">
            <div class="pdf-kpi-label">Clientes</div>
            <div class="pdf-kpi-value">{{ dashboardData.clientesAtendidos || calcularClientes() }}</div>
          </div>
        </div>

        <div class="pdf-chart-section">
          <h4 class="pdf-section-title">Evolución de Ingresos Diarios</h4>
          <svg class="pdf-chart" :viewBox="`0 0 ${chartWidth} ${chartHeight + 60}`" width="100%" height="380">
            <defs>
              <linearGradient id="pdfAreaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#ef4444;stop-opacity:0.35" />
                <stop offset="100%" style="stop-color:#fca5a5;stop-opacity:0.08" />
              </linearGradient>
            </defs>

            <g v-for="i in 5" :key="`pdf-ref-${i}`">
              <line 
                :x1="60" :y1="(chartHeight / 5) * i"
                :x2="chartWidth - 20" :y2="(chartHeight / 5) * i"
                stroke="#d1d5db" stroke-width="2" stroke-dasharray="6,4"/>
              <text 
                :x="10" 
                :y="(chartHeight / 5) * i + 6"
                fill="#1f2937"
                font-size="14"
                font-weight="700"
              >
                ${{ formatNumberShort(Math.round((getMaxValue() / 5) * (5 - i))) }}
              </text>
            </g>

            <path :d="getAreaPath()" fill="url(#pdfAreaGradient)"/>

            <path 
              :d="getLinePath()" 
              fill="none" 
              stroke="#dc2626" 
              stroke-width="4" 
              stroke-linecap="round"
              stroke-linejoin="round"
            />

            <g v-for="(monto, i) in dashboardData.ventasPorDia" :key="`pdf-point-${i}`">
              <circle 
                :cx="getXPosition(i)" 
                :cy="getYPosition(monto)"
                r="6"
                fill="#ffffff"
                stroke="#dc2626"
                stroke-width="3"
              />
            </g>

            <g v-for="(label, i) in dashboardData.labelsDias" :key="`pdf-label-${i}`">
              <text
                :x="getXPosition(i)"
                :y="chartHeight - 20"
                text-anchor="middle"
                fill="#1f2937"
                font-size="13"
                font-weight="700"
              >
                {{ label }}
              </text>
            </g>
          </svg>
        </div>

        <div class="pdf-tables">
          <div class="pdf-table-container">
            <h4 class="pdf-section-title">Top 5 Servicios</h4>
            <table class="pdf-table">
              <thead>
                <tr>
                  <th style="width: 10%">#</th>
                  <th style="width: 60%">Servicio</th>
                  <th style="width: 20%">Cant.</th>
                  <th style="width: 10%">%</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(s, i) in dashboardData.serviciosTop.slice(0, 5)" :key="i">
                  <td>{{ i + 1 }}</td>
                  <td>{{ s.nombre }}</td>
                  <td>{{ s.cantidad }}</td>
                  <td>{{ getItemPercentage(s.cantidad, dashboardData.serviciosTop) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pdf-table-container">
            <h4 class="pdf-section-title">Top 5 Productos</h4>
            <table class="pdf-table">
              <thead>
                <tr>
                  <th style="width: 10%">#</th>
                  <th style="width: 60%">Producto</th>
                  <th style="width: 20%">Unid.</th>
                  <th style="width: 10%">%</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(p, i) in dashboardData.productosTop.slice(0, 5)" :key="i">
                  <td>{{ i + 1 }}</td>
                  <td>{{ p.nombre }}</td>
                  <td>{{ p.cantidad }}</td>
                  <td>{{ getItemPercentage(p.cantidad, dashboardData.productosTop) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="pdf-footer">
          <p>HAIRSOFT © {{ new Date().getFullYear() }} - Reporte generado el {{ new Date().toLocaleDateString('es-AR') }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axiosConfig'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

const router = useRouter()
const selectedPeriod = ref('semana')
const loading = ref(true)
const error = ref(null)
const hoveredPoint = ref(null)
const dashboardContent = ref(null)

const customDateRange = ref(false)
const dateFrom = ref('')
const dateTo = ref('')
const today = new Date().toISOString().split('T')[0]

const periods = [
  { value: 'hoy', label: 'Hoy', icon: 'fas fa-clock' },
  { value: 'semana', label: '7 Días', icon: 'fas fa-calendar-week' },
  { value: 'mes', label: 'Este Mes', icon: 'fas fa-calendar-alt' },
]

const dashboardData = ref({
  ingresosTotales: 0,
  serviciosRealizados: 0,
  productosVendidos: 0,
  stockBajoCount: 0,
  ventasPorDia: [],
  labelsDias: [],
  serviciosTop: [],
  productosTop: [],
  clientesAtendidos: 0,
  inventarioTotal: 0,
  valorInventario: 0
})

const getPeriodDisplay = computed(() => {
  if (customDateRange.value && dateFrom.value && dateTo.value) {
    return `${formatDate(dateFrom.value)} al ${formatDate(dateTo.value)}`
  }
  const period = periods.find(p => p.value === selectedPeriod.value)
  return period ? period.label : 'Período'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const chartWidth = 900
const chartHeight = 320
const padding = 60

const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  value: 0,
  date: '',
  index: 0
})

const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  try {
    const params = customDateRange.value && dateFrom.value && dateTo.value
      ? { date_from: dateFrom.value, date_to: dateTo.value }
      : { period: selectedPeriod.value }
    
    const res = await axios.get('/usuarios/api/dashboard/', { params })
    dashboardData.value = { ...dashboardData.value, ...res.data }
  } catch (err) {
    console.error(err)
    error.value = "Error al conectar con el servidor."
  } finally {
    loading.value = false
  }
}

const selectPeriod = (period) => {
  customDateRange.value = false
  selectedPeriod.value = period
  fetchDashboardData()
}

const toggleCustomRange = () => {
  customDateRange.value = !customDateRange.value
  if (!customDateRange.value) {
    fetchDashboardData()
  }
}

const applyCustomRange = () => {
  if (dateFrom.value && dateTo.value) {
    fetchDashboardData()
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'short'
  })
}

const formatDateLong = (dateStr) => {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
}

const formatNumber = (num) => new Intl.NumberFormat('es-AR').format(num || 0)

const formatNumberShort = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const calculateAverageDaily = () => {
  if (!dashboardData.value.ventasPorDia.length) return 0
  const sum = dashboardData.value.ventasPorDia.reduce((a, b) => a + b, 0)
  return sum / dashboardData.value.ventasPorDia.length
}

const getPeakDay = () => {
  if (!dashboardData.value.ventasPorDia.length) return '--'
  const maxValue = Math.max(...dashboardData.value.ventasPorDia)
  const index = dashboardData.value.ventasPorDia.indexOf(maxValue)
  return dashboardData.value.labelsDias[index] || '--'
}

const getMaxValue = () => {
  return Math.max(...dashboardData.value.ventasPorDia, 1)
}

const getXPosition = (index) => {
  const count = dashboardData.value.ventasPorDia.length
  if (count <= 1) return chartWidth / 2
  return padding + (index / (count - 1)) * (chartWidth - padding * 2)
}

const getXPositionPercent = (index) => {
  const count = dashboardData.value.ventasPorDia.length
  if (count <= 1) return 50
  return (padding / chartWidth * 100) + (index / (count - 1)) * ((chartWidth - padding * 2) / chartWidth * 100)
}

const getYPosition = (value) => {
  const max = getMaxValue()
  const normalized = value / max
  return chartHeight - padding - (normalized * (chartHeight - padding * 2))
}

const getLinePath = () => {
  if (!dashboardData.value.ventasPorDia.length) return ''
  
  let path = ''
  dashboardData.value.ventasPorDia.forEach((value, i) => {
    const x = getXPosition(i)
    const y = getYPosition(value)
    
    if (i === 0) {
      path += `M ${x} ${y}`
    } else {
      const prevX = getXPosition(i - 1)
      const prevY = getYPosition(dashboardData.value.ventasPorDia[i - 1])
      const cpX = (prevX + x) / 2
      
      path += ` Q ${cpX} ${prevY}, ${x} ${y}`
    }
  })
  
  return path
}

const getAreaPath = () => {
  if (!dashboardData.value.ventasPorDia.length) return ''
  
  let path = getLinePath()
  
  const lastX = getXPosition(dashboardData.value.ventasPorDia.length - 1)
  const firstX = getXPosition(0)
  
  path += ` L ${lastX} ${chartHeight - padding}`
  path += ` L ${firstX} ${chartHeight - padding}`
  path += ' Z'
  
  return path
}

const getPiePath = (startPercent, endPercent) => {
  const startAngle = (startPercent / 100) * 360
  const endAngle = (endPercent / 100) * 360
  
  const cx = 100
  const cy = 100
  const r = 80
  
  const startRad = (startAngle - 90) * Math.PI / 180
  const endRad = (endAngle - 90) * Math.PI / 180
  
  const x1 = cx + r * Math.cos(startRad)
  const y1 = cy + r * Math.sin(startRad)
  const x2 = cx + r * Math.cos(endRad)
  const y2 = cy + r * Math.sin(endRad)
  
  const largeArc = endAngle - startAngle > 180 ? 1 : 0
  
  return `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`
}

const getServicePercentage = () => {
  const total = dashboardData.value.serviciosRealizados + dashboardData.value.productosVendidos
  if (total === 0) return 50
  return (dashboardData.value.serviciosRealizados / total) * 100
}

const getProductPercentage = () => {
  return 100 - getServicePercentage()
}

const getTotalServices = () => {
  return dashboardData.value.serviciosTop.reduce((sum, item) => sum + item.cantidad, 0)
}

const getTotalTransactions = () => {
  return dashboardData.value.serviciosRealizados + dashboardData.value.productosVendidos
}

const showTooltip = (index, value, event) => {
  hoveredPoint.value = index
  const rect = event.target.getBoundingClientRect()
  const container = event.target.closest('.trading-chart-container').getBoundingClientRect()
  
  tooltip.value = {
    visible: true,
    x: rect.left - container.left,
    y: rect.top - container.top - 90,
    value: value,
    date: dashboardData.value.labelsDias[index],
    index: index
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
  hoveredPoint.value = null
}

const getComparisonClass = (value) => {
  const avg = calculateAverageDaily()
  if (value > avg * 1.2) return 'positive'
  if (value < avg * 0.8) return 'negative'
  return 'neutral'
}

const getComparisonIcon = (value) => {
  const avg = calculateAverageDaily()
  if (value > avg * 1.2) return 'fas fa-arrow-up'
  if (value < avg * 0.8) return 'fas fa-arrow-down'
  return 'fas fa-equals'
}

const getComparisonText = (value) => {
  const avg = calculateAverageDaily()
  const diff = ((value - avg) / avg) * 100
  if (value > avg * 1.2) return `${diff.toFixed(1)}% sobre el promedio`
  if (value < avg * 0.8) return `${Math.abs(diff).toFixed(1)}% bajo el promedio`
  return 'En línea con el promedio'
}

const getRankClass = (index) => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

const getPercentage = (value, array) => {
  const max = Math.max(...array.map(item => item.cantidad))
  return max > 0 ? (value / max) * 100 : 0
}

const getItemPercentage = (value, array) => {
  const total = array.reduce((sum, item) => sum + item.cantidad, 0)
  return total > 0 ? ((value / total) * 100).toFixed(1) : '0.0'
}

const calcularClientes = () => {
  return Math.round((dashboardData.value.serviciosRealizados + dashboardData.value.productosVendidos) / 2)
}

const irAInventario = () => {
  router.push({ path: '/productos', query: { filtro: 'stock_bajo' } })
}

const generatePDF = async () => {
  try {
    loading.value = true
    
    const printTemplate = document.getElementById('print-template')
    if (!printTemplate) {
      throw new Error('Template de impresión no encontrado')
    }

    printTemplate.style.display = 'block'
    printTemplate.style.width = '210mm'
    printTemplate.style.minHeight = '297mm'
    
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const canvas = await html2canvas(printTemplate, {
      scale: 3,
      backgroundColor: '#ffffff',
      logging: false,
      useCORS: true,
      allowTaint: true,
      width: 794,
      height: 1123,
      windowWidth: 794,
      windowHeight: 1123
    })
    
    printTemplate.style.display = 'none'
    
    const imgData = canvas.toDataURL('image/jpeg', 1.0)
    const pdf = new jsPDF('p', 'mm', 'a4')
    
    pdf.addImage(imgData, 'JPEG', 0, 0, 210, 297, '', 'FAST')
    
    const filename = `Reporte_HAIRSOFT_${selectedPeriod.value}_${Date.now()}.pdf`
    pdf.save(filename)
    
  } catch (err) {
    console.error('Error generando PDF:', err)
    alert('Error al generar el PDF. Por favor, intente nuevamente.')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchDashboardData())
</script>

<style scoped>
:root {
  --bg-dark: #0f172a;
  --bg-card: #1e293b;
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --accent: #3b82f6;
  --border: #334155;
  --positive: #10b981;
  --negative: #ef4444;
  --warning: #f59e0b;
}

.dashboard-wrapper {
  background: linear-gradient(135deg, #0f172a 0%, #0f172a 100%);
  min-height: 100vh;
  color: #f1f5f9;
  padding: 2rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
  position: relative;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1.5rem;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.dashboard-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard-subtitle {
  color: #94a3b8;
  margin: 0.5rem 0 0;
  font-size: 0.95rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.period-display {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #60a5fa;
  display: flex;
  align-items: center;
  gap: 8px;
}

.period-selector {
  background: rgba(15, 23, 42, 0.8);
  border-radius: 12px;
  padding: 6px;
  border: 1px solid #334155;
  display: flex;
  gap: 4px;
}

.period-selector button {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.period-selector button.active {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.period-selector button:hover:not(.active) {
  background: rgba(59, 130, 246, 0.1);
  color: white;
}

.pdf-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
}

.pdf-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.6);
}

.pdf-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.custom-date-panel {
  margin-bottom: 2rem;
  animation: slideDown 0.3s ease-out;
}

.custom-date-content {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 1px solid #334155;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}

.date-inputs {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.date-input-group {
  flex: 1;
  min-width: 200px;
}

.date-input-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #94a3b8;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.date-input-custom {
  width: 100%;
  background: rgba(15, 23, 42, 0.8);
  border: 2px solid #334155;
  border-radius: 10px;
  padding: 12px 16px;
  color: #f1f5f9;
  font-size: 0.95rem;
  font-weight: 600;
  font-family: 'Segoe UI', system-ui, sans-serif;
  transition: all 0.3s;
  cursor: pointer;
}

.date-input-custom:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.date-input-custom:hover {
  border-color: #475569;
}

.date-input-custom::-webkit-calendar-picker-indicator {
  filter: invert(0.8);
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.date-input-custom::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

.apply-btn {
  background: linear-gradient(135deg, #10b981 0%, #047857 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  white-space: nowrap;
}

.apply-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.6);
}

.apply-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.date-range-info {
  margin-top: 1rem;
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #60a5fa;
}

.date-range-info strong {
  color: #3b82f6;
  font-weight: 700;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 18px;
  padding: 1.5rem;
  border: 1px solid #334155;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, currentColor, transparent);
  opacity: 0;
  transition: opacity 0.4s;
}

.kpi-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  border-color: currentColor;
}

.kpi-card:hover::before {
  opacity: 1;
}

.income { color: #10b981; }
.service { color: #3b82f6; }
.product { color: #f97316; }
.clients { color: #8b5cf6; }

.kpi-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.kpi-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  transition: all 0.4s;
  position: relative;
  overflow: hidden;
}

.kpi-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  background: currentColor;
  opacity: 0.1;
}

.kpi-card:hover .kpi-icon {
  transform: scale(1.1) rotate(5deg);
}

.kpi-data {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.kpi-data .label {
  font-size: 0.9rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 700;
}

.kpi-data .value {
  font-size: 2.5rem;
  font-weight: 900;
  color: white;
  line-height: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.kpi-data .subtitle {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.kpi-sparkline {
  height: 40px;
  width: 100%;
  margin-top: 1rem;
  opacity: 0.4;
  transition: opacity 0.3s;
}

.kpi-card:hover .kpi-sparkline {
  opacity: 0.8;
}

.section-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 18px;
  border: 1px solid #334155;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 2rem;
}

.section-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #334155;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #f1f5f9;
}

.subtitle-header {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 600;
  font-style: italic;
}

.chart-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chart-legend {
  font-size: 0.85rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.chart-body {
  padding: 2rem;
  background: linear-gradient(to bottom, rgba(239, 68, 68, 0.02), transparent);
}

.trading-chart-container {
  position: relative;
  width: 100%;
  height: 380px;
  padding: 20px 0 60px 0;
}

.chart-grid,
.chart-svg {
  position: absolute;
  top: 20px;
  left: 0;
  width: 100%;
  height: calc(100% - 80px);
}

.chart-grid {
  pointer-events: none;
}

.chart-area {
  opacity: 0;
  animation: fadeInArea 1.5s ease-out 0.3s forwards;
}

.chart-line-red {
  stroke-dasharray: 3000;
  stroke-dashoffset: 3000;
  animation: drawLine 2s ease-out forwards;
}

.chart-point-red {
  transition: all 0.3s;
  cursor: pointer;
}

.chart-point-red:hover,
.chart-point-red.active {
  r: 8;
  stroke-width: 4;
}

.point-glow.active {
  opacity: 0.3;
  r: 16;
}

.point-center.active {
  r: 3;
}

.peak-point {
  animation: pulse 2s infinite;
  filter: drop-shadow(0 0 8px #dc2626);
}

@keyframes pulse {
  0%, 100% {
    r: 9;
    opacity: 1;
  }
  50% {
    r: 11;
    opacity: 0.8;
  }
}

@keyframes drawLine {
  to {
    stroke-dashoffset: 0;
  }
}

@keyframes fadeInArea {
  to {
    opacity: 1;
  }
}

.chart-labels {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  display: flex;
  padding: 0 60px;
}

.day-label {
  position: absolute;
  transform: translateX(-50%);
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.day-label.active {
  color: #ef4444;
  transform: translateX(-50%) scale(1.15);
}

.day-label.peak {
  color: #ef4444;
}

.peak-badge {
  font-size: 0.7rem;
  background: rgba(239, 68, 68, 0.2);
  padding: 2px 6px;
  border-radius: 10px;
  color: #fca5a5;
}

.chart-tooltip {
  position: absolute;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 2px solid #ef4444;
  border-radius: 16px;
  padding: 0;
  pointer-events: none;
  z-index: 1000;
  min-width: 200px;
  box-shadow: 0 20px 50px rgba(239, 68, 68, 0.5);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.tooltip-enter-active,
.tooltip-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}

.tooltip-header {
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.2);
  border-bottom: 1px solid rgba(239, 68, 68, 0.3);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8rem;
  font-weight: 800;
  color: #fca5a5;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.tooltip-badge {
  margin-left: auto;
  background: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tooltip-body {
  padding: 16px;
  text-align: center;
}

.tooltip-value {
  font-size: 2rem;
  font-weight: 900;
  color: #fca5a5;
  line-height: 1;
  margin-bottom: 8px;
  text-shadow: 0 2px 8px rgba(239, 68, 68, 0.5);
}

.tooltip-label {
  font-size: 0.8rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 12px;
  font-weight: 600;
}

.tooltip-comparison {
  font-size: 0.8rem;
  padding: 8px 12px;
  border-radius: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tooltip-comparison.positive {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.tooltip-comparison.negative {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.tooltip-comparison.neutral {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.distribution-body {
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.distribution-chart-container {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.pie-sector {
  transition: transform 0.3s;
}

.pie-sector:hover {
  transform: scale(1.05);
  transform-origin: center;
}

.distribution-legend {
  flex: 1;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.3s;
}

.legend-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(5px);
}

.legend-color {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  flex-shrink: 0;
}

.legend-color.service {
  background: linear-gradient(135deg, #10b981, #047857);
}

.legend-color.product {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.legend-content {
  flex: 1;
}

.legend-label {
  display: block;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 4px;
}

.legend-value {
  display: block;
  font-size: 0.9rem;
  color: #94a3b8;
  font-weight: 600;
}

.legend-percentage {
  display: block;
  font-size: 1.3rem;
  font-weight: 900;
  color: #3b82f6;
  margin-top: 4px;
}

.distribution-insight {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #60a5fa;
  font-weight: 600;
}

.top-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-subtitle {
  color: #94a3b8;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.top-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.total-count {
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 20px;
}

.list-body {
  padding: 0;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #334155;
  transition: all 0.3s;
}

.list-item:hover {
  background: rgba(59, 130, 246, 0.05);
  padding-left: 2rem;
}

.list-item:last-child {
  border-bottom: none;
}

.rank {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 900;
  background: #334155;
  color: #94a3b8;
  flex-shrink: 0;
  transition: all 0.3s;
}

.rank.gold {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #78350f;
  box-shadow: 0 6px 20px rgba(251, 191, 36, 0.4);
}

.rank.silver {
  background: linear-gradient(135deg, #e5e7eb 0%, #9ca3af 100%);
  color: #374151;
  box-shadow: 0 6px 20px rgba(156, 163, 175, 0.3);
}

.rank.bronze {
  background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%);
  color: #7c2d12;
  box-shadow: 0 6px 20px rgba(251, 146, 60, 0.3);
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-name {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-percentage {
  font-size: 0.85rem;
  font-weight: 800;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.item-progress {
  width: 100%;
}

.progress-bar {
  height: 8px;
  background: rgba(148, 163, 184, 0.15);
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fillBar 2s ease-out;
}

.progress-fill.service {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.progress-fill.product {
  background: linear-gradient(90deg, #f97316 0%, #fb923c 100%);
}

.item-count {
  font-weight: 900;
  color: #f1f5f9;
  font-size: 1.1rem;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 12px;
  min-width: 80px;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-body {
  padding: 1.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 0.9rem;
  color: #94a3b8;
  font-weight: 600;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 800;
  color: #f1f5f9;
}

.stat-value.warning {
  color: #f59e0b;
  animation: pulseWarning 2s infinite;
}

@keyframes pulseWarning {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.insights-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}

.insight-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  transition: all 0.3s;
}

.insight-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(5px);
}

.insight-item i {
  color: #3b82f6;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
  font-size: 0.9rem;
  color: #94a3b8;
  line-height: 1.5;
}

.insight-content strong {
  color: #f1f5f9;
  font-weight: 700;
}

.action-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  width: 100%;
  margin-top: 1rem;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.6);
}

.state-container {
  height: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
}

.loader {
  width: 60px;
  height: 60px;
  border: 5px solid #334155;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s infinite linear;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: #94a3b8;
  font-weight: 700;
  letter-spacing: 0.8px;
  font-size: 1.1rem;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  text-align: center;
  padding: 3rem;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 20px;
  border: 2px solid rgba(239, 68, 68, 0.2);
}

.error-content i {
  font-size: 5rem;
  color: #ef4444;
}

.error-content h3 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: #f1f5f9;
}

.error-content p {
  margin: 0;
  color: #fca5a5;
  max-width: 400px;
  line-height: 1.6;
}

.retry-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-size: 0.9rem;
}

.retry-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.6);
}

.fade-in {
  animation: fadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fillBar {
  from {
    width: 0;
  }
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #64748b;
  gap: 1rem;
}

.no-data i {
  font-size: 3rem;
  opacity: 0.5;
}

.no-data-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #64748b;
}

.no-data-text i {
  font-size: 2rem;
  opacity: 0.5;
}

.pdf-page {
  width: 210mm;
  min-height: 297mm;
  background: white;
  padding: 18mm 20mm;
  box-sizing: border-box;
  font-family: 'Segoe UI', Arial, sans-serif;
  color: #000;
}

.pdf-header {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 4px solid #000;
}

.pdf-title {
  font-size: 56px;
  font-weight: 900;
  margin: 0;
  color: #000;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.pdf-subtitle {
  font-size: 20px;
  color: #666;
  margin: 10px 0 16px;
  font-weight: 600;
  font-style: italic;
}

.pdf-divider {
  width: 100px;
  height: 4px;
  background: linear-gradient(90deg, #ef4444, #dc2626);
  margin: 16px auto;
}

.pdf-report-title {
  font-size: 34px;
  font-weight: 800;
  margin: 14px 0 8px;
  color: #000;
}

.pdf-period {
  font-size: 18px;
  color: #374151;
  margin: 6px 0;
  font-weight: 700;
}

.pdf-kpis {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 22px 0;
}

.pdf-kpi {
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
}

.pdf-kpi-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 700;
  margin-bottom: 10px;
}

.pdf-kpi-value {
  font-size: 32px;
  font-weight: 900;
  color: #000;
  line-height: 1;
}

.pdf-chart-section {
  margin: 22px 0;
  padding: 20px;
  background: #fafafa;
  border-radius: 14px;
  border: 2px solid #e5e7eb;
}

.pdf-section-title {
  font-size: 20px;
  font-weight: 800;
  color: #000;
  margin: 0 0 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e5e7eb;
}

.pdf-chart {
  width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
  background: white;
  border-radius: 10px;
  padding: 16px 12px;
  border: 2px solid #e5e7eb;
}

.pdf-tables {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
  margin: 22px 0;
}

.pdf-table-container {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 18px;
}

.pdf-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}

.pdf-table thead {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
}

.pdf-table th {
  padding: 10px 8px;
  text-align: left;
  font-size: 11px;
  font-weight: 800;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  border-bottom: 2px solid #d1d5db;
}

.pdf-table td {
  padding: 10px 8px;
  font-size: 13px;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.pdf-table tbody tr:last-child td {
  border-bottom: none;
}

.pdf-table td:first-child {
  font-weight: 700;
}

.pdf-table td:last-child {
  font-weight: 800;
  color: #ef4444;
}

.pdf-footer {
  margin-top: 24px;
  padding-top: 14px;
  border-top: 2px solid #e5e7eb;
  text-align: center;
  color: #6b7280;
  font-size: 11px;
}

.pdf-footer p {
  margin: 5px 0;
}

@media (max-width: 768px) {
  .dashboard-wrapper {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
  }
  
  .header-right {
    flex-direction: column;
    gap: 1rem;
  }
  
  .period-selector {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .pdf-btn {
    width: 100%;
    justify-content: center;
  }
  
  .date-inputs {
    flex-direction: column;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .top-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .distribution-body {
    flex-direction: column;
    text-align: center;
  }
  
  .pdf-kpis {
    grid-template-columns: repeat(2, 1fr);
  }

  .pdf-tables {
    grid-template-columns: 1fr;
  }
}
</style>