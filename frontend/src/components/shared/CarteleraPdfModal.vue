<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto"
        @click.self="$emit('update:modelValue', false)"
      >
        <div class="card-neu w-full max-w-4xl max-h-[92vh] flex flex-col relative my-auto shadow-2xl">
          <!-- Barra Superior de Acciones -->
          <div class="flex items-center justify-between pb-3 border-b border-neu-shadow-dark mb-3">
            <div class="flex items-center gap-2">
              <span class="text-2xl">📄</span>
              <div>
                <h3 class="text-base font-bold text-neu-green">Cartelera de Morosidad (Formato Oficial PDF)</h3>
                <p class="text-xs text-neu-text-light">
                  Formato público para ascensores y cartelera (solo números de apartamento, sin datos personales)
                </p>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <button
                @click="imprimirPDF"
                class="px-4 py-2 rounded-neu-sm bg-neu-green hover:bg-neu-green-dark text-white font-bold text-xs shadow-neu flex items-center gap-1.5 cursor-pointer transition-all"
              >
                <span>🖨️</span>
                <span>Descargar como PDF / Imprimir</span>
              </button>

              <button
                @click="$emit('update:modelValue', false)"
                class="w-8 h-8 rounded-full flex items-center justify-center text-neu-text-light hover:text-neu-danger hover:bg-neu-bg-dark transition-colors cursor-pointer"
                title="Cerrar"
              >
                ✕
              </button>
            </div>
          </div>

          <!-- Contenedor Visual de la Hoja (Estilo Papel para Previsualización y Renderizado) -->
          <div class="overflow-y-auto flex-1 p-2 bg-neutral-200/50 rounded-neu-sm border border-neu-shadow-dark">
            <div id="cartelera-imprimible" class="bg-white text-neutral-900 p-6 sm:p-8 shadow-md rounded max-w-3xl mx-auto font-sans text-xs">
              <!-- Encabezado y Cuadro Estadístico -->
              <div class="header-container flex flex-col sm:flex-row justify-between items-start gap-4 pb-3 border-b-2 border-neutral-900 mb-3">
                <div class="header-info flex-1">
                  <h1 class="text-base font-extrabold uppercase tracking-wide text-neutral-900 m-0">
                    JUNTA DE CONDOMINIO EDIFICIO ALCATRAZ
                  </h1>
                  <p class="text-xs text-neutral-600 m-0 mt-0.5 font-medium">
                    RIF: J-30806007-0
                  </p>
                  <p class="text-xs text-neutral-600 m-0 font-medium">
                    Fecha de Emisión: <strong class="text-neutral-900">{{ fechaActual }}</strong>
                  </p>
                  <p class="text-xs text-neutral-600 m-0 font-medium">
                    Tasa Oficial BCV: <strong class="text-neutral-900">{{ formatTasa(tasa) }}</strong>
                  </p>
                </div>

                <!-- Cuadro Resumen Porcentual (Exacto al formato de cartelera) -->
                <div class="stats-container min-w-[240px]">
                  <table class="stats-box w-full border border-neutral-800 text-[10px] border-collapse">
                    <tbody>
                      <tr class="bg-neutral-100 font-bold border-b border-neutral-400">
                        <td class="p-1 border-r border-neutral-400">TOTAL INMUEBLES ({{ totalAptos }})</td>
                        <td class="p-1 text-right">100,00%</td>
                      </tr>
                      <tr class="border-b border-neutral-300">
                        <td class="p-1 border-r border-neutral-300 stats-al-dia font-semibold text-emerald-800">
                          {{ aptosAlDia.length }} APTOS AL DÍA
                        </td>
                        <td class="p-1 text-right font-semibold stats-al-dia text-emerald-800">{{ pctAlDia }}%</td>
                      </tr>
                      <tr class="border-b border-neutral-300">
                        <td class="p-1 border-r border-neutral-300 stats-1a3 text-neutral-800">
                          {{ aptos1a3.length }} APTOS DE 1 A 3 RECIBOS
                        </td>
                        <td class="p-1 text-right font-medium stats-1a3 text-neutral-800">{{ pct1a3 }}%</td>
                      </tr>
                      <tr class="border-b border-neutral-300">
                        <td class="p-1 border-r border-neutral-300 stats-4a11 text-amber-800">
                          {{ aptos4a11.length }} APTOS DE 4 A 11 RECIBOS
                        </td>
                        <td class="p-1 text-right font-medium stats-4a11 text-amber-800">{{ pct4a11 }}%</td>
                      </tr>
                      <tr>
                        <td class="p-1 border-r border-neutral-300 stats-critico text-rose-800 font-bold">
                          {{ aptosCriticos.length }} APTOS EN CRÍTICO (12+)
                        </td>
                        <td class="p-1 text-right font-bold stats-critico text-rose-800">{{ pctCriticos }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Título Formal del Documento -->
              <div class="doc-title text-center text-xs font-bold uppercase tracking-wider bg-neutral-100 py-1 px-2 border border-neutral-300 mb-3 text-neutral-900">
                REPORTE DE CUENTAS POR COBRAR — CARTELERA DE MOROSIDAD
              </div>

              <!-- Tabla de Inmuebles (Sin datos personales para cartelera pública) -->
              <table class="data-table w-full border-collapse text-[10.5px] mb-4">
                <thead>
                  <tr class="bg-neutral-800 text-white text-[10px] uppercase font-semibold">
                    <th class="border border-neutral-800 p-1.5 text-center w-24">Apartamento</th>
                    <th class="border border-neutral-800 p-1.5 text-center w-24">Nº Recibos</th>
                    <th class="border border-neutral-800 p-1.5 text-center">Meses Adeudados</th>
                    <th class="border border-neutral-800 p-1.5 text-right w-28">Deuda ($ USD)</th>
                    <th class="border border-neutral-800 p-1.5 text-right w-32">Deuda (Bs. VES)</th>
                    <th class="border border-neutral-800 p-1.5 text-center w-24">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in matrizOrdenada"
                    :key="item.apartamento_id"
                    class="border-b border-neutral-200"
                    :class="(item.meses_pendientes > 0 || item.estado === 'moroso') ? 'fila-moroso bg-rose-50/40' : 'fila-solvente bg-white'"
                  >
                    <td class="border border-neutral-300 p-1.5 font-bold text-center text-neutral-900">
                      {{ item.numero_apto }}
                    </td>
                    <td class="border border-neutral-300 p-1.5 text-center font-medium">
                      {{ item.meses_pendientes > 0 ? item.meses_pendientes : '0' }}
                    </td>
                    <td class="border border-neutral-300 p-1.5 text-center text-neutral-700">
                      <span v-if="item.meses_pendientes > 0" class="texto-meses-moroso">
                        {{ Array.isArray(item.meses_adeudados) ? item.meses_adeudados.join(', ') : `${item.meses_pendientes} mes(es)` }}
                      </span>
                      <span v-else class="texto-al-dia font-semibold text-emerald-700">Al día</span>
                    </td>
                    <td
                      class="border border-neutral-300 p-1.5 text-right font-bold"
                      :class="(item.meses_pendientes > 0 || item.deuda_total_usd > 0) ? 'monto-moroso text-rose-700' : 'monto-solvente text-emerald-700'"
                    >
                      {{ formatUSD(item.deuda_total_usd) }}
                    </td>
                    <td class="border border-neutral-300 p-1.5 text-right font-medium text-neutral-800">
                      {{ formatVES(item.deuda_total_ves) }}
                    </td>
                    <td class="border border-neutral-300 p-1.5 text-center">
                      <span
                        v-if="item.meses_pendientes === 0 || item.estado === 'solvente'"
                        class="badge-solvente"
                      >
                        ● SOLVENTE
                      </span>
                      <span
                        v-else
                        class="badge-moroso"
                      >
                        ▲ MOROSO
                      </span>
                    </td>
                  </tr>

                  <!-- Fila de Totales -->
                  <tr class="footer-totals bg-neutral-100 font-extrabold border-t-2 border-neutral-800 text-neutral-900">
                    <td class="border border-neutral-300 p-2 text-center" colspan="1">TOTALES</td>
                    <td class="border border-neutral-300 p-2 text-center">{{ totalRecibosImpagos }}</td>
                    <td class="border border-neutral-300 p-2 text-center text-neutral-500">—</td>
                    <td class="border border-neutral-300 p-2 text-right monto-total-moroso text-rose-700 font-black">
                      {{ formatUSD(totalDeudaUSD) }}
                    </td>
                    <td class="border border-neutral-300 p-2 text-right font-black">
                      {{ formatVES(totalDeudaVES) }}
                    </td>
                    <td class="border border-neutral-300 p-2 text-center text-neutral-500">—</td>
                  </tr>
                </tbody>
              </table>

              <!-- Nota Legal y Espacio para Sello / Firma -->
              <div class="disclaimer text-[8.5px] text-neutral-600 leading-tight border-t border-dashed border-neutral-400 pt-2 text-justify">
                <strong>Nota Informativa:</strong> El presente reporte ha sido emitido de conformidad con la Ley de Propiedad Horizontal para fines exclusivos de información general en la cartelera del edificio. Si ya realizó su pago, por favor repórtelo en el portal o comuníquese con la Junta de Condominio con su comprobante para actualizar la conciliación.
              </div>

              <div class="signatures flex justify-between items-center mt-8 pt-2 text-[9.5px] text-neutral-800">
                <div class="signature-line w-48 border-t border-neutral-800 text-center pt-1 font-semibold">
                  Junta de Condominio
                </div>
                <div class="signature-line w-48 border-t border-neutral-800 text-center pt-1 font-semibold">
                  Administración / Cobranzas
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { formatUSD, formatVES, formatTasa } from '@/utils'

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  matriz: { type: Array, default: () => [] },
  tasa: { type: [Number, String], default: 804.8109 },
})

