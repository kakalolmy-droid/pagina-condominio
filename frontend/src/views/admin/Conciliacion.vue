<template>
  <AdminLayout
    titulo="Bandeja de Conciliación de Pagos"
    subtitulo="Revisión, validación bancaria, aprobación/rechazo y emisión de solvencias digitales"
  >
    <!-- Métricas rápidas de conciliación -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-6">
      <NeuCard>
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-neu-text-light uppercase tracking-wider">Por Conciliar</span>
          <span class="text-xl">⏳</span>
        </div>
        <h3 class="text-2xl font-bold text-neu-warning mt-1">
          {{ pagosPendientes.length }} pagos
        </h3>
        <p class="text-xs text-neu-text-light mt-1">Comprobantes en revisión</p>
      </NeuCard>

      <NeuCard>
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-neu-text-light uppercase tracking-wider">Monto por Validar ($)</span>
          <span class="text-xl">💵</span>
        </div>
        <h3 class="text-2xl font-bold text-neu-green mt-1">
          {{ formatUSD(montoTotalPendienteUSD) }}
        </h3>
        <p class="text-xs text-neu-text-light mt-1">
          Equivalente: {{ formatVES(montoTotalPendienteVES) }}
        </p>
      </NeuCard>

      <NeuCard>
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-neu-text-light uppercase tracking-wider">Tasa BCV Aplicada</span>
          <span class="text-xl">💱</span>
        </div>
        <h3 class="text-2xl font-bold text-neu-text mt-1">
          {{ tasaStore.tasaActual ? formatTasa(tasaStore.tasaActual) : '—' }}
        </h3>
        <p class="text-xs text-neu-text-light mt-1">Oficial Banco Central de Venezuela</p>
      </NeuCard>
    </div>

    <!-- Lista de Pagos Pendientes por Conciliar -->
    <NeuCard>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-neu-green">Comprobantes de Pago por Validar</h3>
        <button
          @click="pagosStore.cargarPendientes"
          class="text-xs font-semibold text-neu-green hover:underline cursor-pointer"
        >
          🔄 Actualizar lista
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-neu-shadow-dark text-neu-text-light">
              <th class="pb-3 font-semibold">Fecha Reporte</th>
              <th class="pb-3 font-semibold">Apto</th>
              <th class="pb-3 font-semibold">Método / Banco</th>
              <th class="pb-3 font-semibold">Referencia</th>
              <th class="pb-3 font-semibold">Monto Reportado</th>
              <th class="pb-3 font-semibold">Equivalente USD</th>
              <th class="pb-3 font-semibold text-center">Comprobante</th>
              <th class="pb-3 font-semibold text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="pago in pagosPendientes"
              :key="pago.id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
            >
              <td class="py-3 text-xs text-neu-text-light">{{ formatFecha(pago.fecha_reporte) }}</td>
              <td class="py-3 font-bold text-neu-green">Apto {{ obtenerNumeroApto(pago.apartamento_id) }}</td>
              <td class="py-3 text-neu-text">
                <span class="capitalize font-semibold">{{ pago.metodo_pago.replace('_', ' ') }}</span>
                <span v-if="pago.banco_origen" class="block text-xs text-neu-text-light">
                  {{ pago.banco_origen }}
                </span>
              </td>
              <td class="py-3 font-mono text-xs text-neu-text">{{ pago.referencia_bancaria }}</td>
              <td class="py-3 font-bold text-neu-text">
                {{ pago.moneda_pago === 'VES' ? formatVES(pago.monto_declarado) : formatUSD(pago.monto_declarado) }}
              </td>
              <td class="py-3 font-bold text-neu-green">{{ formatUSD(pago.monto_equivalente_usd) }}</td>
              <td class="py-3 text-center">
                <button
                  @click="abrirComprobante(pago.comprobante_url)"
                  class="text-xs font-bold text-neu-green bg-neu-bg px-3 py-1.5 rounded-neu-sm shadow-neu-sm hover:shadow-neu-inset transition-all cursor-pointer"
                >
                  🔍 Ver Archivo
                </button>
              </td>
              <td class="py-3 text-center">
                <div class="flex items-center justify-center gap-2">
                  <button
                    @click="aprobarPago(pago)"
                    :disabled="procesandoId === pago.id"
                    class="px-3 py-1.5 rounded-neu-sm text-xs font-bold bg-green-600 text-white shadow-neu-sm hover:opacity-90 transition-all cursor-pointer"
                    title="Aprobar pago"
                  >
                    ✓ Aprobar
                  </button>
                  <button
                    @click="abrirModalRechazo(pago)"
                    :disabled="procesandoId === pago.id"
                    class="px-3 py-1.5 rounded-neu-sm text-xs font-bold bg-red-600 text-white shadow-neu-sm hover:opacity-90 transition-all cursor-pointer"
                    title="Rechazar pago"
                  >
                    ✕ Rechazar
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="pagosPendientes.length === 0">
              <td colspan="8" class="py-10 text-center text-neu-text-light">
                <span class="text-3xl block mb-2">🎉</span>
                <p class="font-semibold text-neu-green">¡Todo al día!</p>
                <p class="text-xs">No hay comprobantes pendientes por conciliar.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>

    <!-- Modal para Rechazar Pago con Motivo -->
    <NeuModal v-model="modalRechazoAbierto" title="Rechazar Comprobante de Pago">
      <form @submit.prevent="ejecutarRechazo" class="flex flex-col gap-4">
        <p class="text-xs text-neu-text-light">
          Indique la razón por la cual se rechaza el pago (ej. referencia no encontrada en cuenta bancaria, monto incompleto, captura ilegible).
        </p>

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-neu-text-light">Motivo del Rechazo</label>
          <textarea
            v-model="motivoRechazo"
            rows="3"
            placeholder="Ej. La referencia no aparece reflejada en el estado de cuenta bancario..."
            class="input-neu text-sm"
            required
          ></textarea>
        </div>

        <div class="flex justify-end gap-3 mt-2">
          <NeuButton type="button" @click="modalRechazoAbierto = false">
            Cancelar
          </NeuButton>
          <NeuButton variant="danger" type="submit" :loading="procesandoId !== null">
            Confirmar Rechazo
          </NeuButton>
        </div>
      </form>
    </NeuModal>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { AdminLayout } from '@/components/layout'
