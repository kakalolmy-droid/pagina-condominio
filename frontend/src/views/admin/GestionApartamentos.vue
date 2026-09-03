<template>
  <AdminLayout
    titulo="Padrón de Inmuebles y Cuotas Mensuales"
    subtitulo="Configuración de apartamentos, cuota fija mensual en USD y control de notificaciones"
  >
    <!-- Widget de Resumen Financiero de Cuotas -->
    <div class="mb-6">
      <NeuCard>
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h4 class="font-bold text-sm text-neu-green">Recaudación Mensual Estimada</h4>
            <p class="text-xs text-neu-text-light">
              Total proyectado sumando la cuota fija mensual de todos los apartamentos activos
            </p>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <span class="text-xs text-neu-text-light">Total Activos a Cobrar:</span>
              <p class="font-extrabold text-xl text-neu-green">
                {{ formatUSD(cuotasInfo.suma_cuotas_usd || 0) }}
              </p>
            </div>
            <span class="badge-success text-xs font-bold px-3 py-1.5 rounded-full">
              {{ cuotasInfo.apartamentos_activos || 0 }} de {{ cuotasInfo.total_apartamentos || 0 }} Inmuebles Activos
            </span>
          </div>
        </div>
      </NeuCard>
    </div>

    <!-- Barra de acciones y búsqueda -->
    <div class="flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
      <div class="w-full md:w-80">
        <input
          v-model="busqueda"
          type="text"
          placeholder="Buscar por número de apto, torre o piso..."
          class="input-neu text-sm"
        />
      </div>

      <NeuButton variant="primary" @click="abrirModalCrear">
        ➕ Registrar Apartamento
      </NeuButton>
    </div>

    <!-- Tabla de Apartamentos -->
    <NeuCard>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-neu-shadow-dark text-neu-text-light">
              <th class="pb-3 font-semibold">Inmueble / Apto</th>
              <th class="pb-3 font-semibold">Piso</th>
              <th class="pb-3 font-semibold">Torre</th>
              <th class="pb-3 font-semibold">Cuota Fija Mensual</th>
              <th class="pb-3 font-semibold">Propietario Asignado</th>
              <th class="pb-3 font-semibold">Saldo a Favor</th>
              <th class="pb-3 font-semibold text-center">Estado Notificación</th>
              <th class="pb-3 font-semibold text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="apto in aptosFiltrados"
              :key="apto.id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
              :class="{ 'opacity-60 bg-neu-bg-dark/30': !apto.activo }"
            >
              <td class="py-3 font-bold text-neu-green">
                Apto {{ apto.numero_apto }}
              </td>
              <td class="py-3 text-neu-text">{{ apto.piso || 'PB' }}</td>
              <td class="py-3 text-neu-text">{{ apto.torre }}</td>
              <td class="py-3 font-bold text-neu-green text-base">
                ${{ parseFloat(apto.alicuota || 15).toFixed(2) }} USD
              </td>
              <td class="py-3 text-neu-text">
                <span v-if="apto.propietario">
                  👤 {{ apto.propietario.nombre }} {{ apto.propietario.apellido }}
                </span>
                <span v-else class="text-xs text-neu-danger italic font-semibold">
                  ⚠️ Sin asignar
                </span>
              </td>
              <td class="py-3 font-semibold text-neu-green">
                {{ formatUSD(apto.saldo_favor_usd) }}
              </td>
              <td class="py-3 text-center">
                <span
                  class="text-xs font-bold px-3 py-1 rounded-full inline-block"
                  :class="apto.activo ? 'badge-success' : 'badge-danger'"
                >
                  {{ apto.activo ? '● Activo' : '○ Desactivado' }}
                </span>
              </td>
              <td class="py-3 text-center">
                <div class="flex items-center justify-center gap-2">
                  <!-- Botón Desactivar / Activar (Sin borrar datos) -->
                  <button
                    @click="alternarEstado(apto)"
                    class="px-2.5 py-1.5 rounded-neu-sm text-xs font-bold shadow-neu-sm hover:shadow-neu-inset transition-all cursor-pointer flex items-center gap-1"
                    :class="apto.activo ? 'bg-amber-600 text-white' : 'bg-emerald-700 text-white'"
                    :title="apto.activo ? 'Desactivar para que no reciba cobros ni avisos' : 'Reactivar cobros y avisos'"
                  >
                    <span>{{ apto.activo ? '⏸️ Desactivar' : '▶️ Reactivar' }}</span>
                  </button>

                  <button
                    @click="abrirModalEditar(apto)"
                    class="p-2 rounded-neu-sm hover:shadow-neu-inset text-neu-green transition-all"
                    title="Editar Cuota / Datos"
                  >
                    ✏️
                  </button>
                  <button
                    @click="confirmarEliminacion(apto)"
                    class="p-2 rounded-neu-sm hover:shadow-neu-inset text-neu-danger transition-all"
                    title="Eliminar de la Base de Datos"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="aptosFiltrados.length === 0">
              <td colspan="8" class="py-8 text-center text-neu-text-light">
                No hay apartamentos registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>

    <!-- Modal Crear / Editar Apartamento -->
    <NeuModal v-model="modalAbierto" :title="editandoId ? 'Editar Inmueble / Cuota' : 'Registrar Inmueble'">
      <form @submit.prevent="guardarApartamento" class="flex flex-col gap-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <NeuInput
            id="numero_apto"
            label="Número de Apto"
            v-model="form.numero_apto"
            placeholder="Ej. 2-5"
            required
          />
          <NeuInput
            id="piso"
            label="Piso"
            v-model="form.piso"
            placeholder="Ej. 2"
          />
          <NeuInput
            id="torre"
            label="Torre / Bloque"
            v-model="form.torre"
            placeholder="Principal"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NeuInput
            id="alicuota"
            label="Monto de Cuota Mensual ($ USD)"
            v-model="form.alicuota"
            type="number"
            step="0.01"
            min="0"
            placeholder="15.00"
            required
          />

          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium text-neu-text-light">Propietario Titular</label>
            <select v-model="form.propietario_id" class="input-neu" required>
              <option :value="null" disabled>Seleccionar propietario...</option>
              <option
                v-for="usuario in usuariosStore.lista"
                :key="usuario.id"
                :value="usuario.id"
              >
                {{ usuario.nombre }} {{ usuario.apellido }} ({{ usuario.cedula }})
              </option>
            </select>
          </div>
        </div>

        <div class="flex items-center gap-2 p-3 bg-neu-bg-dark rounded-neu-sm border border-neu-shadow-dark">
          <input type="checkbox" id="apto_activo" v-model="form.activo" class="w-4 h-4 cursor-pointer accent-neu-green" />
          <label for="apto_activo" class="text-xs font-semibold text-neu-text cursor-pointer">
            Inmueble Activo (Recibe avisos automáticos por WhatsApp y emite cuota mensual)
          </label>
        </div>

        <div class="flex justify-end gap-3 mt-4">
          <NeuButton type="button" @click="modalAbierto = false">
            Cancelar
          </NeuButton>
          <NeuButton variant="primary" type="submit" :loading="guardando">
            {{ editandoId ? 'Guardar Cambios' : 'Registrar' }}
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
import { NeuCard, NeuButton, NeuInput, NeuModal } from '@/components/neumorph'
import { useApartamentosStore, useUsuariosStore } from '@/stores'
import { apartamentosService } from '@/services'
import { formatUSD } from '@/utils'

