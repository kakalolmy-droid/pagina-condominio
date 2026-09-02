<template>
  <AdminLayout
    titulo="Avisos y Cobranzas Masivas por WhatsApp"
    subtitulo="Envío masivo automático a todos los números registrados con fecha límite, datos bancarios y link de pago"
  >
    <!-- Tarjeta 1: Vinculación Oficial de la Línea WhatsApp del Condominio (Con Código QR en Vivo) -->
    <NeuCard class="mb-8 border-2 border-neu-green/30">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div class="flex items-center gap-3">
          <span class="text-3xl">📱</span>
          <div>
            <h3 class="text-lg font-bold text-neu-green">Línea Oficial de WhatsApp de la Junta / Condominio</h3>
            <p class="text-xs text-neu-text-light">
              Vincula el número que la junta de condominio o administración utilizará para despachar los mensajes masivos
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <span
            class="px-3 py-1.5 rounded-full text-xs font-bold"
            :class="botEstado.connected ? 'badge-success' : 'badge-warning'"
          >
            {{ botEstado.connected ? '● LÍNEA CONECTADA Y LISTA' : '○ PENDIENTE DE VINCULACIÓN' }}
          </span>
          <button
            v-if="botEstado.connected"
            @click="desvincularNumero"
            class="px-3 py-1.5 rounded-neu-sm text-xs font-bold bg-red-600 text-white shadow-neu-sm hover:bg-red-700 transition-all cursor-pointer"
          >
            Cambiar Número
          </button>
        </div>
      </div>

      <!-- Estado Conectado -->
      <div v-if="botEstado.connected" class="p-4 bg-neu-bg-dark rounded-neu-sm border border-neu-shadow-dark flex flex-col sm:flex-row justify-between items-center gap-2">
        <div class="text-xs text-neu-text">
          <p class="font-bold text-neu-green">✅ WhatsApp Autónomo Activo</p>
          <p class="text-neu-text-light mt-0.5">
            Línea emisora: <span class="font-mono font-semibold text-neu-text">{{ botEstado.session?.id || 'Número Oficial Vinculado' }}</span>
          </p>
        </div>
        <span class="text-xs text-neu-text-light italic">Todos los avisos saldrán directamente desde este número sin abrir WhatsApp Web</span>
      </div>

      <!-- Estado No Conectado: Mostrar Código QR para escanear con el celular -->
      <div v-else class="p-4 bg-neu-bg-dark rounded-neu-sm border border-neu-shadow-dark flex flex-col md:flex-row items-center gap-6">
        <div v-if="botEstado.qr" class="flex flex-col items-center bg-white p-3 rounded-neu-sm shadow-neu-sm">
          <img :src="botEstado.qr" alt="Código QR WhatsApp" class="w-44 h-44 object-contain" />
          <span class="text-xs text-black font-semibold mt-2">Escanea este QR</span>
        </div>
        <div v-else class="flex items-center justify-center w-44 h-44 bg-neu-bg rounded-neu-sm border border-neu-shadow-dark text-xs text-neu-text-light">
          Generando código QR...
        </div>

        <div class="flex-1 text-xs text-neu-text flex flex-col gap-2">
          <p class="font-bold text-neu-green text-sm">📲 Pasos para Vincular la Línea Oficial:</p>
          <ol class="list-decimal list-inside space-y-1 text-neu-text-light">
            <li>Abre la aplicación de <strong>WhatsApp</strong> en el teléfono de la Junta / Condominio.</li>
            <li>Toca en <strong>Menú / Ajustes (⚙️)</strong> y selecciona <strong>Dispositivos vinculados</strong>.</li>
            <li>Toca en <strong>Vincular un dispositivo</strong> y apunta la cámara a este código QR.</li>
          </ol>
          <p class="text-neu-green font-semibold mt-1">
            Una vez escaneado, la sesión queda guardada de forma permanente en Docker y podrás cambiar de número cuando quieras.
          </p>
        </div>
      </div>
    </NeuCard>

    <!-- Tarjeta 2: Formulario de Despacho Masivo Automático -->
    <NeuCard class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <span class="text-3xl">🚀</span>
        <div>
          <h3 class="text-lg font-bold text-neu-green">Configurar Aviso Masivo y Enviar a Todos</h3>
          <p class="text-xs text-neu-text-light">
            Indica la fecha límite de pago y los datos bancarios. Al hacer clic, el servidor enviará a todos los números vinculados en la base de datos de manera inmediata.
          </p>
        </div>
      </div>

      <form @submit.prevent="enviarMasivo" class="flex flex-col gap-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <NeuInput
            id="periodo"
            label="Período / Mes a Facturar (YYYY-MM)"
            v-model="formAvisos.periodo"
            placeholder="2026-09"
            required
          />

          <NeuInput
            id="fecha_limite"
            label="Fecha Límite de Pago"
            v-model="formAvisos.fecha_limite"
            type="date"
            required
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <NeuInput
            id="banco"
            label="Banco de Recaudación"
            v-model="formAvisos.banco"
            placeholder="Banco de Venezuela (0102)"
          />

          <NeuInput
            id="pago_movil"
            label="Pago Móvil Oficial"
            v-model="formAvisos.pago_movil"
            placeholder="0414-1234567 | V-00000001"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <NeuInput
            id="transferencia"
            label="Cuenta Bancaria (Transferencias VES)"
            v-model="formAvisos.transferencia"
            placeholder="0102-0000-00-0000000000"
          />

          <NeuInput
            id="zelle"
            label="Zelle / Divisas (Opcional)"
            v-model="formAvisos.zelle"
            placeholder="pagos@edificioalcatraz.com"
          />
        </div>

        <NeuInput
          id="nota"
          label="Nota o Mensaje Adicional (Opcional)"
          v-model="formAvisos.nota_adicional"
          placeholder="Ej. Recordamos que a partir del día 15 se genera recargo por mora."
        />

        <div class="flex justify-end gap-3 mt-2">
          <NeuButton variant="primary" type="submit" :loading="enviando">
            📲 Enviar Automáticamente a Todos los Números Vinculados
          </NeuButton>
        </div>
      </form>
    </NeuCard>

    <!-- Confirmación de Despacho Exitoso -->
    <NeuCard v-if="resultadoEnvio" class="mb-8 border-2 border-neu-green bg-neu-green/5">
      <div class="flex items-center gap-3">
        <span class="text-3xl">✅</span>
        <div>
          <h3 class="text-lg font-bold text-neu-green">{{ resultadoEnvio.mensaje }}</h3>
          <p class="text-xs text-neu-text-light mt-1">
            Total notificados: <span class="font-bold text-neu-text">{{ resultadoEnvio.total_destinatarios }}</span> propietarios ({{ resultadoEnvio.destinatarios?.join(', ') }})
          </p>
        </div>
      </div>
    </NeuCard>

    <!-- Exportación a Excel -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <NeuCard>
        <div class="flex items-center gap-3 mb-3">
          <span class="text-3xl">📊</span>
          <div>
            <h3 class="text-lg font-bold text-neu-green">Exportar Reporte a Excel</h3>
            <p class="text-xs text-neu-text-light">
              Descarga la matriz contable con 3 hojas: Deudas, Pagos y Saldos a Favor
            </p>
          </div>
        </div>

        <div class="flex items-end gap-3 mt-4">
          <div class="flex-1">
            <NeuInput
              id="periodo_excel"
              label="Período (YYYY-MM)"
              v-model="periodoExcel"
              placeholder="2026-09"
              required
            />
          </div>
          <NeuButton variant="primary" @click="exportarExcel" :loading="exportando">
            📥 Descargar .xlsx
          </NeuButton>
        </div>
      </NeuCard>

      <NeuCard>
        <div class="flex items-center gap-3 mb-3">
          <span class="text-3xl">💱</span>
          <div>
            <h3 class="text-lg font-bold text-neu-green">Tasa Oficial BCV Aplicada</h3>
            <p class="text-xs text-neu-text-light">
              Sincronizada automáticamente desde el Banco Central de Venezuela
            </p>
          </div>
        </div>

        <div class="mt-4 p-4 bg-neu-bg-dark rounded-neu-sm border border-neu-shadow-dark flex justify-between items-center">
          <span class="text-xs text-neu-text-light">Tasa del día:</span>
          <span class="font-bold text-lg text-neu-green">
            {{ tasaStore.tasaActual ? formatTasa(tasaStore.tasaActual) : 'Cargando...' }}
          </span>
        </div>
      </NeuCard>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { AdminLayout } from '@/components/layout'