defineEmits(['update:modelValue'])

const fechaActual = computed(() => {
  const hoy = new Date()
  return hoy.toLocaleDateString('es-VE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
})

const matrizOrdenada = computed(() => {
  return [...props.matriz].sort((a, b) => {
    return String(a.numero_apto || '').localeCompare(String(b.numero_apto || ''), undefined, { numeric: true })
  })
})

const totalAptos = computed(() => props.matriz.length)

const aptosAlDia = computed(() => {
  return props.matriz.filter((a) => (a.meses_pendientes || 0) === 0)
})

const aptos1a3 = computed(() => {
  return props.matriz.filter((a) => (a.meses_pendientes || 0) >= 1 && (a.meses_pendientes || 0) <= 3)
})

const aptos4a11 = computed(() => {
  return props.matriz.filter((a) => (a.meses_pendientes || 0) >= 4 && (a.meses_pendientes || 0) <= 11)
})

const aptosCriticos = computed(() => {
  return props.matriz.filter((a) => (a.meses_pendientes || 0) >= 12)
})

const pctAlDia = computed(() => {
  if (!totalAptos.value) return '0,00'
  return ((aptosAlDia.value.length / totalAptos.value) * 100).toFixed(2).replace('.', ',')
})

const pct1a3 = computed(() => {
  if (!totalAptos.value) return '0,00'
  return ((aptos1a3.value.length / totalAptos.value) * 100).toFixed(2).replace('.', ',')
})

const pct4a11 = computed(() => {
  if (!totalAptos.value) return '0,00'
  return ((aptos4a11.value.length / totalAptos.value) * 100).toFixed(2).replace('.', ',')
})

const pctCriticos = computed(() => {
  if (!totalAptos.value) return '0,00'
  return ((aptosCriticos.value.length / totalAptos.value) * 100).toFixed(2).replace('.', ',')
})

const totalRecibosImpagos = computed(() => {
  return props.matriz.reduce((sum, a) => sum + (parseInt(a.meses_pendientes) || 0), 0)
})

const totalDeudaUSD = computed(() => {
  return props.matriz.reduce((sum, a) => sum + (parseFloat(a.deuda_total_usd) || 0), 0)
})

const totalDeudaVES = computed(() => {
  return props.matriz.reduce((sum, a) => sum + (parseFloat(a.deuda_total_ves) || 0), 0)
})

function imprimirPDF() {
  const contenido = document.getElementById('cartelera-imprimible')
  if (!contenido) return

  const ventana = window.open('', '_blank', 'width=950,height=800')
  ventana.document.write(`
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <title>Cartelera de Morosidad - Edificio Alcatraz</title>
      <style>
        @page {
          size: letter portrait;
          margin: 12mm 14mm 12mm 14mm;
        }
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          margin: 0;
          padding: 0;
          color: #111827;
          background: #ffffff;
          font-size: 11px;
        }
        * {
          box-sizing: border-box;
        }
        .header-container {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 10px;
          border-bottom: 2px solid #111827;
          padding-bottom: 8px;
        }
        .header-info h1 {
          font-size: 15px;
          font-weight: 800;
          margin: 0 0 3px 0;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #111827;
        }
        .header-info p {
          margin: 1.5px 0;
          font-size: 10px;
          color: #4b5563;
        }
        .stats-box {
          border: 1px solid #111827;
          border-collapse: collapse;
          font-size: 9.5px;
          min-width: 230px;
        }
        .stats-box td {
          border: 1px solid #9ca3af;
          padding: 2px 5px;
        }
        .doc-title {
          text-align: center;
          font-size: 12px;
          font-weight: 800;
          margin: 8px 0 10px 0;
          letter-spacing: 0.8px;
          text-transform: uppercase;
          background-color: #f3f4f6;
          padding: 3.5px;
          border: 1px solid #d1d5db;
        }
        table.data-table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 12px;
        }
        table.data-table th {
          background-color: #1f2937 !important;
          color: #ffffff !important;
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
          font-size: 9.5px;
          font-weight: 700;
          padding: 4px 5px;
          text-align: center;
          border: 1px solid #1f2937;
        }
        table.data-table td {
          border: 1px solid #d1d5db;
          padding: 3.5px 5px;
          font-size: 10px;
        }
        table.data-table tr:nth-child(even) {
          background-color: #f9fafb !important;
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }
        .fila-moroso {
          background-color: #fff1f2 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .fila-solvente {
          background-color: #ffffff !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .badge-moroso {
          display: inline-block !important;
          padding: 2.5px 8px !important;
          border-radius: 4px !important;
          background-color: #fee2e2 !important;
          color: #dc2626 !important;
          border: 1px solid #f87171 !important;
          font-weight: 800 !important;
          font-size: 10px !important;
          letter-spacing: 0.5px !important;
          white-space: nowrap !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .badge-solvente {
          display: inline-block !important;
          padding: 2.5px 8px !important;
          border-radius: 4px !important;
          background-color: #dcfce7 !important;
          color: #15803d !important;
          border: 1px solid #86efac !important;
          font-weight: 800 !important;
          font-size: 10px !important;
          letter-spacing: 0.5px !important;
          white-space: nowrap !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .monto-moroso {
          color: #dc2626 !important;
          font-weight: 800 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .monto-solvente {
          color: #15803d !important;
          font-weight: 700 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .texto-al-dia {
          color: #15803d !important;
          font-weight: 600 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .texto-meses-moroso {
          color: #374151 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .monto-total-moroso {
          color: #dc2626 !important;
          font-weight: 900 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .stats-al-dia {
          color: #15803d !important;
          font-weight: 700 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .stats-1a3 {
          color: #374151 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .stats-4a11 {
          color: #b45309 !important;
          font-weight: 600 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .stats-critico {
          color: #dc2626 !important;
          font-weight: 800 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .footer-totals {
          background-color: #f3f4f6 !important;
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
          font-weight: bold;
          border-top: 2px solid #111827;
        }
        .disclaimer {
          font-size: 8.5px;
          color: #4b5563;
          margin-top: 10px;
          text-align: justify;
          line-height: 1.25;
          border-top: 1px dashed #9ca3af;
          padding-top: 5px;
        }
        .signatures {
          display: flex;
          justify-content: space-between;
          margin-top: 30px;
          font-size: 9px;
        }
        .signature-line {
          width: 180px;
          border-top: 1px solid #111827;
          text-align: center;
          padding-top: 4px;
        }
      </style>
    </head>
    <body>
      ${contenido.innerHTML}
    </body>
    </html>
  `)
  ventana.document.close()
  ventana.focus()
  setTimeout(() => {
    ventana.print()
  }, 300)
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.badge-moroso {
  display: inline-block;
  padding: 2.5px 8px;
  border-radius: 4px;
  background-color: #fee2e2;
  color: #dc2626;
  border: 1px solid #f87171;
  font-weight: 800;
  font-size: 10px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.badge-solvente {
  display: inline-block;
  padding: 2.5px 8px;
  border-radius: 4px;
  background-color: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
  font-weight: 800;
  font-size: 10px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.monto-moroso {
  color: #dc2626;
  font-weight: 800;
}

.monto-solvente {
  color: #15803d;
  font-weight: 700;
}

.texto-al-dia {
  color: #15803d;
  font-weight: 600;
}

.texto-meses-moroso {
  color: #374151;
}

.monto-total-moroso {
  color: #dc2626;
  font-weight: 900;
}

.stats-al-dia {
  color: #15803d;
  font-weight: 700;
}

.stats-1a3 {
  color: #374151;
}

.stats-4a11 {
  color: #b45309;
  font-weight: 600;
}

.stats-critico {
  color: #dc2626;
  font-weight: 800;
}
</style>
