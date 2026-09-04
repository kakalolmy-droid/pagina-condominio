<template>
  <AdminLayout
    titulo="Avisos y Cobranzas Masivas por WhatsApp"
    subtitulo="Envío masivo automático a todos los números registrados con fecha límite, datos bancarios y link de pago"
  >
    <!-- Tarjeta 1: Vinculación Oficial de la Línea WhatsApp del Condominio (Con Código QR y Código de 8 Dígitos) -->
    <NeuCard class="mb-8 border-2 border-neu-green/30">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div class="flex items-center gap-3">
          <span class="text-3xl">📱</span>
          <div>
            <h3 class="text-lg font-bold text-neu-green">Línea Oficial de WhatsApp de la Junta / Condominio</h3>
            <p class="text-xs text-neu-text-light">
              Vincula el número que la administración utilizará para despachar los mensajes masivos automáticos
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
        <span class="text-xs text-neu-text-light italic">Todos los avisos saldrán directamente desde este número de forma automática</span>
      </div>

      <!-- Estado No Conectado: 2 Métodos (Código QR O Vincular con Código Numérico) -->
      <div v-else class="p-4 bg-neu-bg-dark rounded-neu-sm border border-neu-shadow-dark flex flex-col md:flex-row items-center gap-6">
        <!-- Método 1: Código QR -->
        <div class="flex flex-col items-center">
          <div v-if="botEstado.qr" class="flex flex-col items-center bg-white p-3 rounded-neu-sm shadow-neu-sm">
            <img :src="botEstado.qr" alt="Código QR WhatsApp" class="w-44 h-44 object-contain" />
            <span class="text-xs text-black font-semibold mt-1">● QR en Tiempo Real</span>
          </div>
          <div v-else class="flex flex-col items-center justify-center w-44 h-44 bg-neu-bg rounded-neu-sm border border-neu-shadow-dark text-xs text-neu-text-light text-center p-3">
            <span class="text-2xl mb-1">⏳</span>
            <span class="font-semibold">Generando QR...</span>
          </div>
          <button @click="forzarNuevoQR" class="mt-2 text-xs text-neu-green font-bold underline cursor-pointer">
            🔄 Refrescar Código QR
          </button>
        </div>

        <!-- Método 2: Código de 8 Dígitos (Pairing Code Directo) -->
        <div class="flex-1 text-xs text-neu-text flex flex-col gap-3 border-t md:border-t-0 md:border-l border-neu-shadow-dark pt-4 md:pt-0 md:pl-6">
          <div>
            <p class="font-bold text-neu-green text-sm">📲 Opción 1: Escanear Código QR</p>
            <p class="text-neu-text-light mt-0.5">
              En tu celular: <strong>WhatsApp > Ajustes > Dispositivos vinculados > Vincular dispositivo</strong> y apunta al QR.
            </p>
          </div>

          <div class="mt-2 p-3 bg-neu-bg rounded-neu-sm border border-neu-shadow-dark">
            <p class="font-bold text-neu-green text-sm">🔢 Opción 2: Vincular con Número de Teléfono</p>
            <p class="text-neu-text-light mt-0.5 mb-2">
              Si el QR tarda, ingresa tu número y genera tu código de 8 dígitos para WhatsApp:
            </p>
            <div class="flex gap-2 items-center">
              <input
                v-model="telefonoPairing"
                type="text"
                placeholder="Ej. 04141234567 o 584141234567"
                class="input-neu text-xs flex-1 py-1.5 px-3"
              />
              <button
                @click="solicitarPairingCode"
                :disabled="pidiendoCodigo"
                class="px-3 py-1.5 rounded-neu-sm bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs shadow-neu-sm cursor-pointer"
              >
                {{ pidiendoCodigo ? 'Generando...' : 'Obtener Código' }}
              </button>
            </div>
            <div v-if="pairingCodeResultado" class="mt-3 p-2.5 bg-emerald-950/40 border border-emerald-500/50 rounded-neu-sm text-center">
              <span class="text-xs text-emerald-300">Tu código de vinculación para WhatsApp es:</span>
              <p class="text-xl font-extrabold tracking-widest text-white mt-1 select-all">
                {{ pairingCodeResultado }}
              </p>
              <p class="text-xxs text-neu-text-light mt-1">
                Toca la notificación en tu WhatsApp o en <em>Vincular con número de teléfono</em> e introduce este código.
              </p>
            </div>
          </div>
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
            Indica la fecha límite de pago y los datos bancarios. Al hacer clic, el servidor enviará a todos los números vinculados en la base de datos de manera automática.
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

        <!-- Advertencia si la línea de WhatsApp no está vinculada -->
        <div
          v-if="!botEstado.connected"
          class="p-3 bg-amber-500/10 border border-amber-500/40 rounded-neu-sm text-xs text-amber-300 flex items-center gap-2.5"
        >
          <span class="text-xl">⚠️</span>
          <div>
            <p class="font-bold">Línea de WhatsApp pendiente de vinculación</p>
            <p class="text-neu-text-light mt-0.5">
              No se pueden enviar avisos automáticos porque la línea no está conectada. Escanea el código QR o ingresa tu número arriba para vincular tu WhatsApp primero.
            </p>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row justify-end gap-3 mt-2">
          <NeuButton
            type="button"
            variant="secondary"
            @click="guardarPredeterminados"
            :loading="guardandoPredeterminados"
          >
            💾 Guardar como Datos Predeterminados
          </NeuButton>
          <NeuButton
            variant="primary"
            type="submit"
            :loading="enviando"
            :disabled="!botEstado.connected"
            :class="!botEstado.connected ? 'opacity-50 cursor-not-allowed' : ''"
          >
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

    <!-- Exportación a Excel y Cartelera Oficial en PDF -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
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

      <!-- Cartelera Oficial de Morosidad en PDF -->
      <NeuCard class="border border-neu-green/30">
        <div class="flex items-center gap-3 mb-3">
          <span class="text-3xl">📄</span>
          <div>
            <h3 class="text-lg font-bold text-neu-green">Cartelera Oficial de Morosidad (PDF)</h3>
            <p class="text-xs text-neu-text-light">
              Reporte público para ascensores y cartelera (solo apartamentos y deudas, sin nombres privados)
            </p>
          </div>
        </div>

        <div class="flex items-center justify-between gap-3 mt-4 pt-3 border-t border-neu-shadow-dark">
          <span class="text-xs text-neu-text-light">
            Formato oficial listo para imprimir o guardar en PDF
          </span>
          <NeuButton variant="primary" @click="abrirCarteleraPDF">
            📄 Descargar Cartelera PDF
          </NeuButton>
        </div>
      </NeuCard>
    </div>

    <!-- Modal de Cartelera de Morosidad PDF -->
    <CarteleraPdfModal
      v-model="mostrarModalCarteleraPDF"
      :matriz="aptosStore.matrizDeudas"
      :tasa="tasaStore.tasaActual"
    />
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { AdminLayout } from '@/components/layout'
import { NeuCard, NeuButton, NeuInput } from '@/components/neumorph'
import { CarteleraPdfModal } from '@/components/shared'
import { reportesService, configuracionService, api } from '@/services'
import { useTasaStore, useApartamentosStore } from '@/stores'
import { formatTasa, periodoActual } from '@/utils'

