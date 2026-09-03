<template>
  <PropietarioLayout>
    <div class="max-w-2xl mx-auto flex flex-col gap-6">
      <!-- Encabezado y Datos de Pago del Condominio -->
      <NeuCard>
        <div class="flex items-center gap-3 mb-4">
          <span class="text-3xl">💳</span>
          <div>
            <h2 class="text-xl font-bold text-neu-green">Reportar Pago de Condominio</h2>
            <p class="text-xs text-neu-text-light">
              Registra tu comprobante para que la administración o junta concilie tu pago
            </p>
          </div>
        </div>

        <!-- Cuentas bancarias del condominio -->
        <div class="bg-neu-bg-dark p-4 rounded-neu-sm border border-neu-shadow-dark text-xs text-neu-text flex flex-col gap-1.5">
          <p class="font-bold text-neu-green">📌 Datos Oficiales de Recaudación (Edificio Alcatraz):</p>
          <p><span class="font-semibold">Banco:</span> Banco de Venezuela (0102)</p>
          <p><span class="font-semibold">Pago Móvil:</span> 0414-1234567 | C.I. V-00000001</p>
          <p><span class="font-semibold">Transferencias VES:</span> 0102-0000-00-0000000000</p>
          <p><span class="font-semibold">Zelle:</span> pagos@edificioalcatraz.com</p>
          <p class="text-neu-green font-semibold mt-1">
            Tasa oficial BCV hoy: {{ tasaStore.tasaActual ? formatTasa(tasaStore.tasaActual) : 'Consultando...' }}
          </p>
        </div>
      </NeuCard>

      <!-- Formulario de Auto-reporte de Pago -->
      <NeuCard>
        <form @submit.prevent="enviarPago" class="flex flex-col gap-4">
          <!-- Recibo a pagar -->
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium text-neu-text-light">Recibo / Período a Cancelar</label>
            <select v-model="form.recibo_id" class="input-neu" required>
              <option :value="null" disabled>Selecciona el recibo pendiente...</option>
              <option
                v-for="recibo in recibosPendientes"
                :key="recibo.id"
                :value="recibo.id"
              >
                {{ formatPeriodo(recibo.mes_periodo) }} — Pendiente: {{ formatUSD(recibo.monto_pendiente_usd) }}
                ({{ formatVES(tasaStore.convertirUSDaVES(recibo.monto_pendiente_usd)) }})
              </option>
            </select>
          </div>

          <!-- Método y Moneda de Pago -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1">
              <label class="text-sm font-medium text-neu-text-light">Método de Pago</label>
              <select v-model="form.metodo_pago" class="input-neu" required>
                <option
                  v-for="metodo in METODOS_PAGO"
                  :key="metodo.value"
                  :value="metodo.value"
                >
                  {{ metodo.label }}
                </option>
              </select>
            </div>

            <div class="flex flex-col gap-1">
              <label class="text-sm font-medium text-neu-text-light">Moneda del Pago</label>
              <select v-model="form.moneda_pago" class="input-neu" required>
                <option value="VES">Bolívares (VES)</option>
                <option value="USD">Dólares (USD)</option>
              </select>
            </div>
          </div>

          <!-- Monto y Referencia -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <NeuInput
              id="monto"
              :label="`Monto Transferido (${form.moneda_pago})`"
              v-model="form.monto_declarado"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="Ej. 500.00"
              required
            />

            <NeuInput
              id="referencia"
              label="Número de Referencia"
              v-model="form.referencia_bancaria"
              placeholder="Últimos 6 u 8 dígitos"
              required
            />
          </div>

          <!-- Banco de Origen (opcional) -->
          <NeuInput
            id="banco"
            label="Banco de Origen (Opcional)"
            v-model="form.banco_origen"
            placeholder="Ej. Mercantil, Banesco, Banesco Panamá, etc."
          />

          <!-- Cálculo en tiempo real de equivalencia -->
          <div v-if="montoCalculadoUSD > 0" class="p-3 bg-neu-bg-dark rounded-neu-sm text-xs flex justify-between items-center border border-neu-shadow-dark">
            <span class="text-neu-text-light">Monto equivalente acreditado:</span>
            <span class="font-bold text-sm text-neu-green">{{ formatUSD(montoCalculadoUSD) }}</span>
          </div>

          <!-- Adjuntar Comprobante de Pago -->
          <div class="flex flex-col gap-1.5">
            <label class="text-sm font-medium text-neu-text-light">Comprobante de Pago (Captura o PDF)</label>
            <input
              type="file"
              @change="manejarArchivo"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              class="input-neu text-xs file:mr-4 file:py-1 file:px-3 file:rounded-neu-sm file:border-0 file:text-xs file:font-semibold file:bg-neu-green file:text-white hover:file:opacity-90"
              required
            />
            <span class="text-xs text-neu-text-light">Formatos permitidos: JPG, PNG, WEBP o PDF (Máximo 5MB)</span>
          </div>

          <!-- Botón de Envío -->
          <div class="mt-4 flex justify-end gap-3">
            <RouterLink to="/mi-cuenta/inicio">
              <NeuButton type="button">Cancelar</NeuButton>
            </RouterLink>
            <NeuButton variant="primary" type="submit" :loading="enviando">
              🚀 Reportar Pago
            </NeuButton>
          </div>
        </form>
      </NeuCard>
    </div>
  </PropietarioLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useToast } from 'vue-toastification'
