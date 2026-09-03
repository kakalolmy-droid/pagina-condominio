<template>
  <AdminLayout
    titulo="Avisos y Cobranzas Masivas por WhatsApp"
    subtitulo="Envío masivo automático a todos los números registrados con fecha límite, datos bancarios y link de pago"
  >
    <!-- Tarjeta 1: Despacho Directo por WhatsApp (Sin dependencias externas) -->
    <NeuCard class="mb-8 border-2 border-neu-green/30">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div class="flex items-center gap-3">
          <span class="text-3xl">📱</span>
          <div>
            <h3 class="text-lg font-bold text-neu-green">Centro de Notificaciones y Cobranzas WhatsApp</h3>
            <p class="text-xs text-neu-text-light">
              Despacho inteligente de avisos de cobro con cálculo de meses pendientes y link de pago
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <span class="px-3 py-1.5 rounded-full text-xs font-bold badge-success">
            ● SISTEMA DE ENVÍO ACTIVO
          </span>
        </div>
      </div>

      <!-- Métodos de envío -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-4 bg-neu-bg-dark rounded-neu-sm border border-neu-shadow-dark flex flex-col justify-between">
          <div>
            <p class="font-bold text-neu-green text-sm flex items-center gap-1.5">
              <span>🚀</span> Envío Masivo 1-Clic
            </p>
            <p class="text-xs text-neu-text-light mt-1">
              Despacha las notificaciones en lote a todos los copropietarios activos registrados con su cuota y meses adeudados calculados.
            </p>
          </div>
        </div>

        <div class="p-4 bg-neu-bg-dark rounded-neu-sm border border-neu-shadow-dark flex flex-col justify-between">
          <div>
            <p class="font-bold text-neu-green text-sm flex items-center gap-1.5">
              <span>💬</span> Lista Individualizada con Enlaces WhatsApp
            </p>
            <p class="text-xs text-neu-text-light mt-1">
              Genera los mensajes individualizados con un solo clic para abrirlos directamente en WhatsApp Web o en tu celular.
            </p>
          </div>
        </div>
      </div>
    </NeuCard>

    <!-- Tarjeta 2: Formulario de Configuración de Aviso Masivo -->
    <NeuCard class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <span class="text-3xl">⚙️</span>
        <div>
          <h3 class="text-lg font-bold text-neu-green">Configuración del Aviso de Cobro</h3>
          <p class="text-xs text-neu-text-light">
            Indica la fecha límite de pago y los datos bancarios para adjuntar en los mensajes
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

        <div class="flex flex-wrap justify-end gap-3 mt-2">
          <NeuButton variant="primary" type="submit" :loading="enviando">
            🚀 Enviar Masivo Automático
          </NeuButton>
        </div>
      </form>
    </NeuCard>

    <!-- Tarjeta 3: Lista de Destinatarios Activos y Enlaces Directos WhatsApp -->
    <NeuCard class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-bold text-neu-green">📋 Copropietarios Activos a Notificar ({{ destinatariosFiltrados.length }})</h3>
          <p class="text-xs text-neu-text-light">
            Puedes enviar el mensaje directo a cada uno con un clic en su botón de WhatsApp
          </p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-neu-shadow-dark text-neu-text-light">
              <th class="pb-3 font-semibold">Apartamento</th>
              <th class="pb-3 font-semibold">Propietario</th>
              <th class="pb-3 font-semibold">Teléfono</th>
              <th class="pb-3 font-semibold">Meses Pendientes</th>
              <th class="pb-3 font-semibold">Total USD</th>
              <th class="pb-3 font-semibold">Equivalente VES</th>
              <th class="pb-3 font-semibold text-center">Acción Directa</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in destinatariosFiltrados"
              :key="item.apto.id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
            >
              <td class="py-3 font-bold text-neu-green">Apto {{ item.apto.numero_apto }}</td>
              <td class="py-3 font-semibold text-neu-text">{{ item.propietario.nombre }} {{ item.propietario.apellido }}</td>
              <td class="py-3 text-neu-text-light">{{ item.propietario.telefono_whatsapp }}</td>
              <td class="py-3">
                <span class="font-bold px-2 py-0.5 rounded-full text-xs" :class="item.meses > 0 ? 'badge-danger' : 'badge-success'">
                  {{ item.meses }} mes(es)
                </span>
              </td>
              <td class="py-3 font-bold text-neu-green">${{ item.totalUsd.toFixed(2) }} USD</td>
              <td class="py-3 text-neu-text-light">
                Bs. {{ (item.totalUsd * tasaActualNum).toLocaleString('es-VE', { minimumFractionDigits: 2 }) }}
              </td>
              <td class="py-3 text-center">
                <a
                  :href="generarLinkWhatsApp(item)"
                  target="_blank"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-neu-sm text-xs font-bold bg-emerald-700 hover:bg-emerald-600 text-white shadow-neu-sm transition-all"
                >
                  <span>💬 Enviar WhatsApp</span>
                </a>
              </td>
            </tr>
            <tr v-if="destinatariosFiltrados.length === 0">
              <td colspan="7" class="py-6 text-center text-neu-text-light">
                No hay apartamentos activos para notificar.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>

    <!-- Confirmación de Despacho Exitoso -->
    <NeuCard v-if="resultadoEnvio" class="mb-8 border-2 border-neu-green bg-neu-green/5">
      <div class="flex items-center gap-3">
        <span class="text-3xl">✅</span>
        <div>
          <h3 class="text-lg font-bold text-neu-green">{{ resultadoEnvio.mensaje }}</h3>
          <p class="text-xs text-neu-text-light mt-1">
            Total procesados: <span class="font-bold text-neu-text">{{ resultadoEnvio.total_destinatarios }}</span> propietarios ({{ resultadoEnvio.destinatarios?.join(', ') }})
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
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { AdminLayout } from '@/components/layout'
import { NeuCard, NeuButton, NeuInput } from '@/components/neumorph'
import { reportesService } from '@/services'
import { useTasaStore, useApartamentosStore, useUsuariosStore } from '@/stores'
import { formatTasa, periodoActual } from '@/utils'

