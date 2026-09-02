<template>
  <PropietarioLayout>
    <div class="flex flex-col gap-6">
      <!-- Tarjeta de Bienvenida y Estado del Propietario -->
      <NeuCard>
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-2xl">👋</span>
              <h2 class="text-xl font-bold text-neu-green">Hola, {{ authStore.nombre }}</h2>
            </div>
            <p class="text-xs text-neu-text-light mt-1">
              Inmueble: <span class="font-semibold text-neu-text">{{ aptoInfo.numero_apto || 'Cargando...' }}</span>
              <span v-if="aptoInfo.torre"> | Torre: {{ aptoInfo.torre }}</span>
              <span v-if="aptoInfo.piso"> | Piso: {{ aptoInfo.piso }}</span>
              <span v-if="aptoInfo.alicuota"> | Alícuota: {{ (parseFloat(aptoInfo.alicuota) * 100).toFixed(2) }}%</span>
            </p>
          </div>

          <div class="flex items-center gap-3">
            <span
              class="px-3 py-1.5 rounded-full text-xs font-bold"
              :class="deudaTotalUSD > 0 ? 'badge-danger' : 'badge-success'"
            >
              {{ deudaTotalUSD > 0 ? '⚠️ SALDO PENDIENTE' : '✓ SOLVENTE' }}
            </span>
            <RouterLink to="/mi-cuenta/pagar">
              <NeuButton variant="primary" class="text-sm">
                💳 Reportar Pago
              </NeuButton>
            </RouterLink>
          </div>
        </div>
      </NeuCard>

      <!-- Resumen Financiero: Tarjetas de Balance -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Deuda Total en USD -->
        <NeuCard>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold text-neu-text-light uppercase tracking-wider">Deuda Total (USD)</span>
            <span class="text-xl">💵</span>
          </div>
          <h3 class="text-2xl font-bold" :class="deudaTotalUSD > 0 ? 'text-neu-danger' : 'text-neu-success'">
            {{ formatUSD(deudaTotalUSD) }}
          </h3>
          <p class="text-xs text-neu-text-light mt-1">
            Monto a cancelar en divisas
          </p>
        </NeuCard>

        <!-- Deuda Equivalente en VES (Tasa BCV) -->
        <NeuCard>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold text-neu-text-light uppercase tracking-wider">Al Cambio BCV (VES)</span>
            <span class="text-xl">💱</span>
          </div>
          <h3 class="text-2xl font-bold text-neu-text">
            {{ formatVES(deudaTotalVES) }}
          </h3>
          <p class="text-xs text-neu-text-light mt-1">
            Tasa: <span class="font-semibold text-neu-green">{{ tasaStore.tasaActual ? formatTasa(tasaStore.tasaActual) : '—' }}</span>
          </p>
        </NeuCard>

        <!-- Saldo a Favor -->
        <NeuCard>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold text-neu-text-light uppercase tracking-wider">Billetera / Saldo a Favor</span>
            <span class="text-xl">🏦</span>
          </div>
          <h3 class="text-2xl font-bold text-neu-green">
            {{ formatUSD(aptoInfo.saldo_favor_usd || 0) }}
          </h3>
          <p class="text-xs text-neu-text-light mt-1">
            Se descuenta automáticamente de futuras cuotas
          </p>
        </NeuCard>
      </div>

      <!-- Recibos Pendientes de Pago -->
      <NeuCard>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-neu-green">Recibos Pendientes</h3>
          <RouterLink to="/mi-cuenta/recibos" class="text-xs font-semibold text-neu-green hover:underline">
            Ver todo el historial ➔
          </RouterLink>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead>
              <tr class="border-b border-neu-shadow-dark text-neu-text-light">
                <th class="pb-3 font-semibold">Período</th>
                <th class="pb-3 font-semibold">Total Recibo</th>
                <th class="pb-3 font-semibold">Pendiente ($ USD)</th>
                <th class="pb-3 font-semibold">Pendiente (Bs. VES)</th>
                <th class="pb-3 font-semibold">Vencimiento</th>
                <th class="pb-3 font-semibold text-center">Estado</th>
                <th class="pb-3 font-semibold text-center">Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="recibo in recibosPendientes"
                :key="recibo.id"
                class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
              >
                <td class="py-3 font-bold text-neu-green">{{ formatPeriodo(recibo.mes_periodo) }}</td>
                <td class="py-3 text-neu-text font-medium">{{ formatUSD(recibo.monto_total_usd) }}</td>
                <td class="py-3 font-bold text-neu-danger">{{ formatUSD(recibo.monto_pendiente_usd) }}</td>
                <td class="py-3 text-neu-text-light font-medium">
                  {{ formatVES(tasaStore.convertirUSDaVES(recibo.monto_pendiente_usd)) }}
                </td>
                <td class="py-3 text-neu-text-light text-xs">{{ formatFecha(recibo.fecha_vencimiento) }}</td>
                <td class="py-3 text-center">
                  <EstadoPagoBadge :estado="recibo.estado_pago" />
                </td>
                <td class="py-3 text-center">
                  <RouterLink
                    :to="{ path: '/mi-cuenta/pagar', query: { recibo_id: recibo.id } }"
                    class="text-xs font-bold text-neu-green bg-neu-bg px-3 py-1.5 rounded-neu-sm shadow-neu-sm hover:shadow-neu-inset transition-all"
                  >
                    Pagar Ahora
                  </RouterLink>
                </td>
              </tr>
              <tr v-if="recibosPendientes.length === 0">
                <td colspan="7" class="py-8 text-center text-neu-text-light">
                  <span class="text-2xl block mb-1">🎉</span>
                  ¡Estás al día! No tienes recibos pendientes por pagar.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </NeuCard>

      <!-- Últimos Pagos Reportados -->
      <NeuCard>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-neu-green">Últimos Pagos Reportados</h3>
          <RouterLink to="/mi-cuenta/pagar" class="text-xs font-semibold text-neu-green hover:underline">
            + Nuevo reporte
          </RouterLink>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead>
              <tr class="border-b border-neu-shadow-dark text-neu-text-light">
                <th class="pb-3 font-semibold">Fecha Reporte</th>
                <th class="pb-3 font-semibold">Método</th>
                <th class="pb-3 font-semibold">Referencia</th>
                <th class="pb-3 font-semibold">Monto Reportado</th>
                <th class="pb-3 font-semibold">Equivalente USD</th>
                <th class="pb-3 font-semibold text-center">Conciliación</th>
                <th class="pb-3 font-semibold text-center">Comprobante</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="pago in pagosStore.misPagos.slice(0, 5)"
                :key="pago.id"
                class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
              >
                <td class="py-3 text-xs text-neu-text-light">{{ formatFecha(pago.fecha_reporte) }}</td>
                <td class="py-3 font-medium text-neu-text capitalize">{{ pago.metodo_pago.replace('_', ' ') }}</td>
                <td class="py-3 font-mono text-xs text-neu-text">{{ pago.referencia_bancaria }}</td>
                <td class="py-3 font-bold text-neu-text">
                  {{ pago.moneda_pago === 'VES' ? formatVES(pago.monto_declarado) : formatUSD(pago.monto_declarado) }}
                </td>
                <td class="py-3 font-semibold text-neu-green">{{ formatUSD(pago.monto_equivalente_usd) }}</td>
                <td class="py-3 text-center">
                  <EstadoConciliacionBadge :estado="pago.estado_conciliacion" />
                </td>
                <td class="py-3 text-center">
                  <a
                    v-if="pago.comprobante_url"
                    :href="pago.comprobante_url"
                    target="_blank"
                    class="text-xs text-neu-green hover:underline font-semibold"
                  >
                    Ver archivo ↗
                  </a>
                  <span v-else class="text-xs text-neu-text-light">—</span>
                </td>
              </tr>
              <tr v-if="pagosStore.misPagos.length === 0">
                <td colspan="7" class="py-6 text-center text-neu-text-light">
                  Aún no has reportado ningún pago.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </NeuCard>
    </div>
  </PropietarioLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { PropietarioLayout } from '@/components/layout'