import { PropietarioLayout } from '@/components/layout'
import { NeuCard, NeuButton, NeuInput } from '@/components/neumorph'
import { useTasaStore, useRecibosStore, usePagosStore } from '@/stores'
import { formatUSD, formatVES, formatTasa, formatPeriodo } from '@/utils'
import { METODOS_PAGO } from '@/constants'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const tasaStore = useTasaStore()
const recibosStore = useRecibosStore()
const pagosStore = usePagosStore()

const enviando = ref(false)
const archivoComprobante = ref(null)

const form = ref({
  recibo_id: null,
  metodo_pago: 'pago_movil',
  moneda_pago: 'VES',
  monto_declarado: '',
  referencia_bancaria: '',
  banco_origen: '',
})

const recibosPendientes = computed(() => {
  return (recibosStore.lista || []).filter((r) => r.estado_pago !== 'pagado')
})

const montoCalculadoUSD = computed(() => {
  const monto = parseFloat(form.value.monto_declarado) || 0
  if (monto <= 0) return 0
  if (form.value.moneda_pago === 'USD') return monto
  const tasa = parseFloat(tasaStore.tasaActual) || 0
  return tasa > 0 ? parseFloat((monto / tasa).toFixed(2)) : 0
})

onMounted(async () => {
  await Promise.all([
    tasaStore.cargarTasa(),
    recibosStore.cargarMisRecibos(),
  ])

  if (route.query.recibo_id) {
    form.value.recibo_id = parseInt(route.query.recibo_id)
  } else if (recibosPendientes.value.length > 0) {
    form.value.recibo_id = recibosPendientes.value[0].id
  }
})

function manejarArchivo(event) {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      toast.error('El comprobante no debe superar los 5MB')
      event.target.value = ''
      return
    }
    archivoComprobante.value = file
  }
}

async function enviarPago() {
  if (!form.value.recibo_id) {
    toast.error('Selecciona el recibo a cancelar')
    return
  }
  if (!archivoComprobante.value) {
    toast.error('Adjunta el comprobante o captura de la transferencia')
    return
  }

  enviando.value = true
  try {
    const data = new FormData()
    data.append('recibo_id', form.value.recibo_id)
    data.append('metodo_pago', form.value.metodo_pago)
    data.append('moneda_pago', form.value.moneda_pago)
    data.append('monto_declarado', form.value.monto_declarado)
    data.append('referencia_bancaria', form.value.referencia_bancaria)
    if (form.value.banco_origen) {
      data.append('banco_origen', form.value.banco_origen)
    }
    data.append('comprobante', archivoComprobante.value)

    await pagosStore.reportarPago(data)
    toast.success('¡Pago reportado con éxito! Se encuentra en revisión.')
    await router.push('/mi-cuenta/inicio')
  } catch (error) {
    const detalle = error.response?.data?.detail
    if (Array.isArray(detalle)) {
      toast.error(detalle.map(d => d.msg || d).join(', '))
    } else if (typeof detalle === 'string') {
      toast.error(detalle)
    } else {
      toast.error('Error al reportar el pago. Por favor verifica los datos o vuelve a iniciar sesión.')
    }
  } finally {
    enviando.value = false
  }
}
</script>
