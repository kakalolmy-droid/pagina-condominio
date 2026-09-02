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
                  <EstadoPagoBadge :estado="recibo.estado_pago" />
                </td>
                <td class="py-3 text-center">
                  <RouterLink
                    v-if="recibo.estado_pago !== 'pagado'"
                    :to="{ path: '/mi-cuenta/pagar', query: { recibo_id: recibo.id } }"
                    class="text-xs font-bold text-neu-green bg-neu-bg px-3 py-1.5 rounded-neu-sm shadow-neu-sm hover:shadow-neu-inset transition-all"
                  >
                    Pagar
                  </RouterLink>
                  <span v-else class="text-xs font-semibold text-neu-success">
                    ✓ Pagado
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
