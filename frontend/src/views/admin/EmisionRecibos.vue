<template>
  <AdminLayout
    titulo="Emisión y Facturación de Recibos"
    subtitulo="Gestión de recibos mensuales por apartamento y residente con consulta de comprobantes de pago"
  >
    <!-- Panel Superior: Generador Masivo de Cuotas -->
    <div class="mb-8">
      <NeuCard>
        <h3 class="text-lg font-bold text-neu-green mb-2">⚡ Emisión Masiva de Cuota Mensual</h3>
        <p class="text-xs text-neu-text-light mb-4">
          Ingrese el monto total de gastos comunes en USD para el mes. El sistema calculará la cuota exacta de cada apartamento según su alícuota registrada.
        </p>

        <form @submit.prevent="ejecutarEmision" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 items-end">
          <NeuInput
            id="periodo"
            label="Período / Mes (YYYY-MM)"
            v-model="emisionForm.periodo"
            placeholder="2026-09"
            required
          />

          <NeuInput
            id="gasto_total"
            label="Gasto Total del Mes ($ USD)"
            v-model="emisionForm.gasto_total_usd"
            type="number"
            step="0.01"
            min="1"
            placeholder="Ej. 1200.00"
            required
          />

          <NeuInput
            id="dias_vencimiento"
            label="Días para Vencimiento"
            v-model="emisionForm.dias_vencimiento"
            type="number"
            min="1"
            placeholder="30"
            required
          />

          <div class="flex flex-col justify-end">
            <span class="text-sm font-medium text-transparent select-none hidden md:block mb-1">Emitir</span>
            <NeuButton variant="primary" type="submit" :loading="emitiendo" class="w-full justify-center h-[46px] font-bold">
              🚀 Emitir a Todos
            </NeuButton>
          </div>
        </form>
      </NeuCard>
    </div>

    <!-- Selector Neumórfico de Pestaña: Vista por Apartamentos (PB al 16) vs Vista de Recibos Sueltos -->
    <div class="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 mb-6">
      <div class="inline-flex rounded-neu bg-neu-bg-dark p-1.5 border border-neu-shadow-dark gap-1 shadow-neu-inset">
        <button
          type="button"
          @click="modoVista = 'apartamentos'"
          class="py-2.5 px-4 text-xs font-bold rounded-neu-sm transition-all duration-200 cursor-pointer flex items-center justify-center gap-2 whitespace-nowrap"
          :class="modoVista === 'apartamentos'
            ? 'bg-neu-bg shadow-neu-sm text-neu-green font-extrabold'
            : 'text-neu-text-light hover:text-neu-text'"
        >
          <span>🏢</span>
          <span>Por Apartamentos y Residentes (PB al 16)</span>
        </button>
        <button
          type="button"
          @click="modoVista = 'recibos'"
          class="py-2.5 px-4 text-xs font-bold rounded-neu-sm transition-all duration-200 cursor-pointer flex items-center justify-center gap-2 whitespace-nowrap"
          :class="modoVista === 'recibos'
            ? 'bg-neu-bg shadow-neu-sm text-neu-green font-extrabold'
            : 'text-neu-text-light hover:text-neu-text'"
        >
          <span>📄</span>
          <span>Lista General de Recibos</span>
        </button>
      </div>

      <!-- Barra de Búsqueda y Filtros con Simetría y Altura Homogénea -->
      <div class="flex items-center gap-3 flex-wrap sm:flex-nowrap justify-end">
        <div class="relative w-full sm:w-64">
          <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-neu-text-light text-xs">
            🔍
          </span>
          <input
            v-model="filtroTexto"
            type="text"
            placeholder="Buscar por apto o habitante..."
            class="input-neu text-xs py-2.5 pl-8 pr-3 w-full"
          />
        </div>

        <select
          v-if="modoVista === 'apartamentos'"
          v-model="filtroEstadoApto"
          class="input-neu text-xs py-2.5 px-3 min-w-[170px] cursor-pointer"
        >
          <option value="todos">Todos los Estados</option>
          <option value="morosos">Solo con Saldo Pendiente</option>
          <option value="solventes">Solo Solventes (Al día)</option>
        </select>

        <select
          v-else
          v-model="filtroEstadoRecibo"
          class="input-neu text-xs py-2.5 px-3 min-w-[150px] cursor-pointer"
        >
          <option value="">Todos los Estados</option>
          <option value="pendiente">Pendientes</option>
          <option value="parcial">Parciales</option>
          <option value="pagado">Pagados</option>
        </select>
      </div>
    </div>

    <!-- ──────────────── VISTA 1: POR APARTAMENTOS Y RESIDENTES (ORDENADOS PB AL 16) ──────────────── -->
    <div v-if="modoVista === 'apartamentos'">
      <NeuCard>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3.5 mb-3 border-b border-neu-shadow-dark/40 gap-2">
          <div>
            <h3 class="text-base font-bold text-neu-green flex items-center gap-2">
              <span>🏢</span> Control de Inmuebles y Residentes
            </h3>
            <p class="text-xs text-neu-text-light mt-0.5">
              Ordenado de Planta Baja (PB) al piso 16. Haz clic en "Ver Recibos y Pagos" para consultar meses y fotos de comprobantes.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-3 py-1 rounded-full bg-neu-bg shadow-neu-sm text-xs font-bold text-neu-text-light border border-white/60 whitespace-nowrap">
              Total: <strong class="text-neu-green font-extrabold">{{ apartamentosFiltrados.length }}</strong> inmuebles
            </span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-neu-shadow-dark text-neu-text-light text-[11px] uppercase tracking-wider">
                <th class="py-3 px-3.5 font-bold text-left whitespace-nowrap">Inmueble</th>
                <th class="py-3 px-3.5 font-bold text-left whitespace-nowrap">Persona que Habita</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Cuota Fijada</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Recibos</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Deuda ($ USD)</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Deuda en Bs.</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Estado</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Expediente</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neu-bg-dark">
              <tr
                v-for="apto in apartamentosFiltrados"
                :key="apto.id"
                class="hover:bg-neu-bg-dark/40 transition-colors"
              >
                <!-- Apartamento -->
                <td class="py-3.5 px-3.5 align-middle whitespace-nowrap">
                  <div class="flex items-center gap-2.5">
                    <span class="px-2.5 py-1 rounded-neu-sm bg-neu-bg shadow-neu-sm font-extrabold text-neu-green text-xs border border-white/60 shrink-0">
                      🏢 Apto {{ apto.numero_apto }}
                    </span>
                    <span class="text-xs text-neu-text-light font-medium whitespace-nowrap">
                      Piso {{ apto.piso || '—' }} · {{ apto.torre || 'Torre Única' }}
                    </span>
                  </div>
                </td>

                <!-- Habitante / Propietario -->
                <td class="py-3.5 px-3.5 align-middle">
                  <div class="flex items-center gap-3">
                    <div
                      class="w-8 h-8 rounded-full text-white font-extrabold flex items-center justify-center text-xs shadow-sm shrink-0"
                      :class="apto.propietario ? 'bg-neu-green' : 'bg-neutral-400'"
                    >
                      {{ apto.propietario ? apto.habitanteNombre.charAt(0) : '?' }}
                    </div>
                    <div class="min-w-0">
                      <span class="font-bold text-neu-text block leading-snug text-xs sm:text-sm truncate">
                        {{ apto.habitanteNombre }}
                      </span>
                      <span v-if="apto.habitanteTelefono" class="text-[11px] text-neu-text-light block font-mono">
                        📱 {{ apto.habitanteTelefono }}
                      </span>
                      <span v-else-if="!apto.propietario" class="text-[11px] text-amber-700 italic block">
                        Sin residente registrado
                      </span>
                    </div>
                  </div>
                </td>

                <!-- Cuota mensual por alícuota -->
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <span class="font-bold text-neu-text text-xs sm:text-sm block">
                    {{ formatUSD(apto.alicuota) }}
                  </span>
                  <span class="text-[10px] text-neu-text-light block font-normal">
                    mensual
                  </span>
                </td>

                <!-- Cantidad de recibos -->
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <span
                      class="inline-flex items-center justify-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap min-w-[125px] shadow-sm"
                      :class="apto.totalPendientes > 0 ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'"
                    >
                      <span>{{ apto.totalPendientes > 0 ? '⚠️' : '✓' }}</span>
                      <span>{{ apto.totalPendientes > 0 ? `${apto.totalPendientes} pendiente(s)` : `${apto.totalEmitidos} al día` }}</span>
                    </span>
                  </div>
                </td>

                <!-- Deuda Total USD -->
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <span
                    class="font-extrabold text-xs sm:text-sm"
                    :class="apto.totalDeudaUSD > 0 ? 'text-neu-danger' : 'text-neu-success'"
                  >
                    {{ formatUSD(apto.totalDeudaUSD) }}
                  </span>
                </td>

                <!-- Deuda Equivalente en VES -->
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <span class="text-xs text-neu-text-light font-semibold">
                    {{ formatVES(apto.totalDeudaVES) }}
                  </span>
                </td>

                <!-- Estado (Simetría Absoluta) -->
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <span
                      class="inline-flex items-center justify-center gap-1.5 px-3.5 py-1 rounded-full text-[11px] font-black uppercase tracking-wider whitespace-nowrap shadow-sm min-w-[105px]"
                      :class="apto.esSolvente ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white'"
                    >
                      <span class="text-[11px] leading-none">{{ apto.esSolvente ? '✓' : '●' }}</span>
                      <span class="leading-none">{{ apto.esSolvente ? 'SOLVENTE' : 'MOROSO' }}</span>
                    </span>
                  </div>
                </td>

                <!-- Botón de acción para ver sus recibos y comprobantes -->
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <button
                      type="button"
                      @click="abrirExpedienteApto(apto)"
                      class="px-3.5 py-1.5 rounded-neu-sm text-xs font-bold bg-neu-bg shadow-neu-sm hover:shadow-neu-inset text-neu-green border border-white/60 transition-all cursor-pointer inline-flex items-center justify-center gap-1.5 whitespace-nowrap"
                      title="Ver todos los meses de pago y fotos de comprobantes de esta persona"
                    >
                      <span>👁️</span>
                      <span>Ver Recibos y Pagos</span>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="apartamentosFiltrados.length === 0">
                <td colspan="8" class="py-12 text-center text-neu-text-light">
                  <div class="flex flex-col items-center justify-center gap-2">
                    <span class="text-2xl">🔍</span>
                    <p class="text-sm">No se encontraron apartamentos con los filtros seleccionados.</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </NeuCard>
    </div>

    <!-- ──────────────── VISTA 2: LISTA GENERAL DE RECIBOS SUELTOS ──────────────── -->
    <div v-else>
      <NeuCard>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3.5 mb-3 border-b border-neu-shadow-dark/40 gap-2">
          <div>
            <h3 class="text-base font-bold text-neu-green flex items-center gap-2">
              <span>📄</span> Lista General de Recibos
            </h3>
            <p class="text-xs text-neu-text-light mt-0.5">
              Histórico cronológico de todos los recibos emitidos en el condominio.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-3 py-1 rounded-full bg-neu-bg shadow-neu-sm text-xs font-bold text-neu-text-light border border-white/60 whitespace-nowrap">
              Total: <strong class="text-neu-green font-extrabold">{{ recibosFiltradosGeneral.length }}</strong> recibos
            </span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-neu-shadow-dark text-neu-text-light text-[11px] uppercase tracking-wider">
                <th class="py-3 px-3.5 font-bold text-left whitespace-nowrap">Período</th>
                <th class="py-3 px-3.5 font-bold text-left whitespace-nowrap">Apartamento</th>
                <th class="py-3 px-3.5 font-bold text-left whitespace-nowrap">Residente</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Monto Total</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Monto Pendiente</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Vencimiento</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Estado</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Comprobante</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Acción</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neu-bg-dark">
              <tr
                v-for="recibo in recibosFiltradosGeneral"
                :key="recibo.id"
                class="hover:bg-neu-bg-dark/40 transition-colors"
              >
                <td class="py-3.5 px-3.5 align-middle font-bold text-neu-green whitespace-nowrap">
                  {{ formatPeriodo(recibo.mes_periodo) }}
                </td>
                <td class="py-3.5 px-3.5 align-middle whitespace-nowrap">
                  <span class="px-2.5 py-1 rounded-neu-sm bg-neu-bg shadow-neu-sm font-extrabold text-neu-green text-xs border border-white/60">
                    🏢 Apto {{ obtenerNumeroApto(recibo.apartamento_id) }}
                  </span>
                </td>
                <td class="py-3.5 px-3.5 align-middle">
                  <span class="font-bold text-neu-text text-xs sm:text-sm block truncate max-w-[180px]">
                    {{ obtenerNombreHabitantePorAptoId(recibo.apartamento_id) }}
                  </span>
                </td>
                <td class="py-3.5 px-3.5 align-middle text-center font-bold text-neu-text text-xs sm:text-sm whitespace-nowrap">
                  {{ formatUSD(recibo.monto_total_usd) }}
                </td>
                <td class="py-3.5 px-3.5 align-middle text-center font-extrabold text-xs sm:text-sm whitespace-nowrap" :class="recibo.monto_pendiente_usd > 0 ? 'text-neu-danger' : 'text-neu-success'">
                  {{ formatUSD(recibo.monto_pendiente_usd) }}
                </td>
                <td class="py-3.5 px-3.5 align-middle text-center text-neu-text-light text-xs whitespace-nowrap font-medium">
                  {{ formatFecha(recibo.fecha_vencimiento) }}
                </td>
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <EstadoPagoBadge :estado="recibo.estado_pago" />
                  </div>
                </td>
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <button
                      v-if="recibo.comprobante_url"
                      type="button"
                      @click="verFotoComprobante(recibo)"
                      class="px-3 py-1.5 rounded-neu-sm text-xs font-bold text-neu-green bg-neu-bg shadow-neu-sm hover:shadow-neu-inset border border-white/60 transition-all cursor-pointer inline-flex items-center gap-1 whitespace-nowrap"
                      title="Ver foto del comprobante enviado"
                    >
                      <span>📷</span>
                      <span>Ver Captura</span>
                    </button>
                    <span v-else class="text-xs text-neu-text-light italic font-medium">—</span>
                  </div>
                </td>
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <button
                      type="button"
                      @click="confirmarEliminarRecibo(recibo)"
                      class="p-2 rounded-neu-sm text-neu-danger hover:text-red-600 hover:bg-rose-50 transition-all cursor-pointer"
                      title="Eliminar este recibo"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="recibosFiltradosGeneral.length === 0">
                <td colspan="9" class="py-12 text-center text-neu-text-light">
                  <div class="flex flex-col items-center justify-center gap-2">
                    <span class="text-2xl">📄</span>
                    <p class="text-sm">No hay recibos generados para este filtro.</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </NeuCard>
    </div>

    <!-- ──────────────── MODAL 1: EXPEDIENTE DE RECIBOS Y PAGOS DEL APARTAMENTO ──────────────── -->
    <NeuModal
      v-model="modalExpedienteAbierto"
      :title="aptoSeleccionado ? `Expediente de Recibos — Apto ${aptoSeleccionado.numero_apto}` : 'Expediente de Recibos'"
      size="4xl"
    >
      <div v-if="aptoSeleccionado" class="flex flex-col gap-4">
        <!-- Banner de datos de la persona -->
        <div class="p-3.5 bg-neu-bg-dark rounded-neu-sm border border-neu-shadow-dark flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-neu-green text-white font-black flex items-center justify-center text-base shadow-sm shrink-0">
              {{ aptoSeleccionado.habitanteNombre ? aptoSeleccionado.habitanteNombre.charAt(0) : 'A' }}
            </div>
            <div>
              <span class="text-xs text-neu-text-light uppercase tracking-wider font-bold block">Residente / Propietario</span>
              <h4 class="text-sm sm:text-base font-extrabold text-neu-text">{{ aptoSeleccionado.habitanteNombre }}</h4>
              <p class="text-[11px] text-neu-text-light font-mono">
                {{ aptoSeleccionado.habitanteTelefono || 'Sin teléfono' }} • {{ aptoSeleccionado.habitanteEmail || 'Sin email' }}
              </p>
            </div>
          </div>

          <div class="text-left sm:text-right border-t sm:border-t-0 pt-2 sm:pt-0 w-full sm:w-auto">
            <span class="text-xs text-neu-text-light block">Balance Total Pendiente:</span>
            <span
              class="text-lg font-black"
              :class="aptoSeleccionado.totalDeudaUSD > 0 ? 'text-neu-danger' : 'text-neu-green'"
            >
              {{ formatUSD(aptoSeleccionado.totalDeudaUSD) }}
            </span>
            <span class="text-xs text-neu-text-light block">
              Al cambio: <strong>{{ formatVES(aptoSeleccionado.totalDeudaVES) }}</strong>
            </span>
          </div>
        </div>

        <!-- Tabla de todos los recibos mensuales de este residente -->
        <div class="overflow-x-auto max-h-[55vh]">
          <table class="w-full text-left border-collapse text-xs sm:text-sm">
            <thead>
              <tr class="border-b border-neu-shadow-dark text-neu-text-light text-[11px] uppercase tracking-wider sticky top-0 bg-neu-bg">
                <th class="py-2.5 px-3 font-bold text-left whitespace-nowrap">Período / Mes</th>
                <th class="py-2.5 px-3 font-bold text-center whitespace-nowrap">Cuota Total</th>
                <th class="py-2.5 px-3 font-bold text-center whitespace-nowrap">Pendiente</th>
                <th class="py-2.5 px-3 font-bold text-center whitespace-nowrap">Vencimiento</th>
                <th class="py-2.5 px-3 font-bold text-center whitespace-nowrap">Estado</th>
                <th class="py-2.5 px-3 font-bold text-center whitespace-nowrap">Comprobante de Pago</th>
                <th class="py-2.5 px-3 font-bold text-center whitespace-nowrap">Acción</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neu-bg-dark">
              <tr
                v-for="recibo in aptoSeleccionado.recibos"
                :key="recibo.id"
                class="hover:bg-neu-bg-dark/40 transition-colors"
              >
                <!-- Período -->
                <td class="py-3 px-3 align-middle font-bold text-neu-green whitespace-nowrap">
                  {{ formatPeriodo(recibo.mes_periodo) }}
                </td>

                <!-- Cuota Total -->
                <td class="py-3 px-3 align-middle text-center font-semibold text-neu-text whitespace-nowrap">
                  {{ formatUSD(recibo.monto_total_usd) }}
                </td>

                <!-- Monto Pendiente -->
                <td class="py-3 px-3 align-middle text-center font-black whitespace-nowrap" :class="recibo.monto_pendiente_usd > 0 ? 'text-neu-danger' : 'text-neu-success'">
                  {{ formatUSD(recibo.monto_pendiente_usd) }}
                </td>

                <!-- Vencimiento -->
                <td class="py-3 px-3 align-middle text-center text-neu-text-light text-xs whitespace-nowrap font-medium">
                  {{ formatFecha(recibo.fecha_vencimiento) }}
                </td>

                <!-- Estado -->
                <td class="py-3 px-3 align-middle text-center whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <EstadoPagoBadge :estado="recibo.estado_pago" />
                  </div>
                </td>

                <!-- Comprobante de Pago Enviado por la Persona -->
                <td class="py-3 px-3 align-middle text-center whitespace-nowrap">
                  <div v-if="recibo.comprobante_url" class="flex flex-col items-center justify-center gap-1">
                    <button
                      type="button"
                      @click="verFotoComprobante(recibo)"
                      class="px-3 py-1.5 rounded-neu-sm bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition-all cursor-pointer inline-flex items-center justify-center gap-1.5 whitespace-nowrap"
                    >
                      <span>📷</span>
                      <span>Ver Foto Captura</span>
                    </button>
                    <span v-if="recibo.ultimo_pago_referencia" class="text-[10px] text-neu-text-light font-mono font-bold">
                      Ref: {{ recibo.ultimo_pago_referencia }}
                    </span>
                  </div>
                  <div v-else class="text-xs text-neu-text-light italic font-medium">
                    Sin comprobante
                  </div>
                </td>

                <!-- Acción: Eliminar -->
                <td class="py-3 px-3 align-middle text-center whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <button
                      type="button"
                      @click="confirmarEliminarRecibo(recibo)"
                      class="p-2 rounded-neu-sm text-neu-danger hover:bg-rose-50 transition-all cursor-pointer"
                      title="Eliminar este recibo"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="!aptoSeleccionado.recibos || aptoSeleccionado.recibos.length === 0">
                <td colspan="7" class="py-10 text-center text-neu-text-light">
                  <div class="flex flex-col items-center justify-center gap-2">
                    <span class="text-2xl">📂</span>
                    <p class="text-sm">No hay recibos generados aún para este apartamento.</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-end pt-3 border-t border-neu-shadow-dark">
          <NeuButton type="button" @click="modalExpedienteAbierto = false">
            Cerrar Expediente
          </NeuButton>
        </div>
      </div>
    </NeuModal>

    <!-- ──────────────── MODAL 2: VISOR DE FOTO DEL COMPROBANTE ──────────────── -->
    <NeuModal
      v-model="modalFotoComprobanteAbierto"
      :title="reciboParaComprobante ? `Comprobante de Pago — Período ${formatPeriodo(reciboParaComprobante.mes_periodo)}` : 'Comprobante de Pago'"
      size="3xl"
    >
      <div v-if="reciboParaComprobante" class="flex flex-col items-center gap-4">
        <!-- Tarjeta de Resumen del Pago -->
        <div class="w-full grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs bg-neu-bg-dark p-3 rounded-neu-sm border border-neu-shadow-dark">
          <div>
            <span class="text-[10px] font-bold text-neu-text-light uppercase tracking-wider block">Apartamento</span>
            <strong class="text-neu-text">Apto {{ obtenerNumeroApto(reciboParaComprobante.apartamento_id) }}</strong>
          </div>
          <div>
            <span class="text-[10px] font-bold text-neu-text-light uppercase tracking-wider block">Método de Pago</span>
            <span class="capitalize text-neu-text font-semibold">{{ (reciboParaComprobante.ultimo_pago_metodo || 'pago_movil').replace('_', ' ') }}</span>
          </div>
          <div>
            <span class="text-[10px] font-bold text-neu-text-light uppercase tracking-wider block">N° Referencia</span>
            <span class="font-mono font-bold text-neu-green">{{ reciboParaComprobante.ultimo_pago_referencia || '—' }}</span>
          </div>
          <div>
            <span class="text-[10px] font-bold text-neu-text-light uppercase tracking-wider block">Monto Declarado</span>
            <strong class="text-neu-text">{{ reciboParaComprobante.ultimo_pago_monto ? formatUSD(reciboParaComprobante.ultimo_pago_monto) : 'Declarado' }}</strong>
          </div>
        </div>

        <!-- Visor del Comprobante (Imagen o PDF) -->
        <div class="w-full flex justify-center bg-black/5 p-2 rounded-neu-sm border border-neu-shadow-dark max-h-[65vh] overflow-auto">
          <iframe
            v-if="esPdf(reciboParaComprobante.comprobante_url)"
            :src="reciboParaComprobante.comprobante_url"
            class="w-full h-[60vh] rounded-neu-sm border-0"
          ></iframe>
          <img
            v-else-if="reciboParaComprobante.comprobante_url"
            :src="reciboParaComprobante.comprobante_url"
            alt="Foto del Comprobante de Pago enviado por la persona"
            class="max-h-[60vh] max-w-full object-contain rounded-neu-sm shadow-md"
          />
          <div v-else class="py-8 text-center text-neu-text-light text-xs">
            No se encontró el archivo del comprobante.
          </div>
        </div>

        <!-- Botones inferiores -->
        <div class="flex items-center justify-between w-full mt-2">
          <a
            v-if="reciboParaComprobante.comprobante_url"
            :href="reciboParaComprobante.comprobante_url"
            target="_blank"
            download
            class="text-xs text-neu-green hover:underline font-bold"
          >
            🔗 Abrir archivo en pestaña nueva
          </a>
          <span v-else></span>

          <NeuButton type="button" @click="modalFotoComprobanteAbierto = false">
            Cerrar
          </NeuButton>
        </div>
      </div>
    </NeuModal>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { AdminLayout } from '@/components/layout'
