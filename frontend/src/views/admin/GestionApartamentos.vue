<template>
  <AdminLayout
    titulo="Padrón de Inmuebles y Cuotas"
    subtitulo="Configuración de apartamentos, cuota mensual en USD, meses pendientes y control de notificaciones"
  >
    <!-- Widget de Resumen Financiero -->
    <div class="mb-6">
      <NeuCard>
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h4 class="font-bold text-sm text-neu-green">Total de Deuda por Cobrar</h4>
            <p class="text-xs text-neu-text-light">
              Total proyectado sumando (Cuota Mensual × Meses Pendientes) de todos los apartamentos activos
            </p>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <span class="text-xs text-neu-text-light">Deuda Total Activa:</span>
              <p class="font-extrabold text-xl text-neu-green">
                {{ formatUSD(totalDeudaGeneral) }}
              </p>
            </div>
            <span class="badge-success text-xs font-bold px-3 py-1.5 rounded-full">
              {{ aptosActivos.length }} de {{ (aptosStore.lista || []).length }} Inmuebles Activos
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

      <div class="flex items-center gap-2.5 flex-wrap w-full md:w-auto justify-end">
        <!-- Botón de Simulación de Cambio de Mes -->
        <button
          type="button"
          @click="simularAvanceMes"
          :disabled="simulando"
          class="px-3.5 py-2 rounded-neu-sm bg-neu-bg shadow-neu-sm hover:shadow-neu text-xs font-bold text-neu-green border border-white/60 flex items-center gap-1.5 cursor-pointer transition-all"
          title="Simular paso al siguiente mes sumando +1 mes de cuota a todos los apartamentos activos"
        >
          <span>📅</span>
          <span>{{ simulando ? 'Simulando...' : 'Simular Fin de Mes (+1 Cuota)' }}</span>
        </button>

        <button
          v-if="seHaSimulado"
          type="button"
          @click="revertirSimulacion"
          :disabled="simulando"
          class="px-3 py-2 rounded-neu-sm bg-neu-bg shadow-neu-sm hover:shadow-neu text-xs font-bold text-neu-text-light hover:text-neu-danger border border-white/60 flex items-center gap-1 cursor-pointer transition-all"
          title="Deshacer el mes de prueba sumado"
        >
          <span>↩️</span>
          <span>Deshacer</span>
        </button>

        <NeuButton variant="primary" @click="abrirModalCrear">
          ➕ Registrar Apartamento
        </NeuButton>
      </div>
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
              <th class="pb-3 font-semibold">Cuota Mensual</th>
              <th class="pb-3 font-semibold text-center">Meses Pendientes</th>
              <th class="pb-3 font-semibold">Total Adeudado</th>
              <th class="pb-3 font-semibold">Propietario Asignado</th>
              <th class="pb-3 font-semibold text-center">Estado Notificaciones</th>
              <th class="pb-3 font-semibold text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="apto in aptosFiltrados"
              :key="apto.id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
              :class="{ 'opacity-50 bg-neu-bg-dark/40': estaInactivo(apto.id, apto.propietario_id) }"
            >
              <td class="py-3 font-bold text-neu-green">
                Apto {{ apto.numero_apto }}
              </td>
              <td class="py-3 text-neu-text">{{ apto.piso || 'PB' }}</td>
              <td class="py-3 text-neu-text">{{ apto.torre }}</td>
              <td class="py-3 font-semibold text-neu-text">
                ${{ parseFloat(apto.alicuota || 15).toFixed(2) }} USD
              </td>
              <td class="py-3 text-center">
                <span class="font-bold px-2.5 py-1 rounded-full text-xs" :class="(apto.meses_pendientes || 0) > 0 ? 'badge-danger' : 'badge-success'">
                  {{ apto.meses_pendientes || 0 }} mes(es)
                </span>
              </td>
              <td class="py-3 font-extrabold text-base" :class="(apto.meses_pendientes || 0) > 0 ? 'text-neu-danger' : 'text-neu-success'">
                ${{ (parseFloat(apto.alicuota || 15) * (apto.meses_pendientes || 0)).toFixed(2) }} USD
              </td>
              <td class="py-3 text-neu-text">
                <span v-if="apto.propietario">
                  👤 {{ apto.propietario.nombre }} {{ apto.propietario.apellido }}
                </span>
                <span v-else class="text-xs text-neu-danger italic font-semibold">
                  ⚠️ Sin asignar
                </span>
              </td>
              <td class="py-3 text-center">
                <span
                  class="text-xs font-bold px-3 py-1 rounded-full inline-block"
                  :class="estaInactivo(apto.id, apto.propietario_id) ? 'badge-danger' : 'badge-success'"
                >
                  {{ estaInactivo(apto.id, apto.propietario_id) ? '○ Desactivado' : '● Activo' }}
                </span>
              </td>
              <td class="py-3 text-center">
                <div class="flex items-center justify-center gap-2">
                  <!-- Botón Desactivar / Activar (Sin borrar datos) -->
                  <button
                    @click="alternarEstado(apto)"
                    class="px-2.5 py-1.5 rounded-neu-sm text-xs font-bold shadow-neu-sm hover:shadow-neu-inset transition-all cursor-pointer flex items-center gap-1"
                    :class="estaInactivo(apto.id, apto.propietario_id) ? 'bg-emerald-700 text-white' : 'bg-amber-600 text-white'"
                    :title="estaInactivo(apto.id, apto.propietario_id) ? 'Reactivar cobros y avisos' : 'Desactivar para que no reciba cobros ni avisos'"
                  >
                    <span>{{ estaInactivo(apto.id, apto.propietario_id) ? '▶️ Reactivar' : '⏸️ Desactivar' }}</span>
                  </button>

                  <button
                    @click="abrirModalEditar(apto)"
                    class="p-2 rounded-neu-sm hover:shadow-neu-inset text-neu-green transition-all"
                    title="Editar Cuota / Meses Pendientes"
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
              <td colspan="9" class="py-8 text-center text-neu-text-light">
                No hay apartamentos registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>

    <!-- Modal Crear / Editar Apartamento -->
    <NeuModal v-model="modalAbierto" :title="editandoId ? 'Editar Inmueble y Deuda' : 'Registrar Inmueble'">
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
            label="Cuota Mensual ($ USD)"
            v-model="form.alicuota"
            type="number"
            step="0.01"
            min="0"
            placeholder="15.00"
            required
          />

          <NeuInput
            id="meses_pendientes"
            label="Meses Pendientes de Pago"
            v-model="form.meses_pendientes"
            type="number"
            min="0"
            placeholder="1"
            required
          />
        </div>

        <!-- Previsualización del cálculo -->
        <div class="p-3 bg-neu-bg-dark rounded-neu-sm flex justify-between items-center">
          <span class="text-xs text-neu-text-light font-semibold">Total Deuda Calculada:</span>
          <span class="text-base font-extrabold text-neu-green">
            ${{ ((parseFloat(form.alicuota) || 0) * (parseInt(form.meses_pendientes) || 0)).toFixed(2) }} USD
          </span>
        </div>

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
import { apartamentosService, usuariosService } from '@/services'
import { formatUSD } from '@/utils'

