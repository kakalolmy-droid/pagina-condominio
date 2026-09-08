<template>
  <AdminLayout
    titulo="Recibos por Apartamento y Residentes"
    subtitulo="Control de cuotas mensuales, solvencia y comprobantes de pago organizados por apartamento (PB al 16)"
  >
    <!-- Barra de Búsqueda y Filtros con Simetría y Mayor Espacio -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-6">
      <div class="relative w-full sm:w-80 md:w-96">
        <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-neu-text-light text-xs">
          🔍
        </span>
        <input
          v-model="filtroTexto"
          type="text"
          placeholder="Buscar por apartamento, residente o teléfono..."
          class="input-neu text-xs py-2.5 pl-9 pr-3 w-full"
        />
      </div>

      <div class="flex items-center gap-3 flex-wrap sm:flex-nowrap justify-end">
        <!-- Filtro por Pisos del Edificio (PB al Piso 16 y PH) -->
        <select
          v-model="filtroPiso"
          class="input-neu text-xs py-2.5 px-3 min-w-[150px] cursor-pointer"
          title="Filtrar por piso del edificio"
        >
          <option value="todos">🏢 Todos los Pisos</option>
          <option value="PB">Planta Baja (PB)</option>
          <option v-for="p in pisosDisponibles" :key="p" :value="p">
            Piso {{ p }}
          </option>
          <option value="PH">Penthouse (PH)</option>
        </select>

        <!-- Filtro por Solvencia -->
        <select
          v-model="filtroEstadoApto"
          class="input-neu text-xs py-2.5 px-3 min-w-[160px] cursor-pointer"
        >
          <option value="todos">Todos los Estados</option>
          <option value="morosos">Solo con Deuda (Morosos)</option>
          <option value="solventes">Solo Solventes (Al día)</option>
        </select>
      </div>
    </div>

    <!-- ──────────────── VISTA PRINCIPAL: POR APARTAMENTOS Y RESIDENTES (PB AL 16) ──────────────── -->
    <div>
      <NeuCard>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3.5 mb-3 border-b border-neu-shadow-dark/40 gap-2">
          <div>
            <h3 class="text-base font-bold text-neu-green flex items-center gap-2">
              <span>🏢</span> Control por Apartamentos y Residentes
            </h3>
            <p class="text-xs text-neu-text-light mt-0.5">
              Ordenado de Planta Baja (PB) al piso 16. Haz clic en "Ver Recibos y Pagos" para consultar meses y fotos de comprobantes.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-3 py-1 rounded-full bg-neu-bg shadow-neu-sm text-xs font-bold text-neu-text-light border border-white/60 whitespace-nowrap">
              Total: <strong class="text-neu-green font-extrabold">{{ apartamentosFiltrados.length }}</strong> apartamentos
            </span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-neu-shadow-dark text-neu-text-light text-[11px] uppercase tracking-wider">
                <th class="py-3 px-3.5 font-bold text-left whitespace-nowrap">Apartamento</th>
                <th class="py-3 px-3.5 font-bold text-left whitespace-nowrap">Residente</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Cuota Fijada</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Recibos</th>
                <th class="py-3 px-3.5 font-bold text-center whitespace-nowrap">Total Deuda</th>
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
                      {{ formatPiso(apto.piso) }}
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
                      <span v-if="apto.habitanteTelefono" class="text-[11px] text-neu-text font-bold block font-mono mt-0.5">
                        📱 {{ apto.habitanteTelefono }}
                      </span>
                      <span v-else-if="apto.propietario || apto.propietario_id" class="text-[10px] text-neu-text-light italic block mt-0.5">
                        Sin teléfono registrado
                      </span>
                      <span v-else class="text-[11px] text-amber-700 italic block mt-0.5">
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
                      class="inline-flex items-center justify-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap min-w-[120px] shadow-sm"
                      :class="apto.totalPendientes > 0 ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'"
                    >
                      <span>{{ apto.totalPendientes > 0 ? '⚠️' : '✓' }}</span>
                      <span>{{ apto.totalPendientes > 0 ? `${apto.totalPendientes} pendiente(s)` : `${apto.totalEmitidos} al día` }}</span>
                    </span>
                  </div>
                </td>

                <!-- Total Deuda (USD y Bs. juntos para evitar desborde horizontal) -->
                <td class="py-3.5 px-3.5 align-middle text-center whitespace-nowrap">
                  <span
                    class="font-extrabold text-xs sm:text-sm block"
                    :class="apto.totalDeudaUSD > 0 ? 'text-neu-danger' : 'text-neu-success'"
                  >
                    {{ formatUSD(apto.totalDeudaUSD) }}
                  </span>
                  <span class="text-[11px] text-neu-text-light font-medium block mt-0.5">
                    {{ formatVES(apto.totalDeudaVES) }}
                  </span>
                </td>

                <!-- Estado (Solvente / Moroso) -->
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
                <td colspan="7" class="py-12 text-center text-neu-text-light">
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
              <div class="flex items-center gap-2 flex-wrap text-xs mt-1">
                <span v-if="aptoSeleccionado.habitanteTelefono" class="font-bold text-neu-text font-mono inline-flex items-center gap-1 bg-neu-bg px-2.5 py-1 rounded shadow-neu-sm border border-white/60">
                  📱 {{ aptoSeleccionado.habitanteTelefono }}
                </span>
                <span v-else class="text-amber-700 italic text-xs">
                  Sin teléfono registrado
                </span>
                <span v-if="aptoSeleccionado.habitanteCedula" class="text-neu-text-light font-mono text-xs">
                  • C.I: <strong>{{ aptoSeleccionado.habitanteCedula }}</strong>
                </span>
                <span v-if="aptoSeleccionado.habitanteEmail" class="text-neu-text-light text-xs">
                  • ✉️ {{ aptoSeleccionado.habitanteEmail }}
                </span>
              </div>
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
              </tr>

              <tr v-if="!aptoSeleccionado.recibos || aptoSeleccionado.recibos.length === 0">
                <td colspan="6" class="py-10 text-center text-neu-text-light">
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
import { NeuCard, NeuButton, NeuModal } from '@/components/neumorph'
import { EstadoPagoBadge } from '@/components/shared'
import { useRecibosStore, useApartamentosStore, useTasaStore, useUsuariosStore } from '@/stores'
import { formatUSD, formatVES, formatFecha, formatPeriodo } from '@/utils'

