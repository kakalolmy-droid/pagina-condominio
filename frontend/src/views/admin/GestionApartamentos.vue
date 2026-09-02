<template>
  <AdminLayout
    titulo="Padrón de Inmuebles y Alícuotas"
    subtitulo="Configuración de apartamentos, alícuotas porcentuales y asignación de propietarios"
  >
    <!-- Widget de Verificación de Suma de Alícuotas (100%) -->
    <div class="mb-6">
      <NeuCard>
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h4 class="font-bold text-sm text-neu-green">Control de Distribución de Alícuotas</h4>
            <p class="text-xs text-neu-text-light">
              La suma de todas las alícuotas debe totalizar exactamente 100% (1.0000)
            </p>
          </div>
          <div class="flex items-center gap-3">
            <div class="text-right">
              <span class="text-xs text-neu-text-light">Suma Total Actual:</span>
              <p class="font-bold text-lg" :class="alicuotasInfo.es_valida ? 'text-neu-success' : 'text-neu-danger'">
                {{ (alicuotasInfo.suma_alicuotas * 100).toFixed(2) }}% ({{ alicuotasInfo.suma_alicuotas }})
              </p>
            </div>
            <span
              class="text-xs font-semibold px-3 py-1.5 rounded-full"
              :class="alicuotasInfo.es_valida ? 'badge-success' : 'badge-danger'"
            >
              {{ alicuotasInfo.es_valida ? '✓ 100% Cuadrado' : '⚠️ Descuadrado' }}
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
              <th class="pb-3 font-semibold">Alícuota</th>
              <th class="pb-3 font-semibold">Propietario Asignado</th>
              <th class="pb-3 font-semibold">Saldo a Favor</th>
              <th class="pb-3 font-semibold text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="apto in aptosFiltrados"
              :key="apto.id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
            >
              <td class="py-3 font-bold text-neu-green">{{ apto.numero_apto }}</td>
              <td class="py-3 text-neu-text">{{ apto.piso || 'PB' }}</td>
              <td class="py-3 text-neu-text">{{ apto.torre }}</td>
              <td class="py-3 font-semibold text-neu-text">
                {{ (parseFloat(apto.alicuota) * 100).toFixed(2) }}%
                <span class="text-xs text-neu-text-light">({{ apto.alicuota }})</span>
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
                <div class="flex items-center justify-center gap-2">
                  <button
                    @click="abrirModalEditar(apto)"
                    class="p-2 rounded-neu-sm hover:shadow-neu-inset text-neu-green transition-all"
                    title="Editar"
                  >
                    ✏️
                  </button>
                  <button
                    @click="confirmarEliminacion(apto)"
                    class="p-2 rounded-neu-sm hover:shadow-neu-inset text-neu-danger transition-all"
                    title="Eliminar"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="aptosFiltrados.length === 0">
              <td colspan="7" class="py-8 text-center text-neu-text-light">
                No hay apartamentos registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>

    <!-- Modal Crear / Editar Apartamento -->
    <NeuModal v-model="modalAbierto" :title="editandoId ? 'Editar Apartamento' : 'Registrar Apartamento'">
      <form @submit.prevent="guardarApartamento" class="flex flex-col gap-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <NeuInput
            id="numero_apto"
            label="Número de Apto"
            v-model="form.numero_apto"
            placeholder="Ej. 1-A"
            required
          />
          <NeuInput
            id="piso"
            label="Piso"
            v-model="form.piso"
            placeholder="Ej. 1"
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
            label="Alícuota Decimal (Ej. 0.025 para 2.50%)"
            v-model="form.alicuota"
            type="number"
            step="0.0001"
            min="0.0001"
            max="1"
            placeholder="0.0250"
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
const alicuotasInfo = ref({ total_apartamentos: 0, suma_alicuotas: 0, es_valida: true })

const form = ref({
  numero_apto: '',
  piso: '',
  torre: 'Principal',
  alicuota: '',
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
    verificarAlicuotas(),
  ])
})

async function verificarAlicuotas() {
  try {
    const { data } = await apartamentosService.sumaAlicuotas()
    alicuotasInfo.value = data
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
    alicuota: '',
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
    alicuota: apto.alicuota,
    propietario_id: apto.propietario_id,
  }
  modalAbierto.value = true
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
    await verificarAlicuotas()
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Error al guardar el apartamento')
  } finally {
    guardando.value = false
  }
}

async function confirmarEliminacion(apto) {
  if (confirm(`¿Eliminar el apartamento ${apto.numero_apto}?`)) {
    try {
      await aptosStore.eliminar(apto.id)
      toast.success('Apartamento eliminado')
      await verificarAlicuotas()
    } catch (error) {
      toast.error('Error al eliminar apartamento')
    }
  }
}
</script>
