<template>
  <AdminLayout
    titulo="Padrón de Propietarios"
    subtitulo="Gestión de copropietarios, datos de contacto, estados y accesos"
  >
    <div class="flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
      <!-- Buscador -->
      <div class="w-full md:w-80">
        <input
          v-model="busqueda"
          type="text"
          placeholder="Buscar por nombre, cédula o email..."
          class="input-neu text-sm"
        />
      </div>

      <!-- Botón Nuevo Propietario -->
      <NeuButton variant="primary" @click="abrirModalCrear">
        ➕ Registrar Propietario
      </NeuButton>
    </div>

    <!-- Tabla de Propietarios -->
    <NeuCard>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-neu-shadow-dark text-neu-text-light">
              <th class="pb-3 font-semibold">Nombre y Apellido</th>
              <th class="pb-3 font-semibold">Cédula</th>
              <th class="pb-3 font-semibold">WhatsApp / Teléfono</th>
              <th class="pb-3 font-semibold">Correo Electrónico</th>
              <th class="pb-3 font-semibold text-center">Rol</th>
              <th class="pb-3 font-semibold text-center">Estado Notificaciones</th>
              <th class="pb-3 font-semibold text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="usuario in usuariosFiltrados"
              :key="usuario.id"
              class="border-b border-neu-bg-dark hover:bg-neu-bg-dark/50 transition-colors"
              :class="{ 'opacity-50 bg-neu-bg-dark/40': estaInactivo(usuario.id) }"
            >
              <td class="py-3 font-semibold text-neu-green">
                {{ usuario.nombre }} {{ usuario.apellido }}
              </td>
              <td class="py-3 text-neu-text">{{ usuario.cedula }}</td>
              <td class="py-3 text-neu-text">
                <a
                  :href="`https://wa.me/${usuario.telefono_whatsapp.replace(/[^0-9]/g, '')}`"
                  target="_blank"
                  class="text-neu-green hover:underline flex items-center gap-1"
                >
                  💬 {{ usuario.telefono_whatsapp }}
                </a>
              </td>
              <td class="py-3 text-neu-text-light">{{ usuario.email }}</td>
              <td class="py-3 text-center">
                <span :class="usuario.rol === 'admin' ? 'badge-danger' : (usuario.rol === 'junta' ? 'badge-warning' : 'badge-info')">
                  {{ usuario.rol.toUpperCase() }}
                </span>
              </td>
              <td class="py-3 text-center">
                <span
                  class="text-xs font-bold px-3 py-1 rounded-full inline-block"
                  :class="estaInactivo(usuario.id) ? 'badge-danger' : 'badge-success'"
                >
                  {{ estaInactivo(usuario.id) ? '○ Desactivado' : '● Activo' }}
                </span>
              </td>
              <td class="py-3 text-center">
                <div class="flex items-center justify-center gap-2">
                  <!-- Botón Desactivar / Reactivar Propietario -->
                  <button
                    @click="alternarEstado(usuario)"
                    class="px-2.5 py-1.5 rounded-neu-sm text-xs font-bold shadow-neu-sm hover:shadow-neu-inset transition-all cursor-pointer flex items-center gap-1"
                    :class="estaInactivo(usuario.id) ? 'bg-emerald-700 text-white' : 'bg-amber-600 text-white'"
                    :title="estaInactivo(usuario.id) ? 'Reactivar usuario e inmuebles' : 'Desactivar usuario e inmuebles para que no reciba avisos'"
                  >
                    <span>{{ estaInactivo(usuario.id) ? '▶️ Reactivar' : '⏸️ Desactivar' }}</span>
                  </button>

                  <button
                    @click="abrirModalEditar(usuario)"
                    class="p-2 rounded-neu-sm hover:shadow-neu-inset text-neu-green transition-all"
                    title="Editar Datos"
                  >
                    ✏️
                  </button>
                  <button
                    @click="confirmarEliminacion(usuario)"
                    class="p-2 rounded-neu-sm hover:shadow-neu-inset text-neu-danger transition-all"
                    title="Eliminar de la Base de Datos"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="usuariosFiltrados.length === 0">
              <td colspan="7" class="py-8 text-center text-neu-text-light">
                No se encontraron propietarios registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </NeuCard>

    <!-- Modal Crear / Editar Propietario -->
    <NeuModal v-model="modalAbierto" :title="editandoId ? 'Editar Propietario' : 'Registrar Nuevo Propietario'">
      <form @submit.prevent="guardarPropietario" class="flex flex-col gap-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NeuInput
            id="nombre"
            label="Nombre"
            v-model="form.nombre"
            placeholder="Ej. Carlos"
            required
          />
          <NeuInput
            id="apellido"
            label="Apellido"
            v-model="form.apellido"
            placeholder="Ej. Pérez"
            required
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NeuInput
            id="cedula"
            label="Cédula de Identidad"
            v-model="form.cedula"
            placeholder="V-12345678"
            required
          />
          <NeuInput
            id="telefono"
            label="Teléfono WhatsApp"
            v-model="form.telefono_whatsapp"
            placeholder="04141234567"
            required
          />
        </div>

        <NeuInput
          id="email"
          label="Correo Electrónico"
          v-model="form.email"
          type="email"
          placeholder="propietario@correo.com"
          required
        />

        <NeuInput
          id="password"
          label="Contraseña"
          v-model="form.password"
          type="password"
          :placeholder="editandoId ? 'Dejar en blanco para no cambiar' : '••••••••'"
          :required="!editandoId"
        />

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-neu-text-light">Rol en el Condominio</label>
          <select v-model="form.rol" class="input-neu">
            <option value="propietario">Propietario</option>
            <option value="junta">Miembro de la Junta</option>
            <option value="admin">Administrador Principal</option>
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
import { useUsuariosStore, useApartamentosStore } from '@/stores'
import { usuariosService, apartamentosService } from '@/services'