const toast = useToast()
const recibosStore = useRecibosStore()
const aptosStore = useApartamentosStore()
const tasaStore = useTasaStore()
const usuariosStore = useUsuariosStore()

const filtroTexto = ref('')
const filtroPiso = ref('todos') // 'todos' | 'PB' | '1' ... '16'
const filtroEstadoApto = ref('todos') // 'todos' | 'morosos' | 'solventes'

const pisosDisponibles = computed(() => Array.from({ length: 16 }, (_, i) => String(i + 1)))

const modalExpedienteAbierto = ref(false)
const aptoSeleccionado = ref(null)

const modalFotoComprobanteAbierto = ref(false)
const reciboParaComprobante = ref(null)

onMounted(async () => {
  await Promise.all([
    recibosStore.cargar(),
    aptosStore.cargar(),
    tasaStore.cargarTasa(),
    usuariosStore.cargar(),
  ])
})

// ── ORDENAMIENTO NATURAL DE APARTAMENTOS: DE PB AL 16 Y PH ──
function getPisoVal(item) {
  const p = String(item.piso || '').trim().toUpperCase()
  if (p.includes('PB') || p === '0') return 0
  if (p.includes('PH') || p.includes('PENTHOUSE')) return 99
  const parsedP = parseInt(p, 10)
  if (!isNaN(parsedP)) return parsedP

  const num = String(item.numero_apto || '').trim().toUpperCase()
  if (num.includes('PB')) return 0
  if (num.includes('PH') || num.includes('PENTHOUSE')) return 99
  const match = num.match(/^(\d+)/)
  if (match) return parseInt(match[1], 10)
  return 999
}