const toast = useToast()
const tasaStore = useTasaStore()
const aptosStore = useApartamentosStore()
const usuariosStore = useUsuariosStore()

const periodoExcel = ref(periodoActual())
const exportando = ref(false)
const enviando = ref(false)
const resultadoEnvio = ref(null)

const formAvisos = ref({
  periodo: periodoActual(),
  fecha_limite: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  banco: 'Banco de Venezuela (0102)',
  pago_movil: '0414-1234567 | C.I. V-00000001',
  transferencia: '0102-0000-00-0000000000',
  zelle: 'pagos@edificioalcatraz.com',
  nota_adicional: '',
})

const tasaActualNum = computed(() => {
  if (!tasaStore.tasaActual) return 800.0
  return typeof tasaStore.tasaActual === 'number'
    ? tasaStore.tasaActual
    : parseFloat(tasaStore.tasaActual.tasa_usd_ves || 800.0)
})

const destinatariosFiltrados = computed(() => {
  const inactivosAptos = new Set(JSON.parse(localStorage.getItem('alcatraz_aptos_inactivos') || '[]'))
  const inactivosUsers = new Set(JSON.parse(localStorage.getItem('alcatraz_usuarios_inactivos') || '[]'))
  
  const res = []
  for (const apto of (aptosStore.lista || [])) {
    if (inactivosAptos.has(apto.id) || (apto.propietario_id && inactivosUsers.has(apto.propietario_id))) {
      continue
    }
    const prop = (usuariosStore.lista || []).find(u => u.id === apto.propietario_id) || apto.propietario
    if (!prop) continue

    const cuota = parseFloat(apto.alicuota) || 15.0
    const meses = parseInt(apto.meses_pendientes !== undefined ? apto.meses_pendientes : 1)
    const totalUsd = cuota * meses

    res.push({
      apto,
      propietario: prop,
      cuota,
      meses,
      totalUsd,
    })
  }
  return res
})

onMounted(async () => {
  await Promise.all([
    tasaStore.cargarTasa(),
    aptosStore.cargar(),
    usuariosStore.cargar(),
  ])
})

function generarLinkWhatsApp(item) {
  const telLimpio = item.propietario.telefono_whatsapp ? item.propietario.telefono_whatsapp.replace(/[^0-9]/g, '') : ''
  const telFormateado = (!telLimpio.startsWith('58') && telLimpio.length === 10) ? `58${telLimpio}` : telLimpio

  const totalVes = (item.totalUsd * tasaActualNum.value).toLocaleString('es-VE', { minimumFractionDigits: 2 })
  const portalUrl = 'https://pagina-condominio.vercel.app/mi-cuenta/pagar'

  const msg = 
`🏢 *Edificio Alcatraz — AVISO DE COBRO*

Estimado/a *${item.propietario.nombre} ${item.propietario.apellido}* (Apto *${item.apto.numero_apto}*),

Le informamos los datos de pago para el período *${formAvisos.value.periodo}*:
💵 *Cuota Mensual:* $${item.cuota.toFixed(2)} USD
📌 *Meses Pendientes:* ${item.meses} mes(es)
💰 *TOTAL A PAGAR:* $${item.totalUsd.toFixed(2)} USD
🇻🇪 *Equivalente en Bs:* Bs. ${totalVes} (Tasa BCV: Bs. ${tasaActualNum.value.toFixed(2)})
📅 *Fecha Límite de Pago:* ${formAvisos.value.fecha_limite}

📌 *DATOS OFICIALES DE RECAUDACIÓN:*
• Banco: ${formAvisos.value.banco}
• Pago Móvil: ${formAvisos.value.pago_movil}
• Transferencia: ${formAvisos.value.transferencia}
• Zelle: ${formAvisos.value.zelle}

🔗 *Reporte su pago y adjunte su comprobante aquí:*
${portalUrl}

${formAvisos.value.nota_adicional || '¡Gracias por su puntualidad y colaboración!'}`

  return `https://wa.me/${telFormateado}?text=${encodeURIComponent(msg)}`
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