const toast = useToast()
const tasaStore = useTasaStore()
const aptosStore = useApartamentosStore()

const mostrarModalCarteleraPDF = ref(false)
const periodoExcel = ref(periodoActual())
const exportando = ref(false)
const enviando = ref(false)
const guardandoPredeterminados = ref(false)
const resultadoEnvio = ref(null)
const botEstado = ref({ connected: false, session: null, qr: null })
let pollingTimer = null

const telefonoPairing = ref('')
const pidiendoCodigo = ref(false)
const pairingCodeResultado = ref('')

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
    cargarDatosBancarios(),
  ])

  // Sondeo continuo de estado del QR cada 2.5 segundos
  pollingTimer = setInterval(async () => {
    if (!botEstado.value.connected) {
      await cargarEstadoBot()
    }
  }, 2500)
})

async function cargarDatosBancarios() {
  try {
    const { data } = await configuracionService.getDatosBancarios()
    if (data) {
      if (data.banco) formAvisos.value.banco = data.banco
      if (data.pago_movil) formAvisos.value.pago_movil = data.pago_movil
      if (data.cuenta_transferencia) formAvisos.value.transferencia = data.cuenta_transferencia
      if (data.zelle) formAvisos.value.zelle = data.zelle
      if (data.nota_predeterminada) formAvisos.value.nota_adicional = data.nota_predeterminada
    }
  } catch (e) {
    console.error('Error al cargar datos bancarios predeterminados:', e)
  }
}