const toast = useToast()
const aptosStore = useApartamentosStore()
const usuariosStore = useUsuariosStore()

const busqueda = ref('')
const modalAbierto = ref(false)
const editandoId = ref(null)
const guardando = ref(false)
const cuotasInfo = ref({ total_apartamentos: 0, apartamentos_activos: 0, suma_cuotas_usd: 0 })

const form = ref({
  numero_apto: '',
  piso: '',
  torre: 'Principal',
  alicuota: 15.00,
  activo: true,
  propietario_id: null,
})

const aptosFiltrados = computed(() => {
  const lista = aptosStore.lista || []
  if (!busqueda.value) return lista
  const q = busqueda.value.toLowerCase()
  return lista.filter(
    (a) =>
      a.numero_apto.toLowerCase().includes(q) ||
      (a.torre && a.torre.toLowerCase().includes(q)) ||
      (a.piso && a.piso.toLowerCase().includes(q))
  )
})

onMounted(async () => {
  await Promise.all([
    aptosStore.cargar(),
    usuariosStore.cargar(),
    verificarCuotas(),
  ])
})

async function verificarCuotas() {
  try {
    const { data } = await apartamentosService.sumaAlicuotas()
    cuotasInfo.value = data
  } catch (e) {
    console.error(e)
  }
}

function abrirModalCrear() {
  editandoId.value = null
  form.value = {
    numero_apto: '',
    piso: '',
    torre: 'Principal',
    alicuota: 15.00,
    activo: true,
    propietario_id: usuariosStore.lista[0]?.id || null,
  }
  modalAbierto.value = true
}

function abrirModalEditar(apto) {
  editandoId.value = apto.id
  form.value = {
    numero_apto: apto.numero_apto,
    piso: apto.piso || '',
    torre: apto.torre || 'Principal',
    alicuota: parseFloat(apto.alicuota || 15.00),
    activo: apto.activo !== false,
    propietario_id: apto.propietario_id,
  }
  modalAbierto.value = true
}

async function alternarEstado(apto) {
  try {
    await apartamentosService.toggleActivo(apto.id)
    apto.activo = !apto.activo
    toast.info(apto.activo ? `Apto ${apto.numero_apto} reactivado` : `Apto ${apto.numero_apto} desactivado de avisos y cobros`)
    await verificarCuotas()
  } catch (error) {
    toast.error('Error al cambiar estado del apartamento')
  }
}

async function guardarApartamento() {
  guardando.value = true
  try {
    if (editandoId.value) {
      await aptosStore.actualizar(editandoId.value, form.value)
      toast.success('Apartamento actualizado con éxito')
    } else {
      await aptosStore.crear(form.value)
      toast.success('Apartamento registrado con éxito')
    }
    modalAbierto.value = false
    await Promise.all([aptosStore.cargar(), verificarCuotas()])
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Error al guardar el apartamento')
  } finally {
    guardando.value = false
  }
}

async function confirmarEliminacion(apto) {
  if (confirm(`¿Eliminar definitivamente el apartamento ${apto.numero_apto}? (Se sugiere usar 'Desactivar' si solo desea pausar avisos)`)) {
    try {
      await aptosStore.eliminar(apto.id)
      toast.success('Apartamento eliminado')
      await verificarCuotas()
    } catch (error) {
      toast.error('Error al eliminar apartamento')
    }
  }
}
</script>
