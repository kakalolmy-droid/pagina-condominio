<template>
  <PropietarioLayout>
    <div class="flex flex-col gap-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold text-neu-green">Mis Recibos e Historial de Solvencias</h2>
          <p class="text-xs text-neu-text-light">
            Consulta todas tus cuotas mensuales y descarga tus recibos de pago
          </p>
        </div>

        <RouterLink to="/mi-cuenta/pagar">
          <NeuButton variant="primary" class="text-sm">
            ➕ Reportar Pago
          </NeuButton>
        </RouterLink>
      </div>

      <!-- Tabla Historial de Recibos -->
      <NeuCard>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead>
              <tr class="border-b border-neu-shadow-dark text-neu-text-light">
                <th class="pb-3 font-semibold">Período</th>
                <th class="pb-3 font-semibold">Emisión</th>
                <th class="pb-3 font-semibold">Vencimiento</th>
                <th class="pb-3 font-semibold">Total Cuota ($)</th>
                <th class="pb-3 font-semibold">Monto Pendiente</th>
                <th class="pb-3 font-semibold text-center">Estado</th>
                <th class="pb-3 font-semibold text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="recibo in recibosStore.lista"
                :key="recibo.id"
                class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
              >
                <td class="py-3 font-bold text-neu-green">{{ formatPeriodo(recibo.mes_periodo) }}</td>
                <td class="py-3 text-neu-text-light text-xs">{{ formatFecha(recibo.fecha_emision) }}</td>
                <td class="py-3 text-neu-text-light text-xs">{{ formatFecha(recibo.fecha_vencimiento) }}</td>
                <td class="py-3 font-bold text-neu-text">{{ formatUSD(recibo.monto_total_usd) }}</td>
                <td
                  class="py-3 font-semibold"
                  :class="recibo.monto_pendiente_usd > 0 ? 'text-neu-danger' : 'text-neu-success'"
                >
                  {{ formatUSD(recibo.monto_pendiente_usd) }}
                  <span v-if="recibo.monto_pendiente_usd > 0" class="block text-xs text-neu-text-light">
                    {{ formatVES(tasaStore.convertirUSDaVES(recibo.monto_pendiente_usd)) }}
                  </span>
                </td>
                <td class="py-3 text-center">
                  <!-- Estado sincronizado con la verificación del administrador -->
                  <span
                    v-if="recibo.ultimo_pago_estado === 'en_revision'"
                    class="badge-warning text-[11px] font-bold px-2.5 py-1 inline-flex items-center gap-1 shadow-sm"
                    title="Tu pago fue enviado y está siendo verificado por la administración"
                  >
                    ⏳ En Revisión
                  </span>
                  <span
                    v-else-if="recibo.ultimo_pago_estado === 'rechazado'"
                    class="badge-danger text-[11px] font-bold px-2.5 py-1 inline-flex items-center gap-1 shadow-sm"
                    title="El comprobante fue rechazado. Por favor vuelve a reportar el pago"
                  >
                    ❌ Rechazado
                  </span>
                  <span
                    v-else-if="recibo.estado_pago === 'pagado'"
                    class="badge-success text-[11px] font-bold px-2.5 py-1 inline-flex items-center gap-1 shadow-sm"
                  >
                    ✓ Aprobado
                  </span>
                  <span
                    v-else
                    class="badge-danger text-[11px] font-bold px-2.5 py-1 inline-flex items-center gap-1 shadow-sm"
                  >
                    ● Pendiente
                  </span>
                </td>
                <td class="py-3 text-center">
                  <span
                    v-if="recibo.ultimo_pago_estado === 'en_revision'"
                    class="text-[11px] font-semibold text-amber-700 bg-amber-50 px-2.5 py-1 rounded-neu-sm border border-amber-300"
                  >
                    Verificando...
                  </span>
                  <RouterLink
                    v-else-if="recibo.ultimo_pago_estado === 'rechazado'"
                    :to="{ path: '/mi-cuenta/pagar', query: { recibo_id: recibo.id } }"
                    class="text-xs font-bold text-neu-danger bg-neu-bg px-3 py-1.5 rounded-neu-sm shadow-neu-sm hover:shadow-neu-inset transition-all"
                  >
                    Reintentar Pago
                  </RouterLink>
                  <RouterLink
                    v-else-if="recibo.estado_pago !== 'pagado'"
                    :to="{ path: '/mi-cuenta/pagar', query: { recibo_id: recibo.id } }"
                    class="text-xs font-bold text-neu-green bg-neu-bg px-3 py-1.5 rounded-neu-sm shadow-neu-sm hover:shadow-neu-inset transition-all"
                  >
                    Pagar
                  </RouterLink>
                  <span v-else class="text-xs font-bold text-neu-green">
                    ✓ Solvente
                  </span>
                </td>
              </tr>
              <tr v-if="recibosStore.lista.length === 0">
                <td colspan="7" class="py-8 text-center text-neu-text-light">
                  No hay recibos registrados para tu apartamento.
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
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { PropietarioLayout } from '@/components/layout'
import { NeuCard, NeuButton } from '@/components/neumorph'
import { EstadoPagoBadge } from '@/components/shared'
import { useRecibosStore, useTasaStore } from '@/stores'
import { formatUSD, formatVES, formatFecha, formatPeriodo } from '@/utils'

const recibosStore = useRecibosStore()
const tasaStore = useTasaStore()

onMounted(async () => {
  await Promise.all([
    recibosStore.cargarMisRecibos(),
    tasaStore.cargarTasa(),
  ])
})
</script>