import { NeuCard, NeuButton, NeuInput, NeuModal } from '@/components/neumorph'
import { EstadoPagoBadge } from '@/components/shared'
import { useRecibosStore, useApartamentosStore, useTasaStore } from '@/stores'
import { formatUSD, formatVES, formatFecha, formatPeriodo, periodoActual } from '@/utils'

const toast = useToast()
const recibosStore = useRecibosStore()
const aptosStore = useApartamentosStore()
const tasaStore = useTasaStore()

const emitiendo = ref(false)
const modoVista = ref('apartamentos') // 'apartamentos' | 'recibos'
const filtroTexto = ref('')
const filtroEstadoApto = ref('todos') // 'todos' | 'morosos' | 'solventes'
const filtroEstadoRecibo = ref('')

const modalExpedienteAbierto = ref(false)
const aptoSeleccionado = ref(null)

const modalFotoComprobanteAbierto = ref(false)
const reciboParaComprobante = ref(null)

const emisionForm = ref({
  periodo: periodoActual(),
  gasto_total_usd: '',
  dias_vencimiento: 30,
})

onMounted(async () => {
  await Promise.all([
    recibosStore.cargar(),
    aptosStore.cargar(),
    tasaStore.cargarTasa(),
  ])
})

// ── ORDENAMIENTO NATURAL DE APARTAMENTOS: DE PB AL 16 ──
function getPisoVal(item) {
  const p = String(item.piso || '').trim().toUpperCase()
  if (p.includes('PB') || p === '0') return 0
  const parsedP = parseInt(p, 10)
  if (!isNaN(parsedP)) return parsedP

  const num = String(item.numero_apto || '').trim().toUpperCase()
  if (num.includes('PB')) return 0
  const match = num.match(/^(\d+)/)
  if (match) return parseInt(match[1], 10)
  return 999
}