const toast = useToast()
const usuariosStore = useUsuariosStore()
const aptosStore = useApartamentosStore()

const busqueda = ref('')
const modalAbierto = ref(false)
const editandoId = ref(null)
const guardando = ref(false)

// Estado persistente sincronizado de usuarios e inmuebles inactivos
const inactivosIds = ref(new Set())

const form = ref({
  nombre: '',
  apellido: '',
  cedula: '',
  telefono_whatsapp: '',
  email: '',
  password: '',
  rol: 'propietario',
})

function cargarInactivosLocales() {
  try {
    const data = localStorage.getItem('alcatraz_usuarios_inactivos')
    if (data) {
      inactivosIds.value = new Set(JSON.parse(data))
    }
  } catch (e) {}
}

function guardarInactivosLocales() {
  try {
    localStorage.setItem('alcatraz_usuarios_inactivos', JSON.stringify([...inactivosIds.value]))
  } catch (e) {}
}

function estaInactivo(id) {
  return inactivosIds.value.has(id)
}

const usuariosFiltrados = computed(() => {
  const lista = usuariosStore.lista || []
  if (!busqueda.value) return lista
  const q = busqueda.value.toLowerCase()
  return lista.filter(
    (u) =>
      u.nombre.toLowerCase().includes(q) ||
      u.apellido.toLowerCase().includes(q) ||
      u.cedula.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q)
  )
})

onMounted(async () => {
  cargarInactivosLocales()
  await Promise.all([usuariosStore.cargar(), aptosStore.cargar()])
})

function abrirModalCrear() {
  editandoId.value = null
  form.value = {
    nombre: '',
    apellido: '',
    cedula: '',
    telefono_whatsapp: '',
    email: '',
    password: '',
    rol: 'propietario',
  }
  modalAbierto.value = true
}

function abrirModalEditar(usuario) {
  editandoId.value = usuario.id
  form.value = {
    nombre: usuario.nombre,
    apellido: usuario.apellido,
    cedula: usuario.cedula,
    telefono_whatsapp: usuario.telefono_whatsapp,
    email: usuario.email,
    password: '',
    rol: usuario.rol,
  }
  modalAbierto.value = true
}

async function alternarEstado(usuario) {
  const nuevoEstadoInactivo = !inactivosIds.value.has(usuario.id)
  if (nuevoEstadoInactivo) {
    inactivosIds.value.add(usuario.id)
    toast.info(`Propietario ${usuario.nombre} y sus apartamentos desactivados`)
  } else {
    inactivosIds.value.delete(usuario.id)
    toast.info(`Propietario ${usuario.nombre} y sus apartamentos reactivados`)
  }
  guardarInactivosLocales()

  // Sincronizar en cascada en apartamentos del usuario
  const aptosDelUsuario = (aptosStore.lista || []).filter(a => a.propietario_id === usuario.id)
  for (const apto of aptosDelUsuario) {
    try {
      await apartamentosService.actualizar(apto.id, { activo: !nuevoEstadoInactivo })
    } catch (e) {}
  }

  // Intento de actualización en backend
  try {
    await usuariosService.actualizar(usuario.id, { activo: !nuevoEstadoInactivo })
  } catch (e) {}
  await aptosStore.cargar()
}

async function guardarPropietario() {
  guardando.value = true
  try {
    if (editandoId.value) {
      await usuariosStore.actualizar(editandoId.value, form.value)
      toast.success('Propietario actualizado correctamente')
    } else {
      await usuariosStore.crear(form.value)
      toast.success('Propietario registrado con éxito')
    }
    modalAbierto.value = false
    await usuariosStore.cargar()
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Error al guardar el propietario')
  } finally {
    guardando.value = false
  }
}

async function confirmarEliminacion(usuario) {
  if (confirm(`¿Está seguro de eliminar al propietario ${usuario.nombre} ${usuario.apellido}? (Se sugiere usar 'Desactivar' para conservar su historial)`)) {
    try {
      await usuariosStore.eliminar(usuario.id)
      inactivosIds.value.delete(usuario.id)
      guardarInactivosLocales()
      toast.success('Propietario eliminado')
      await usuariosStore.cargar()
    } catch (error) {
      toast.error('Error al eliminar el propietario')
    }
  }
}
</script>