function formatPiso(p) {
  if (!p) return 'PB'
  const val = String(p).trim().toUpperCase()
  if (val === 'PB' || val === '0') return 'PB'
  if (val === 'PH' || val.includes('PENTHOUSE')) return 'PH'
  return `Piso ${val}`
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
  const usuarios = usuariosStore.lista || []

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

    // Buscar habitante en la relación directa o en la lista general de usuarios
    const habitante = apto.propietario || usuarios.find((u) => u.id === apto.propietario_id)
    const habitanteNombre = habitante
      ? `${habitante.nombre} ${habitante.apellido}`.trim()
      : 'Sin habitante asignado'
    const habitanteEmail = habitante?.email || ''
    const habitanteTelefono = habitante?.telefono_whatsapp || apto.propietario?.telefono_whatsapp || ''
    const habitanteCedula = habitante?.cedula || apto.propietario?.cedula || ''

    return {
      ...apto,
      habitanteNombre,
      habitanteEmail,
      habitanteTelefono,
      habitanteCedula,
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

  // Filtro por Estado (Solvente / Moroso)
  if (filtroEstadoApto.value === 'solventes') {
    lista = lista.filter((a) => a.esSolvente)
  } else if (filtroEstadoApto.value === 'morosos') {
    lista = lista.filter((a) => !a.esSolvente)
  }

  // Filtro por Piso (PB al 16 y PH)
  if (filtroPiso.value !== 'todos') {
    const target = filtroPiso.value.trim().toUpperCase()
    lista = lista.filter((a) => {
      const p = String(a.piso || '').trim().toUpperCase()
      if (target === 'PB') return p === 'PB' || p === '0'
      if (target === 'PH') return p === 'PH' || p.includes('PH') || p.includes('PENTHOUSE')
      return p === target
    })
  }

  // Buscador de texto inteligente (apto, piso, persona, cédula)
  if (filtroTexto.value.trim()) {
    const term = filtroTexto.value.trim().toLowerCase()
    const termSinGuion = term.replace(/[^a-z0-9]/g, '')
    lista = lista.filter((a) => {
      const aptoNum = String(a.numero_apto || '').toLowerCase()
      const aptoNumSinGuion = aptoNum.replace(/[^a-z0-9]/g, '')
      const piso = String(a.piso || '').toLowerCase()
      const nom = String(a.habitanteNombre || '').toLowerCase()
      const email = String(a.habitanteEmail || '').toLowerCase()
      const cedula = String(a.habitanteCedula || '').toLowerCase()
      const tel = String(a.habitanteTelefono || '').toLowerCase()

      // Coincidencia con número de apartamento
      if (aptoNum.includes(term) || (termSinGuion && aptoNumSinGuion.includes(termSinGuion))) return true
      if (`apto ${aptoNum}`.includes(term)) return true

      // Coincidencia con piso
      if (
        piso === term ||
        `piso ${piso}`.includes(term) ||
        (term === 'pb' && (piso === '0' || piso.includes('pb'))) ||
        (term === 'ph' && (piso === 'ph' || piso.includes('ph'))) ||
        (term.includes('penthouse') && piso.includes('ph'))
      ) return true

      // Coincidencia con persona, email o cédula
      if (nom.includes(term) || email.includes(term) || cedula.includes(term)) return true

      // Teléfono: solo si el término tiene 4 o más caracteres o inicia con + o 0 (evita falsos positivos con dígitos individuales)
      if ((term.length >= 4 || term.startsWith('+') || term.startsWith('0')) && tel.includes(term)) return true

      return false
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
  if (apto) {
    const habitante = apto.propietario || usuariosStore.lista.find((u) => u.id === apto.propietario_id)
    if (habitante) {
      return `${habitante.nombre} ${habitante.apellido}`.trim()
    }
  }
  return 'Sin habitante'
}

function obtenerTelefonoHabitantePorAptoId(aptoId) {
  const apto = aptosStore.lista.find((a) => a.id === aptoId)
  if (apto) {
    const habitante = apto.propietario || usuariosStore.lista.find((u) => u.id === apto.propietario_id)
    return habitante?.telefono_whatsapp || ''
  }
  return ''
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
</script>