const toast = useToast()
const aptosStore = useApartamentosStore()
const usuariosStore = useUsuariosStore()

const busqueda = ref('')
const modalAbierto = ref(false)
const editandoId = ref(null)
const guardando = ref(false)
const simulando = ref(false)
const seHaSimulado = ref(false)

// Sincronización persistente
const inactivosAptosIds = ref(new Set())
const inactivosUsersIds = ref(new Set())

const form = ref({
  numero_apto: '',
  piso: '',
  torre: 'Principal',
  alicuota: 15.00,
  meses_pendientes: 1,
  propietario_id: null,
})

function cargarInactivosLocales() {
  try {
    const dataAptos = localStorage.getItem('alcatraz_aptos_inactivos')
    if (dataAptos) inactivosAptosIds.value = new Set(JSON.parse(dataAptos))
    const dataUsers = localStorage.getItem('alcatraz_usuarios_inactivos')
    if (dataUsers) inactivosUsersIds.value = new Set(JSON.parse(dataUsers))
  } catch (e) {}
}

function guardarInactivosLocales() {
  try {
    localStorage.setItem('alcatraz_aptos_inactivos', JSON.stringify([...inactivosAptosIds.value]))
    localStorage.setItem('alcatraz_usuarios_inactivos', JSON.stringify([...inactivosUsersIds.value]))
  } catch (e) {}
}

function estaInactivo(aptoId, propId) {
  return inactivosAptosIds.value.has(aptoId) || (propId && inactivosUsersIds.value.has(propId))
}

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