function getAptoSubVal(item) {
  const num = String(item.numero_apto || '').trim().toUpperCase()
  if (num.includes('-')) {
    const parts = num.split('-')
    const sub = parseInt(parts[1], 10)
    return isNaN(sub) ? parts[1] : sub
  }
  return num
}

// ── AGRUPACIÓN Y CÁLCULOS POR APARTAMENTO ──
const apartamentosConRecibos = computed(() => {
  const aptos = aptosStore.lista || []
  const recibos = recibosStore.lista || []

  const mapeados = aptos.map((apto) => {
    const recibosApto = recibos
      .filter((r) => r.apartamento_id === apto.id)
      .sort((a, b) => b.mes_periodo.localeCompare(a.mes_periodo))

    const totalEmitidos = recibosApto.length
    const recibosPendientes = recibosApto.filter((r) => r.estado_pago !== 'pagado')
    const totalDeudaUSD = recibosPendientes.reduce(
      (acc, r) => acc + (parseFloat(r.monto_pendiente_usd) || 0),
      0
    )
    const totalDeudaVES = tasaStore.tasaActual
      ? totalDeudaUSD * parseFloat(tasaStore.tasaActual)
      : 0

    const habitanteNombre = apto.propietario
      ? `${apto.propietario.nombre} ${apto.propietario.apellido}`.trim()
      : 'Sin habitante asignado'
    const habitanteEmail = apto.propietario?.email || ''
    const habitanteTelefono = apto.propietario?.telefono_whatsapp || ''

    return {
      ...apto,
      habitanteNombre,
      habitanteEmail,
      habitanteTelefono,
      recibos: recibosApto,
      totalEmitidos,
      totalPendientes: recibosPendientes.length,
      totalDeudaUSD,
      totalDeudaVES,
      esSolvente: totalDeudaUSD <= 0,
    }
  })

  // Ordenar de PB al 16
  return mapeados.sort((a, b) => {
    const pisoA = getPisoVal(a)
    const pisoB = getPisoVal(b)
    if (pisoA !== pisoB) return pisoA - pisoB

    const subA = getAptoSubVal(a)
    const subB = getAptoSubVal(b)
    if (typeof subA === 'number' && typeof subB === 'number') {
      return subA - subB
    }
    return String(subA).localeCompare(String(subB), undefined, { numeric: true, sensitivity: 'base' })
  })
})

