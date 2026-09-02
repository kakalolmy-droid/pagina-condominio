<template>
  <AdminLayout
    titulo="Emisión y Facturación de Recibos"
    subtitulo="Generación automatizada de recibos mensuales por alícuotas y consulta de cobranza"
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

          <NeuButton variant="primary" type="submit" :loading="emitiendo" class="w-full justify-center">
            🚀 Emitir a Todos
          </NeuButton>
        </form>
      </NeuCard>
    </div>

    <!-- Filtros de Recibos Emitidos -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <select v-model="filtroEstado" class="input-neu text-sm py-2">
          <option value="">Todos los Estados</option>
          <option value="pendiente">Pendientes</option>
          <option value="parcial">Parciales</option>
          <option value="pagado">Pagados</option>
        </select>

        <input
          v-model="filtroPeriodo"
          type="text"
          placeholder="Filtrar período (ej. 2026-09)"
          class="input-neu text-sm py-2 w-48"
        />
      </div>

      <p class="text-xs text-neu-text-light">
        Total recibos listados: <span class="font-bold text-neu-green">{{ recibosFiltrados.length }}</span>
      </p>
    </div>

    <!-- Tabla de Recibos Emitidos -->
    <NeuCard>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-neu-shadow-dark text-neu-text-light">
              <th class="pb-3 font-semibold">Período</th>
              <th class="pb-3 font-semibold">Apartamento</th>
              <th class="pb-3 font-semibold">Monto Total</th>
              <th class="pb-3 font-semibold">Monto Pendiente</th>
              <th class="pb-3 font-semibold">Equivalente VES (BCV)</th>
              <th class="pb-3 font-semibold">Vencimiento</th>
              <th class="pb-3 font-semibold text-center">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="recibo in recibosFiltrados"
              :key="recibo.id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
            >
              <td class="py-3 font-bold text-neu-green">{{ formatPeriodo(recibo.mes_periodo) }}</td>
              <td class="py-3 font-semibold text-neu-text">Apto {{ obtenerNumeroApto(recibo.apartamento_id) }}</td>
              <td class="py-3 font-bold text-neu-text">{{ formatUSD(recibo.monto_total_usd) }}</td>
              <td class="py-3 font-bold" :class="recibo.monto_pendiente_usd > 0 ? 'text-neu-danger' : 'text-neu-success'">
                {{ formatUSD(recibo.monto_pendiente_usd) }}
              </td>
              <td class="py-3 text-neu-text-light">
                {{ formatVES(tasaStore.convertirUSDaVES(recibo.monto_pendiente_usd)) }}
              </td>
              <td class="py-3 text-neu-text-light">{{ formatFecha(recibo.fecha_vencimiento) }}</td>
              <td class="py-3 text-center">
                <EstadoPagoBadge :estado="recibo.estado_pago" />
              </td>
            </tr>
            <tr v-if="recibosFiltrados.length === 0">
              <td colspan="7" class="py-8 text-center text-neu-text-light">
                No hay recibos generados para este filtro.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { AdminLayout } from '@/components/layout'
import { NeuCard, NeuButton, NeuInput } from '@/components/neumorph'
import { EstadoPagoBadge } from '@/components/shared'
import { useRecibosStore, useApartamentosStore, useTasaStore } from '@/stores'
import { formatUSD, formatVES, formatFecha, formatPeriodo, periodoActual } from '@/utils'

const toast = useToast()
const recibosStore = useRecibosStore()
const aptosStore = useApartamentosStore()
const tasaStore = useTasaStore()

const emitiendo = ref(false)
const filtroEstado = ref('')
const filtroPeriodo = ref('')

const emisionForm = ref({
  periodo: periodoActual(),
  gasto_total_usd: '',
  dias_vencimiento: 30,
})

const recibosFiltrados = computed(() => {
  let lista = recibosStore.lista || []
  if (filtroEstado.value) {
    lista = lista.filter((r) => r.estado_pago === filtroEstado.value)
  }
  if (filtroPeriodo.value) {
    lista = lista.filter((r) => r.mes_periodo.includes(filtroPeriodo.value))
  }
  return lista
})

onMounted(async () => {
  await Promise.all([
    recibosStore.cargar(),
    aptosStore.cargar(),
    tasaStore.cargarTasa(),
  ])
})

function obtenerNumeroApto(aptoId) {
  const apto = aptosStore.lista.find((a) => a.id === aptoId)
  return apto ? apto.numero_apto : `#${aptoId}`
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
    await recibosStore.cargar()
    emisionForm.value.gasto_total_usd = ''
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Error al emitir los recibos')
  } finally {
    emitiendo.value = false
  }
}
</script>