const aptosActivos = computed(() => {
  return (aptosStore.lista || []).filter(a => !estaInactivo(a.id, a.propietario_id))
})

const totalDeudaGeneral = computed(() => {
  return aptosActivos.value.reduce((acc, a) => {
    const cuota = parseFloat(a.alicuota) || 15.0
    const meses = parseInt(a.meses_pendientes) || 0
    return acc + (cuota * meses)
  }, 0)
})

onMounted(async () => {
  cargarInactivosLocales()
  await Promise.all([
    aptosStore.cargar(),
    usuariosStore.cargar(),
  ])

  // Asegurar persistencia en el backend Render de cualquier apartamento desactivado previamente
  for (const a of (aptosStore.lista || [])) {
    if (estaInactivo(a.id, a.propietario_id) && a.activo) {
      apartamentosService.actualizar(a.id, { activo: false }).catch(() => {})
      if (a.propietario_id) {
        usuariosService.actualizar(a.propietario_id, { activo: false }).catch(() => {})
      }
    }
  }
})

function abrirModalCrear() {
  editandoId.value = null
  form.value = {
    numero_apto: '',
    piso: '',
    torre: 'Principal',
    alicuota: 15.00,
    meses_pendientes: 1,
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
    meses_pendientes: parseInt(apto.meses_pendientes !== undefined ? apto.meses_pendientes : 1),
    propietario_id: apto.propietario_id,
  }
  modalAbierto.value = true
}

async function alternarEstado(apto) {
  const inactivoActualmente = estaInactivo(apto.id, apto.propietario_id)
  const nuevoEstadoInactivo = !inactivoActualmente

  if (nuevoEstadoInactivo) {
    inactivosAptosIds.value.add(apto.id)
    if (apto.propietario_id) inactivosUsersIds.value.add(apto.propietario_id)
    toast.info(`Apto ${apto.numero_apto} y propietario desactivados`)
  } else {
    inactivosAptosIds.value.delete(apto.id)
    if (apto.propietario_id) inactivosUsersIds.value.delete(apto.propietario_id)
    toast.info(`Apto ${apto.numero_apto} y propietario reactivados`)
  }
  guardarInactivosLocales()

  // Sincronizar en backend
  try {
    await apartamentosService.actualizar(apto.id, { activo: !nuevoEstadoInactivo })
    if (apto.propietario_id) {
      await usuariosService.actualizar(apto.propietario_id, { activo: !nuevoEstadoInactivo })
    }
    await aptosStore.cargar()
    await usuariosStore.cargar()
  } catch (e) {
    console.error('Error sincronizando estado:', e)
  }
}

async function guardarApartamento() {
  guardando.value = true
  try {
    if (editandoId.value) {
      await aptosStore.actualizar(editandoId.value, form.value)
      toast.success('Apartamento y estado de cuenta actualizados')
    } else {
      await aptosStore.crear(form.value)
      toast.success('Apartamento registrado con éxito')
    }
    modalAbierto.value = false
    await aptosStore.cargar()
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
      inactivosAptosIds.value.delete(apto.id)
      guardarInactivosLocales()
      toast.success('Apartamento eliminado')
      await aptosStore.cargar()
    } catch (error) {
      toast.error('Error al eliminar apartamento')
    }
  }
}

async function simularAvanceMes() {
  const confirmacion = confirm(
    "¿Deseas simular el avance al siguiente mes?\n\nEsto generará automáticamente los nuevos recibos oficiales del período y sumará 1 mes de cuota pendiente a todos los apartamentos activos."
  )
  if (!confirmacion) return

  simulando.value = true
  try {
    const res = await apartamentosService.simularAvanceMes()
    toast.success(res.data?.mensaje || "¡Mes avanzado con éxito! Recibos y deudas actualizados.")
    seHaSimulado.value = true
    await aptosStore.cargar()
  } catch (e) {
    toast.error("Error al simular el cambio de mes")
  } finally {
    simulando.value = false
  }
}

async function revertirSimulacion() {
  simulando.value = true
  try {
    const res = await apartamentosService.revertirMes()
    toast.info(res.data?.mensaje || "Mes revertido correctamente.")
    seHaSimulado.value = false
    await aptosStore.cargar()
  } catch (e) {
    toast.error("Error al revertir simulación")
  } finally {
    simulando.value = false
  }
}
</script>