const apartamentosFiltrados = computed(() => {
  let lista = apartamentosConRecibos.value
  if (filtroEstadoApto.value === 'solventes') {
    lista = lista.filter((a) => a.esSolvente)
  } else if (filtroEstadoApto.value === 'morosos') {
    lista = lista.filter((a) => !a.esSolvente)
  }

  if (filtroTexto.value.trim()) {
    const term = filtroTexto.value.trim().toLowerCase()
    lista = lista.filter(
      (a) =>
        a.numero_apto.toLowerCase().includes(term) ||
        a.habitanteNombre.toLowerCase().includes(term) ||
        (a.habitanteEmail && a.habitanteEmail.toLowerCase().includes(term))
    )
  }
  return lista
})

const recibosFiltradosGeneral = computed(() => {
  let lista = recibosStore.lista || []
  if (filtroEstadoRecibo.value) {
    lista = lista.filter((r) => r.estado_pago === filtroEstadoRecibo.value)
  }
  if (filtroTexto.value.trim()) {
    const term = filtroTexto.value.trim().toLowerCase()
    lista = lista.filter((r) => {
      const aptoNum = obtenerNumeroApto(r.apartamento_id).toLowerCase()
      const nom = obtenerNombreHabitantePorAptoId(r.apartamento_id).toLowerCase()
      const per = r.mes_periodo.toLowerCase()
      return aptoNum.includes(term) || nom.includes(term) || per.includes(term)
    })
  }
  return lista
})