import { NeuCard, NeuButton, NeuInput } from '@/components/neumorph'
import { reportesService, api } from '@/services'
import { useTasaStore } from '@/stores'
import { formatTasa, periodoActual } from '@/utils'

const toast = useToast()
const tasaStore = useTasaStore()

const periodoExcel = ref(periodoActual())
const exportando = ref(false)
const enviando = ref(false)
const resultadoEnvio = ref(null)
const botEstado = ref({ connected: false, session: null, qr: null })
let pollingTimer = null

const formAvisos = ref({
  periodo: periodoActual(),
  fecha_limite: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  banco: 'Banco de Venezuela (0102)',
  pago_movil: '0414-1234567 | C.I. V-00000001',
  transferencia: '0102-0000-00-0000000000',
  zelle: 'pagos@edificioalcatraz.com',
  nota_adicional: '',
})

onMounted(async () => {
  await Promise.all([
    tasaStore.cargarTasa(),
    cargarEstadoBot(),
  ])

  // Sondeo de estado del QR cada 3 segundos hasta que se vincule
  pollingTimer = setInterval(async () => {
    if (!botEstado.value.connected) {
      await cargarEstadoBot()
    }
  }, 3000)
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})

async function cargarEstadoBot() {
  try {
    const { data } = await api.get('/whatsapp-bot/status')
    botEstado.value = data
  } catch (e) {
    console.error('Error al cargar estado del bot:', e)
  }
}

async function desvincularNumero() {
  if (confirm('¿Desea desvincular el número actual de WhatsApp para configurar uno nuevo?')) {
    try {
      await api.post('/whatsapp-bot/logout')
      toast.info('Línea desvinculada. Listo para nuevo escaneo.')
      await cargarEstadoBot()
    } catch (e) {
      toast.error('Error al desvincular el número')
    }
  }
}

async function enviarMasivo() {
  enviando.value = true
  resultadoEnvio.value = null
  try {
    const { data } = await reportesService.enviarMasivoAutomatico(formAvisos.value)
    resultadoEnvio.value = data
    toast.success(data.mensaje)
  } catch (error) {
    console.error('Error al enviar avisos:', error)
    toast.error('Error al enviar los avisos masivos')
  } finally {
    enviando.value = false
  }
}

async function exportarExcel() {
  if (!periodoExcel.value) {
    toast.error('Ingrese un período válido')
    return
  }

  exportando.value = true
  try {
    const res = await reportesService.exportarExcel(periodoExcel.value)
    const blob = new Blob([res.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `reporte_alcatraz_${periodoExcel.value}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    toast.success('¡Reporte Excel descargado!')
  } catch (error) {
    toast.error('Error al generar el reporte en Excel')
  } finally {
    exportando.value = false
  }
}
</script>
