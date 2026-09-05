<template>
  <component :is="authStore.isAdmin ? AdminLayout : PropietarioLayout" titulo="Mi Perfil" subtitulo="Gestión de datos personales y consulta protegida de inmueble">
    <div class="flex flex-col gap-6 max-w-5xl mx-auto w-full">
      <!-- ── Encabezado Neumórfico del Usuario ── -->
      <NeuCard>
        <div class="flex flex-col sm:flex-row items-center sm:items-start gap-4">
          <div class="w-16 h-16 rounded-full bg-neu-green text-white font-extrabold text-2xl flex items-center justify-center shadow-neu border-2 border-white/80 shrink-0">
            {{ perfil.nombre?.charAt(0) || 'U' }}
          </div>
          <div class="text-center sm:text-left flex-1">
            <div class="flex flex-col sm:flex-row sm:items-center gap-2">
              <h2 class="text-xl sm:text-2xl font-black text-neu-green tracking-tight">
                {{ perfil.nombre }} {{ perfil.apellido }}
              </h2>
              <span
                class="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider self-center sm:self-auto"
                :class="perfil.rol === 'admin' ? 'badge-info' : 'badge-success'"
              >
                {{ perfil.rol }}
              </span>
            </div>
            <p class="text-xs text-neu-text-light mt-1">
              Cédula: <strong class="text-neu-text">{{ perfil.cedula || '—' }}</strong> | Correo: <strong class="text-neu-text">{{ perfil.email }}</strong>
            </p>
          </div>
        </div>
      </NeuCard>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- ── SECCIÓN 1: DATOS PERSONALES EDITABLES (7 cols) ── -->
        <div class="lg:col-span-7 flex flex-col gap-6">
          <NeuCard>
            <div class="flex items-center gap-2 mb-4 pb-2 border-b border-neu-shadow-dark/40">
              <span class="text-xl">✏️</span>
              <div>
                <h3 class="text-base font-bold text-neu-green">Mis Datos Personales</h3>
                <p class="text-[11px] text-neu-text-light">Puedes actualizar tu nombre, teléfono WhatsApp y correo de contacto.</p>
              </div>
            </div>

            <form @submit.prevent="guardarDatosPersonales" class="flex flex-col gap-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <NeuInput
                  id="perfil_nombre"
                  label="Nombre"
                  v-model="form.nombre"
                  placeholder="Tu nombre"
                  required
                />
                <NeuInput
                  id="perfil_apellido"
                  label="Apellido"
                  v-model="form.apellido"
                  placeholder="Tu apellido"
                  required
                />
              </div>

              <div>
                <label class="block text-xs font-semibold text-neu-text mb-1">
                  WhatsApp / Teléfono <span class="text-neu-danger">*</span>
                </label>
                <input
                  id="perfil_whatsapp"
                  v-model="form.telefono_whatsapp"
                  type="text"
                  placeholder="+584120000000"
                  class="input-neu text-xs py-2.5 w-full"
                  required
                />
                <span class="text-[10px] text-neu-green font-semibold mt-1 block">
                  💡 Ejemplo: +584120000000 (Incluye el código de país +58)
                </span>
              </div>

              <NeuInput
                id="perfil_email"
                label="Correo Electrónico"
                v-model="form.email"
                type="email"
                placeholder="tu@correo.com"
                required
              />

              <!-- Separador Neumórfico -->
              <div class="mt-2 pt-4 border-t border-neu-shadow-dark/40">
                <div class="flex items-center gap-2 mb-3">
                  <span class="text-base">🔑</span>
                  <div>
                    <h4 class="text-xs font-bold text-neu-text uppercase tracking-wider">Cambiar Contraseña (Opcional)</h4>
                    <p class="text-[11px] text-neu-text-light">Deja estos campos vacíos si deseas conservar tu contraseña actual.</p>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <NeuInput
                    id="perfil_pwd_nueva"
                    label="Nueva Contraseña"
                    v-model="form.password"
                    type="password"
                    placeholder="••••••••"
                  />
                  <NeuInput
                    id="perfil_pwd_conf"
                    label="Confirmar Contraseña"
                    v-model="form.confirmPassword"
                    type="password"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <div v-if="errorGuardado" class="bg-red-50 border border-neu-danger text-neu-danger text-xs px-4 py-2.5 rounded-neu-sm mt-1">
                {{ errorGuardado }}
              </div>

              <div class="flex justify-end mt-2">
                <NeuButton
                  variant="primary"
                  type="submit"
                  :loading="guardando"
                  class="w-full sm:w-auto px-6 py-2.5"
                >
                  💾 Guardar Cambios
                </NeuButton>
              </div>
            </form>
          </NeuCard>
        </div>

        <!-- ── SECCIÓN 2: DATOS PROTEGIDOS DEL APARTAMENTO Y DEUDAS (5 cols) ── -->
        <div class="lg:col-span-5 flex flex-col gap-6">
          <NeuCard>
            <div class="flex items-center gap-2 mb-3 pb-2 border-b border-neu-shadow-dark/40">
              <span class="text-xl">🔒</span>
              <div>
                <h3 class="text-base font-bold text-neu-green">Inmueble y Balance Financiero</h3>
                <span class="text-[10px] font-bold text-amber-700 uppercase tracking-wider bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  Solo Lectura Protegido
                </span>
              </div>
            </div>

            <!-- Banner Informativo Explicativo de Inmutabilidad -->
            <div class="p-3 bg-amber-50/70 border border-amber-300/80 rounded-neu-sm text-xs text-amber-900 leading-relaxed mb-4">
              <div class="flex items-start gap-2">
                <span class="text-base leading-none">🛡️</span>
                <div>
                  <span class="font-bold block">Protección de Datos Inmobiliarios:</span>
                  <p class="text-[11px] text-amber-800/90 mt-0.5">
                    Por requerimientos normativos del condominio, los datos de tu apartamento, porcentaje de alícuota y balances de deuda <strong>no pueden ser modificados</strong> por el residente. Cualquier ajuste debe ser gestionado a través de la Junta de Condominio o Administración.
                  </p>
                </div>
              </div>
            </div>

            <!-- Datos del Apartamento con Candados 🔒 -->
            <div v-if="apartamento" class="flex flex-col gap-3">
              <div class="p-3 rounded-neu-sm bg-neu-bg-dark border border-neu-shadow-dark flex items-center justify-between">
                <div>
                  <span class="text-[10px] font-bold text-neu-text-light uppercase tracking-wider block">Apartamento Asignado</span>
                  <span class="text-sm font-extrabold text-neu-green">Apto {{ apartamento.numero_apto }}</span>
                </div>
                <span class="text-base text-neu-text-light" title="Campo protegido">🔒</span>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div class="p-2.5 rounded-neu-sm bg-neu-bg-dark border border-neu-shadow-dark flex items-center justify-between">
                  <div>
                    <span class="text-[9px] font-bold text-neu-text-light uppercase tracking-wider block">Torre</span>
                    <span class="text-xs font-bold text-neu-text">{{ apartamento.torre || 'Principal' }}</span>
                  </div>
                  <span class="text-xs text-neu-text-light">🔒</span>
                </div>

                <div class="p-2.5 rounded-neu-sm bg-neu-bg-dark border border-neu-shadow-dark flex items-center justify-between">
                  <div>
                    <span class="text-[9px] font-bold text-neu-text-light uppercase tracking-wider block">Piso</span>
                    <span class="text-xs font-bold text-neu-text">Piso {{ apartamento.piso || '1' }}</span>
                  </div>
                  <span class="text-xs text-neu-text-light">🔒</span>
                </div>
              </div>

              <div class="p-2.5 rounded-neu-sm bg-neu-bg-dark border border-neu-shadow-dark flex items-center justify-between">
                <div>
                  <span class="text-[9px] font-bold text-neu-text-light uppercase tracking-wider block">Alícuota Condominial</span>
                  <span class="text-xs font-bold text-neu-text">{{ formatAlicuota(apartamento.alicuota) }}%</span>
                </div>
                <span class="text-xs text-neu-text-light">🔒</span>
              </div>

              <div class="p-3 rounded-neu-sm bg-neu-bg-dark border border-neu-shadow-dark flex items-center justify-between">
                <div>
                  <span class="text-[10px] font-bold text-neu-text-light uppercase tracking-wider block">Meses Pendientes</span>
                  <span
                    class="text-xs font-black"
                    :class="(apartamento.meses_pendientes || 0) > 0 ? 'text-neu-danger' : 'text-neu-green'"
                  >
                    {{ (apartamento.meses_pendientes || 0) > 0 ? `${apartamento.meses_pendientes} mes(es) pendiente(s)` : '0 meses (Al día)' }}
                  </span>
                </div>
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="(apartamento.meses_pendientes || 0) > 0 ? 'badge-danger' : 'badge-success'"
                >
                  {{ (apartamento.meses_pendientes || 0) > 0 ? 'MOROSO' : 'SOLVENTE' }}
                </span>
              </div>

              <!-- Saldo a Favor si existe -->
              <div v-if="parseFloat(apartamento.saldo_favor_usd || 0) > 0" class="p-2.5 rounded-neu-sm bg-emerald-50 border border-emerald-300 text-xs text-emerald-900 flex justify-between items-center">
                <span>Billetera / Saldo a Favor:</span>
                <strong class="font-extrabold text-sm">{{ formatUSD(apartamento.saldo_favor_usd) }}</strong>
              </div>
            </div>

            <div v-else class="py-6 text-center text-neu-text-light text-xs">
              No tienes un apartamento asociado actualmente a tu usuario.
            </div>
          </NeuCard>
        </div>
      </div>
    </div>
  </component>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import PropietarioLayout from '@/components/layout/PropietarioLayout.vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import NeuCard from '@/components/neumorph/NeuCard.vue'