function obtenerNumeroApto(aptoId) {
  const apto = aptosStore.lista.find((a) => a.id === aptoId)
  return apto ? apto.numero_apto : `#${aptoId}`
}

function obtenerNombreHabitantePorAptoId(aptoId) {
  const apto = aptosStore.lista.find((a) => a.id === aptoId)
  if (apto && apto.propietario) {
    return `${apto.propietario.nombre} ${apto.propietario.apellido}`.trim()
  }
  return 'Sin habitante'
}

function abrirExpedienteApto(apto) {
  aptoSeleccionado.value = apto
  modalExpedienteAbierto.value = true
}

function esPdf(url) {
  return url && (url.startsWith('data:application/pdf') || url.toLowerCase().includes('.pdf'))
}

function verFotoComprobante(recibo) {
  reciboParaComprobante.value = recibo
  modalFotoComprobanteAbierto.value = true
}

async function ejecutarEmision() {
  if (!emisionForm.value.gasto_total_usd || parseFloat(emisionForm.value.gasto_total_usd) <= 0) {
    toast.error('Ingrese un monto válido de gastos')
    return
  }

  emitiendo.value = true
  try {
    const res = await recibosStore.emitirMasivo(emisionForm.value)
    toast.success(`¡Éxito! ${res.mensaje}`)
    await Promise.all([
      recibosStore.cargar(),
      aptosStore.cargar(),
    ])
    emisionForm.value.gasto_total_usd = ''
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Error al emitir los recibos')
  } finally {
    emitiendo.value = false
  }
}

async function confirmarEliminarRecibo(recibo) {
  const aptoNum = obtenerNumeroApto(recibo.apartamento_id)
  const periodoStr = formatPeriodo(recibo.mes_periodo)
  if (!confirm(`¿Estás seguro de eliminar el recibo de ${periodoStr} para el Apto ${aptoNum}?\n\nEsta acción recalculará automáticamente la deuda pendiente y los meses adeudados del apartamento.`)) {
    return
  }

  try {
    await recibosStore.eliminar(recibo.id)
    await Promise.all([
      recibosStore.cargar(),
      aptosStore.cargar(),
    ])

    // Actualizar el expediente abierto si coincide
    if (aptoSeleccionado.value) {
      const actualizado = apartamentosConRecibos.value.find((a) => a.id === aptoSeleccionado.value.id)
      if (actualizado) {
        aptoSeleccionado.value = actualizado
      }
    }

    toast.success('Recibo eliminado y deuda sincronizada correctamente.')
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Error al eliminar el recibo')
  }
}
</script>
