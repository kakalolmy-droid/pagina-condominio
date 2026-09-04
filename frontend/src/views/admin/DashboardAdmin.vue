<template>
  <AdminLayout
    titulo="Dashboard General"
    subtitulo="Resumen operativo, financiero y control de morosidad"
  >
    <!-- Widget de Tasa BCV y Métricas Rápidas -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Tarjeta 1: Recaudación Mes -->
      <NeuCard>
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-neu-text-light">Recaudado (Mes Actual)</span>
          <span class="text-2xl">💵</span>
        </div>
        <h3 class="text-2xl font-bold text-neu-green">{{ formatUSD(totalRecaudadoMes) }}</h3>
        <p class="text-xs text-neu-text-light mt-1">
          Equivalente: <span class="font-semibold text-neu-text">{{ formatVES(totalRecaudadoMesVES) }}</span>
        </p>
      </NeuCard>

      <!-- Tarjeta 2: Deuda Total Condominio -->
      <NeuCard>
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-neu-text-light">Deuda Total Pendiente</span>
          <span class="text-2xl">⚠️</span>
        </div>
        <h3 class="text-2xl font-bold text-neu-danger">{{ formatUSD(deudaTotalUSD) }}</h3>
        <p class="text-xs text-neu-text-light mt-1">
          Equivalente: <span class="font-semibold text-neu-text">{{ formatVES(deudaTotalVES) }}</span>
        </p>
      </NeuCard>

      <!-- Tarjeta 3: Inmuebles Solventes vs Morosos -->
      <NeuCard>
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-neu-text-light">Estado de Inmuebles</span>
          <span class="text-2xl">🏢</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="badge-success text-sm px-3 py-1">{{ totalSolventes }} Solventes</span>
          <span class="badge-danger text-sm px-3 py-1">{{ totalMorosos }} Morosos</span>
        </div>
        <p class="text-xs text-neu-text-light mt-2">
          Total unidades registradas: <span class="font-bold">{{ matriz.length }}</span>
        </p>
      </NeuCard>

      <!-- Tarjeta 4: Tasa BCV Oficial -->
      <NeuCard>
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-neu-text-light">Tasa BCV del Día</span>
          <span class="text-2xl">💱</span>
        </div>
        <h3 class="text-2xl font-bold text-neu-green">
          {{ tasaStore.tasaActual ? formatTasa(tasaStore.tasaActual) : 'Consultando...' }}
        </h3>
        <div class="flex items-center justify-between mt-2">
          <span class="text-xs text-neu-text-light">{{ formatFecha(tasaStore.fecha) }}</span>
          <button
            @click="sincronizarBCV"
            :disabled="sincronizando"
            class="text-xs font-semibold text-neu-green hover:underline cursor-pointer"
          >
            {{ sincronizando ? 'Actualizando...' : '🔄 Sincronizar' }}
          </button>
        </div>
      </NeuCard>
    </div>

    <!-- Acciones Rápidas del Administrador -->
    <div class="mb-8">
      <h2 class="text-lg font-bold text-neu-green mb-4">Acciones Rápidas</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <RouterLink to="/admin/recibos" class="card-neu-sm hover:shadow-neu transition-all flex items-center gap-3">
          <span class="text-2xl">📑</span>
          <div>
            <h4 class="font-bold text-sm text-neu-green">Emitir Recibos</h4>
            <p class="text-xs text-neu-text-light">Facturación mensual por alícuotas</p>
          </div>
        </RouterLink>

        <RouterLink to="/admin/conciliacion" class="card-neu-sm hover:shadow-neu transition-all flex items-center gap-3">
          <span class="text-2xl">✅</span>
          <div>
            <h4 class="font-bold text-sm text-neu-green">Conciliar Pagos</h4>
            <p class="text-xs text-neu-text-light">Validar comprobantes de pago</p>
          </div>
        </RouterLink>

        <RouterLink to="/admin/propietarios" class="card-neu-sm hover:shadow-neu transition-all flex items-center gap-3">
          <span class="text-2xl">👥</span>
          <div>
            <h4 class="font-bold text-sm text-neu-green">Padrón de Propietarios</h4>
            <p class="text-xs text-neu-text-light">Directorio y contactos</p>
          </div>
        </RouterLink>

        <RouterLink to="/admin/deudas" class="card-neu-sm hover:shadow-neu transition-all flex items-center gap-3">
          <span class="text-2xl">📊</span>
          <div>
            <h4 class="font-bold text-sm text-neu-green">Control de Morosidad</h4>
            <p class="text-xs text-neu-text-light">Matriz general y cobranzas</p>
          </div>
        </RouterLink>
      </div>
    </div>

    <!-- Tabla Resumen: Últimos Inmuebles con Deuda -->
    <NeuCard>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-neu-green">Resumen de Morosidad y Cobranza</h2>
        <div class="flex items-center gap-4">
          <button
            @click="mostrarModalPDF = true"
            class="text-xs font-bold text-neu-green hover:underline flex items-center gap-1 cursor-pointer"
          >
            <span>📄</span>
            <span>Cartelera PDF</span>
          </button>
          <RouterLink to="/admin/deudas" class="text-sm font-medium text-neu-green hover:underline">
            Ver matriz completa ➔
          </RouterLink>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-neu-shadow-dark text-neu-text-light">
              <th class="pb-3 font-semibold">Apartamento</th>
              <th class="pb-3 font-semibold">Propietario</th>
              <th class="pb-3 font-semibold">Deuda (USD)</th>
              <th class="pb-3 font-semibold">Deuda (VES)</th>
              <th class="pb-3 font-semibold">Saldo a Favor</th>
              <th class="pb-3 font-semibold text-center">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in matriz.slice(0, 5)"
              :key="item.apartamento_id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
            >
              <td class="py-3 font-bold text-neu-green">{{ item.numero_apto }}</td>
              <td class="py-3 text-neu-text">{{ item.propietario }}</td>
              <td class="py-3 font-semibold" :class="item.deuda_total_usd > 0 ? 'text-neu-danger' : 'text-neu-success'">
                {{ formatUSD(item.deuda_total_usd) }}
              </td>
              <td class="py-3 text-neu-text-light">{{ formatVES(item.deuda_total_ves) }}</td>
              <td class="py-3 font-semibold text-neu-green">{{ formatUSD(item.saldo_favor_usd) }}</td>
              <td class="py-3 text-center">
                <EstadoPagoBadge :estado="item.estado" />
              </td>
            </tr>
            <tr v-if="matriz.length === 0">
              <td colspan="6" class="py-6 text-center text-neu-text-light">
                No hay apartamentos registrados aún.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>

    <!-- Modal de Cartelera de Morosidad PDF -->
    <CarteleraPdfModal
      v-model="mostrarModalPDF"
      :matriz="matriz"
      :tasa="tasaStore.tasaActual"
    />
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useToast } from 'vue-toastification'
import { AdminLayout } from '@/components/layout'
import { NeuCard } from '@/components/neumorph'
import { EstadoPagoBadge, CarteleraPdfModal } from '@/components/shared'
import { useTasaStore, useApartamentosStore } from '@/stores'
import { formatUSD, formatVES, formatTasa, formatFecha } from '@/utils'
import { tasaService } from '@/services'