import { NeuCard, NeuButton } from '@/components/neumorph'
import { EstadoPagoBadge, EstadoConciliacionBadge } from '@/components/shared'
import { useAuthStore, useTasaStore, useRecibosStore, usePagosStore } from '@/stores'
import { formatUSD, formatVES, formatTasa, formatFecha, formatPeriodo } from '@/utils'
import { api } from '@/services'

const authStore = useAuthStore()
const tasaStore = useTasaStore()
const recibosStore = useRecibosStore()
const pagosStore = usePagosStore()

const aptoInfo = ref({})

const recibosPendientes = computed(() => {
  return (recibosStore.lista || []).filter((r) => r.estado_pago !== 'pagado')
})

const deudaTotalUSD = computed(() => {
  return recibosPendientes.value.reduce((acc, r) => acc + (parseFloat(r.monto_pendiente_usd) || 0), 0)
})

const deudaTotalVES = computed(() => {
  return tasaStore.tasaActual ? deudaTotalUSD.value * parseFloat(tasaStore.tasaActual) : 0
})

onMounted(async () => {
  await Promise.all([
    tasaStore.cargarTasa(),
    recibosStore.cargarMisRecibos(),
    pagosStore.cargarMisPagos(),
    cargarApartamento(),
  ])
})

async function cargarApartamento() {
  try {
    const { data } = await api.get('/apartamentos/')
    const miApto = data.find((a) => String(a.propietario_id) === String(authStore.usuarioId))
    if (miApto) {
      aptoInfo.value = miApto
    }
  } catch (e) {
    console.error('Error al cargar datos del apartamento:', e)
  }
}
</script>