async function guardarPredeterminados(mostrarToast = true) {
  guardandoPredeterminados.value = true
  try {
    await configuracionService.guardarDatosBancarios({
      banco: formAvisos.value.banco,
      pago_movil: formAvisos.value.pago_movil,
      cuenta_transferencia: formAvisos.value.transferencia,
      zelle: formAvisos.value.zelle,
      nota_predeterminada: formAvisos.value.nota_adicional,
    })
    if (mostrarToast) {
      toast.success('¡Datos bancarios guardados como predeterminados y sincronizados con los propietarios!')
    }
  } catch (e) {
    if (mostrarToast) {
      toast.error('Error al guardar datos bancarios predeterminados')
    }
  } finally {
    guardandoPredeterminados.value = false
  }
}

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

async function forzarNuevoQR() {
  try {
    toast.info('Generando nuevo código QR...')
    botEstado.value.qr = null
    await api.post('/whatsapp-bot/refresh-qr')
    await new Promise(r => setTimeout(r, 1000))
    await cargarEstadoBot()
  } catch (e) {
    toast.error('Error al solicitar nuevo QR')
  }
}

async function solicitarPairingCode() {
  if (!telefonoPairing.value) {
    toast.error('Ingresa tu número de teléfono')
    return
  }
  pidiendoCodigo.value = true
  pairingCodeResultado.value = ''
  try {
    const { data } = await api.post('/whatsapp-bot/request-pairing-code', { phone: telefonoPairing.value })
    if (data.code) {
      pairingCodeResultado.value = data.code
      toast.success('¡Código de vinculación generado!')
    }
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Error al generar código de vinculación')
  } finally {
    pidiendoCodigo.value = false
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
  if (!botEstado.value.connected) {
    toast.error('⚠️ No se pueden enviar los avisos: La línea oficial de WhatsApp no está vinculada. Por favor escanea el código QR o vincula tu número arriba primero.')
    return
  }

  enviando.value = true
  resultadoEnvio.value = null
  try {
    guardarPredeterminados(false)
    const { data } = await reportesService.enviarMasivoAutomatico(formAvisos.value)
    resultadoEnvio.value = data
    toast.success(data.mensaje)
  } catch (error) {
    console.error('Error al enviar avisos:', error)
    const detalle = error.response?.data?.detail || 'Error al enviar los avisos masivos: Verifique que la línea de WhatsApp esté vinculada y los números sean válidos'
    toast.error(detalle)
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

async function abrirCarteleraPDF() {
  if (!aptosStore.matrizDeudas || aptosStore.matrizDeudas.length === 0) {
    try {
      await aptosStore.cargarMatrizDeudas()
    } catch (e) {
      console.error('Error cargando matriz deudas:', e)
    }
  }
  mostrarModalCarteleraPDF.value = true
}
</script>