import NeuInput from '@/components/neumorph/NeuInput.vue'
import NeuButton from '@/components/neumorph/NeuButton.vue'
import { formatUSD } from '@/utils'

const authStore = useAuthStore()
const toast = useToast()

const perfil = ref({})
const apartamento = ref(null)
const guardando = ref(false)
const errorGuardado = ref('')

const form = ref({
  nombre: '',
  apellido: '',
  telefono_whatsapp: '',
  email: '',
  password: '',
  confirmPassword: '',
})

onMounted(async () => {
  await cargarDatosPerfil()
})

async function cargarDatosPerfil() {
  try {
    const data = await authStore.obtenerMiPerfil()
    perfil.value = data
    form.value.nombre = data.nombre || ''
    form.value.apellido = data.apellido || ''
    form.value.telefono_whatsapp = data.telefono_whatsapp || ''
    form.value.email = data.email || ''

    if (data.apartamentos && data.apartamentos.length > 0) {
      apartamento.value = data.apartamentos[0]
    }
  } catch (err) {
    console.error('Error al cargar perfil:', err)
    toast.error('No se pudieron cargar los datos de tu perfil.')
  }
}

function formatAlicuota(val) {
  if (!val) return '0.00'
  const num = parseFloat(val)
  return num < 1 ? (num * 100).toFixed(2) : num.toFixed(2)
}

