<template>
  <AdminLayout
    titulo="Matriz Consolidada de Deudas y Cobranzas"
    subtitulo="Listado general de solvencia, meses adeudados y montos al cambio oficial BCV"
  >
    <!-- Filtros rápidos por estado de solvencia -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
      <div class="flex items-center gap-2">
        <button
          @click="filtroEstado = ''"
          :class="filtroEstado === '' ? 'shadow-neu-inset bg-neu-bg-dark font-bold text-neu-green' : 'btn-neu'"
          class="text-xs px-4 py-2 rounded-neu-sm transition-all"
        >
          Todos ({{ matriz.length }})
        </button>
        <button
          @click="filtroEstado = 'moroso'"
          :class="filtroEstado === 'moroso' ? 'shadow-neu-inset bg-red-100 font-bold text-neu-danger' : 'btn-neu text-neu-danger'"
          class="text-xs px-4 py-2 rounded-neu-sm transition-all"
        >
          Morosos ({{ conteoMorosos }})
        </button>
        <button
          @click="filtroEstado = 'solvente'"
          :class="filtroEstado === 'solvente' ? 'shadow-neu-inset bg-green-100 font-bold text-neu-success' : 'btn-neu text-neu-success'"
          class="text-xs px-4 py-2 rounded-neu-sm transition-all"
        >
          Solventes ({{ conteoSolventes }})
        </button>
      </div>

      <!-- Buscador y botón de Cartelera PDF -->
      <div class="w-full sm:w-auto flex flex-col sm:flex-row items-center gap-3">
        <div class="w-full sm:w-64">
          <input
            v-model="busqueda"
            type="text"
            placeholder="Buscar apartamento o propietario..."
            class="input-neu text-sm py-2"
          />
        </div>

        <button
          @click="mostrarModalPDF = true"
          class="w-full sm:w-auto px-4 py-2 rounded-neu-sm bg-neu-green hover:bg-neu-green-dark text-white font-bold text-xs shadow-neu flex items-center justify-center gap-1.5 cursor-pointer transition-all whitespace-nowrap"
        >
          <span>📄</span>
          <span>Cartelera PDF</span>
        </button>
      </div>
    </div>

    <!-- Tabla General de Matriz -->
    <NeuCard>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-neu-shadow-dark text-neu-text-light">
              <th class="pb-3 font-semibold">Apto</th>
              <th class="pb-3 font-semibold">Torre / Piso</th>
              <th class="pb-3 font-semibold">Propietario Titular</th>
              <th class="pb-3 font-semibold">Contacto Directo</th>
              <th class="pb-3 font-semibold">Meses Impagos</th>
              <th class="pb-3 font-semibold">Deuda ($ USD)</th>
              <th class="pb-3 font-semibold">Deuda (Bs. VES)</th>
              <th class="pb-3 font-semibold">Saldo a Favor</th>
              <th class="pb-3 font-semibold text-center">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in matrizFiltrada"
              :key="item.apartamento_id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
            >
              <td class="py-3 font-bold text-neu-green">{{ item.numero_apto }}</td>
              <td class="py-3 text-neu-text-light">{{ item.torre }} - P{{ item.piso || 'B' }}</td>
              <td class="py-3 font-semibold text-neu-text">{{ item.propietario }}</td>
              <td class="py-3 text-neu-text">
                <a
                  v-if="item.telefono && item.telefono !== '-'"
                  :href="`https://wa.me/${item.telefono.replace(/[^0-9]/g, '')}`"
                  target="_blank"
                  class="text-neu-green hover:underline flex items-center gap-1 text-xs"
                >
                  💬 {{ item.telefono }}
                </a>
                <span v-else class="text-xs text-neu-text-light">-</span>
              </td>
              <td class="py-3 text-xs">
                <span v-if="item.meses_adeudados.length > 0" class="text-neu-danger font-semibold">
                  {{ item.meses_adeudados.join(', ') }}
                </span>
                <span v-else class="text-neu-success font-medium">Al día</span>
              </td>
              <td class="py-3 font-bold" :class="item.deuda_total_usd > 0 ? 'text-neu-danger' : 'text-neu-success'">
                {{ formatUSD(item.deuda_total_usd) }}
              </td>
              <td class="py-3 text-neu-text-light font-medium">
                {{ formatVES(item.deuda_total_ves) }}
              </td>
              <td class="py-3 font-semibold text-neu-green">
                {{ formatUSD(item.saldo_favor_usd) }}
              </td>
              <td class="py-3 text-center">
                <EstadoPagoBadge :estado="item.estado" />
              </td>
            </tr>
            <tr v-if="matrizFiltrada.length === 0">
              <td colspan="9" class="py-8 text-center text-neu-text-light">
                No hay registros que coincidan con la búsqueda o filtro.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>

    <!-- Modal de Cartelera de Morosidad para Descarga / Impresión en PDF -->
    <CarteleraPdfModal
      v-model="mostrarModalPDF"
      :matriz="matriz"
      :tasa="tasaStore.tasaActual"
    />
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { AdminLayout } from '@/components/layout'
import { NeuCard } from '@/components/neumorph'
import { EstadoPagoBadge, CarteleraPdfModal } from '@/components/shared'
import { useApartamentosStore, useTasaStore } from '@/stores'
import { formatUSD, formatVES } from '@/utils'

const aptosStore = useApartamentosStore()
const tasaStore = useTasaStore()

const mostrarModalPDF = ref(false)
const filtroEstado = ref('')
const busqueda = ref('')

const matriz = computed(() => aptosStore.matrizDeudas || [])

const conteoMorosos = computed(() => matriz.value.filter((a) => a.estado === 'moroso').length)
const conteoSolventes = computed(() => matriz.value.filter((a) => a.estado === 'solvente').length)

const matrizFiltrada = computed(() => {
  let lista = matriz.value
  if (filtroEstado.value) {
    lista = lista.filter((a) => a.estado === filtroEstado.value)
  }
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase()
    lista = lista.filter(
      (a) =>
        a.numero_apto.toLowerCase().includes(q) ||
        a.propietario.toLowerCase().includes(q) ||
        a.torre.toLowerCase().includes(q)
    )
  }
  return lista
})

onMounted(async () => {
  await Promise.all([
    aptosStore.cargarMatrizDeudas(),
    tasaStore.cargarTasa(),
  ])
})
</script>