const toast = useToast()
const tasaStore = useTasaStore()
const aptosStore = useApartamentosStore()

const mostrarModalPDF = ref(false)

const sincronizando = ref(false)
const matriz = computed(() => aptosStore.matrizDeudas || [])

const totalRecaudadoMes = ref(0)
const totalRecaudadoMesVES = computed(() => {
  return tasaStore.tasaActual ? totalRecaudadoMes.value * parseFloat(tasaStore.tasaActual) : 0
})

const deudaTotalUSD = computed(() => {
  return matriz.value.reduce((acc, curr) => acc + (parseFloat(curr.deuda_total_usd) || 0), 0)
})

const deudaTotalVES = computed(() => {
  return matriz.value.reduce((acc, curr) => acc + (parseFloat(curr.deuda_total_ves) || 0), 0)
})

const totalSolventes = computed(() => matriz.value.filter(a => a.estado === 'solvente').length)
const totalMorosos = computed(() => matriz.value.filter(a => a.estado === 'moroso').length)

onMounted(async () => {
  await Promise.all([
    tasaStore.cargarTasa(),
    aptosStore.cargarMatrizDeudas(),
  ])
})

async function sincronizarBCV() {
  sincronizando.value = true
  try {
    const { data } = await tasaService.sincronizar()
    tasaStore.tasaActual = data.tasa_usd_ves
    tasaStore.fecha = data.fecha
    toast.success('Tasa BCV sincronizada con éxito')
    await aptosStore.cargarMatrizDeudas()
  } catch (error) {
    toast.error('Error al sincronizar con el portal del BCV')
  } finally {
    sincronizando.value = false
  }
}
</script>