import { NeuCard, NeuButton, NeuModal } from '@/components/neumorph'
import { usePagosStore, useApartamentosStore, useTasaStore } from '@/stores'
import { formatUSD, formatVES, formatTasa, formatFecha } from '@/utils'

const toast = useToast()
const pagosStore = usePagosStore()
const aptosStore = useApartamentosStore()
const tasaStore = useTasaStore()

const procesandoId = ref(null)
const modalRechazoAbierto = ref(false)
const pagoSeleccionado = ref(null)
const motivoRechazo = ref('')

const pagosPendientes = computed(() => pagosStore.pendientesConciliacion || [])

const montoTotalPendienteUSD = computed(() => {
  return pagosPendientes.value.reduce((acc, p) => acc + (parseFloat(p.monto_equivalente_usd) || 0), 0)
})

const montoTotalPendienteVES = computed(() => {
  return tasaStore.tasaActual ? montoTotalPendienteUSD.value * parseFloat(tasaStore.tasaActual) : 0
})

onMounted(async () => {
  await Promise.all([
    pagosStore.cargarPendientes(),
    aptosStore.cargar(),
    tasaStore.cargarTasa(),
  ])
})

function obtenerNumeroApto(aptoId) {
  const apto = aptosStore.lista.find((a) => a.id === aptoId)
  return apto ? apto.numero_apto : `#${aptoId}`
}

function abrirComprobante(url) {
  if (url) {
    window.open(url, '_blank')
  } else {
    toast.warning('No hay archivo adjunto')
  }
}

async function aprobarPago(pago) {
  if (confirm(`¿Aprobar el pago de ${formatUSD(pago.monto_equivalente_usd)} para el Apto ${obtenerNumeroApto(pago.apartamento_id)}?`)) {
    procesandoId.value = pago.id
    try {
      await pagosStore.aprobar(pago.id)
      toast.success('¡Pago aprobado con éxito! Recibo actualizado y solvencia emitida.')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al aprobar el pago')
    } finally {
      procesandoId.value = null
    }
  }
}

function abrirModalRechazo(pago) {
  pagoSeleccionado.value = pago
  motivoRechazo.value = ''
  modalRechazoAbierto.value = true
}

async function ejecutarRechazo() {
  if (!pagoSeleccionado.value || !motivoRechazo.value.trim()) return

  procesandoId.value = pagoSeleccionado.value.id
  try {
    await pagosStore.rechazar(pagoSeleccionado.value.id, motivoRechazo.value.trim())
    toast.info('Pago rechazado')
    modalRechazoAbierto.value = false
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Error al procesar el rechazo')
  } finally {
    procesandoId.value = null
  }
}
</script>