async function guardarDatosPersonales() {
  errorGuardado.value = ''

  if (!form.value.nombre.trim() || !form.value.apellido.trim()) {
    errorGuardado.value = 'El nombre y apellido son obligatorios.'
    return
  }

  if (!form.value.telefono_whatsapp.trim()) {
    errorGuardado.value = 'El número de WhatsApp es obligatorio.'
    return
  }

  if (!form.value.email.trim()) {
    errorGuardado.value = 'El correo electrónico es obligatorio.'
    return
  }

  if (form.value.password) {
    if (form.value.password.length < 6) {
      errorGuardado.value = 'La nueva contraseña debe tener al menos 6 caracteres.'
      return
    }
    if (form.value.password !== form.value.confirmPassword) {
      errorGuardado.value = 'Las contraseñas no coinciden. Por favor verifícalas.'
      return
    }
  }

  guardando.value = true
  try {
    const payload = {
      nombre: form.value.nombre.trim(),
      apellido: form.value.apellido.trim(),
      telefono_whatsapp: form.value.telefono_whatsapp.trim(),
      email: form.value.email.trim(),
    }
    if (form.value.password) {
      payload.password = form.value.password
    }

    const actualizado = await authStore.actualizarMiPerfil(payload)
    perfil.value = actualizado
    form.value.password = ''
    form.value.confirmPassword = ''
    toast.success('¡Tus datos personales han sido actualizados con éxito!')
  } catch (err) {
    console.error('Error actualizando perfil:', err)
    const msg = err.response?.data?.detail || err.message || 'Error al guardar los datos del perfil.'
    errorGuardado.value = msg
  } finally {
    guardando.value = false
  }
}
</script>
